# -*- coding: utf-8 -*-
# Sinh LIBRARY.md (danh mục sách giáo án cần) và cập nhật số liệu trong README.md
import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import META, TOC

subj, days = common.all_data()
weeks, _ = common.schedule(days)
pages = {}
for c in common.SUBJECTS:
    for d in days[c]:
        for rd in d['r']:
            if rd[0] in common.SPECIAL:
                continue
            pages[rd[0]] = pages.get(rd[0], 0) + rd[3] - rd[2] + 1
rows = []
for code in sorted(pages, key=lambda k: -pages[k]):
    m = META[code]
    rows.append('| %s | %s | %s · %s | `%s` | %d | %d |' % (code, m[0], m[1], m[2], TOC[code]['path'], TOC[code]['pages'], pages[code]))
lib = ('# Danh mục sách mà giáo án cần\n\n'
       'Repo này **có kèm bản sao các sách PDF** mà giáo án dùng (để dùng cá nhân; repo để PRIVATE, đừng công khai vì bản quyền). Giáo án `giao-an-theo-mon.html` trỏ tới các PDF theo đường dẫn tương đối ở bảng dưới.\n'
       'Clone repo về là link mở được ngay. Nếu bạn chỉ có HTML: đặt PDF đúng đường dẫn này **cạnh** file HTML. Số trang là số trang PDF (khớp thanh trang của trình xem). '
       'Nếu file của bạn là bản khác (khác số trang), chạy lại `_src-giao-an/mktoc.py` rồi `build.py` để sinh lại trang.\n\n'
       '| Mã | Sách | Tác giả · năm | Đường dẫn | Số trang PDF | Trang đã xếp vào lịch |\n|---|---|---|---|---|---|\n' + '\n'.join(rows) + '\n')
open('D:/Documentation/LIBRARY.md', 'w', encoding='utf-8').write(lib)

nd = sum(len(v) for v in days.values())
r = open('D:/Documentation/README.md', encoding='utf-8').read()
r = re.sub(r'\*\*Giáo án chính\*\*: .*? Mỗi ngày:', '**Giáo án chính**: %d ngày, %d môn (Linux, lập trình hệ thống, kernel, mạng, Go, container, Kubernetes, database internals, hệ phân tán, AI infrastructure), %d tuần. Mỗi ngày:' % (nd, len(common.SUBJECTS), len(weeks)), r, count=1, flags=re.S)
open('D:/Documentation/README.md', 'w', encoding='utf-8').write(r)
print(len(rows), 'sách;', nd, 'ngày;', len(weeks), 'tuần')
