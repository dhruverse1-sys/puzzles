"""Verify that the bytecode deployed on Ethereum mainnet for each of the 8 Fe
bountiful contracts is exactly what the published Fe source compiles to.

This needs only an Ethereum RPC (no EVM, no compiler). It fetches each contract's
runtime bytecode with eth_getCode and compares its sha256 to the value recorded in
expected.json. To also prove deployed == compiled-source, build the repo with
fe 26.1.0 (`make build` in fe-lang/bountiful) and compare contracts/out/*.bin; the
recorded hashes were taken on 2026-10-19 when that comparison was byte-for-byte equal
for all 8, including GameBitboard and GameTrait (which Sourcify does not verify).
"""
import hashlib
import json
import os
import sys
import urllib.request

RPC = os.environ.get("ETH_RPC_URL", "https://ethereum-rpc.publicnode.com")
ADDR = {
    "Game": "0x046a3a4968282BaA7ad6291723873C8275434623",
    "Game2D": "0xE959e7ecA1afCa6cf2Bf8b07e25Da355b6C8E8c7",
    "GameEnum": "0xfb5423aDfBAC65ac675845Bb4FEBf8aeC128272E",
    "GameBitboard": "0x5E987b6aADD4DFC2236D21edE6D07feb04350b06",
    "GameMonadic": "0x86B7AEce1503242fED29E593FAEde3b7b00a5a1D",
    "GameNested": "0x3dF9789634995546B0126bC28B9F9FcBCB129F18",
    "GameTrait": "0x85b4d0B32b8a285111c244E52524B642f1A5ccFE",
    "BountyRegistry": "0x71fB6afcD98c5BD611712ad4b8D314EF729aa69D",
}


def get_code(addr):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                       "params": [addr, "latest"]}).encode()
    req = urllib.request.Request(RPC, data=body,
                                 headers={"content-type": "application/json",
                                          "User-Agent": "Mozilla/5.0"})
    return bytes.fromhex(json.loads(urllib.request.urlopen(req, timeout=30).read())["result"][2:])


def main():
    expected = json.load(open(os.path.join(os.path.dirname(__file__), "expected.json")))
    ok = True
    for name, addr in ADDR.items():
        code = get_code(addr)
        h = hashlib.sha256(code).hexdigest()
        exp = expected[name]
        match = (h == exp["sha256"] and len(code) == exp["runtime_bytes"])
        ok = ok and match
        print(f"{name:16} {len(code):5}b sha256={h[:16]}... "
              f"{'OK' if match else 'CHANGED since 2026-10-19!'}")
    print("ALL MATCH RECORDED HASHES" if ok else "MISMATCH")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
