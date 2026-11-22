# -*- coding: utf-8 -*-
import sys, os, re, subprocess, random
from html.parser import HTMLParser
from urllib.parse import unquote, urlparse
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import TOC

FLAT = os.environ.get('GA_FLAT_OUT')
DOC = (FLAT.rstrip('/') + '/') if FLAT else 'D:/Documentation/'
PATH = DOC + 'giao-an-theo-mon.html'
t = open(PATH, encoding='utf-8').read()
err = []

VOID = {'meta', 'link', 'input', 'br', 'hr', 'img'}


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.ids = []
        self.hrefs = []
        self.cb = []
        self.counts = {}
        self.script = []
        self._in_script = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.counts[tag] = self.counts.get(tag, 0) + 1
        if 'id' in a:
            self.ids.append(a['id'])
        if tag == 'a' and 'href' in a:
            self.hrefs.append(a['href'])
        if tag == 'input' and a.get('type') == 'checkbox':
            self.cb.append(a.get('data-id'))
        if tag == 'script':
            self._in_script = True
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == 'script':
            self._in_script = False
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            err.append('Đóng thẻ sai: </%s> trong khi đang mở %s (dòng %s)' % (tag, self.stack[-3:], self.getpos()[0]))
            if tag in self.stack:
                while self.stack and self.stack[-1] != tag:
                    self.stack.pop()
                self.stack.pop()
        else:
            self.stack.pop()

    def handle_data(self, data):
        if self._in_script:
            self.script.append(data)


p = P()
p.feed(t)
if p.stack:
    err.append('Thẻ chưa đóng: %s' % p.stack)
dup = {i for i in p.ids if p.ids.count(i) > 1}
if dup:
    err.append('id trùng: %s' % list(dup)[:10])
_s, _d = common.all_data()
_wk, _ = common.schedule(_d)
NDAY = sum(len(x) for x in _d.values())
if len(p.cb) != NDAY or len(set(p.cb)) != NDAY:
    err.append('checkbox: %d (duy nhất %d), mong %d' % (len(p.cb), len(set(p.cb)), NDAY))
for k in ('details', 'div', 'ul', 'ol', 'li', 'table', 'p'):
    pass
if p.counts.get('details') != len(_wk):
    err.append('số tuần (details) = %s' % p.counts.get('details'))

# --- liên kết
EXT_OK = {
    'https://github.com/mit-pdos/xv6-public', 'https://github.com/mit-pdos/xv6-riscv',
    'https://elixir.bootlin.com/linux/v2.6.34/source/kernel/sched_fair.c', 'https://elixir.bootlin.com/linux/v2.6.34/source/kernel/sched.c',
    'https://go.dev/doc/', 'https://go.dev/dl/', 'https://docs.docker.com/', 'https://kubernetes.io/docs/home/',
    'https://kubernetes.io/docs/concepts/overview/components/', 'https://kind.sigs.k8s.io/',
    'https://www.rfc-editor.org/rfc/rfc9293', 'https://www.rfc-editor.org/rfc/rfc9000', 'https://www.rfc-editor.org/rfc/rfc9114',
    'https://www.rfc-editor.org/rfc/rfc8446', 'https://www.kernel.org/doc/html/latest/networking/index.html',
    'https://raft.github.io/raft.pdf', 'https://pdos.csail.mit.edu/6.824/',
    'https://www.postgresql.org/docs/current/',
}
import html as H
ext = set()
local_pdf = {}
anch_html = []
for h in p.hrefs:
    h = H.unescape(h)
    if h.startswith('http'):
        ext.add(h)
        if h not in EXT_OK:
            err.append('URL ngoài chưa kiểm: %s' % h)
    elif h.startswith('#'):
        if h[1:] not in p.ids:
            err.append('neo nội bộ không tồn tại: %s' % h)
    else:
        base, _, frag = h.partition('#')
        fp = DOC + unquote(base)
        if not os.path.exists(fp):
            err.append('file không tồn tại: %s' % fp)
        if base.endswith('.pdf'):
            local_pdf.setdefault(base, []).append(frag)
        elif base.endswith('.html') and frag:
            anch_html.append((base, frag))
print('liên kết ngoài:', len(ext), '| PDF cục bộ:', len(local_pdf), '| neo html:', len(anch_html))
cache = {}
for base, frag in anch_html:
    if base not in cache:
        cache[base] = open(DOC + base, encoding='utf-8').read()
    if not re.search(r'id="%s"' % re.escape(frag), cache[base]):
        err.append('neo %s#%s không có trong file đích' % (base, frag))

# --- JS
js = ''.join(p.script)
jp = os.path.join(common.SP, 'out_ga.js')
open(jp, 'w', encoding='utf-8').write(js)
r = subprocess.run(['node', '--check', jp], capture_output=True, text=True)
if r.returncode != 0:
    err.append('node --check lỗi: %s' % r.stderr[:400])
else:
    print('node --check: OK')

# --- mỗi ngày đủ trường
nday = t.count('class="day s-')
for lab in ('Đọc', 'Nắm được khi đọc xong', 'Thực hành', 'Tự kiểm (trả lời miệng, không nhìn tài liệu)', 'Vì sao / nối từ bài trước'):
    n = t.count('>%s</span>' % lab)
    if n != nday:
        err.append('nhãn "%s": %d != %d ngày' % (lab, n, nday))
print('ngày:', nday)
print('--- ERR', len(err))
for e in err:
    print(' ', e)
sys.exit(1 if err else 0)
