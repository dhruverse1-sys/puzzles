import sys, numpy as np
from PIL import Image
D = sys.argv[1]
im = np.array(Image.open(D + '/gem.jpg').convert('RGB')).astype(float)
g = im.max(axis=2)
bands = [(25,54),(83,112),(141,170),(199,228),(257,286),(315,344),(373,402),(431,460),(489,518),(547,576),(605,632),(663,692),(721,750),(779,808),(837,866),(895,924),(953,982),(1010,1039),(1068,1097),(1126,1155),(1184,1211)]
# fit pitch from row 0 column profile
def colprof(b):
    y0, y1 = b; return (g[y0-2:y1+2] > 90).sum(axis=0)
best = None
for x0 in np.arange(18, 26, 0.25):
    for p in np.arange(21.8, 22.6, 0.01):
        # gaps should be at x0 + k*p (cell boundaries): minimize ink at boundaries over all rows
        xs = (x0 + np.arange(51) * p).round().astype(int)
        xs = xs[xs < g.shape[1]]
        s = sum(colprof(b)[xs].sum() for b in bands[:5])
        if best is None or s < best[0]: best = (s, x0, p)
print('fit', best)
_, x0, p = best
cells = []
for r, (y0, y1) in enumerate(bands):
    for k in range(50):
        xa = int(round(x0 + k * p)); xb = int(round(x0 + (k + 1) * p))
        if xb > g.shape[1]: break
        patch = g[y0-3:y1+3, xa:xb]
        rgb = im[y0-3:y1+3, xa:xb]
        cells.append((r, k, patch, rgb))
np.save(D + '/cells_meta.npy', np.array([(c[0], c[1]) for c in cells]))
# normalized patches
P = []
for r, k, patch, rgb in cells:
    a = patch - patch.min(); a = a / (a.max() + 1e-9)
    a = np.array(Image.fromarray((a * 255).astype(np.uint8)).resize((16, 24), Image.BILINEAR)) / 255.0
    P.append(a.ravel())
P = np.array(P); np.save(D + '/cells.npy', P)
# mean color of ink per cell
C = []
for r, k, patch, rgb in cells:
    m = patch > 120
    C.append(rgb[m].mean(axis=0) if m.any() else np.zeros(3))
np.save(D + '/colors.npy', np.array(C))
print(len(cells), 'cells')
