"""Parallel candidate runner with a planted witness.

run(gen) consumes (label, bytes) pairs, de-duplicates by MD5, inserts a synthetic witness whose
index-2 address is added to the targets, and reports the rate and whether the witness was found.
A negative only counts if witness_recovered=True.
"""
import hashlib
import os
import sys
import time
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coincurve  # noqa: E402
import fastoracle as fo  # noqa: E402


def _init(wit):
    fo.TH160.update(wit)


def _work(item):
    label, b = item
    r = fo.check_entropy(hashlib.md5(b).digest(), n=6)
    return (label, r) if r else None


def run(gen, witness_text=b'witness::planted::text', nproc=4, chunk=16):
    ent = hashlib.md5(witness_text).digest()
    k, c = fo.account_node(fo.mnemonic_from_entropy(ent))
    ki, _ = fo.ckd_priv(k, c, 2)
    wh = {fo.h160(coincurve.PrivateKey(ki.to_bytes(32, 'big')).public_key.format(True)): 'WITNESS'}
    seen, hits = set(), []
    n = 0
    t0 = time.time()

    def stream():
        nonlocal n
        inserted = False
        for label, b in gen:
            h = hashlib.md5(b).digest()
            if h in seen:
                continue
            seen.add(h)
            n += 1
            yield (label, b)
            if not inserted and n >= 50:
                inserted = True
                yield ('WITNESS', witness_text)
        if not inserted:
            yield ('WITNESS', witness_text)

    with Pool(nproc, initializer=_init, initargs=(wh,)) as pool:
        for r in pool.imap_unordered(_work, stream(), chunksize=chunk):
            if r:
                hits.append(r)
                print('HIT', r, flush=True)
    dt = time.time() - t0
    wit = any(h[0] == 'WITNESS' for h in hits)
    real = [h for h in hits if h[0] != 'WITNESS']
    print(f'unique={n} time={dt:.1f}s rate={n / dt:.0f}/s witness_recovered={wit} real_hits={len(real)}',
          flush=True)
    return real, n, wit
