"""MD5 -> BIP39 (12 words) -> BIP44 m/44'/0'/0'/0/i -> P2PKH hash160, in pure Python + coincurve.

Certified on import-free self-test (run this file directly):
  * the author's own published vector: entropy 2941774a... at index 1 -> WIF L5Z66qPm...
  * Block 77 Stage One: MD5 9dd2efb9... -> 19TbyN5K... at index 0
"""
import hashlib
import hmac
import struct

import coincurve
from mnemonic import Mnemonic

WL = Mnemonic('english').wordlist
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
B58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def b58dec(s):
    n = 0
    for c in s:
        n = n * 58 + B58.index(c)
    return n.to_bytes(25, 'big')


def b58enc(b):
    n = int.from_bytes(b, 'big')
    s = ''
    while n:
        n, r = divmod(n, 58)
        s = B58[r] + s
    pad = len(b) - len(b.lstrip(b'\0'))
    return '1' * pad + s


TARGETS = {
    "14zMkTgaVXJcxdh4JdWi29MLRR44iUSG9W": "RBB current",
    "1EFojcAo2vbhRGCGCa7q8Wwvzss28mhQYC": "RBB superseded 2019-07-24",
    "19TbyN5KCg1Lg7qHwezifsLVcdSa2Rj5KN": "Stage One (solved ref)",
}
TH160 = {b58dec(a)[1:21]: l for a, l in TARGETS.items()}


def add_target(address, label):
    TH160[b58dec(address)[1:21]] = label


def mnemonic_from_entropy(ent: bytes) -> str:
    h = hashlib.sha256(ent).digest()
    bits = int.from_bytes(ent, 'big') << 4 | (h[0] >> 4)
    return ' '.join(WL[(bits >> (11 * (11 - i))) & 0x7FF] for i in range(12))


def ckd_priv(k, c, i):
    if i & 0x80000000:
        data = b'\0' + k.to_bytes(32, 'big') + struct.pack('>I', i)
    else:
        data = coincurve.PrivateKey(k.to_bytes(32, 'big')).public_key.format(True) + struct.pack('>I', i)
    I = hmac.new(c, data, hashlib.sha512).digest()
    return (int.from_bytes(I[:32], 'big') + k) % N, I[32:]


def h160(pub):
    return hashlib.new('ripemd160', hashlib.sha256(pub).digest()).digest()


def account_node(mn: str, passphrase=''):
    seed = hashlib.pbkdf2_hmac('sha512', mn.encode(), ('mnemonic' + passphrase).encode(), 2048)
    I = hmac.new(b'Bitcoin seed', seed, hashlib.sha512).digest()
    k, c = int.from_bytes(I[:32], 'big'), I[32:]
    for i in (44 | 0x80000000, 0x80000000, 0x80000000, 0):
        k, c = ckd_priv(k, c, i)
    return k, c


def check_entropy(ent: bytes, n=6, passphrase=''):
    """Return [(label, index, compressed)] for any target hit at m/44'/0'/0'/0/0..n-1."""
    k, c = account_node(mnemonic_from_entropy(ent), passphrase)
    hits = []
    for i in range(n):
        ki, _ = ckd_priv(k, c, i)
        pub = coincurve.PrivateKey(ki.to_bytes(32, 'big')).public_key
        for comp in (True, False):
            hh = h160(pub.format(comp))
            if hh in TH160:
                hits.append((TH160[hh], i, comp))
    return hits


def check_text(t, enc='utf-8', n=6):
    b = t.encode(enc) if isinstance(t, str) else t
    return check_entropy(hashlib.md5(b).digest(), n)


def wif(ent, index):
    k, c = account_node(mnemonic_from_entropy(ent))
    ki, _ = ckd_priv(k, c, index)
    payload = b'\x80' + ki.to_bytes(32, 'big') + b'\x01'
    return b58enc(payload + hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4])


if __name__ == '__main__':
    import time
    e = bytes.fromhex("2941774a2abec9f30c7d6777d1d53d91")
    assert wif(e, 1) == "L5Z66qPmUkTAsWQywjRNHDxHrX6J1X1SQedp6V8QsbaXR7rGd6ex"
    print("author's vector OK")
    assert check_entropy(bytes.fromhex("9dd2efb9bc976c2095bd534d7b8d431c")) == [('Stage One (solved ref)', 0, True)]
    print("Stage One MD5 -> 19TbyN5K... index 0 OK")
    t = time.time()
    for j in range(200):
        check_text("x%d" % j)
    print("single-core rate/s", round(200 / (time.time() - t)))
