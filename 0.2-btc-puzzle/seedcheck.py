"""Candidate checker for the 0.2 BTC "Brave New World" puzzle.

Prize address: 1KfZGvwZxsvSmemoCmEV75uqcNzYBHjkHZ
hash160:       ccbd031e54cde2a3189fd59bc49f731367a1779e

Each candidate is turned into keys several ways (BIP39 and Electrum seed
derivations, several P2PKH paths, compressed and uncompressed pubkeys, plus
brainwallet SHA256) and compared against the prize hash160.

Requires: coincurve (pip install coincurve).
"""
import hashlib
import hmac
import os
import sys
import unicodedata

from coincurve import PrivateKey

TARGET = bytes.fromhex("ccbd031e54cde2a3189fd59bc49f731367a1779e")
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
H = 0x80000000

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "bip39_english.txt")) as f:
    BIP39 = f.read().split()
BIP39_INDEX = {w: i for i, w in enumerate(BIP39)}

# P2PKH paths used by common wallets in 2020: BIP44 (most HD wallets),
# Electrum "standard" / BIP32 root chains, Bitcoin Core / Multibit HD, BRD.
PATHS = {
    "m/44'/0'/0'/0": [44 | H, 0 | H, 0 | H, 0],
    "m/44'/0'/0'/1": [44 | H, 0 | H, 0 | H, 1],
    "m/0": [0],
    "m/0'/0": [0 | H, 0],
    "m/0'/0'": [0 | H, 0 | H],
    "m/44'/0'/1'/0": [44 | H, 0 | H, 1 | H, 0],
}
ADDR_COUNT = 5


def hash160(b):
    return hashlib.new("ripemd160", hashlib.sha256(b).digest()).digest()


def pubkey_hashes(priv32):
    pk = PrivateKey(priv32)
    return (hash160(pk.public_key.format(compressed=True)),
            hash160(pk.public_key.format(compressed=False)))


def bip39_valid(words):
    """True if `words` passes the BIP39 checksum (English list).

    3/6/9-word phrases are non-standard but accepted by tools such as
    iancoleman.io/bip39, so they are allowed here too.
    """
    if len(words) not in (3, 6, 9, 12, 15, 18, 21, 24):
        return False
    try:
        bits = 0
        for w in words:
            bits = (bits << 11) | BIP39_INDEX[w]
    except KeyError:
        return False
    total = 11 * len(words)
    cs_len = total // 33
    ent_len = total - cs_len
    entropy = (bits >> cs_len).to_bytes(ent_len // 8, "big")
    checksum = bits & ((1 << cs_len) - 1)
    return hashlib.sha256(entropy).digest()[0] >> (8 - cs_len) == checksum


def mnemonic_to_seed(mnemonic, passphrase="", salt_prefix="mnemonic"):
    m = unicodedata.normalize("NFKD", mnemonic)
    s = unicodedata.normalize("NFKD", salt_prefix + passphrase)
    return hashlib.pbkdf2_hmac("sha512", m.encode(), s.encode(), 2048)


def electrum_seed_type(mnemonic):
    h = hmac.new(b"Seed version", mnemonic.encode(), hashlib.sha512).hexdigest()
    for prefix, name in (("01", "standard"), ("100", "segwit"), ("101", "2fa")):
        if h.startswith(prefix):
            return name
    return None


def master_from_seed(seed):
    i = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
    return int.from_bytes(i[:32], "big"), i[32:]


def ckd_priv(k, c, index, parent_pub=None):
    if index & H:
        data = b"\x00" + k.to_bytes(32, "big") + index.to_bytes(4, "big")
    else:
        if parent_pub is None:
            parent_pub = PrivateKey(k.to_bytes(32, "big")).public_key.format(compressed=True)
        data = parent_pub + index.to_bytes(4, "big")
    i = hmac.new(c, data, hashlib.sha512).digest()
    return (int.from_bytes(i[:32], "big") + k) % N, i[32:]


def check_seed(seed, paths=None):
    """Return a description of the matching path, or None."""
    mk, mc = master_from_seed(seed)
    for name, path in (paths or PATHS).items():
        k, c = mk, mc
        for idx in path:
            k, c = ckd_priv(k, c, idx)
        parent_pub = PrivateKey(k.to_bytes(32, "big")).public_key.format(compressed=True)
        for i in range(ADDR_COUNT):
            ck, _ = ckd_priv(k, c, i, parent_pub)
            hc, hu = pubkey_hashes(ck.to_bytes(32, "big"))
            if hc == TARGET:
                return f"{name}/{i} compressed"
            if hu == TARGET:
                return f"{name}/{i} uncompressed"
    return None


def check_brainwallet(phrase):
    priv = hashlib.sha256(phrase.encode()).digest()
    if not 0 < int.from_bytes(priv, "big") < N:
        return None
    hc, hu = pubkey_hashes(priv)
    if hc == TARGET:
        return "brainwallet compressed"
    if hu == TARGET:
        return "brainwallet uncompressed"
    return None


def check_mnemonic(words, passphrases=("",)):
    """Try one word sequence as BIP39 and as an Electrum standard seed."""
    phrase = " ".join(words)
    hits = []
    if bip39_valid(words):
        for pw in passphrases:
            r = check_seed(mnemonic_to_seed(phrase, pw))
            if r:
                hits.append(f"BIP39 passphrase={pw!r} {r}")
    if electrum_seed_type(phrase) == "standard":
        for pw in passphrases:
            r = check_seed(mnemonic_to_seed(phrase, pw, "electrum"))
            if r:
                hits.append(f"Electrum passphrase={pw!r} {r}")
    return hits


def _self_test():
    # BIP39 reference vector (trezor/python-mnemonic vectors.json, passphrase "TREZOR").
    words = ("abandon " * 11 + "about").split()
    assert bip39_valid(words)
    seed = mnemonic_to_seed(" ".join(words), "TREZOR")
    assert seed.hex().startswith("c55257c360c07c72029aebc1b53c05ed0362ada3")
    # BIP32 test vector 1: seed 000102...0f, m/0' chain code.
    mk, mc = master_from_seed(bytes(range(16)))
    assert mk.to_bytes(32, "big").hex() == "e8f32e723decf4051aefac8e2c93c9c5b214313817cdb01a1494b917c8436b35"
    k, c = ckd_priv(mk, mc, 0 | H)
    assert k.to_bytes(32, "big").hex() == "edb2e14f9ee77d26dd93b4ecede8d16ed408ce149b6cd80b0715a2d911a0afea"
    # Known address: private key 1 -> 1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH (compressed).
    assert pubkey_hashes((1).to_bytes(32, "big"))[0].hex() == "751e76e8199196d454941c45d1b3a323f1433bd6"
    print("self-test ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _self_test()
    else:
        for line in sys.stdin:
            line = line.strip().lower()
            if not line:
                continue
            for hit in check_mnemonic(line.split()) + [r for r in [check_brainwallet(line)] if r]:
                print("FOUND", repr(line), hit, flush=True)
