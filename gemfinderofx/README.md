# GemfinderOfX 0.02 BTC tweet puzzle: session notes, 2026-10-20

Source: [x.com/GemfinderOfX/status/1870319691295764655](https://x.com/GemfinderOfX/status/1870319691295764655),
posted 2024-12-21. Text: "I want to have you all the chance to win 0.02 bitcoin ... Everything
for the private key can be found within this message. Address showing proof of funds. 9vw04".
One image: a grid of letter+digit pairs. Raised upstream as
[floflo777/open-crypto-puzzles#32](https://github.com/floflo777/open-crypto-puzzles/issues/32)
(one solver reports 4 to 5 days and "blockers"). Not in the open-crypto-puzzles catalog.

Escrow `bc1qr5mssp6snmduqp9enx4dzmcxvk7qw83lceyy2v`, checked 2026-10-20: 2,020,760 sats unspent
(UTXOs of 1,928,356 sats from 2021-11-03 and 92,404 sats from 2024-11-28). It is the author's own
wallet, used since 2021-01 with change returning to it, so a future spend would not by itself
mean someone solved it.

**Status: not solved, and probably not solvable from the image alone.**

## What the image contains

`grid-transcription.txt` is the full grid: 21 rows, 525 letter+digit pairs, OCR'd by template
matching (`tools/gem_ocr.py`, `tools/gem_cls.py`). Check: all 525 letters match the expected
cycle with 0 mismatches. Rows 1 to 3 and 21 were also checked by eye.

- **The letters carry no data.** They repeat one fixed 26-letter cycle,
  `TUVWYZROBMJKHLXQNPACDEFGIS`. That cycle is a keyword alphabet: the keyword `ROBMJKHLXQNP`
  followed by the 14 remaining letters in alphabetical order (`ACDEFGISTUVWYZ`), rotated to
  start at T.
- **The colors are almost certainly editor syntax highlighting.** Every O pair is gray, every M
  and G pair light blue, every N pair lavender, everything else white letter plus pink digit.
  The coloring depends only on the letter, and O, M, N and G are the G-code word letters a
  G-code highlighter colors.
- **The digits look generated, not encoded.** In 525 digits, no digit ever repeats any of the
  previous 3 (0 violations; random digits would give about 52 adjacent repeats alone). Repeats
  at lags 4 to 6 are suppressed, and lags 9 to 10 are elevated. That is the signature of a
  "pick a digit not used recently" generator, typical of a person or a language model writing
  "random" digits. It is not shuffled 0-9 decks (no block alignment).

## Decodings tried (no structure found)

- Caesar shift of each letter by its digit, plus and minus, in both the standard and the keyed
  alphabet: index of coincidence 0.038, i.e. random.
- Digits as 2- and 3-digit ASCII: no text.
- Digits as a base-7 channel (the rank of each digit among the 7 allowed after excluding the
  last 3): close to uniform except a deficit at rank 6. Converted to bytes, 33% printable, no
  text.

Not tried: anything keyed on "9vw04"; the full-resolution image may also be cropped (the
stream ends mid-cycle).
