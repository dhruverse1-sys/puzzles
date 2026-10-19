"""Parallel BIP39 / Electrum search over word-sequence hypotheses.

Usage examples:
  # every ordered choice of K words from a pool
  python3 search.py perms --k 3 --pool pool.txt
  # a template where '*' is any BIP39 word and '{a|b}' is a choice
  python3 search.py template "moon tower food * * * this real subject black * *"
"""
import argparse
import itertools
import multiprocessing as mp
import sys
import time

import seedcheck as s

FAST_PATHS = {k: s.PATHS[k] for k in ("m/44'/0'/0'/0", "m/0", "m/0'/0")}
PASSPHRASES = ("",)


def _check(words):
    phrase = " ".join(words)
    hits = []
    if s.bip39_valid(words):
        for pw in PASSPHRASES:
            r = s.check_seed(s.mnemonic_to_seed(phrase, pw), FAST_PATHS)
            if r:
                hits.append(f"BIP39 pw={pw!r} {r}")
    if s.electrum_seed_type(phrase) == "standard":
        r = s.check_seed(s.mnemonic_to_seed(phrase, "", "electrum"), FAST_PATHS)
        if r:
            hits.append(f"Electrum {r}")
    return phrase, hits


def _valid_only(gen):
    # Cheap pre-filter in the parent so workers only see candidates that
    # need a PBKDF2 (BIP39 checksum OK, or an Electrum "standard" version).
    for words in gen:
        if s.bip39_valid(words) or s.electrum_seed_type(" ".join(words)) == "standard":
            yield words


def run(gen, label):
    t0 = time.time()
    n = 0
    found = []
    with mp.Pool() as pool:
        for phrase, hits in pool.imap_unordered(_check, _valid_only(gen), chunksize=256):
            n += 1
            for h in hits:
                print("FOUND", repr(phrase), h, flush=True)
                found.append((phrase, h))
            if n % 50000 == 0:
                print(f"  {label}: {n} seeds checked, {time.time() - t0:.0f}s", flush=True)
    print(f"{label}: done, {n} seeds checked in {time.time() - t0:.0f}s, hits={len(found)}", flush=True)
    return found


def template_gen(tpl):
    slots = []
    for tok in tpl.split():
        if tok == "*":
            slots.append(s.BIP39)
        elif tok.startswith("{"):
            slots.append(tok.strip("{}").split("|"))
        else:
            slots.append([tok])
    for combo in itertools.product(*slots):
        yield list(combo)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("perms")
    p.add_argument("--k", type=int, required=True)
    p.add_argument("--pool", required=True)
    t = sub.add_parser("template")
    t.add_argument("tpl")
    a = ap.parse_args()
    if a.cmd == "perms":
        pool = [w for w in open(a.pool).read().split() if w in s.BIP39_INDEX]
        print(f"pool of {len(pool)} BIP39 words, k={a.k}", file=sys.stderr)
        run((list(c) for c in itertools.permutations(pool, a.k)), f"perms k={a.k}")
    else:
        run(template_gen(a.tpl), f"template {a.tpl!r}")
