import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
import fitz

D = 'D:\\Documentation\\'
BOOKS = [
    ('TLCL', 'OS-Linux-Networking/The Linux Command Line 7th Internet Ed (William Shotts) - free.pdf'),
    ('CSAPP', 'OS-Linux-Networking/CSAPP_2016.pdf'),
    ('OSTEP', 'OS-Linux-Networking/Operating Systems - Three Easy Pieces.pdf'),
    ('TLPI', 'OS-Linux-Networking/The Linux Programming Interface (Kerrisk).pdf'),
    ('APUE', '_repo-technical-books/Advanced.Programming.in.the.UNIX.Environment.3rd.Edition.0321637739.pdf'),
    ('XV6', 'OS-Linux-Networking/xv6 book rev7 2012 x86 (Cox, Kaashoek, Morris) - free.pdf'),
    ('LKD', 'OS-Linux-Networking/Linux Kernel Development 3rd Ed (Robert Love).pdf'),
    ('HPBN', 'OS-Linux-Networking/High Performance Browser Networking (Ilya Grigorik).pdf'),
    ('STEVENS', 'OS-Linux-Networking/Stevens W.R. - TCP IP Illustrated, Vol.1, The Protocols.pdf'),
    ('UNP', 'OS-Linux-Networking/UNIX Network Programming Vol 1 3rd Ed (Stevens, Fenner, Rudoff).pdf'),
    ('MMT', 'Giao-trinh-Tieng-Viet/Mạng máy tính.pdf'),
    ('LGO2', 'Go/Learning Go 2nd Ed (Jon Bodner).pdf'),
    ('MGO', 'Go/Mastering Go 3rd Ed (Mihalis Tsoukalos).pdf'),
    ('NETGO', 'Go/Network Programming with Go (Adam Woodbeck).pdf'),
    ('DSGO', 'Go/Distributed Services with Go (Travis Jeffery).pdf'),
    ('CNGO', 'Go/Cloud Native Go 1st Ed 2021 (Matthew Titmus).pdf'),
    ('CONSEC', 'Kubernetes/Container Security 2nd Ed (Liz Rice).pdf'),
    ('DOCKER', 'Kubernetes/Docker Deep Dive 2020 Ed (Nigel Poulton).pdf'),
    ('KUAR', 'Kubernetes/Kubernetes Up and Running - 3rd Ed 2022 (Early Release).pdf'),
    ('DS', 'System-Design-Architecture/Distributed Systems Principles and Paradigms 2nd Ed (Tanenbaum, van Steen).pdf'),
    ('DDIA', 'System-Design-Architecture/Designing Data-Intensive Applications (Kleppmann).pdf'),
    ('DBI', 'Database/Database Internals - A Deep Dive (Alex Petrov).pdf'),
    ('PG14', 'Database/PostgreSQL 14 Internals (Egor Rogov).pdf'),
    ('MLS1', 'AI-ML/Machine Learning Systems Vol 1.pdf'),
    ('MLS2', 'AI-ML/Machine Learning Systems Vol 2.pdf'),
    ('BOJIE', 'AI-ML/Understanding AI Infra v1.0 EN (Bojie Li).pdf'),
]
out = {}
for code, rel in BOOKS:
    p = D + rel.replace('/', '\\')
    if not os.path.exists(p):
        print('MISSING', code, p)
        continue
    d = fitz.open(p)
    toc = [[l, t.strip(), pg] for l, t, pg in d.get_toc()]
    out[code] = {'path': rel, 'pages': len(d), 'toc': toc}
    front = ' '.join(d[min(1, len(d) - 1)].get_text().split())[:70]
    print('%-7s pages=%4d toc=%4d | %s' % (code, len(d), len(toc), front))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'toc.json'), 'w', encoding='utf-8'), ensure_ascii=False)
