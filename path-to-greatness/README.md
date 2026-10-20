# Path to Greatness: Treasure Hunt (3.026 LTC): session notes, 2026-10-20

Target: Justin Patterson's (jpatt94) Litecoin hunt at [p2gtreasure.com](https://p2gtreasure.com/).
Escrow `LUtL7qnm3gzxKjHcfVLSjydqhhinTVmTmS`, checked 2026-10-20: 302,608,794 litoshis received,
0 spent. Research base: [open-crypto-puzzles/2-mid-prizes/path-to-greatness-treasure-hunt-3ltc](https://github.com/dhruverse1-sys/open-crypto-puzzles/tree/main/2-mid-prizes/path-to-greatness-treasure-hunt-3ltc).

**Status: not solved.** This session adds two witnessed negatives and four new readings of the
clues that the upstream folder does not record.

## How the hunt is locked (from the author's own `computer_screen.jpg`)

Four AES-256-CBC segments, each one 16-byte block holding 8 bytes of the super key, so each
segment has an exact test (PKCS7 padding of eight `0x08`, false positive rate 2^-64). Each
segment key is two clue answers concatenated, so each pair of clues is tested on its own.

| Segment | IV | Clues (lengths) | Ciphertext (base64) |
|---|---|---|---|
| 1 | `few_n_far_btween` | imagine (16) + beach (16) | `I2c6TXU/Z1oCKnEQTWZUvg==` |
| 2 | `nocturnal_sugars` | chess (12) + wonders (20) | `RWaBo4ChEOM/i+MLy2NUpg==` |
| 3 | `colors_on_leaves` | wasd (8) + ship (24) | `16GmtUINaYuN7f1RlBO5sQ==` |
| 4 | `seconds_of_dream` | scramble (15) + sky (17) | `7CZlZjwCMGUb/TZm07b9dg==` |

## What I tested (all negative, all witnessed)

Tools: `tools/pairs.c` (generic left x right pair tester) and `tools/seg1map.c` (segment 1
mapping sweep), both AES-NI, about 42 million keys/s on 4 cores. Every run either had a
planted witness (a payload encrypted beforehand under a known key from the same family) that
was re-found through the same code path, or ran right after such a run on the same binary.

| Segment | Hypothesis | Space | Result | Witness | Date |
|---|---|---|---|---|---|
| 1 | `imagine` = Dec 7 of 1941+N in the puzzle's own YYYYDDMM format, written twice, N = 4 (`1945071219450712`) or N = 2403 (`4344071243440712`); `beach` = the 15 measured notes, one token per note identity (pitch + octave: A#5 F#5 B5 D#5/E5 F5 C#5 B4 A#4), any digit per identity, with exactly one once-occurring note (6th, 7th, 9th or 11th) written as 2 characters (two digits, or a digit plus `#` or `b` either side) | 2 x 5.6e9 = 1.12e10 pairs | 0 match | yes, `27327b6643422732` planted and re-found | 2026-10-20 |
| 3 | `wasd` from 1,120 structural readings of the grid (see below); `ship` = every 24-character window of the full IMSDb screenplay, all offsets, plus 3,272 two- and three-part name/role concatenations | 1,120 x 188,712 = 2.1e8 pairs | 0 match | yes, `2w1s5d4a` + `isamathematicalcertainty` planted and re-found | 2026-10-20 |
| 3 | `wasd` = any 4 x (digit + w/a/s/d letter), both orders (5,120,000); `ship` = all 24-character windows of the chart-room scene (163) plus the name concatenations (4,347) | 2.23e10 pairs | 0 match | same binary, witnessed above | 2026-10-20 |
| 3 | `wasd` = every 8-character string over `0-9wasd` (14^8 = 1,475,789,056); `ship` = `isamathematicalcertainty`, `jonathanhydevictorgarber`, `victorgarberjonathanhyde`, `jbruceismaythomasandrews`, `thomasandrewsjbruceismay` | 7.38e9 pairs | 0 match | yes, re-found in its own run | 2026-10-20 |

The segment 1 family is a superset of every scale-degree numbering of the measured melody:
any tonic, any octave convention, any accidental notation for the single 2-character note.
Upstream had already swept every 8-digit `imagine` block against several thousand hand-built
melody readings (up to 6,243 per run). Together these say that if `imagine` is one date written twice, the melody as
measured from the 2019 YouTube video is probably the wrong source, not just the wrong notation.

## New readings (not in the upstream folder, untested or only partly tested)

1. **Clue 6 (`beach`): "the sun" is *re*, not *sol*.** The poem pairs "Our counting starts
   with a deer" with "Our pattern starts with the sun". Both come from the same song: "Doe,
   a deer" and "Ray, a drop of golden sun". So *do* = 1 and the melody starts on *re* (2).
   Upstream reads the sun as *sol*, which makes the YouTube opening fit. Under *re* it fits
   only as G# Dorian. Combined with the negative above, this suggests the 15 notes come from
   somewhere else. "This time we change the channel / And traverse to lost dimensions" may
   mean a stereo channel, or the left-minus-right difference signal, which disappears
   ("lost") when the audio is mixed to mono. Upstream's audio work never mentions stereo.
   Next step: extract the game's audio clip and look at L, R and L-R separately.
2. **Clue 5 (`wonders`) has 3 lines upstream never transcribed.** The full poem on the panel is
   8 lines: "Charting the eight wonders / A thousand maps drawn with blood / A bit of help
   from each line / To shelter my ship on the flood / We used to swim the same moonlight
   waters / Dragged by the force of some inner tide / No longer will we wait for your answers
   / With the stars in the sky our guide". Upstream quotes only 4 of them. "Eight wonders"
   may be the 8 tracks of the author's other album *Archaic Reveries* (2018: Age of Lamps,
   Lost and Found, Welcome to the Mansion, Effugium, On the Other Side, Alone, Seven Miles,
   The Regents); "Seven Miles" would explain the `mi` torch. The red pictograms on clues 5
   and 8 together make 8 icons (ghost, sprouting hill, anchor, three-headed devil, horned
   helmet, stars, banner marked "0,0,0", television), which looks like a track legend:
   ghost = Ghost March, hill = Hills of Life, television = As Seen From Afar ("tele-vision"
   means seeing from afar).
3. **Clue 8 (`sky`): the dashes are spaces, giving a 4 + 13 word split.** The author's
   `fix_clues.script` removes spaces, so the written answer has spaces. In
   `ehk-bqNEFRUn-`, 6 letters have two-digit alphabet values (k, q, N, R, U, n) and 5 have one
   (e, h, b, E, F): 6 x 2 + 5 = 17, the required length. So each digit yields one letter, and
   the answer is a 4-letter word (`e h k`), then a 13-letter word (`b q N E F R U n`). That
   constrains any pairing rule a lot. Note also that clue 2's instruction ("With your
   capital, addition. To the lower, subtract.") and clue 2's own mixed-case, dashed string
   use the same notation as clue 8.
4. **Clue 3 (`wasd`): stars pair with tails.** The grid (transcribed in `tools/grid.py`;
   `tools/analyze.py` prints the structure) is a 92-cell cycle, 4 one-cell tails that feed
   into it, and 4 isolated stars. Each numbered star sits next to exactly one tail: star 1
   (r5c7) to 2-up (r4c9), star 2 (r9c3) to 1-down (r9c1), star 3 (r2c4) to 5-right (r1c2),
   star 4 (r9c9) to 4-left (r8c10). Read in star order with wasd letters that is `2w1s5d4a`,
   exactly 8 characters. It is included in both segment 3 runs above, so it is negative
   against those `ship` families only.

## Reproduce

```
gcc -O3 -march=native -fopenmp -o pairs tools/pairs.c
gcc -O3 -march=native -fopenmp -o seg1map tools/seg1map.c
./pairs <ct_hex> <iv16> <left_len> <left_file|enum8x2|enumwd8> <right_len> <right_file>
./seg1map 23673a4d753f675a022a71104d6654be few_n_far_btween imagine_list.txt <witness_ct_hex>
```

The screenplay is not included (copyright); the candidate lists were built from
https://imsdb.com/scripts/Titanic.html by lowercasing, stripping everything but `a-z0-9`,
and taking every 24-character window.
