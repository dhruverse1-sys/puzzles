"""RBB: planted F-F-W-W groups flipped together with the "I" paragraph that completes "I STNM".

Grycoin Block 2's worked example says the "I" paragraph next to the signs may be flipped "as
well". Each unit is off, on, or on plus its I paragraph(s): G1+[3], G3+[91], G2+[166] or
G2+[164,165,166], Finney quote+[233]. 3 flip modes x 2 joins x 2 tails x NBSP kept/space x
headings (all / drop title / drop all). Result 2026-10-19: 7,704 unique texts, 0 match,
witness recovered.
"""
import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import chapter as C  # noqa: E402
import harness as H  # noqa: E402

UNITS = {
    'G1': [[], C.G1, C.G1 + [3]],
    'G3': [[], C.G3, C.G3 + [91]],
    'G2': [[], C.G2, C.G2 + [166], C.G2 + [164, 165, 166]],
    'Q': [[], C.Q, C.Q + [233]],
}


def gen():
    for combo in itertools.product(*UNITS.values()):
        S = set(itertools.chain(*combo))
        if not S:
            continue
        for mode in ((1, 1), (1, 0), (0, 1)):
            paras = [C.flip(p, *mode) if i in S else p for i, p in enumerate(C.T)]
            for join in ('\n\n', '\r\n\r\n'):
                br = '\n' if join == '\n\n' else '\r\n'
                for tail in ('', join[:len(join) // 2]):
                    for nbsp in (True, False):
                        for drop in ((), (0,), tuple(C.HEAD)):
                            yield (f'{sorted(S)} m{mode} j{join!r} t{tail!r} nb{nbsp} d{len(drop)}',
                                   C.serialize(paras, join, tail, nbsp, br, drop))


if __name__ == '__main__':
    H.run(gen())
