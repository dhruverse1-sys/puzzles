"""Helpers over the cached "Second" chapter (run fetch_sources.py first)."""
import json
import os

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cache')
T = json.load(open(os.path.join(CACHE, 'paras_text.json')))

# bold heading paragraphs (0 is the title "Second")
HEAD = [0, 1, 2, 53, 70, 87, 88, 90, 114, 129, 151, 156, 160, 162, 163, 174, 175, 181, 208, 214,
        246, 249, 251, 253, 255, 257, 259, 264]

# the three planted F-F-W-W groups whose last letters spell S T N M, and the Finney quote
G1 = [4, 5, 6, 7]
G3 = [92, 93, 94, 95]
G2 = [167, 168, 169, 170]
Q = [230, 231, 232, 234]


def flip(p, first=True, last=True):
    """Stage One rule: first letter to lower case, last letter to upper case."""
    c = list(p)
    L = [i for i, ch in enumerate(c) if ch.isalpha()]
    if not L:
        return p
    if first:
        c[L[0]] = c[L[0]].lower()
    if last:
        c[L[-1]] = c[L[-1]].upper()
    return ''.join(c)


def serialize(paras, join='\n\n', tail='\n', nbsp=True, br='\n', drop=()):
    out = []
    for i, p in enumerate(paras):
        if i in drop:
            continue
        if not nbsp:
            p = p.replace(' ', ' ')
        out.append(p.replace('\n', br))
    return (join.join(out) + tail).encode('utf-8')
