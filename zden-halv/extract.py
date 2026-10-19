#!/usr/bin/env python3
"""Extract the 256 waveform samples from Zden's Level HALV image and rebuild the frame stream.

Usage:
    python3 extract.py path/to/cryptoHALV.png

Model (verified against the image, see README.md):
  * The waveform is a polyline drawn twice, mirrored about y = 475.
  * Vertices sit on a 3 px grid: x = 89 + 3k, k = 1..256.
  * Each run of 32 samples ("era") is drawn at half the previous scale:
    one level = 128, 64, 32, 16, 8, 4, 2, 1 px.  Levels are 0..3.
  * Lines are rendered roughly as a Gaussian of sigma 0.75 px, max-blended.

The fit is a Viterbi search over pairs of consecutive levels, scoring each
3-column window by squared error against the rendered model.
"""
import json
import math
import sys

import numpy as np
from PIL import Image

X0, PITCH, SIGMA, CENTER = 89, 3, 0.75, 475
N = 256
LEVELS = range(4)
ROWS = np.arange(60, 476)  # the top half is enough: the bottom is a mirror


def xk(k):
    return X0 + PITCH * k


def unit(k):
    return 128.0 / 2 ** ((k - 1) // 32)


def ypos(k, v):
    return CENTER - v * unit(k)


def seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    t = np.clip(((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy), 0, 1)
    return np.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def window_cost(img, k, vprev, vk, vnext):
    cols = np.arange(xk(k), xk(k + 1))
    px, py = np.meshgrid(cols, ROWS)
    out = np.zeros(px.shape)
    segs = []
    if vprev is not None:
        segs.append((xk(k - 1), ypos(k - 1, vprev), xk(k), ypos(k, vk)))
    if vnext is not None:
        segs.append((xk(k), ypos(k, vk), xk(k + 1), ypos(k + 1, vnext)))
    for x1, y1, x2, y2 in segs:
        for a, b in ((y1, y2), (2 * CENTER - y1, 2 * CENTER - y2)):
            d = seg_dist(px, py, x1, a, x2, b)
            out = np.maximum(out, 255 * np.exp(-d * d / (2 * SIGMA * SIGMA)))
    act = img[60:476, cols[0]:cols[-1] + 1]
    return ((out - act) ** 2).sum()


def fit_samples(img):
    cur = {(a, b): window_cost(img, 1, None, a, b) for a in LEVELS for b in LEVELS}
    back = {}
    for k in range(2, N):
        nxt, bk = {}, {}
        for b in LEVELS:
            for c in LEVELS:
                best = min((cur[(a, b)] + window_cost(img, k, a, b, c), a) for a in LEVELS)
                nxt[(b, c)], bk[(b, c)] = best
        back[k], cur = bk, nxt
    fin = {key: c + window_cost(img, N, key[0], key[1], None) for key, c in cur.items()}
    a, b = min(fin, key=fin.get)
    seq = [b, a]
    for k in range(N - 1, 1, -1):
        seq.append(back[k][(seq[-1], seq[-2])])
    return seq[::-1]


def source_frames(samples):
    """Display sample k shows source sample floor(k*33/32); group the source into 4-sample frames."""
    src = {math.floor(k * 33 / 32): v for k, v in enumerate(samples)}
    return [[src.get(4 * f + i) for i in range(4)] for f in range(66)]


def main():
    img = np.array(Image.open(sys.argv[1]).convert("L")).astype(float)
    samples = fit_samples(img)
    frames = source_frames(samples)
    json.dump(samples, open("data/samples.json", "w"))
    json.dump(frames, open("data/frames.json", "w"))
    for e in range(8):
        print("era", e + 1, "".join(map(str, samples[32 * e:32 * e + 32])))
    print(" ".join("".join("?" if v is None else str(v) for v in fr) for fr in frames))


if __name__ == "__main__":
    main()
