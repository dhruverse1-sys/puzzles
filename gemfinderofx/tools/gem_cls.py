import sys, numpy as np
D = sys.argv[1]
P = np.load(D + '/cells.npy'); meta = np.load(D + '/cells_meta.npy'); C = np.load(D + '/colors.npy')
CYC = "TUVWYZROBMJKHLXQNPACDEFGIS"
row1 = [9,3,8,2,0,5,4,1,9,6,2,7,0,3,1,5,8,7,4,9,3,6,2,8,7]
dig_idx = [i for i in range(len(P)) if meta[i][1] % 2 == 1]
let_idx = [i for i in range(len(P)) if meta[i][1] % 2 == 0]
# templates from row 1
T = {}
for j, d in enumerate(row1):
    T.setdefault(d, []).append(P[2*j+1])
for it in range(3):
    Tm = {d: np.mean(v, axis=0) for d, v in T.items()}
    lab = {}; dist = {}
    for i in dig_idx:
        ds = {d: np.linalg.norm(P[i] - t) for d, t in Tm.items()}
        srt = sorted(ds.items(), key=lambda x: x[1])
        lab[i] = srt[0][0]; dist[i] = (srt[0][1], srt[1][1])
    T = {}
    for i in dig_idx: T.setdefault(lab[i], []).append(P[i])
# letters check: expected letter by stream position
pos = 0; lettermis = 0
LT = {}
for n, i in enumerate(let_idx):
    LT.setdefault(CYC[n % 26], []).append(P[i])
LTm = {l: np.mean(v, axis=0) for l, v in LT.items()}
for n, i in enumerate(let_idx):
    best = min(LTm, key=lambda l: np.linalg.norm(P[i] - LTm[l]))
    if best != CYC[n % 26]: lettermis += 1
print('letter mismatches vs cycle:', lettermis, 'of', len(let_idx))
amb = sorted(dig_idx, key=lambda i: dist[i][1] - dist[i][0])[:12]
print('least confident digits (row,col,label,d1,d2):')
for i in amb: print(meta[i], lab[i], round(dist[i][0], 2), round(dist[i][1], 2))
# output stream
stream = []
for n, i in enumerate(dig_idx):
    L = CYC[n % 26]
    col = C[i]
    stream.append((L, lab[i], tuple(int(x) for x in col)))
import json
json.dump([(a, b, c) for a, b, c in stream], open(D + '/stream.json', 'w'))
rows = {}
for n, i in enumerate(dig_idx):
    rows.setdefault(int(meta[i][0]), []).append(CYC[n % 26] + str(lab[i]))
for r in sorted(rows): print(r + 1, ''.join(rows[r]))
