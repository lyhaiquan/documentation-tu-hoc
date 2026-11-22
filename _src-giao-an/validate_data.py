# -*- coding: utf-8 -*-
import sys, os, re, random
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import TOC, DENSE, SPECIAL, LOAD_CAP

subj, days = common.all_data()
weeks, ptr = common.schedule(days)
err = []
warn = []
KEYS = ['t', 'why', 'r', 'g', 'lab', 'q']
TAGS = {'root', 'kvm', 'cgroup-v2', 'perf', 'cẩn-thận', 'go', 'k8s', 'kiểm-máy'}

for c in common.SUBJECTS:
    for i, d in enumerate(days[c], 1):
        ident = '%s-%02d' % (c, i)
        for k in KEYS:
            if not d.get(k):
                err.append('%s thiếu %s' % (ident, k))
        if not (2 <= len(d.get('g', [])) <= 3):
            err.append('%s: g cần 2–3 ý, có %d' % (ident, len(d.get('g', []))))
        if ('?' not in d.get('q', '')) and not d.get('q', '').startswith('Không nhìn tài liệu'):
            warn.append('%s: q dạng mệnh lệnh (không có ?)' % ident)
        for tg in d.get('tags', []):
            if tg not in TAGS:
                err.append('%s: tag lạ %s' % (ident, tg))
        dense = light = 0
        for rd in d.get('r', []):
            code, label, p1, p2 = rd[0], rd[1], rd[2], rd[3]
            if code in SPECIAL:
                continue
            if code not in TOC:
                err.append('%s: sách %s không có trong toc' % (ident, code))
                continue
            n = TOC[code]['pages']
            if not (1 <= p1 <= p2 <= n):
                err.append('%s: %s trang %d–%d ngoài 1..%d' % (ident, code, p1, p2, n))
                continue
            cnt = p2 - p1 + 1
            if code in DENSE:
                dense += cnt
            else:
                light += cnt
        load = dense + 0.75 * light
        d['_load'] = load
        d['_pages'] = dense + light
        if load > LOAD_CAP + 0.01:
            err.append('%s: tải đọc %.1f > %.0f (nặng %d, nhẹ %d)' % (ident, load, LOAD_CAP, dense, light))
        if load < 8 and not any(rd[0] in SPECIAL for rd in d['r']):
            warn.append('%s: tải đọc chỉ %.1f' % (ident, load))

# --- thứ tự tiên quyết (theo thứ tự ngày toàn cục)
order = {}
n = 0
for wi, wk in enumerate(weeks, 1):
    for di, (c, idx) in enumerate(wk):
        order[(c, idx)] = (wi, di)


def pos(c, i):  # i bắt đầu từ 1
    return order[(c, i - 1)]


def before(a, b, what):
    if not (a < b):
        err.append('Thứ tự sai: %s (%s không đứng trước %s)' % (what, a, b))


L = len
# môn sau chỉ bắt đầu khi môn tiên quyết đã xong
PRE = {
    'SYS': [('LIN', L(days['LIN']))],
    'KER': [('SYS', L(days['SYS']))],
    'NET': [('LIN', L(days['LIN']))],
    'CON': [('NET', L(days['NET'])), ('SYS', L(days['SYS']))],
    'K8S': [('CON', L(days['CON'])), ('GOL', L(days['GOL'])), ('NET', L(days['NET']))],
    'DIS': [('GOL', L(days['GOL'])), ('NET', L(days['NET'])), ('KER', 23)],
}
for c, lst in PRE.items():
    for (p, k) in lst:
        before(pos(p, k), pos(c, 1), '%s cần %s ngày %d' % (c, p, k))
# yêu cầu mức ngày
before(pos('SYS', 13), pos('NET', 19), 'NET-19 (socket) cần SYS-13 (tín hiệu)')
before(pos('GOL', L(days['GOL'])), pos('NET', 24), 'NET-24 (Go) cần GOL xong')
before(pos('NET', 6), pos('CON', 3), 'CON-03 cần NET-06 (netns)')
before(pos('GOL', L(days['GOL'])), pos('CON', 12), 'CON-12 cần GOL xong')
before(pos('K8S', L(days['K8S'])), pos('DIS', L(days['DIS'])), 'DIS-22 cần K8S xong')
before(pos('NET', 25), pos('K8S', 5), 'K8S-05 cần NET-25 (nft/NAT)')
before(pos('NET', 6), pos('DIS', 4), 'DIS-04 cần NET-06')


# --- khoảng hở nhỏ giữa các lần đọc liên tiếp của cùng một sách (thường là sơ suất)
GAP_OK = {('LIN', 5, 'TLCL'), ('KER', 1, 'OSTEP'), ('SYS', 2, 'CSAPP')}  # trang chia phần / đối thoại, bỏ có chủ đích
for c in common.SUBJECTS:
    last = {}
    for i, d in enumerate(days[c], 1):
        for rd in d['r']:
            code, p1, p2 = rd[0], rd[2], rd[3]
            if code in SPECIAL:
                continue
            if code in last:
                lp, lid = last[code]
                gap = p1 - lp - 1
                if 1 <= gap <= 6 and (c, i, code) not in GAP_OK:
                    err.append('Hở %d trang: %s %s từ %s (kết thúc tr.%d) tới %s-%02d (bắt đầu tr.%d)' % (gap, c, code, lid, lp, c, i, p1))
            last[code] = (p2, '%s-%02d' % (c, i))

print('Ngày/môn:', {c: len(days[c]) for c in common.SUBJECTS}, 'tổng', sum(len(v) for v in days.values()))
print('Số tuần:', len(weeks))
tot = {c: sum(d['_pages'] for d in days[c]) for c in common.SUBJECTS}
print('Tổng trang đọc/môn:', tot)
mx = max((d['_load'], '%s-%02d' % (c, i)) for c in common.SUBJECTS for i, d in enumerate(days[c], 1))
print('Tải đọc cao nhất:', mx)
print('--- WARN', len(warn))
for w in warn:
    print(' ', w)
print('--- ERR', len(err))
for e in err:
    print(' ', e)
sys.exit(1 if err else 0)
