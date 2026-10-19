# Aoi Nakamoto "Real Big Block": session notes, 2026-10-19

Target: `14zMkTgaVXJcxdh4JdWi29MLRR44iUSG9W`, 0.777 BTC. Research base:
[open-crypto-puzzles/1-big-prizes/aoi-nakamoto-quizchain-0-854btc](https://github.com/dhruverse1-sys/open-crypto-puzzles/tree/main/1-big-prizes/aoi-nakamoto-quizchain-0-854btc).

**Status: not solved.** On 2026-10-19 the escrow still held 77,700,000 sats and had never been spent
(`tools/check_escrows.py`). This file lists what I verified, what I learned that the upstream
README does not have, and the new families I tested. Every one of them was negative.

## Verified

| Check | Result |
|---|---|
| The author's vector: entropy `2941774a…` at index 1 gives WIF `L5Z66qPm…` | reproduced |
| Stage One from Hal Finney's post, plain rule (flip paragraphs whose first letter is not I/T/A/S/M, `\n\n` joins, the single `<br />` before "[edited slightly]" as `\n`) | MD5 `9dd2efb9…`, `19TbyN5K…` at index 0 |
| Grycoin Chain Block 1, "Still 21st Century" | `18EpYz5q…` at index 0 |
| Grycoin Block 2 question text, posted version | MD5 `7759227d…`, the digits the author confirmed |
| "Second" chapter from the Wattpad API | 273 paragraphs; `\n\n` joins plus a final `\n` give exactly 45,451 characters |

## New findings

1. **The "lost the solution" quote is from before the rehash.** Wattpad part 762380140, "Starting
   Up", was created 2019-07-23 23:09 and last modified 23:24 the same day. That is before the funds
   moved on 2019-07-30. So "I have lost any information on the solution of that one" is about the
   superseded `1EFojc…` solution. The current solution was made seven days later. Upstream README
   fact 9 dates the quote after the August shutdown; the API dates do not support that.

2. **Grycoin Block 2 is a second calibration that nobody has reproduced, and the author tied it
   to this block.** The block was funded 2019-08-01 to `1tzieUfbeQghz2zjDeGHcAEfzCRgX6eLi`.
   puzzleponky swept it on 2019-08-03 at 14:02 and Stage One seven minutes later, both to the
   same address (`129jw1GU…`). The author wrote two things in the thread:
   - "The question of what letters to change in capitalization is obvious if you know the solution
     to Satoshi's bitcointalk puzzle … The question of how to go from that to claiming the prize is
     not, not even to me … good job figuring out a solution even I don't know."
   - "knowing this is an advantage for solving the real big block."

   The plain rule that reproduces Stage One does **not** reproduce Block 2, so the hashed Block 2
   text holds something the author herself did not know about. Whatever that is probably sits on
   top of the Real Big Block text too. Upstream does not record this. Its oracle docstring says the
   `\n\n` separator was "confirmed on … Grycoin Block 2", but only the base-text MD5 confirms that.
   A 2026-09-02 Reddit comment reports more than 100 billion GPU candidates on Block 2 (any 1 to 4
   case flips anywhere, plus 1 to 5 at sentence and paragraph boundaries), all negative.

3. **Wattpad `data-p-id` is MD5 of the paragraph's stored HTML, and every id is now accounted
   for.** The one id that did not match (paragraph 77, the second `"What?"`) is
   `md5(md5('"What?"') + "1")`, Wattpad's scheme for duplicate paragraphs. That rules out the public
   theory (Reddit, 2026-10-10) that this id hides a sentence. The ids describe today's text only and
   say nothing about the 2019 bytes.

4. **The chapter's Finney quote differs from the original in only one word.** Paragraphs 230 to 234
   match the post except for the added quotation marks and "facinating", which the chapter
   corrects to "fascinating". Earlier single-edit sweeps already cover this difference.

5. **The author probably types on a US layout and habitually holds Shift too long.** puzzleponky
   pointed out "FIrst", "SInce" and "BItcoin" in 2019; she also wrote "DIscussion", and "don;t"
   is a US-layout neighbour-key slip. This prompted the Shift-accident families below.

## Tested here (all 0 match)

Real Big Block. Both the current and the superseded escrow were targets, at indices 0 to 5,
compressed and uncompressed. Each run planted a synthetic witness and recovered it.

| Family | Unique texts | Script |
|---|---|---|
| Planted groups G1/G3/G2 plus the Finney quote, each off, on, or on plus its adjacent "I" paragraph (the I in "I STNM"); 3 flip modes, `\n\n`/`\r\n\r\n`, trailing newline or not, NBSP kept or turned to space, headings kept, title dropped, or all headings dropped | 7,704 | `experiments/rbb_i_paragraph.py` |
| Group flips plus a Shift-held accident on the character after any subset of the newly capitalised last letters (`.`→`>` on US, `.`→`:` on German), every non-empty subset of the 4 units, 4 join/tail variants | 668,040 (ran 2026-10-19, witness recovered) | `experiments/rbb_shift_habit.py` |

Grycoin Block 2. Escrow `1tzieUfb…`. Every candidate went through the free `3c6` prefix filter
first. The certified oracle reproduces Grycoin Block 1 and Stage One.

| Family | Size | Result |
|---|---|---|
| Every subset of case toggles at the 20 paragraph first/last letters, on 4 versions of the text (as posted; without "Even after … detail."; that sentence as its own paragraph; that sentence on its own line), `\n` and `\r\n` | 4 × 2^20 × 2 | 0 |
| Toggles of the first letter of any paragraph combined with toggles of up to one sentence-final letter per paragraph, with and without that sentence | ≈ 23.6M | 0 |
| 5 rule readings (non-ITASM, ITASM, paragraphs containing "recognize the signs", I-only, none) plus any 1 or 2 more case toggles anywhere | 7.2M | 0 |
| 7 rule readings plus any single insert, delete or replace (printable ASCII or `\n`) anywhere | ≈ 3.5M | 0 |
| Each paragraph unchanged, flipped, flipped with Shift-held punctuation (US or German), last letter only, first letter only, or flipped with the 2nd letter capitalised | 144,120,025 × 2 joins | 70,392 passed the 3c6 filter, 0 address match (uncertified: no planted witness in this run) |
| Every per-paragraph flip subset × 7 joins × 5 leads × 6 tails × UTF-8/UTF-16 | 5.2M | 0 |
| Quote handling: `\"`, `&quot;`, `&#039;`, smart quotes, quotes removed (Stage One contains `"Trusted Computing"` with plain quotes and still reproduces, so this was a long shot) | 122,880 | 0 |
| The plain rule-applied texts under 12 derivation paths (BIP44/49/84, BIP32 `m/0`, Core, Multibit…), indices 0 to 29, hardened and normal, passphrases `""`/`TOMI`, plus brainwallet readings | 32 texts | 0 |

Not finished: rule readings plus **two** arbitrary edits near the flipped letters on Grycoin
Block 2 (stopped at the run limit; the single-edit and structured variants above are complete).

## What I would do next

1. **Get puzzleponky's Block 2 solution.** It is the one known instance of the author's unknown
   quirk. The account last posted in 2020. In the Block 2 thread the author says knowing it is "an
   advantage for solving the real big block", which makes this more useful than the Block 76
   lead upstream ranks first.
2. **Treat Block 2 as the oracle for any "quirk" hypothesis.** It is 1.3 KB with a free 3-hex
   filter, so a quirk family costs about 1/35 of the same family on the 45 KB chapter. Only move a
   family to the Real Big Block once it reproduces `1tzieUfb…`.
3. Correct upstream fact 9 and the "Starting Up" note in `clues/author-posts.md` to the 2019-07-23
   date (finding 1). Add finding 3 so nobody keeps chasing the paragraph-77 id.

## Running

```bash
pip install coincurve mnemonic
python3 tools/fastoracle.py           # self-test: author's vector + Stage One
python3 tools/fetch_sources.py        # fills cache/ (git-ignored; texts are not redistributed)
python3 tools/calibrate.py            # Stage One, Grycoin 1, Grycoin 2 base, data-p-id
python3 tools/experiments/rbb_i_paragraph.py
python3 tools/experiments/rbb_shift_habit.py
python3 tools/experiments/gry2_search.py boundary|plus2|edit1|structured
```

No key material is printed or stored. On a hit the scripts print only the label, the derivation
index and the candidate description.
