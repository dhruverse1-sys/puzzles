"""Solver for the "Puzzle designed for 8964" magic-card puzzle (r/Bitcoin, June 2026).

Rebuilds the Back-card from the six hollowed cards, finds the Front-card
(perfect Franklin square), derives the magician's XOR shortcut and decodes the
Chinese message.  Requires: numpy, ortools.

Coordinates are as seen from the front, with the hollowed cards lying unrotated.
"""
import numpy as np
from ortools.sat.python import cp_model

LABELS = (32, 16, 8, 4, 2, 1)

# Hole patterns transcribed from images 1-6 of the post ('#' = hollowed-out spot).
CARDS = {
    32: """#.#..#.# #.#..#.# #.#..#.# #.#..#.# .#.##.#. .#.##.#. .#.##.#. .#.##.#.""",
    16: """.##..##. .##..##. #..##..# #..##..# .##..##. .##..##. #..##..# #..##..#""",
    8: """##....## ..####.. ..####.. ##....## ..####.. ##....## ##....## ..####..""",
    4: """.##.#..# #..#.##. #..#.##. .##.#..# .##.#..# #..#.##. #..#.##. .##.#..#""",
    2: """####.... ....#### ####.... ....#### ....#### ####.... ....#### ####....""",
    1: """.#.##.#. #.#..#.# #.#..#.# .#.##.#. #.#..#.# .#.##.#. .#.##.#. #.#..#.#""",
}
holes = {k: np.array([[ch == "#" for ch in row] for row in s.split()], dtype=int) for k, s in CARDS.items()}

# Image 9, laid out like the printed Back-card.
CHARS = """主 岸 操 的 安 畏 民， 計，
升 轉 錯。 屠 彼 尾， 不 降。
刀 門 自 兩 於 民 天 首
攻 殺， 東 型。 流 西 時 畏
克 必 途， 由 國 富 不 64
鎮 以 典 然 中 血 灣 台
殊 如 坦 割， 可 89 人 藏
範 儼 壓 可 台 灣 為 的"""

CELLS = [(r, c) for r in range(8) for c in range(8)]


def show(grid, title):
    print(title)
    for row in grid:
        print("   " + " ".join(f"{v:>2}" for v in row))
    print()


def appears(r, c):
    """Cards a number at front cell (r, c) is printed on: those where (r, c) is solid."""
    return {k for k in LABELS if not holes[k][r, c]}


# --- 1. Back-card ----------------------------------------------------------
# Rotating any card 180 degrees turns its holes exactly into its solid cells, so for
# every cell each card has one orientation with a hole there.  The host's index is
# 64 - sum(turned cards) = 1 + sum(labels of the cards on which the cell is a hole).
for k in LABELS:
    assert np.array_equal(np.rot90(holes[k], 2), 1 - holes[k])
back = 1 + sum(k * holes[k] for k in LABELS)
assert sorted(back.ravel()) == list(range(1, 65))
code_at = {int(back[r, c]): (r, c) for r, c in CELLS}
show(back[:, ::-1], "Back-card, as printed (card turned over):")


# --- 2. Front-card ---------------------------------------------------------
def perfect_franklin(anchors):
    """All 8x8 squares with every 2x2 block = 130, rows/cols/broken diagonals = 260."""
    m = cp_model.CpModel()
    x = [[m.NewIntVar(1, 64, f"x{r}{c}") for c in range(8)] for r in range(8)]
    m.AddAllDifferent([v for row in x for v in row])
    for i in range(8):
        m.Add(sum(x[i]) == 260)
        m.Add(sum(x[r][i] for r in range(8)) == 260)
        m.Add(sum(x[r][(r + i) % 8] for r in range(8)) == 260)
        m.Add(sum(x[r][(i - r) % 8] for r in range(8)) == 260)
        for j in range(8):
            m.Add(x[i][j] + x[i][(j + 1) % 8] + x[(i + 1) % 8][j] + x[(i + 1) % 8][(j + 1) % 8] == 130)
    for code, value in anchors.items():
        r, c = code_at[code]
        m.Add(x[r][c] == value)

    found = []

    class Collect(cp_model.CpSolverSolutionCallback):
        def on_solution_callback(self):
            found.append(np.array([[self.Value(v) for v in row] for row in x]))

    solver = cp_model.CpSolver()
    solver.parameters.enumerate_all_solutions = True
    solver.parameters.num_workers = 1
    solver.Solve(m, Collect())
    return found


def classic_franklin(f):
    """Franklin's own properties: half rows/cols = 130 and bent (V) diagonals = 260."""
    if not all(f[i, :4].sum() == f[i, 4:].sum() == f[:4, i].sum() == f[4:, i].sum() == 130 for i in range(8)):
        return False
    bend = [0, 1, 2, 3, 3, 2, 1, 0]
    return all(
        sum(f[i, (s + d * bend[i]) % 8] for i in range(8)) == 260
        and sum(f[(s + d * bend[j]) % 8, j] for j in range(8)) == 260
        for s in range(8)
        for d in (1, -1)
    )


# (front, back) anchors: 9<->6 and 8<->4 from the story and images 7/8, 38<->64 since it
# appears on no card, and 20/26 appear on every card except 8- so they sit on codes 1 and 9.
known = {6: 9, 4: 8, 64: 38}
assert not perfect_franklin({**known, 1: 26, 9: 20}), "20<->9, 26<->1 is impossible"
candidates = perfect_franklin({**known, 1: 20, 9: 26})
front, = [f for f in candidates if classic_franklin(f)]
assert front[0, 3] == 8 and front[0, 4] == 9
print(f"{len(candidates)} perfect squares fit the anchors; exactly one is also a classic Franklin square.")
show(front, "Front-card:")


# --- 3. Magician's shortcut ----------------------------------------------
start = int(front[code_at[64]]) - 1
key = {}
for k in LABELS:
    (r, c), = [(r, c) for r, c in CELLS if appears(r, c) == {k}]
    key[k] = (int(front[r, c]) - 1) ^ start


def magician(cards):
    acc = start
    for k in cards:
        acc ^= key[k]
    return acc + 1


assert all(magician(appears(r, c)) == front[r, c] for r, c in CELLS)
print(f"Magician: start at {start:o} (octal), XOR the spirit number of every card the number is on, add 1.")
print("   " + "  ".join(f"{k}-:{key[k]:02o}" for k in LABELS) + "   (octal) -- verified for all 64 numbers")
for cards in [set(), {32, 16, 8, 2}, {32, 4, 1}, {32, 8, 1}]:
    print(f"   on {sorted(cards, reverse=True) or 'no card'}: {magician(cards)}")
print()


# --- 4. Hidden message ----------------------------------------------------
grid = [line.split() for line in CHARS.splitlines()]
printed = back[:, ::-1]
message = "".join(ch for _, ch in sorted((int(printed[r, c]), grid[r][c]) for r, c in CELLS))
print("Message (characters in Back-card order 1..64):")
print("   " + message)
