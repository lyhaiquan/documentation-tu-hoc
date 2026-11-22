# -*- coding: utf-8 -*-
import sys, os, re, random, unicodedata
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import TOC, SPECIAL
import fitz

D = 'D:/Documentation/'
subj, days = common.all_data()
docs = {}


def doc(code):
    if code not in docs:
        docs[code] = fitz.open(D + TOC[code]['path'])
    return docs[code]


def norm(s):
    s = unicodedata.normalize('NFKD', s.lower())
    return re.sub(r'[^a-z0-9 ]+', ' ', s)


items = []
for c in common.SUBJECTS:
    for i, d in enumerate(days[c], 1):
        for rd in d['r']:
            if rd[0] in SPECIAL:
                continue
            items.append(('%s-%02d' % (c, i), rd))

random.seed(7)
print('=== 14 mẫu ngẫu nhiên: trang bắt đầu có đúng nội dung không ===')
for ident, rd in random.sample(items, 14):
    code, label, p1, p2 = rd[0], rd[1], rd[2], rd[3]
    txt = ' '.join(doc(code)[p1 - 1].get_text().split())[:170]
    print('%s | %s tr.%d-%d | %s\n    -> %s' % (ident, code, p1, p2, label[:70], txt))

print('\n=== Kiểm từ khoá tự động cho mọi mục (cảnh báo = cần xem) ===')
STOP = set('chuong phan dau cuoi con lai the and for with des from tham khao ch'.split())
bad = 0
for ident, rd in items:
    code, label, p1, p2 = rd[0], rd[1], rd[2], rd[3]
    lab = re.sub(r'\([^)]*\)', ' ', label)
    lab = re.sub(r'^(Ch\.|App\.|Appendix |\d+\.\d+)[^:]*:', ' ', lab)
    first = re.split(r'[;]', lab)[0]
    words = [w for w in norm(first).split() if len(w) >= 5 and w not in STOP]
    if not words:
        continue
    pages = ' '.join(norm(doc(code)[q - 1].get_text()) for q in range(p1, min(p1 + 3, p2) + 1))
    if not any(w in pages for w in words):
        bad += 1
        print('  ? %s %s tr.%d-%d | %s | tìm: %s' % (ident, code, p1, p2, label[:80], words[:4]))
print('Cảnh báo:', bad, '/', len(items))
