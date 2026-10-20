exec(open('grid.py').read())
pred = {}
for r in range(10):
    for c in range(10):
        s = succ(r, c)
        if s is None: continue
        if not (0 <= s[0] < 10 and 0 <= s[1] < 10): print('outside', (r, c)); continue
        pred.setdefault(s, []).append((r, c))
nopred = [(r, c) for r in range(10) for c in range(10) if (r, c) not in pred]
print('no predecessor:', [(p, cells[p[0]][p[1]]) for p in nopred])
print('multi-pred:', {k: (cells[k[0]][k[1]], v) for k, v in pred.items() if len(v) > 1})
for p in nopred:
    path = [p]; cur = p
    while True:
        s = succ(*cur)
        if s is None: break
        if s in path: path.append(('loop->', s)); break
        path.append(s); cur = s
    print(p, cells[p[0]][p[1]], 'len', len(path), path[:5], '...', path[-3:])
