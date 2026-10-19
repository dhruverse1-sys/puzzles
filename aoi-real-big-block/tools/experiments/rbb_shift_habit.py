"""RBB: group flips where the character after a newly capitalised last letter was also shifted.

The author habitually holds Shift a beat too long ("FIrst", "SInce", "BItcoin", "DIscussion").
Re-typing a capital at the end of a paragraph could also shift the next key: "." -> ">" on a US
layout, "." -> ":" on a German one. Every non-empty subset of the 4 units, every subset of the
flipped paragraphs carrying the accident, both layouts, joins \\n\\n and \\r\\n\\r\\n with and
without a trailing newline.
"""
import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import chapter as C  # noqa: E402
import harness as H  # noqa: E402

US = {'.': '>', ',': '<', ';': ':', "'": '"', '/': '?'}
DE = {'.': ':', ',': ';'}
UNITS = {'G1': C.G1, 'G3': C.G3, 'G2': C.G2, 'Q': C.Q}


def shifted(p, M):
    L = [i for i, ch in enumerate(p) if ch.isalpha()]
    for j in (L[-1] + 1, L[-1] + 2):  # skip one closing quote
        if j < len(p) and p[j] in M:
            return p[:j] + M[p[j]] + p[j + 1:]
    return None


def gen():
    names = list(UNITS)
    for r in range(1, 5):
        for us in itertools.combinations(names, r):
            S = sorted(itertools.chain(*[UNITS[u] for u in us]))
            base = [C.flip(p) if i in S else p for i, p in enumerate(C.T)]
            for lay, M in (('US', US), ('DE', DE)):
                for mask in range(1, 1 << len(S)):
                    paras = list(base)
                    changed = False
                    for k, i in enumerate(S):
                        if mask >> k & 1:
                            s = shifted(paras[i], M)
                            if s:
                                paras[i] = s
                                changed = True
                    if not changed:
                        continue
                    for join, tail in (('\n\n', '\n'), ('\n\n', ''), ('\r\n\r\n', '\r\n'), ('\r\n\r\n', '')):
                        br = '\n' if join == '\n\n' else '\r\n'
                        yield (f'{us} {lay} {mask:x} {join!r}{tail!r}', C.serialize(paras, join, tail, True, br))


if __name__ == '__main__':
    H.run(gen())
