# Puzzles already checked

Index of every rewarded crypto puzzle looked at by sessions on this repo, so new sessions
don't redo work. Escrow states are as of the date shown; re-check on-chain before working on one.

## Worked in depth (notes on a branch)

| Puzzle | Prize | Result | Notes |
|---|---|---|---|
| Path to Greatness (jpatt94) | 3.03 LTC | unsolved; 2 new witnessed negatives, 4 new clue readings | `path-to-greatness/` on `claude/gracious-fermi-qya9og` (2026-10-20) |
| GemfinderOfX tweet grid | 0.0202 BTC | unsolved; grid digits look generated, no hidden channel found | `gemfinderofx/` on `claude/gracious-fermi-qya9og` (2026-10-20) |
| Aoi Nakamoto Quizchain (Real Big Block) | 0.777 BTC | unsolved | `aoi-real-big-block/` on `claude/serene-rubin-jgp7jj` |
| Fe "Bountiful" compiler bounty | 1 ETH | unsolved; deployed bytecode = source, 960k-step differential walk clean | `fe-bountiful/` on `claude/serene-rubin-jgp7jj` |
| Zden Level HALV | 312,500 sats | unsolved | `zden-halv/` on `claude/admiring-gates-3a50qq` |
| BLM "Brave New World" collage | 0.2 BTC | unsolved; ~383k phrases negative | `0.2-btc-puzzle/` on `claude/determined-brahmagupta-fkrnqy` |
| RushWallet Contest #30 | 0.01 BTC | stopped; needed web.archive.org access | session "Bitcoin Rushwallet puzzle" |
| Smith, Lyle & Moore Hunt #2 | 0.032 BTC | stopped; other teams far ahead (10 of 12 words claimed) | sessions "Puzzle solving from repo", "Public Bitcoin puzzles" |
| Hunghuatang "8964" Reddit puzzle | BTC | in progress in another session (2026-10-20) | session "Bitcoin puzzle solution" |

## Triaged and set aside

| Puzzle | Why |
|---|---|
| 1000 BTC puzzle (#71 and up, #140) | GPU-farm scale; one session declined #140 |
| Ballet / Bobby Lee cards (2 BTC) | missing halves are physically on the cards |
| Bitaps Shamir (1 BTC) | ~125 bits without the third share |
| GSMG.io (1.26 BTC) | final AES blobs need an insight nobody has found |
| Guntis Vitolins MetaMask (8.61 ETH) | ~35 billion GPU-tested seeds, active community; needs word identification, not compute |
| Keir Finlow-Bates book hunt | answers only in the paper book |
| Corey Phillips kitten passphrase, School of Bitcoin | information the authors never published |
| Arweave #11 (1 ETH) | 6 years unsolved; bit-plane ASCII, zlib and first-row raw-key scans already done upstream |
| Arweave #3, #10 | rebus readings, upstream has millions of negatives; no new angle found |
| Wealth in Poetry (0.031 BTC) | carrier text and numeric key are author-specific by design |
| Exitonly Challenge 14 | brute force costs thousands of times the prize |
| crypto-puzzles-2018 #2 | key must be read off YouTube videos, which this container can't reach |
| FTPK Season 2, Pindar NFT | escrow already swept / NFT gone |
| Teikhos bounties, Peter Todd collisions | need a research breakthrough |
| KwikbitL "swipe my sats" | 2 of its 3 "ways to win" are hacking an email/drive (declined); the seed part has no published address |
| dlay_on 10M sats | 8 of 12 seed words missing (~2^88) |
| SimplestBTCBook 369k sats | already solved (Keysa, swept 2026-09-08) |
| Genesis Block Wallet Puzzle (block 963,629) | solved and swept 2026-10-17 |
| LuckyLurker Bitcoin Vault #2 (1 BTC, `bc1qnepv9pcnqvndux9h9mcaxvk6u993rc0lew9fpp`) | funded and unspent 2026-10-20, but the page says "Postponed until further notice" (sponsor issue); none of the 12 riddles published. Re-check https://luckylurker.com/bitcoin-vault-2/ |
| kTimesG "phy" (0.008 BTC, bitcointalk topic 5584952) | open since 2026-06-05; 19 author hints, solvers stuck 4 months; possible reasoning target, not attempted |
| The Great Riddle (0.0042 BTC) | words are hidden only in the physical original drawings |
| bitaddress BIP38 "brute force and the coins are yours" (0.0053 BTC) | forgotten ~30-char passphrase, scrypt N=16384 p=8: infeasible |

## Upcoming (fresh, not yet open)

| Puzzle | Prize | Opens | Notes |
|---|---|---|---|
| ProofOfSolve #1 Meridian, MS (free) and #3 Alcatraz ($10 entry) | ~151k sats each | 2026-10-24 11:00 UTC | Google Street View hunt, 12 clues give 12 BIP39 words; answer submitted on proofofsolve.com, first correct wins, 3 tries per email per 24h. [Public record](https://github.com/ProofOfSolve/puzzles) |
| ProofOfSolve #2 Mount Vernon (free), #4 Lafayette ($5) | ~151k / ~$75 | 2026-10-31 | same |
| ProofOfSolve #5 Orange Beach, #6 Boston ($5 each) | ~$75 each | 2026-11-07, 2026-11-14 | same |
