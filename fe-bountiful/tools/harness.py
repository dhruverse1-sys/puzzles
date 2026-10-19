"""pyrevm harness for the Fe bountiful games: deploy from the repo's creation
bytecode, drive moveField/getBoard/isSolved, and a reference 15-puzzle model."""
import os
from Crypto.Hash import keccak
from pyrevm import EVM

REPO = "/home/user/fe-lang/bountiful/contracts"
HEX = os.path.join(REPO, "hex")
UNSOLVABLE = 0x0EFDCBA987654321
SOLVED = 0x0FEDCBA987654321
DEPLOYER = "0x00000000000000000000000000000000000000A1"

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return k.digest()[:4]

MOVE1 = sel("moveField(uint256)")
MOVE2 = sel("moveField(uint256,uint256)")
GET1  = sel("getBoard(uint256)")
GET2  = sel("getBoard(uint256,uint256)")
SOLVEDSEL = sel("isSolved()")

def w(x): return int(x).to_bytes(32, "big")
def creation(name): return bytes.fromhex(open(os.path.join(HEX, name + ".bin")).read().strip())

GAMES_1D = ["Game", "GameEnum", "GameBitboard", "GameTrait", "GameNested", "GameMonadic"]

def new_evm():
    e = EVM()
    e.set_balance(DEPLOYER, 10**24)
    return e

def deploy(e, name, args: bytes):
    return e.deploy(DEPLOYER, creation(name) + args, gas=30_000_000)

def deploy_game(e, name, board=UNSOLVABLE):
    validator = deploy(e, "DummyLockValidator", w(0))      # false -> never reverts
    return deploy_game_with_validator(e, name, validator, board)

def deploy_game_with_validator(e, name, validator, board=UNSOLVABLE):
    return deploy(e, name, bytes(12) + bytes.fromhex(validator[2:]) + w(board))

def call(e, to, calldata, value=0):
    try:
        out = e.message_call(DEPLOYER, to, calldata=calldata, value=value, gas=30_000_000)
        return True, bytes(out)
    except Exception as ex:
        return False, str(ex)

def get_board_1d(e, g):
    b = 0
    for i in range(16):
        ok, out = call(e, g, GET1 + w(i))
        assert ok, out
        b |= (int.from_bytes(out, "big") & 0xF) << (i * 4)
    return b

def get_board_2d(e, g):
    b = 0
    for i in range(16):
        ok, out = call(e, g, GET2 + w(i // 4) + w(i % 4))
        assert ok, out
        b |= (int.from_bytes(out, "big") & 0xF) << (i * 4)
    return b

def is_solved(e, g):
    ok, out = call(e, g, SOLVEDSEL)
    return ok and int.from_bytes(out, "big") == 1

# ---------- reference 15-puzzle semantics ----------
def cell(b, i): return (b >> (i * 4)) & 0xF
def setc(b, i, v): s = i * 4; return (b & ~(0xF << s)) | (v << s)
def empty_idx(b):
    e = 16
    for i in range(16):
        if cell(b, i) == 0: e = i
    return e
def adjacent(a, c):
    ra, ca, rb, cb = a // 4, a % 4, c // 4, c % 4
    rd = abs(ra - rb); cd = abs(ca - cb)
    return (rd == 1 and cd == 0) or (rd == 0 and cd == 1)
def ref_move(b, idx):
    if idx > 15: return False, b
    e = empty_idx(b)
    if e > 15 or not adjacent(e, idx): return False, b
    v = cell(b, idx); nb = setc(b, idx, 0); return True, setc(nb, e, v)

if __name__ == "__main__":
    # Controls: every game must mirror the published rules on the deployed bytecode.
    for name in GAMES_1D:
        e = new_evm(); g = deploy_game(e, name)
        assert get_board_1d(e, g) == UNSOLVABLE, name
        assert not is_solved(e, g), name
        ok0, _ = call(e, g, MOVE1 + w(0));  assert not ok0, name + " move 0 should revert"
        ok14, _ = call(e, g, MOVE1 + w(14)); assert ok14, name + " move 14 should succeed"
        print(f"{name:14} controls OK (board, isSolved=false, move0 revert, move14 ok)")
    e = new_evm(); g = deploy_game(e, "Game2D")
    assert get_board_2d(e, g) == UNSOLVABLE
    assert not is_solved(e, g)
    assert not call(e, g, MOVE2 + w(0) + w(0))[0]
    assert call(e, g, MOVE2 + w(3) + w(2))[0]   # index 14 = row3,col2, neighbour of empty@15
    print("Game2D         controls OK")
    print("ALL CONTROLS OK")
