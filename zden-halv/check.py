#!/usr/bin/env python3
"""Check whether a hex private key controls the Level HALV prize address.

Usage:
    python3 check.py <64 hex chars> [...]

Requires: pip install coincurve base58
"""
import hashlib
import sys

import base58
import coincurve

TARGET = "1crypto24HCr178iMcKd5iUi5D4rsg1nK"
TARGET_H160 = base58.b58decode_check(TARGET)[1:]
ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def h160(data):
    return hashlib.new("ripemd160", hashlib.sha256(data).digest()).digest()


def matches(key):
    """True if the integer key gives the target address (compressed or uncompressed)."""
    if not 0 < key < ORDER:
        return False
    pub = coincurve.PrivateKey(key.to_bytes(32, "big")).public_key
    return TARGET_H160 in (h160(pub.format(True)), h160(pub.format(False)))


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        print(arg, "MATCH" if matches(int(arg, 16)) else "no match")
