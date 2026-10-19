# 0.2 BTC "Brave New World" puzzle

Source: <https://privatekeys.pw/puzzles/0.2-btc-puzzle> (posted by Reddit user
`stsh_n`, 2020-10-08). Image: <https://i.redd.it/n1x7g8ceaur51.png>
(1600×1200 RGBA PNG, sha256 prefix `d0b04378f75d6399`).

| | |
|---|---|
| Prize address | `1KfZGvwZxsvSmemoCmEV75uqcNzYBHjkHZ` (hash160 `ccbd031e54cde2a3189fd59bc49f731367a1779e`) |
| Funded | 0.2 BTC on 2020-05-10 (tx `fcee21d4…`), plus 4 small tips 2023–2025 |
| Status (checked 2026-10-19 via mempool.space) | **Unsolved**: 0.20107284 BTC, 5 receives, 0 spends |
| Author hints | None. The only instruction is the faint background text "FIND THE SEED PHRASE IN THE THIS PICTURE" |

**Status of this attempt: not solved.** This folder holds the verified clue
inventory, a tested key-derivation checker, and a record of which hypotheses
have been ruled out, so later attempts don't repeat them.

## Verified clues

I checked each item below in the image with local-contrast and high-pass
enhancement. Items marked *community* were reported elsewhere and confirmed
here.

### Deliberately hidden micro-text (strongest seed-word candidates)
| Word | Where | Notes |
|---|---|---|
| `moon` | Red second hand of the clock, printed mirrored | *community*; points between 12 and 1 |
| `tower` | Thin minute hand, printed mirrored | *community*; points between 1 and 2 |
| `food` | Vertical red text inside the Space Needle shaft | *community* |
| (nothing found) | Thick hour hand, between 10 and 11 | Inspected at 6× with high-pass. If text exists, the image's noise hides it |

All three are BIP39 words. `food` is **not** in the old Electrum word list,
which argues for BIP39 or new-style Electrum over old Electrum.

### Rune inscriptions (substitution cipher over Russian)
The glyph mapping is consistent across inscriptions. For example А=∆, Д=⫛,
Ю=⊱, С=◇ hold in both НАДЕЮСЬ and СЮДА.
* Top left: "Я надеюсь что сюда будут присылать много биткоинов" = "I hope many bitcoins will be sent here"
* Bottom, next to the clock: "Сумма двух чисел" = "**sum of two numbers**". Each clock hand points between two numbers: 12+1=13 (moon), 1+2=3 (tower), 10+11=21 (hour hand). This may mean word positions 13, 3 and 21, which would imply a phrase of at least 21 words.
* Right edge: "здесь зашифрованы биткоины на чёрный день номер X" = "here are encrypted bitcoins for a rainy (lit. *black*) day, number X"
* Above Trump (Gravity Falls / Bill Cipher alphabet): "TUESDAY", the 2020 election day

### Other text in the picture
* A faint, yellow handwritten line across the top reads "**Order and stability**". It starts in the face-tracking lines and runs to the CCTV camera, and is a *Brave New World* motto.
* Faint background text: "FIND THE SEED PHRASE IN THE **THIS** PICTURE". The odd grammar and the darker strokes of "THIS" suggest it was inserted on purpose. "THIS" also appears in "FUCK THIS SHIT" and "THIS IS THE FIRST PREDICTION", so `this` is a strong candidate.
* "ONLY real BITCOIN" on the Statue of Liberty pedestal, with "real" in lowercase
* "PAY FOR THE FUTURE. THIS IS THE FIRST PREDICTION." in faint text beside the statue
* "Section 1", with "subject" underlined, on the Leopold II pedestal (13th Amendment text)
* "BREATHE" on Floyd's shirt and on the gag of the Leopold bust. Not a BIP39 word.
* "STOP" sign with the BLM fist. Not a BIP39 word.
* "1865-202…?", "05.25.20", "11.03.20", "XX" on the tablet and the bust, a 44-star flag, and a gold price chart (2003–2020)
* The handwritten Bitcoin-whitepaper text has typos: introdue, participans, doudle, sing, abcense, wich, proot, arrrived
* Signature "CHR" in the bottom right; "CHaRLy" written vertically in the top left

### Image forensics
* No metadata chunks (only IHDR/sRGB/sBIT/IDAT/IEND) and no trailing data
* Alpha channel is constant 255
* LSB bit planes show nothing beyond image content

## Hypotheses tested (all negative)

Each candidate is checked as BIP39 (empty passphrase) and as an Electrum
"standard" seed. The derivation paths are m/44'/0'/0'/0/i, m/0/i and
m/0'/0/i for i=0..4, with compressed and uncompressed keys. The checker is
validated against the BIP39 and BIP32 test vectors and a planted-phrase
positive control.

| Test | Candidates checked | Result |
|---|---|---|
| Brainwallet SHA256 of every text string in the image (269 case/spacing variants) | 269 | no match |
| 6-word permutations of {moon, tower, food, this, real, subject, black} | 1,224 valid seeds | no match |
| 6-word permutations of the 9 BIP39 words in `pools/core10.txt` | 15,378 valid seeds | no match |
| 9-word permutations of the same 9 words | 46,889 valid seeds | no match |
| 3-word permutations of the 87 BIP39 words in `pools/wide.txt` | 319,510 valid seeds | no match |
| Image numbers as BIP39 indices (1865, 202, 1663, 13, 3, 21, 44, 525, 1103, 10, 20, …) | checked by hand | no obviously meaningful words |

The community has already tested 12-word guesses with 10 fixed words and the
last two brute-forced (HomelessPhD/BLM_0.2BTC); this attempt does not repeat
that. Brute force alone cannot reach a full 12-word ordering: 12! / 16 ≈ 30M
PBKDF2 runs per guessed word set, about 6–7 hours on 4 cores. A 24-word
phrase is impossible to brute-force without the order.

## Tools

```
pip install coincurve
python3 seedcheck.py --self-test                 # BIP39/BIP32 test vectors
echo "word1 word2 ..." | python3 seedcheck.py   # check one phrase (BIP39, Electrum, brainwallet)
python3 search.py perms --k 6 --pool pools/core.txt
python3 search.py template "moon tower food * * * ..."   # '*' = any BIP39 word, {a|b} = choice
```
