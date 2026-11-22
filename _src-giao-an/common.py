# -*- coding: utf-8 -*-
import os, sys, json, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
SP = os.path.dirname(os.path.abspath(__file__))
TOC = json.load(open(os.path.join(SP, 'toc.json'), encoding='utf-8'))

SUBJECTS = ['LIN', 'SYS', 'KER', 'NET', 'GOL', 'CON', 'K8S', 'DBS', 'DIS', 'AIS']
MODS = {'LIN': 's_lin', 'SYS': 's_sys', 'KER': 's_ker', 'NET': 's_net', 'GOL': 's_gol', 'CON': 's_con', 'K8S': 's_k8s', 'DBS': 's_dbs', 'DIS': 's_dis', 'AIS': 's_ais'}

# nặng (đọc chậm) hay nhẹ
DENSE = {'CSAPP', 'TLPI', 'STEVENS', 'UNP', 'DS', 'DDIA', 'DBI', 'LKD', 'APUE', 'PG14', 'BOJIE'}
SPECIAL = {'WEB', 'MAN', 'HW'}
LOAD_CAP = 40.0

META = {
 'TLCL': ('The Linux Command Line, 7th Internet Ed', 'William Shotts', '2026', 'OS-Linux-Networking'),
 'CSAPP': ("Computer Systems: A Programmer's Perspective, Global Ed (3e, Y86-64)", 'Bryant, O\'Hallaron', '2016', 'OS-Linux-Networking'),
 'OSTEP': ('Operating Systems: Three Easy Pieces', 'Arpaci-Dusseau', '2018+', 'OS-Linux-Networking'),
 'TLPI': ('The Linux Programming Interface', 'Michael Kerrisk', '2010', 'OS-Linux-Networking'),
 'XV6': ('xv6 book (rev7, bản x86)', 'Cox, Kaashoek, Morris', '08/2012', 'OS-Linux-Networking'),
 'LKD': ('Linux Kernel Development, 3rd Ed (kernel 2.6.34)', 'Robert Love', '2010', 'OS-Linux-Networking'),
 'HPBN': ('High Performance Browser Networking', 'Ilya Grigorik', '2013', 'OS-Linux-Networking'),
 'STEVENS': ('TCP/IP Illustrated Vol.1, 1st Ed', 'W. Richard Stevens', '1994', 'OS-Linux-Networking'),
 'UNP': ('UNIX Network Programming Vol.1, 3rd Ed', 'Stevens, Fenner, Rudoff', '2003', '_repo-technical-books'),
 'LGO2': ('Learning Go, 2nd Ed', 'Jon Bodner', '2024', 'Go'),
 'MGO': ('Mastering Go, 3rd Ed', 'Mihalis Tsoukalos', '2024', 'Go'),
 'NETGO': ('Network Programming with Go', 'Adam Woodbeck', '2021', 'Go'),
 'DSGO': ('Distributed Services with Go', 'Travis Jeffery', '2021', 'Go'),
 'CONSEC': ('Container Security, 2nd Ed', 'Liz Rice', '2024', 'Kubernetes'),
 'DOCKER': ('Docker Deep Dive, 2020 Ed (tham khảo công cụ)', 'Nigel Poulton', '2020', 'Kubernetes'),
 'KUAR': ('Kubernetes: Up and Running, 3rd Ed (Early Release)', 'Burns, Beda, Hightower, Evenson', '2022', 'Kubernetes'),
 'DS': ('Distributed Systems: Principles and Paradigms, 2nd Ed', 'Tanenbaum, van Steen', '2007', 'System-Design-Architecture'),
 'DDIA': ('Designing Data-Intensive Applications', 'Martin Kleppmann', '2017', 'System-Design-Architecture'),
 'DBI': ('Database Internals', 'Alex Petrov', '2019', 'Database'),
 'PG14': ('PostgreSQL 14 Internals', 'Egor Rogov', '2022', 'Database'),
 'MLS1': ('Machine Learning Systems Vol 1: Introduction to Machine Learning Systems (mlsysbook)', 'Vijay Janapa Reddi và cộng sự', '2025–2026', 'AI-ML'),
 'MLS2': ('Machine Learning Systems Vol 2: ML Systems at Scale (mlsysbook)', 'Vijay Janapa Reddi và cộng sự', '2025–2026', 'AI-ML'),
 'BOJIE': ('Understanding AI Infra: Quantitative Analysis and System Design, v1.0 EN', 'Bojie Li', '10/2026', 'AI-ML'),
}


def load_subject(code):
    m = importlib.import_module(MODS[code])
    importlib.reload(m)
    return m.SUBJ, m.DAYS


def all_data():
    subj, days = {}, {}
    for c in SUBJECTS:
        s, d = load_subject(c)
        subj[c] = s
        days[c] = d
    return subj, days


# Phân bổ tuần: (môn A, số ngày a, môn B, số ngày b)
ALLOC = []
def _w(n, A, a, B, b):
    for _ in range(n):
        ALLOC.append((A, a, B, b))
_w(4, 'LIN', 3, 'GOL', 3)
_w(2, 'SYS', 3, 'GOL', 3)
_w(1, 'SYS', 5, 'GOL', 1)
_w(4, 'SYS', 3, 'NET', 3)
_w(3, 'KER', 3, 'NET', 3)
_w(1, 'KER', 2, 'NET', 4)
_w(4, 'KER', 3, 'CON', 3)
_w(1, 'KER', 3, 'K8S', 3)
_w(1, 'KER', 1, 'K8S', 5)
_w(1, 'K8S', 4, 'DBS', 2)
_w(5, 'DBS', 3, 'DIS', 3)
_w(1, 'DBS', 5, 'DIS', 1)
_w(1, 'DIS', 3, 'AIS', 3)
_w(3, 'AIS', 6, None, 0)
_w(1, 'AIS', 5, None, 0)


def interleave(A, a, B, b):
    total = a + b
    seq = [A] * total
    if b:
        pos = set()
        for k in range(b):
            p = int((k + 0.5) * total / b)
            while p in pos:
                p += 1
            pos.add(p)
        for p in pos:
            seq[p] = B
    return seq


def schedule(days):
    """Trả danh sách tuần: mỗi tuần là list các (code, idx) theo thứ tự thứ 2..thứ 7."""
    ptr = {c: 0 for c in SUBJECTS}
    weeks = []
    for (A, a, B, b) in ALLOC:
        seq = interleave(A, a, B, b) if B else [A] * a
        wk = []
        for c in seq:
            wk.append((c, ptr[c]))
            ptr[c] += 1
        weeks.append(wk)
    return weeks, ptr
