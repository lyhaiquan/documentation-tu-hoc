# -*- coding: utf-8 -*-
"""Dựng bản PHẲNG của kho để đẩy lên GitHub.
   Nguồn : D:/Documentation (bố cục theo chủ đề, giữ nguyên trên máy)
   Đích  : D:/documentation-tu-hoc (có .git), gồm: HTML và tài liệu ở gốc, sách gom vào sach/
   Chạy  : python export_repo.py [thư mục đích]
"""
import os, re, shutil, subprocess, sys
from urllib.parse import unquote, quote
sys.stdout.reconfigure(encoding='utf-8')

SRC = 'D:/Documentation'
DST = (sys.argv[1] if len(sys.argv) > 1 else 'D:/documentation-tu-hoc').rstrip('/')
HERE = os.path.dirname(os.path.abspath(__file__))
CATS = ['OS-Linux-Networking', 'Go', 'Kubernetes', 'System-Design-Architecture', 'AI-ML', 'Giao-trinh-Tieng-Viet', 'Database']
OLD_HTML = ['lo-trinh-c.html', 'lo-trinh-aws.html', 'lo-trinh-ai-infrastructure.html', 'ke-hoach-vdt.html',
            'ke-hoach-he-thong.html', 'lo-trinh-lap-trinh-mang.html', 'doi-chieu-lap-trinh-mang.html', 'lo-trinh-tong-52-tuan.html']

assert os.path.isdir(DST), 'thư mục đích chưa có: ' + DST

# 1. dọn đích (giữ .git)
for name in os.listdir(DST):
    if name == '.git':
        continue
    p = os.path.join(DST, name)
    shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)

# 2. sách -> sach/ (phẳng)
os.makedirs(DST + '/sach')
seen = {}
for cat in CATS:
    for root, _, fs in os.walk(os.path.join(SRC, cat)):
        for f in fs:
            if not f.lower().endswith('.pdf'):
                continue
            assert f not in seen, 'trùng tên: ' + f
            seen[f] = os.path.join(root, f)
            shutil.copy2(seen[f], DST + '/sach/' + f)
print('sach/:', len(seen), 'PDF')

# 3. các HTML cũ: link sách trỏ sang sach/, bỏ đường dẫn tuyệt đối
CAT_RE = '|'.join(re.escape(c) for c in CATS)
PAT = re.compile(r'(?<![\w/%.-])(?:' + CAT_RE + r')/((?:Bai-giang-slide/)?[^"\'<>\n]*?\.pdf)')


def to_flat(t):
    t = t.replace('file:///D:/Documentation/', '')
    return PAT.sub(lambda m: 'sach/' + m.group(1).split('/')[-1], t)


for f in OLD_HTML:
    t = open(os.path.join(SRC, f), encoding='utf-8').read()
    open(os.path.join(DST, f), 'w', encoding='utf-8').write(to_flat(t))

# 4. ouroboros: trải phẳng (bỏ _cu)
OU = os.path.join(SRC, 'ouroboros')
ren = {}
open(DST + '/ouroboros.html', 'w', encoding='utf-8').write(to_flat(open(os.path.join(OU, 'ouroboros.html'), encoding='utf-8').read()))
for f in sorted(os.listdir(os.path.join(OU, '_cu'))):
    ren[f] = 'ouroboros-' + f
for f, new in ren.items():
    t = open(os.path.join(OU, '_cu', f), encoding='utf-8').read()
    if f.endswith('.html'):
        t = to_flat(re.sub(r'href="([^"#:]+)"', lambda m: 'href="%s"' % ren.get(m.group(1), m.group(1)), t))
    else:
        t = re.sub(r'\]\(([^)#:]+)\)', lambda m: '](%s)' % ren.get(m.group(1), m.group(1)), t)
    open(os.path.join(DST, new), 'w', encoding='utf-8').write(t)

# 5. IoT-Bai1: một thư mục iot-bai1/ phẳng (tên tệp mang tiền tố thư mục con); bỏ .docx
IOT = os.path.join(SRC, 'IoT-Bai1')
os.makedirs(DST + '/iot-bai1')
for root, _, fs in os.walk(IOT):
    for f in fs:
        if f.lower().endswith('.docx'):
            continue
        rel = os.path.relpath(os.path.join(root, f), IOT).replace(chr(92), '/')
        flat = rel.replace('/', '-')
        shutil.copy2(os.path.join(root, f), DST + '/iot-bai1/' + flat)

# 6. nguồn sinh giáo án
shutil.copytree(os.path.join(SRC, '_src-giao-an'), DST + '/nguon-giao-an', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))

# 7. giáo án (bản phẳng) + kiểm
SRCDIR = os.path.join(SRC, '_src-giao-an')
env = dict(os.environ, GA_FLAT_OUT=DST, PYTHONIOENCODING='utf-8')
for script in ('build.py', 'check_html.py'):
    r = subprocess.run([sys.executable, '-I', os.path.join(SRCDIR, script)], env=env, capture_output=True, text=True, encoding='utf-8')
    print(script, '->', (r.stdout.strip().splitlines() or ['(không in)'])[-1], '| mã', r.returncode)
    if r.returncode != 0:
        print(r.stdout[-800:], r.stderr[-800:])
        sys.exit(1)

# 8. LIBRARY.md (đường dẫn sach/...)
sys.path.insert(0, SRCDIR)
import common
from common import META, TOC
subj, days = common.all_data()
pages = {}
for c in common.SUBJECTS:
    for d in days[c]:
        for rd in d['r']:
            if rd[0] not in common.SPECIAL:
                pages[rd[0]] = pages.get(rd[0], 0) + rd[3] - rd[2] + 1
rows = []
for code in sorted(pages, key=lambda k: -pages[k]):
    m = META[code]
    rows.append('| %s | %s | %s · %s | `sach/%s` | %d | %d |' % (code, m[0], m[1], m[2], TOC[code]['path'].split('/')[-1], TOC[code]['pages'], pages[code]))
lib = ('# Danh mục sách mà giáo án cần\n\n'
       'Các PDF nằm trong thư mục `sach/` (bản sao cá nhân; **repo để PRIVATE**, sách có bản quyền, đừng công khai). `giao-an-theo-mon.html` trỏ tới chúng theo đường dẫn tương đối, nên clone repo về là link mở đúng trang sách hoạt động ngay. '
       'Số trang là số trang PDF (khớp thanh trang của trình xem). Nếu bạn thay bằng bản khác (khác số trang), chạy lại `nguon-giao-an/mktoc.py` rồi `build.py`.\n\n'
       '| Mã | Sách | Tác giả · năm | Đường dẫn | Số trang PDF | Trang đã xếp vào lịch |\n|---|---|---|---|---|---|\n' + '\n'.join(rows) + '\n')
open(DST + '/LIBRARY.md', 'w', encoding='utf-8').write(lib)

# 9. README.md (mục lục) và .gitignore
n_pdf = len(seen)
readme = '''# Tài liệu tự học (Linux, mạng, Go, container, Kubernetes, database, hệ phân tán, AI infrastructure)

Mọi thứ nằm ở cấp ngoài cùng: các trang HTML mở thẳng bằng trình duyệt, tài liệu `.md`, và một thư mục `sach/` chứa toàn bộ PDF (không chia nhánh).

**Repo để PRIVATE.** Có sách có bản quyền, đừng đổi sang public.

## Giáo án và lộ trình

| Tệp | Nội dung |
|---|---|
| [giao-an-theo-mon.html](giao-an-theo-mon.html) | **Giáo án chính**: 197 ngày, 10 môn, 33 tuần; mỗi ngày ghi sách, chương, trang, bài thực hành |
| [lo-trinh-tong-52-tuan.html](lo-trinh-tong-52-tuan.html) | Lộ trình tổng 52 tuần |
| [lo-trinh-c.html](lo-trinh-c.html) | 55 đơn vị lập trình C |
| [lo-trinh-aws.html](lo-trinh-aws.html) | Lộ trình AWS |
| [lo-trinh-ai-infrastructure.html](lo-trinh-ai-infrastructure.html) | Lộ trình AI infrastructure chi tiết |
| [ke-hoach-vdt.html](ke-hoach-vdt.html) | Kế hoạch VDT 8 tuần |
| [ke-hoach-he-thong.html](ke-hoach-he-thong.html) | Kế hoạch 71 buổi hệ thống |
| [lo-trinh-lap-trinh-mang.html](lo-trinh-lap-trinh-mang.html), [doi-chieu-lap-trinh-mang.html](doi-chieu-lap-trinh-mang.html) | Lập trình mạng |

## Dự án và bài thực hành

| Tệp | Nội dung |
|---|---|
| [ouroboros.html](ouroboros.html) | Dự án ouroboros |
| `ouroboros-*.html`, `ouroboros-*.md` | Tài liệu kiến trúc, sơ đồ, lộ trình, đặc tả, tiến độ của ouroboros |
| `iot-bai1/` | Bài thực hành IoT (Wokwi): mã nguồn, mô phỏng, phiếu lab |

## Sách và công cụ

- `sach/`: %d sách PDF. Danh mục, đường dẫn và số trang xem [LIBRARY.md](LIBRARY.md).
- `nguon-giao-an/`: mã nguồn sinh giáo án (dữ liệu từng môn `s_*.py`, mục lục sách `toc.json`, bộ dựng và bộ kiểm). Xem `nguon-giao-an/README.txt`.

## Ghi chú

- Một số lộ trình cũ có link tới sách không nằm trong repo (Java, C/C++, Quản lý dự án...); các link đó không mở được.
- Bản trên máy tác giả giữ bố cục theo chủ đề (`Go/`, `Kubernetes/`...); repo này là bản phẳng sinh bằng `nguon-giao-an/export_repo.py`.
- Tiến độ học lưu trong trình duyệt (localStorage), không nằm trong repo.
''' % n_pdf
open(DST + '/README.md', 'w', encoding='utf-8').write(readme)
open(DST + '/.gitignore', 'w', encoding='utf-8').write('*.zip\n*.epub\n*.docx\n__pycache__/\n')
shutil.copy2(os.path.abspath(__file__), DST + '/nguon-giao-an/export_repo.py')

# 10. kiểm link sách trong các HTML (đích)
bad = {}
tot = 0
for f in sorted(os.listdir(DST)):
    if not f.endswith('.html'):
        continue
    t = open(os.path.join(DST, f), encoding='utf-8').read()
    for m in re.finditer(r'sach/([^"\'#<>\s]+?\.pdf)', t):
        tot += 1
        name = unquote(m.group(1))
        if not os.path.exists(DST + '/sach/' + name):
            bad.setdefault(f, set()).add(name)
    left = re.findall(r'(?:' + CAT_RE + r')/[^"\'<>\n]*?\.pdf', t)
    if left:
        bad.setdefault(f + ' (chưa đổi)', set()).update(left[:3])
print('link sach/ trong HTML:', tot)
for f, s in bad.items():
    print('  ! %s: %d mục, vd %s' % (f, len(s), sorted(s)[0][:70]))
print('xong ->', DST)
