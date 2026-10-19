# Fe "Bountiful" compiler bug bounty: session notes, 2026-10-19

Target: the Fe language team's bug bounty. Make `isSolved()` return `true` on one of 7 game
contracts whose board starts in the mathematically unsolvable 15-puzzle state (tiles 14 and 15
swapped), which would prove a bug in the Fe compiler, and claim 0.25 ETH (pot 1 ETH) from the
registry `0x71fB6afcD98c5BD611712ad4b8D314EF729aa69D`. Research base:
[open-crypto-puzzles/2-mid-prizes/fe-lang-bountiful-compiler-bounty-1eth](https://github.com/dhruverse1-sys/open-crypto-puzzles/tree/main/2-mid-prizes/fe-lang-bountiful-compiler-bounty-1eth);
contracts: [fe-lang/bountiful](https://github.com/fe-lang/bountiful).

**Status: not solved.** No compiler miscompilation found; no claim is possible without one.
What this session adds is a certified-negative that the upstream folder lists as an open lead
(lead 3), plus an independent differential search on the real deployed bytecode.

## What I verified

1. **All 7 games and the registry are logically correct at the source level.** Every
   `moveField` checks the lock, rejects out-of-range indices, locates the empty cell, verifies
   4-neighbour adjacency, and swaps. The registry's `claim` closes the challenge *before* the
   external `isSolved()` call (correct checks-effects-interactions) and only pays if that call
   returns true. So a win requires the compiler to miscompile this correct source.

2. **Deployed bytecode == published source, for all 8 contracts, including the two Sourcify
   does not verify.** I fetched each contract's runtime bytecode from mainnet (`eth_getCode`)
   and compared it to the repo built with fe 26.1.0: a byte-for-byte match for all 8, and in
   particular for `GameBitboard` (`0x5E98…350b06`) and `GameTrait` (`0x85b4…5ccFE`), which have
   no verified source on Sourcify. This closes the upstream "rebuild the two unverified
   contracts" lead with a clean negative: what is deployed is the published source, so the
   search space is exactly that source, attackable identically on a local fork.
   `tools/verify_deployed.py` re-checks this against recorded sha256 hashes
   (`tools/expected.json`); it passed on 2026-10-19.

3. **No economic path exists without solving a game.** The registry only pays on
   `isSolved()==true`; challenges are registered by the admin, so an attacker cannot register
   an always-true contract; `withdraw()` is admin-only and blocked while any lock is active;
   the lock deposit is kept. The payout uses a raw call forwarding all gas to the caller, but
   `claim` marks the challenge closed before paying, so reentering `claim` on it reverts with
   `InvalidClaim`. Every route to the money runs through a solved board.

4. **The unsolvable start is unreachable by correct moves.** For a 4x4 board the parity of
   (tile inversions + empty-cell row) is invariant under any legal slide; the start has
   invariant 0 and the solved board 1, so no sequence of correctly-executed `moveField` calls
   connects them. Only a miscompiled move can bridge the gap.

## What I searched (0 findings)

I ran the actual deployed bytecode in a local EVM (`pyrevm` / revm), driving all 7 games in
lockstep with a reference 15-puzzle model. The win check each step is `isSolved()==false` and
move-acceptance matching the reference; board state is fully compared periodically. Controls
pass first: each game reproduces the unsolvable board, `isSolved()==false`, a known-good move
succeeds, and a non-adjacent move reverts.

| Search | Scope | Result |
|---|---|---|
| Complete depth-7 enumeration | every one of the 414 distinct boards reachable within 7 moves, replayed on all 7 games, full board compared | 0 divergence, none solved |
| Game2D two-argument sweep | `moveField(row,col)` for row,col over 0..19 plus dirty 64/128/256-bit values; reference rejects any row>3 or col>3 | 0 divergence, none solved |
| Lockstep random walk | 8 seeds x 120,000 steps (960,000 total), neighbour-biased with periodic fully-random/illegal indices, full board compared every 20 steps | 0 divergence, none solved (completed in 441s) |

This complements, with an independent implementation and much higher step counts, the two
Solidity suites already in the repo (the maintainers' `ExploitSearch`: deep walks, dirty-high-bit
indices, every first move; and a `MalformedCalldata` sweep: truncated/trailing calldata, unknown
selectors, value-bearing calls). All agree: every variant mirrors the reference and nothing
becomes solved.

## Honest assessment

The source is correct, the deployed bytecode is exactly that source, and the obvious dynamic
attack surface is hardened and now independently re-tested. A win requires a genuine Fe
compiler miscompilation that none of these searches has triggered — the previous round of this
bounty ran unsolved for nearly three years. The realistic next steps are not more black-box
fuzzing but compiler-level work:

1. Audit fe 26.1.0's codegen for the specific constructs each game isolates (StorageMap slot
   hashing, nested fixed-array offset math, enum/`match` dispatch, bit-packing shifts/masks,
   the `Fn`-trait monadic chain, `u128 as u256` casts in `WordRepr`), looking for an input-
   dependent wrong opcode rather than a structural error.
2. Differential-test the compiler itself: compile many small Fe programs exercising those
   constructs with fe 26.1.0 and compare against an independent EVM reference.

Both need the Fe toolchain (not installed here) and are open-ended research, not a bounded
solve.

## Running

```bash
pip install pyrevm pycryptodome            # local EVM + keccak
python3 tools/verify_deployed.py           # deployed bytecode == recorded hashes (RPC only)
# the search tools expect fe-lang/bountiful cloned at /home/user/fe-lang/bountiful
python3 tools/harness.py                   # controls: all games mirror the rules
python3 tools/exploit_search.py 120000 8   # depth-7 + 2D grid + 8x120000 lockstep steps
```

No key material is produced. A real finding would print `SOLVED`/`MOVE`/`BOARD` with the
contract and inputs; this session printed none.
