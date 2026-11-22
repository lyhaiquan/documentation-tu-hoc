import sys, json, os
sys.stdout.reconfigure(encoding='utf-8')
sp = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(sp, 'toc.json'), encoding='utf-8'))
code = sys.argv[1]
maxlvl = int(sys.argv[2]) if len(sys.argv) > 2 else 1
lo = int(sys.argv[3]) if len(sys.argv) > 3 else 0
hi = int(sys.argv[4]) if len(sys.argv) > 4 else 10 ** 6
b = T[code]
print(code, 'pages', b['pages'])
for l, t, p in b['toc']:
    if l <= maxlvl and lo <= p <= hi:
        print('  ' * (l - 1) + '%d  %s' % (p, t[:78]))
