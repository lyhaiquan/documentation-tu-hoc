# -*- coding: utf-8 -*-
import sys, os, re, unicodedata
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import TOC, SPECIAL
import fitz
D = 'D:/Documentation/'
subj, days = common.all_data()
docs = {}
def doc(c):
    if c not in docs: docs[c] = fitz.open(D + TOC[c]['path'])
    return docs[c]
def norm(s):
    return re.sub(r'[^a-z0-9]+', ' ', unicodedata.normalize('NFKD', s.lower()).encode('ascii','ignore').decode())
STOP = {'phan','chuong','dau','cuoi','con','lai','nhat','the','and','for','with','from','tham','khao','intro','hien','thi'}
cache = {}
def pagetext(c, q):
    k = (c, q)
    if k not in cache: cache[k] = norm(doc(c)[q-1].get_text())
    return cache[k]
bad = 0; tot = 0
for c in common.SUBJECTS:
    for i, d in enumerate(days[c], 1):
        for rd in d['r']:
            code, label, p1, p2 = rd[0], rd[1], rd[2], rd[3]
            if code in SPECIAL: continue
            for par in re.findall(r'\(([^)]*)\)', label):
                toks = re.findall(r"[A-Za-z][A-Za-z0-9_\-/\.]{3,}", par)
                for tk in toks:
                    if tk.lower() in STOP: continue
                    tot += 1
                    key = norm(tk).strip()
                    if not key: continue
                    found = any(key in pagetext(code, q) for q in range(p1, p2 + 1))
                    if not found:
                        bad += 1
                        print('  ? %s-%02d %s tr.%d-%d | "%s" không thấy | %s' % (c, i, code, p1, p2, tk, label[:70]))
print('Thuật ngữ trong ngoặc: %d, không thấy: %d' % (tot, bad))
