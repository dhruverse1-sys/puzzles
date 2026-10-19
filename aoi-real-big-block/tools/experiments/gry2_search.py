"""Grycoin Block 2 (escrow 1tzieUfbeQghz2zjDeGHcAEfzCRgX6eLi, MD5 prefix 3c6): searches for the
"tricky bits". Every candidate passes the free 3c6 prefix filter before a full derivation.

  boundary    every subset of case toggles at the 20 paragraph first/last letters, on the posted
              text, the text without "Even after ... detail.", that sentence as its own paragraph
              and on its own line; \\n and \\r\\n
  plus2       5 rule readings (non-ITASM, ITASM, "recognize the signs", I-only, none) + any 1 or 2
              further case toggles anywhere
  edit1       7 rule readings + any single insert/delete/replace (printable ASCII or \\n) anywhere
  structured  per paragraph: unchanged / rule flip / flip + Shift-held punctuation (US, DE) /
              last only / first only / flip + second letter capitalised  (144,120,025 texts)

Results 2026-10-19: all 0 match.
"""
import hashlib
import itertools
import os
import sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import fastoracle as fo  # noqa: E402

Q = open(os.path.join(HERE, '..', '..', 'cache', 'gry2_base.txt')).read()
PARAS = Q.split('\n\n')
SENT = ' Even after I explained the method used and the result in detail.'
ESCROW = '1tzieUfbeQghz2zjDeGHcAEfzCRgX6eLi'


def prefix_ok(b):
    h = hashlib.md5(b).digest()
    return h.hex() if h[0] == 0x3c and h[1] >> 4 == 6 else None


def both(t):
    return (t.encode(), t.replace('\n', '\r\n').encode())


def rule(idx, f=1, l=1, paras=PARAS):
    out = []
    for i, p in enumerate(paras):
        c = list(p)
        L = [k for k, ch in enumerate(c) if ch.isalpha()]
        if i in idx:
            if f:
                c[L[0]] = c[L[0]].lower()
            if l:
                c[L[-1]] = c[L[-1]].upper()
        out.append(''.join(c))
    return '\n\n'.join(out)


RULES = {'nonITASM': [2, 3, 5, 6, 7], 'FFWW': [2, 3, 6, 7], 'FFIWW': [2, 3, 4, 6, 7],
         'nonITASM+I': [2, 3, 4, 5, 6, 7], 'ITASM': [0, 1, 4, 8, 9], 'recog': [3, 4, 5, 7], 'none': []}


def boundary():
    variants = {'posted': Q, 'nosent': Q.replace(SENT, ''), 'splitpara': Q.replace(SENT, '\n\n' + SENT[1:]),
                'splitline': Q.replace(SENT, '\n' + SENT[1:])}
    for name, t in variants.items():
        pos, s = [], 0
        for p in t.split('\n\n'):
            L = [s + i for i, c in enumerate(p) if c.isalpha()]
            pos += [L[0], L[-1]]
            s += len(p) + 2
        b = bytearray(t.encode())
        for k in range(len(pos) + 1):
            for comb in itertools.combinations(sorted(set(pos)), k):
                bb = bytearray(b)
                for p in comb:
                    bb[p] ^= 0x20
                for x in (bytes(bb), bytes(bb).replace(b'\n', b'\r\n')):
                    h = prefix_ok(x)
                    if h:
                        yield h


def _plus2(args):
    name, i = args
    base = rule(RULES[name]).encode()
    letters = [k for k, c in enumerate(Q) if c.isalpha()]
    out = []
    for j in letters[letters.index(i):]:
        bb = bytearray(base)
        bb[i] ^= 0x20
        if j != i:
            bb[j] ^= 0x20
        for x in (bytes(bb), bytes(bb).replace(b'\n', b'\r\n')):
            h = prefix_ok(x)
            if h:
                out.append(h)
    return out


CH = [chr(c) for c in range(32, 127)] + ['\n']


def _edit1(args):
    name, lo, hi = args
    t = rule(RULES[name])
    out = []
    for p in range(lo, min(hi, len(t))):
        vs = [t[:p] + t[p + 1:]]
        for ch in CH:
            vs.append(t[:p] + ch + t[p:])
            if ch != t[p]:
                vs.append(t[:p] + ch + t[p + 1:])
        for v in vs:
            for x in both(v):
                h = prefix_ok(x)
                if h:
                    out.append(h)
    return out


US = {'.': '>', ',': '<', ';': ':', "'": '"', '/': '?'}
DE = {'.': ':', ',': ';'}


def _opts(p):
    c = list(p)
    L = [i for i, ch in enumerate(c) if ch.isalpha()]
    f = list(c)
    f[L[0]] = f[L[0]].lower()
    f[L[-1]] = f[L[-1]].upper()
    o = [p, ''.join(f)]
    nxt = L[-1] + 1
    for M in (US, DE):
        g = list(f)
        if nxt < len(g) and g[nxt] in M:
            g[nxt] = M[g[nxt]]
            o.append(''.join(g))
        elif nxt + 1 < len(g) and g[nxt + 1] in M:
            g[nxt + 1] = M[g[nxt + 1]]
            o.append(''.join(g))
    l1 = list(c); l1[L[-1]] = l1[L[-1]].upper(); o.append(''.join(l1))  # noqa: E702
    f1 = list(c); f1[L[0]] = f1[L[0]].lower(); o.append(''.join(f1))  # noqa: E702
    if len(L) > 1:
        s2 = list(f); s2[L[1]] = s2[L[1]].upper(); o.append(''.join(s2))  # noqa: E702
    return list(dict.fromkeys(o))


OPTS = [_opts(p) for p in PARAS]


def _structured(first):
    out = []
    for rest in itertools.product(*OPTS[1:]):
        for x in both('\n\n'.join((first,) + rest)):
            h = prefix_ok(x)
            if h:
                out.append(h)
    return out


def main(mode):
    fo.add_target(ESCROW, 'Grycoin Block 2')
    if mode == 'boundary':
        cands = list(boundary())
    else:
        if mode == 'plus2':
            fn, tasks = _plus2, [(n, i) for n in ('nonITASM', 'ITASM', 'recog', 'none', 'FFWW')
                                 for i, c in enumerate(Q) if c.isalpha()]
        elif mode == 'edit1':
            fn, tasks = _edit1, [(n, lo, lo + 50) for n in RULES for lo in range(0, len(Q) + 1, 50)]
        else:
            fn, tasks = _structured, OPTS[0]
        cands = []
        with Pool(4) as pool:
            for r in pool.imap_unordered(fn, tasks):
                cands += r
    hits = [(h, fo.check_entropy(bytes.fromhex(h))) for h in set(cands)]
    hits = [x for x in hits if x[1]]
    print(mode, 'prefix survivors', len(set(cands)), 'hits', hits)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'boundary')
