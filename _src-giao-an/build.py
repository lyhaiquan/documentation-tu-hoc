# -*- coding: utf-8 -*-
import sys, os, re, html, json
from urllib.parse import quote
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import TOC, META, DENSE, SPECIAL

OUT = 'D:/Documentation/giao-an-theo-mon.html'
subj, days = common.all_data()
weeks, ptr = common.schedule(days)
SUB = common.SUBJECTS

COL = {  # sáng / tối
    'LIN': ('#1b6b4a', '#5fcf9f'), 'SYS': ('#7a3fb5', '#c39bf0'), 'KER': ('#b4530a', '#f0a860'),
    'NET': ('#0c6e9c', '#6cc4ee'), 'GOL': ('#7a7a00', '#d8d85a'), 'CON': ('#a8324a', '#f08a9e'),
    'K8S': ('#3a54b4', '#8fa4f5'), 'DIS': ('#107a7a', '#5fd0d0'),
}
TAGTXT = {
    'root': ('cần sudo', 'Cần quyền root (sudo). Chỉ làm trong máy của bạn.'),
    'kvm': ('cần KVM', 'Cần /dev/kvm (kiểm ở LIN-01).'),
    'cgroup-v2': ('cgroup v2', 'Cần cgroup v2 (kiểm ở LIN-01: stat -fc %T /sys/fs/cgroup).'),
    'perf': ('đo hiệu năng', 'Bài đo: kết quả phụ thuộc máy; có thể cần perf_event_paranoid thấp.'),
    'cẩn-thận': ('cẩn thận', 'Thao tác có thể làm hỏng dữ liệu nếu gõ sai: chỉ dùng file ảnh/đĩa thử, KHÔNG chạm ổ Windows.'),
    'go': ('cần Go', 'Dùng Go: đã học ở môn GOL.'),
    'k8s': ('cần K8S', 'Dùng cụm kind (môn K8S).'),
    'kiểm-máy': ('kiểm máy', 'Ngày kiểm tra cấu hình máy.'),
}


def esc(s):
    return html.escape(s, quote=True)


def md(s):
    s = esc(s)
    return re.sub(r'`([^`]+)`', r'<code>\1</code>', s)


def pdf_href(code, page=None):
    rel = TOC[code]['path']
    h = '/'.join(quote(p, safe='') for p in rel.split('/'))
    return h + ('#page=%d' % page if page else '')


def rel_link(h):
    return h  # liên kết tương đối (lo-trinh-c.html#G3 ...)



CHAP = re.compile(r'^(\[Trial version\]\s*)?(Chapter\s+\d+|\d+\s*[–:\-]\s|\d+\s+[A-Z]|Part\s|Appendix|[A-Z]\.\s|Exercises|Summary|Wrapping Up|Index|Further Reading|Extra Credit|Summing Up)')


def clean(s):
    return re.sub(r'^\[Trial version\]\s*', '', s).strip()


def secs(code, p1, p2):
    ents = [(l, clean(tt), pg) for l, tt, pg in TOC[code]['toc']
            if l >= 2 and not CHAP.match(tt.strip()) and not clean(tt).endswith(('Summary', 'Exercises'))]
    chap_pages = {pg for l, tt, pg in TOC[code]['toc'] if CHAP.match(tt.strip())}
    inr = [e for e in ents if p1 <= e[2] <= p2]
    if not inr:
        return ''
    minl = min(e[0] for e in inr)
    sel = [e for e in inr if e[0] == minl]
    out = []
    if sel[0][2] > p1 and p1 not in chap_pages:
        prev = [e for e in ents if e[2] < p1 and e[0] == minl]
        if prev:
            out.append('(tiếp) ' + prev[-1][1])
    seen = set()
    for e in sel:
        if e[1] in seen:
            continue
        seen.add(e[1])
        out.append('%s (tr.%d)' % (e[1], e[2]))
    if len(out) > 12:
        out = out[:12] + ['… +%d mục' % (len(out) - 12)]
    return '<div class="secs"><span class="lb2">Gồm</span> %s</div>' % ' · '.join(esc(x) for x in out)


def read_li(rd):
    code, label, p1, p2 = rd[0], rd[1], rd[2], rd[3]
    if code in SPECIAL:
        url = rd[4] if len(rd) > 4 else None
        name = {'WEB': 'Web', 'MAN': 'Trong máy', 'HW': 'Hard Way'}[code]
        inner = '<span class="bk">%s</span> %s' % (name, md(label))
        if url:
            inner = '<a href="%s" target="_blank" rel="noopener">%s</a>' % (esc(url), inner)
        return '<li>%s</li>' % inner
    nm = META[code][0]
    pg = 'tr.%d–%d' % (p1, p2) if p2 != p1 else 'tr.%d' % p1
    return ('<li><a href="%s" target="_blank" rel="noopener"><span class="bk">%s</span></a> %s <span class="pg">%s</span>%s</li>'
            % (esc(pdf_href(code, p1)), esc(code), md(label), pg, secs(code, p1, p2)))


def day_html(c, i, d, wi, wd):
    ident = '%s-%02d' % (c, i)
    tags = ''.join('<span class="tg" title="%s">%s</span>' % (esc(TAGTXT[t][1]), esc(TAGTXT[t][0])) for t in d.get('tags', []))
    first = ''
    if i == 1:
        pre = subj[c]['prereq']
        first = '<p class="fst"><b>Mở môn %s.</b> %s</p>' % (esc(subj[c]['name']), md(subj[c]['need']))
    reads = ''.join(read_li(r) for r in d['r'])
    grasp = ''.join('<li>%s</li>' % md(x) for x in d['g'])
    xs = ''
    if d.get('x'):
        items = []
        for lab, href in d['x']:
            if href:
                ext = href.startswith('http')
                items.append('<a href="%s"%s>%s</a>' % (esc(href), ' target="_blank" rel="noopener"' if ext else '', esc(lab)))
            else:
                items.append('<span>%s</span>' % esc(lab))
        xs = '<div class="xl"><span class="lb">Liên quan</span> %s</div>' % ' · '.join(items)
    return (
        '<div class="day s-%s" id="d-%s" data-w="%d" data-d="%d" data-s="%s">'
        '<label class="ck"><input type="checkbox" data-id="%s" aria-label="Đã học %s"></label>'
        '<div class="wd"><b>%s</b><span class="dt"></span></div>'
        '<div class="bd">'
        '<div class="hd"><span class="chip">%s</span><span class="no">%s</span><b class="tt">%s</b>%s</div>'
        '%s<p class="why"><span class="lb">Vì sao / nối từ bài trước</span> %s</p>'
        '<div class="rd"><span class="lb">Đọc</span><ul>%s</ul></div>'
        '<div class="gr"><span class="lb">Nắm được khi đọc xong</span><ul>%s</ul></div>'
        '<div class="lab"><span class="lb">Thực hành</span> %s</div>'
        '<div class="q"><span class="lb">Tự kiểm (trả lời miệng, không nhìn tài liệu)</span> %s</div>'
        '%s</div></div>'
    ) % (c, ident, wi, wd, c, ident, ident, ['T2', 'T3', 'T4', 'T5', 'T6', 'T7'][wd],
         esc(subj[c]['name']), ident, md(d['t']), tags, first, md(d['why']), reads, grasp, md(d['lab']), md(d['q']), xs)


# ---- tuần
week_html = []
for wi, wk in enumerate(weeks, 1):
    subs = []
    for c, _ in wk:
        if c not in subs:
            subs.append(c)
    rows = []
    qs = []
    for wd, (c, idx) in enumerate(wk):
        d = days[c][idx]
        rows.append(day_html(c, idx + 1, d, wi, wd))
        qs.append('<li><span class="no">%s-%02d</span> %s</li>' % (c, idx + 1, md(d['q'])))
    sun = ('<div class="sun" data-w="%d"><div class="wd"><b>CN</b><span class="dt"></span></div><div class="bd">'
           '<div class="hd"><b class="tt">Ôn tuần %d</b></div>'
           '<p class="why">Không học bài mới. Trả lời miệng các câu tự kiểm của tuần (không nhìn tài liệu, không hỏi AI); câu nào bí thì đánh dấu để đọc lại đúng đoạn. Viết ghi chú tuần (5–10 câu) và bù phần còn nợ; nợ quá 2 ngày thì lùi cả lịch một tuần, không học dồn.</p>'
           '<ol class="qs">%s</ol></div></div>') % (wi, wi, ''.join(qs))
    ids = ' + '.join(esc(c) for c in subs)
    week_html.append(
        '<details class="wk" id="w-%d" data-w="%d"><summary><span class="n">Tuần %d</span>'
        '<span class="sb">%s</span><span class="rg"></span><span class="pc"></span></summary>'
        '<div class="in">%s%s</div></details>' % (wi, wi, wi, ids, ''.join(rows), sun))

# ---- thẻ môn
first_week, last_week = {}, {}
for wi, wk in enumerate(weeks, 1):
    for c, _ in wk:
        first_week.setdefault(c, wi)
        last_week[c] = wi
book_pages = {}
subj_books = {c: {} for c in SUB}
for c in SUB:
    for d in days[c]:
        for rd in d['r']:
            if rd[0] in SPECIAL:
                continue
            n = rd[3] - rd[2] + 1
            book_pages[rd[0]] = book_pages.get(rd[0], 0) + n
            subj_books[c][rd[0]] = subj_books[c].get(rd[0], 0) + n

cards = []
for c in SUB:
    s = subj[c]
    bk = ', '.join('%s (%d tr.)' % (k, v) for k, v in sorted(subj_books[c].items(), key=lambda kv: -kv[1]))
    pre = ', '.join(subj[p]['name'] for p in s['prereq']) or 'không'
    cards.append(
        '<div class="sc s-%s"><div class="sh"><b>%s</b><span class="nm">%s</span></div>'
        '<p>%s</p><p class="mt"><b>%d ngày</b> · tuần %d–%d · tiên quyết: %s</p>'
        '<p class="mt">Sách: %s</p></div>' % (c, esc(c), esc(s['name']), md(s['goal']), len(days[c]), first_week[c], last_week[c], esc(pre), esc(bk)))

# ---- ma trận thời gian
mat = ['<div class="tw"><table class="mx"><thead><tr><th>Môn</th>%s</tr></thead><tbody>' % ''.join('<th>%d</th>' % w for w in range(1, len(weeks) + 1))]
for c in SUB:
    row = ['<tr class="s-%s"><th>%s</th>' % (c, esc(c))]
    for wi, wk in enumerate(weeks, 1):
        n = sum(1 for cc, _ in wk if cc == c)
        row.append('<td class="%s">%s</td>' % ('on' if n else '', n if n else ''))
    row.append('</tr>')
    mat.append(''.join(row))
mat.append('</tbody></table></div>')

# ---- thư viện
lib = ['<div class="tw"><table><thead><tr><th>Mã</th><th>Sách (mở PDF)</th><th>Tác giả · năm</th><th>PDF</th><th>Đã xếp vào lịch</th></tr></thead><tbody>']
for code in sorted(book_pages, key=lambda k: -book_pages[k]):
    m = META[code]
    lib.append('<tr><td><b>%s</b></td><td><a href="%s" target="_blank" rel="noopener">%s</a></td><td>%s · %s</td><td>%d tr.</td><td>%d tr.</td></tr>'
               % (esc(code), esc(pdf_href(code)), esc(m[0]), esc(m[1]), esc(m[2]), TOC[code]['pages'], book_pages[code]))
lib.append('</tbody></table></div>')

total_days = sum(len(days[c]) for c in SUB)
total_pages = sum(book_pages.values())
nweeks = len(weeks)

CSS_COL = ''.join('.s-%s{--c:%s}' % (c, COL[c][0]) for c in SUB)
CSS_COL_D = ''.join('.s-%s{--c:%s}' % (c, COL[c][1]) for c in SUB)

PAGE = '''<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Giáo án tự học theo môn — Linux, mạng, Go, container, Kubernetes, hệ phân tán</title>
<style>
:root{--bg:#f6f5f1;--card:#fff;--ink:#1d1f23;--mute:#626873;--line:#dedbd2;--acc:#0b6e4f;--soft:#eef4f0;--warn:#fff4e0;--hl:#fff8d6}
@media (prefers-color-scheme:dark){:root{--bg:#15171a;--card:#1d2024;--ink:#e6e4de;--mute:#9aa0aa;--line:#33373d;--acc:#5fcf9f;--soft:#1f2a26;--warn:#33291a;--hl:#3a3418}}
__COLL__
@media (prefers-color-scheme:dark){__COLD__}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 "Segoe UI",system-ui,sans-serif}
.wrap{max-width:1040px;margin:0 auto;padding:26px 18px 90px}
h1{font-size:28px;line-height:1.25;margin:0 0 6px}
h2{font-size:20px;margin:36px 0 10px;padding-top:10px;border-top:2px solid var(--line)}
p{margin:8px 0}a{color:var(--acc)}
code{font:13px Consolas,"Cascadia Mono",monospace;background:var(--soft);padding:1px 5px;border-radius:4px}
.sub{color:var(--mute)}
.box{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 16px;margin:12px 0}
.warn{background:var(--warn)}
.box ul{margin:6px 0;padding-left:20px}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;vertical-align:top;padding:6px 8px;border-bottom:1px solid var(--line)}
th{color:var(--mute);font-weight:600}.tw{overflow-x:auto}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}
.sc{background:var(--card);border:1px solid var(--line);border-top:4px solid var(--c);border-radius:8px;padding:10px 14px}
.sc .sh{display:flex;gap:8px;align-items:baseline}.sc .sh b{color:var(--c)}.sc .nm{font-weight:600}
.sc p{margin:6px 0;font-size:14px}.mt{color:var(--mute)}
table.mx{width:auto;font-size:12px}table.mx th,table.mx td{padding:2px 4px;text-align:center;border:1px solid var(--line)}
table.mx th:first-child{text-align:left;color:var(--c);font-weight:700}
table.mx td.on{background:var(--c);color:#fff;font-weight:700}
@media (prefers-color-scheme:dark){table.mx td.on{color:#111}}
.bar{position:sticky;top:0;z-index:5;background:var(--bg);padding:10px 0;border-bottom:1px solid var(--line);display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.meter{flex:1;min-width:140px;height:8px;background:var(--line);border-radius:5px;overflow:hidden}.meter i{display:block;height:100%;background:var(--acc);width:0}
button,input[type=date]{font:inherit;padding:4px 9px;border:1px solid var(--line);border-radius:7px;background:var(--card);color:var(--ink)}
button{cursor:pointer}
.flt{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}
.flt button{border-radius:14px;font-size:13px;padding:2px 11px}
.flt button.on{background:var(--c,var(--acc));color:#fff;border-color:transparent}
@media (prefers-color-scheme:dark){.flt button.on{color:#111}}
details.wk{background:var(--card);border:1px solid var(--line);border-radius:10px;margin:10px 0}
details.wk>summary{cursor:pointer;padding:10px 14px;font-weight:600;display:flex;gap:12px;align-items:baseline;flex-wrap:wrap}
details.wk>summary .n{white-space:nowrap}.sb{color:var(--mute);font-weight:500}
details.wk>summary .rg{color:var(--mute);font-weight:400;font-size:13px}
details.wk>summary .pc{margin-left:auto;color:var(--mute);font-weight:400;font-size:13px}
.in{padding:0 14px 12px}
.day,.sun{display:grid;grid-template-columns:24px 46px 1fr;gap:8px;padding:12px 0;border-top:1px dashed var(--line)}
.sun{grid-template-columns:70px 1fr}
.day .wd,.sun .wd{display:flex;flex-direction:column;font-size:12px;color:var(--mute)}.wd b{color:var(--c,var(--ink));font-size:14px}
.sun .wd b{color:var(--mute)}
.hd{display:flex;flex-wrap:wrap;gap:6px 8px;align-items:baseline}
.chip{font-size:11px;font-weight:700;color:var(--c);border:1px solid var(--c);border-radius:11px;padding:0 8px;white-space:nowrap}
.no{font:12px Consolas,monospace;color:var(--mute)}.tt{font-size:15.5px}
.tg{font-size:11px;border:1px solid var(--line);border-radius:4px;padding:0 5px;color:var(--mute);cursor:help}
.lb{display:inline-block;font-size:11px;letter-spacing:.03em;text-transform:uppercase;color:var(--c,var(--mute));font-weight:700;margin-right:6px}
.why{color:var(--mute);margin:4px 0 6px}.fst{background:var(--soft);padding:6px 10px;border-radius:6px;margin:6px 0}
.bd ul{margin:2px 0 4px;padding-left:18px}.bd li{margin:1px 0}
.rd{background:var(--soft);border-radius:6px;padding:6px 10px;margin:6px 0}
.secs{font-size:12.5px;color:var(--mute);margin:1px 0 4px}.lb2{font-weight:700;margin-right:4px}.bk{font-weight:700}.pg{color:var(--mute);font-size:13px;white-space:nowrap}
.lab{margin:6px 0}.q{margin:6px 0;border-left:3px solid var(--c,var(--line));padding-left:10px}
.xl{font-size:13.5px;color:var(--mute)}.sun .qs{margin:6px 0 0;padding-left:20px}.sun .qs li{margin:3px 0}
.day.done .bd>*:not(.hd){opacity:.5}.day.today{outline:2px solid var(--acc);outline-offset:4px;border-radius:6px}
.day.hide,.sun.hide{display:none}
.foot{color:var(--mute);font-size:14px}
@media (max-width:600px){.day{grid-template-columns:22px 1fr}.day .wd{grid-column:2;flex-direction:row;gap:8px}.day .bd{grid-column:1/-1}.sun{grid-template-columns:1fr}.sun .wd{flex-direction:row;gap:8px}}
@media print{.bar,.flt{display:none}details.wk>.in{display:block}}
</style>
</head>
<body>
<div class="wrap">
<h1>Giáo án tự học theo môn</h1>
<p class="sub">Linux · mạng · Go · container · Kubernetes · hệ phân tán. __ND__ ngày học trong __NW__ tuần, 8 môn, khoảng __NP__ trang đọc có chỉ rõ chương và trang. Lập ngày 22/11/2026 cho máy cài Linux thật (dual-boot, SSD 500 GB riêng, RAM 16 GB).</p>

<div class="box">
<p><b>Cách dùng.</b> Mỗi tuần 6 ngày học và Chủ nhật ôn. Mỗi ngày 2–3 giờ đọc và 1–2 giờ thực hành (nhịp giống <a href="lo-trinh-tong-52-tuan.html">lộ trình tổng 52 tuần</a>). Mỗi ngày ghi rõ: <b>môn</b>, <b>chủ đề</b>, <b>đọc sách nào, chương nào, trang nào</b> (bấm vào tên sách để mở đúng trang), <b>nắm được gì</b> khi đọc xong, <b>bài thực hành</b> với lệnh cụ thể, và <b>một câu tự kiểm</b> để trả lời miệng. Chọn ngày bắt đầu bên dưới, trang tự tính ngày cho từng buổi.</p>
<p><b>Tốc độ đọc giả định:</b> khoảng 13–16 trang tiếng Anh kỹ thuật mỗi giờ; trung bình __AVG__ trang mỗi ngày, tối đa 40 trang "nặng" (CSAPP, TLPI, Stevens, DDIA...) hoặc 50 trang sách nhẹ, nằm trong 2–3 giờ đọc. Hai tuần đầu đọc TLCL (nhẹ): hãy bấm giờ để biết tốc độ thật của bạn; chậm hơn thì kéo giãn lịch thay vì đọc lướt.</p>
<p>Đọc kỹ ở <b>bản tiếng Anh</b>; thấy khó thì đọc lướt bản Việt hoặc song ngữ (nếu có) trước. Giờ thực hành tự làm trước, bí quá 30 phút mới hỏi AI; hỏi để giải thích và soát bài, không để viết lab hộ.</p>
</div>

<div class="box warn">
<p><b>Những điều tôi chưa kiểm chứng được — nói trước để bạn không bị bất ngờ.</b></p>
<ul>
<li>Toàn bộ <b>chương và số trang</b> lấy từ mục lục của chính các file PDF trong kho (đã kiểm tự động mọi khoảng trang nằm trong sách, mỗi ngày không quá tải đọc), nhưng tôi <b>chưa chạy các bài thực hành trên máy của bạn</b>. Có thể có lệnh cần cài thêm gói hoặc khác tên trên bản phân phối của bạn: ghi lại và sửa tại chỗ.</li>
<li>Các bài đo (đánh dấu <span class="tg">đo hiệu năng</span>) <b>không có số kết quả mẫu</b>: bạn tự đo và ghi. Tôi không đưa con số nào mà chưa đo trên máy bạn.</li>
<li>Bài đánh dấu <span class="tg">cần KVM</span>, <span class="tg">cgroup v2</span>, <span class="tg">cần sudo</span> phụ thuộc kết quả của <b>ngày LIN-01</b> (kiểm máy). Nếu thiếu KVM thì QEMU vẫn chạy được, chỉ chậm hơn nhiều.</li>
<li>Nhiều sách cũ (xem bảng phiên bản bên dưới). Phần nào đã đổi, bài đó ghi rõ và trỏ sang tài liệu chính thức.</li>
</ul>
</div>

<h2>Quan hệ với các lộ trình khác</h2>
<div class="box">
<p>Tệp này <b>thay thế thứ tự</b> của <a href="lo-trinh-tong-52-tuan.html">lộ trình tổng 52 tuần</a> cho sáu mảng: Linux, mạng, Go, container/Docker, Kubernetes, hệ phân tán. Tệp 52 tuần chưa bị sửa; nếu dùng tệp này làm lịch chính, bỏ qua các giai đoạn tương ứng bên đó. <a href="lo-trinh-aws.html">AWS</a>, <a href="lo-trinh-ai-infrastructure.html">AI infrastructure</a> và <a href="ke-hoach-vdt.html">kế hoạch VDT</a> vẫn theo tệp riêng của chúng, làm sau hoặc song song tuỳ mục tiêu.</p>
<p>Các bài thực hành C tham chiếu thẳng vào đơn vị của <a href="lo-trinh-c.html">lộ trình C</a> (ví dụ G3, H2, J4) thay vì làm lại. <a href="ke-hoach-he-thong.html">Kế hoạch 71 buổi</a> dùng khi bạn muốn thêm chiều sâu hoặc số trang bổ sung cho cơ sở dữ liệu.</p>
<p><b>Không có trong giáo án này:</b> cơ sở dữ liệu quan hệ (ngoài phần lưu trữ và giao dịch trong môn DIS), bảo mật ứng dụng web, an ninh mạng chuyên sâu, hạ tầng cloud cụ thể, GPU và AI infra.</p>
</div>

<h2>Tám môn học</h2>
<div class="cards">__CARDS__</div>
<p class="sub">Thứ tự môn đi theo phụ thuộc: Linux → lập trình hệ thống → kernel; Linux → mạng (cùng lúc, mạng dùng namespace cho môn container); Go đi sớm vì mọi môn sau đều viết mã Go; container cần mạng và hệ thống; Kubernetes cần container, Go và mạng; hệ phân tán cần Go, mạng và kernel (khoá, nhật ký, fsync), và kết thúc bằng một hệ thống chạy trên Kubernetes.</p>

<h2>Thời khoá biểu theo tuần</h2>
<p class="sub">Mỗi ô là số ngày học của môn đó trong tuần (tối đa 6). Mỗi tuần chạy song song hai môn xen kẽ để đổi không khí và để môn này củng cố môn kia.</p>
__MATRIX__

<h2>Thư viện dùng trong giáo án</h2>
__LIB__
<p class="sub">Số trang là số trang PDF (như thanh trang của trình xem), không phải số in trong sách.</p>

<h2>Cặp phiên bản: sách và mã nguồn</h2>
<div class="box">
<ul>
<li><b>xv6:</b> sách rev7 (08/2012) mô tả <b>xv6 bản x86</b>, đúng cặp với kho <a href="https://github.com/mit-pdos/xv6-public" target="_blank" rel="noopener">mit-pdos/xv6-public</a> (README của kho ghi MIT đã ngừng bảo trì bản x86 và chuyển sang RISC-V; trang MIT 2012 xác nhận sách rev7 đi kèm bản x86). Bản RISC-V là <a href="https://github.com/mit-pdos/xv6-riscv" target="_blank" rel="noopener">xv6-riscv</a>: khái niệm giống nhau nhưng tên file và hàm khác. Hãy dùng cặp sách x86 + xv6-public, đối chiếu theo tên hàm (<code>grep -n</code>) vì mã trong kho mới hơn sách vài chỗ.</li>
<li><b>Linux Kernel Development (2010):</b> viết cho kernel 2.6.34. Cấu trúc (lập lịch, bộ nhớ, VFS, khoá) còn đúng; chi tiết đã đổi: CFS được EEVDF thay từ kernel 6.6; <code>do_fork</code> nay là <code>kernel_clone</code>; mã lập lịch chuyển sang <code>kernel/sched/</code>; SLAB/SLOB đã gỡ, còn SLUB. Bài KER ghi rõ chỗ này; kiểm bằng <code>uname -r</code> của bạn. Mã nguồn đúng phiên bản sách xem trên Elixir ở bản v2.6.34 (đã mở được: <a href="https://elixir.bootlin.com/linux/v2.6.34/source/kernel/sched_fair.c" target="_blank" rel="noopener">kernel/sched_fair.c</a>, <a href="https://elixir.bootlin.com/linux/v2.6.34/source/kernel/sched.c" target="_blank" rel="noopener">kernel/sched.c</a>).</li>
<li><b>TCP/IP Illustrated (1994):</b> bản 1; không có IPv6, CUBIC/BBR, QUIC. Dùng cho nguyên lý; phần hiện đại đọc HPBN và RFC (bài NET-12, NET-13, NET-18).</li>
<li><b>High Performance Browser Networking (2013):</b> không có QUIC/HTTP/3; bài NET-18 bù bằng RFC 9000 và RFC 9114.</li>
<li><b>Distributed Systems (Tanenbaum, 2007):</b> không có Raft và thiết kế hiện đại; dùng làm khung, DDIA và paper Raft bù phần mới.</li>
<li><b>Docker Deep Dive (2020):</b> sách theo công cụ, chỉ để tham khảo; lệnh hiện hành tra tài liệu chính thức.</li>
<li><b>Kubernetes Up and Running (bản Early Release):</b> thiếu một số chương (ConfigMap/Secret, StatefulSet): bài K8S-07 và K8S-10 trỏ sang tài liệu chính thức và sách khác.</li>
<li><b>Mạng máy tính (giáo trình tiếng Việt)</b> trong kho: file chỉ có 9 trang, nên giáo án không dùng.</li>
</ul>
</div>

<h2>Nguồn cập nhật trên internet</h2>
<div class="box">
<p>Công nghệ đổi hằng ngày, nên các nguồn sau là chỗ tra phiên bản hiện hành (mọi liên kết dưới đây đã mở được lúc soạn):</p>
<ul>
<li><a href="https://go.dev/doc/" target="_blank" rel="noopener">Tài liệu Go</a> · <a href="https://go.dev/dl/" target="_blank" rel="noopener">tải Go</a></li>
<li><a href="https://docs.docker.com/" target="_blank" rel="noopener">Tài liệu Docker</a></li>
<li><a href="https://kubernetes.io/docs/home/" target="_blank" rel="noopener">Tài liệu Kubernetes</a> · <a href="https://kubernetes.io/docs/concepts/overview/components/" target="_blank" rel="noopener">các thành phần</a> · <a href="https://kind.sigs.k8s.io/" target="_blank" rel="noopener">kind</a></li>
<li>Giao thức: <a href="https://www.rfc-editor.org/rfc/rfc9293" target="_blank" rel="noopener">RFC 9293 (TCP)</a>, <a href="https://www.rfc-editor.org/rfc/rfc9000" target="_blank" rel="noopener">RFC 9000 (QUIC)</a>, <a href="https://www.rfc-editor.org/rfc/rfc9114" target="_blank" rel="noopener">RFC 9114 (HTTP/3)</a>, <a href="https://www.rfc-editor.org/rfc/rfc8446" target="_blank" rel="noopener">RFC 8446 (TLS 1.3, trang ghi đã có RFC thay thế)</a></li>
<li><a href="https://www.kernel.org/doc/html/latest/networking/index.html" target="_blank" rel="noopener">Tài liệu mạng của kernel</a></li>
<li><a href="https://raft.github.io/raft.pdf" target="_blank" rel="noopener">Raft (paper)</a> · <a href="https://pdos.csail.mit.edu/6.824/" target="_blank" rel="noopener">MIT 6.5840 (trước đây 6.824)</a></li>
</ul>
</div>

<h2>Lịch học</h2>
<div class="bar">
<label>Bắt đầu ngày <input type="date" id="start"></label>
<div class="meter"><i id="mt"></i></div><span id="pct">0%</span>
<button id="goto" type="button">Đến hôm nay</button>
<button id="reset" type="button">Xoá tiến độ</button>
</div>
<div class="flt" id="flt"><button type="button" data-s="ALL" class="on">Tất cả</button>__FLT__</div>
__WEEKS__

<h2>Nếu trễ lịch thì cắt ở đâu</h2>
<div class="box">
<p>Không cắt các nền: LIN, SYS, KER-01…KER-17, KER-22…KER-23, NET-01…NET-15, NET-19…NET-23, DIS-04…DIS-14. Khi buộc phải cắt, theo thứ tự: bài tham khảo Docker (CON-05, CON-10) → NET-16…NET-18 (HTTP) → KER-18 (thời gian) và KER-21 (đĩa cứng) → DIS-15 và DIS-20. Không cắt các ngày tổng kết cuối môn (có bài làm ghép nhiều môn).</p>
</div>

<p class="foot">Dữ liệu và trang kiểm tự động từ mục lục PDF; chưa chạy lab trên máy bạn. Khi sách và máy khác nhau, lấy máy làm chuẩn rồi ghi lại sự khác biệt vào sổ ghi (đó cũng là kiến thức).</p>
</div>
<script>
(function(){
"use strict";
var KEY="giaoan-theo-mon-v1", TOTAL=__ND__;
var st={start:"2026-11-23",done:{}};
try{var raw=localStorage.getItem(KEY);if(raw){var o=JSON.parse(raw);if(o&&typeof o==="object"){if(o.start)st.start=o.start;if(o.done)st.done=o.done;}}}catch(e){}
function save(){try{localStorage.setItem(KEY,JSON.stringify(st));}catch(e){}}
var WD=["T2","T3","T4","T5","T6","T7","CN"];
function pad(n){return n<10?"0"+n:""+n}
function addDays(d,n){var x=new Date(d.getTime());x.setDate(x.getDate()+n);return x}
function fmt(d){return pad(d.getDate())+"/"+pad(d.getMonth()+1)}
function parse(s){var p=(s||"").split("-");if(p.length!==3)return null;var d=new Date(+p[0],+p[1]-1,+p[2]);return isNaN(d.getTime())?null:d}
function monday(d){var x=new Date(d.getFullYear(),d.getMonth(),d.getDate());var k=(x.getDay()+6)%7;return addDays(x,-k)}
var startEl=document.getElementById("start");
startEl.value=st.start;
function dates(){
  var s=parse(st.start)||new Date();var m=monday(s);
  var wks=document.querySelectorAll("details.wk");
  for(var i=0;i<wks.length;i++){
    var w=+wks[i].getAttribute("data-w"),b=addDays(m,(w-1)*7);
    wks[i].querySelector(".rg").textContent=fmt(b)+" – "+fmt(addDays(b,6));
    var ds=wks[i].querySelectorAll(".day");
    for(var j=0;j<ds.length;j++){var d=+ds[j].getAttribute("data-d");ds[j].querySelector(".dt").textContent=fmt(addDays(b,d));}
    var sn=wks[i].querySelector(".sun");if(sn)sn.querySelector(".dt").textContent=fmt(addDays(b,6));
  }
}
function refresh(){
  var cbs=document.querySelectorAll(".day input[type=checkbox]"),n=0;
  for(var i=0;i<cbs.length;i++){
    var id=cbs[i].getAttribute("data-id"),on=!!st.done[id];cbs[i].checked=on;if(on)n++;
    cbs[i].closest(".day").classList.toggle("done",on);
  }
  var p=Math.round(100*n/TOTAL);
  document.getElementById("mt").style.width=p+"%";document.getElementById("pct").textContent=n+"/"+TOTAL+" ("+p+"%)";
  var wks=document.querySelectorAll("details.wk");
  for(var k=0;k<wks.length;k++){
    var ds=wks[k].querySelectorAll(".day"),c=0;
    for(var j=0;j<ds.length;j++){if(st.done[ds[j].querySelector("input").getAttribute("data-id")])c++;}
    wks[k].querySelector(".pc").textContent=c+"/"+ds.length;
  }
}
document.addEventListener("change",function(e){
  var t=e.target;if(t&&t.matches&&t.matches(".day input[type=checkbox]")){
    var id=t.getAttribute("data-id");if(t.checked)st.done[id]=1;else delete st.done[id];save();refresh();}
});
startEl.addEventListener("change",function(){if(parse(startEl.value)){st.start=startEl.value;save();dates();markToday();}});
document.getElementById("reset").addEventListener("click",function(){if(confirm("Xoá toàn bộ tiến độ đã đánh dấu?")){st.done={};save();refresh();}});
var cur="ALL";
document.getElementById("flt").addEventListener("click",function(e){
  var b=e.target.closest("button");if(!b)return;cur=b.getAttribute("data-s");
  var bs=this.querySelectorAll("button");for(var i=0;i<bs.length;i++){bs[i].classList.toggle("on",bs[i]===b);}
  var ds=document.querySelectorAll(".day");
  for(var j=0;j<ds.length;j++){ds[j].classList.toggle("hide",cur!=="ALL"&&ds[j].getAttribute("data-s")!==cur);}
  var sn=document.querySelectorAll(".sun");for(var k=0;k<sn.length;k++){sn[k].classList.toggle("hide",cur!=="ALL");}
  if(cur!=="ALL"){var wks=document.querySelectorAll("details.wk");for(var m=0;m<wks.length;m++){wks[m].open=!!wks[m].querySelector(".day:not(.hide)");}}
});
function markToday(){
  var old=document.querySelector(".day.today");if(old)old.classList.remove("today");
  var s=parse(st.start);if(!s)return null;var m=monday(s);var now=new Date();now=new Date(now.getFullYear(),now.getMonth(),now.getDate());
  var diff=Math.round((now-m)/86400000);if(diff<0)return null;
  var w=Math.floor(diff/7)+1,d=diff%7;if(d>5)return document.getElementById("w-"+w);
  var el=document.querySelector('.day[data-w="'+w+'"][data-d="'+d+'"]');if(el){el.classList.add("today");return el;}
  return document.getElementById("w-"+w);
}
document.getElementById("goto").addEventListener("click",function(){
  var el=markToday();
  if(!el){var first=document.querySelector(".day:not(.done)");el=first;}
  if(el){var w=el.closest("details.wk");if(w)w.open=true;el.scrollIntoView({behavior:"smooth",block:"center"});}
});
dates();refresh();
var t=markToday();
var firstOpen=t&&t.closest?t.closest("details.wk"):null;
if(!firstOpen){var nd=document.querySelector(".day:not(.done)");firstOpen=nd?nd.closest("details.wk"):document.querySelector("details.wk");}
if(firstOpen)firstOpen.open=true;
if(location.hash){var h=document.getElementById(location.hash.slice(1));if(h){var ww=h.closest("details.wk");if(ww)ww.open=true;}}
})();
</script>
</body>
</html>
'''

flt = ''.join('<button type="button" data-s="%s" class="s-%s">%s</button>' % (c, c, esc(c)) for c in SUB)
page = (PAGE.replace('__COLL__', CSS_COL).replace('__COLD__', CSS_COL_D)
        .replace('__AVG__', str(round(total_pages/total_days))).replace('__ND__', str(total_days)).replace('__NW__', str(nweeks)).replace('__NP__', '{:,}'.format(total_pages).replace(',', '.'))
        .replace('__CARDS__', ''.join(cards)).replace('__MATRIX__', ''.join(mat)).replace('__LIB__', ''.join(lib))
        .replace('__FLT__', flt).replace('__WEEKS__', ''.join(week_html)))
open(OUT, 'w', encoding='utf-8').write(page)
print('wrote', OUT, len(page), 'bytes;', total_days, 'days;', nweeks, 'weeks;', total_pages, 'pages')
