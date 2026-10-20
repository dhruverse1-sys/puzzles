# Puzzle designed for 8964 (BTC reward 0.00896400)

Source: [r/Bitcoin post by u/hunghuatang](https://www.reddit.com/r/Bitcoin/comments/1tw7glw/puzzle_designed_for_8964_btc_reward_00896400/), 4 June 2026.
The author's own explanation: [u/hunghuatang post](https://www.reddit.com/user/hunghuatang/comments/1udez3a/).

## The puzzle

There are six hollowed cards, labelled `32-` to `1-`. Each is an 8×8 grid with 32 holes. A seventh card has a number grid on both sides.
A volunteer picks a number from 1 to 64 and turns over (rotates 180°) every hollowed card that shows the number. The host computes
`64 − (sum of turned cards)`, finds that value on the Back of card 7, and reads the number printed directly behind it on the Front, which is a "perfect Franklin
magic square". When the stacked cards are laid on the Front, the one hole left open shows the number.

Then a volunteer says their number appears on **no** card. A magician who has seen nothing calls out **38**.
**How does the magician find any number from the yes/no answers alone?**

## Answer

**The magician's rule:** start at **45** (octal). For each card the number *appears on*, XOR in that card's "spirit number". Convert the result to decimal and add 1.

| card | 32- | 16- | 8- | 4- | 2- | 1- |
|---|---|---|---|---|---|---|
| spirit number (octal) | 32 | 26 | 12 | 44 | 53 | 77 |
| (decimal) | 26 | 22 | 10 | 36 | 43 | 63 |

XOR in octal is easy to do in your head. Each octal digit is 3 bits, so you XOR the high digits and the low digits separately.

* **"I can't find it on any card"**: nothing is XORed in, so the result is 45₈ = 37, and 37 + 1 = **38**.
* The host's example: 9 appears on 32-, 16-, 8- and 2-. 45⊕32⊕26⊕12⊕53 = 10₈ = 8, so the number is **9**. The host's check: 64 − 58 = 6, and Back 6 sits behind Front 9.
* The author's example: yes/no/no/yes/no/yes. 45⊕32⊕44⊕77 = 44₈ = 36, so the number is **37**. The host's check: 64 − 37 = 27, and Back 27 sits behind Front 37.

`solve.py` checks this rule against all 64 numbers.

## Insights

**1. A 180° turn swaps holes and solid cells.** On every card, the rotated hole pattern is exactly the complement of the original.
So for any cell, each card has exactly one orientation that leaves a hole there. The six yes/no answers choose that orientation for every card, and exactly one hole survives.
This means each number has its own 6-bit "appears on" signature. The Back card is just the binary readout of the holes:
`Back(cell) = 1 + Σ labels of cards with a hole at that cell = 64 − Σ turned cards`.

**2. Everything is XOR-linear in the cell's coordinates.** Write a cell's row and column in binary as `r2 r1 r0` and `c2 c1 c0`. Then every card's hole pattern
is an XOR of those six bits, for example `hole₃₂ = 1⊕r2⊕c2⊕c0` and `hole₁₆ = r1⊕c1⊕c0`. Every binary digit of (Front − 1) is also an XOR of them, for example
the 32-bit is `1⊕r0⊕c2⊕c1` and the 1-bit is `r1⊕c0`. Composing the two maps makes (Front − 1) an affine function over GF(2) of the six yes/no answers.
That function is "a constant XOR one fixed key per *yes* card", which is the magician's rule. The constant is the value for "on no card", Front(Back 64) − 1 = 37.
The number 38 is not special; it is just whatever sits behind Back 64.

## Reconstructing the cards

**Back card** (as printed; it is mirrored because the card is turned over, which is why the top row reads `6 4` while the Front reads `8 9`):

```
45 26 49  6  4 55 32 43
36 23 64 11 13 58 17 38
50  5 46 25 31 44  3 56
63 12 35 24 18 37 14 57
 8 51 28 47 41 30 53  2
 9 62 21 34 40 19 60 15
27 48  7 52 54  1 42 29
22 33 10 61 59 16 39 20
```

**Front card.** The (Front, Back) anchors are (9, 6), (8, 4) and (38, 64). The numbers 20 and 26 appear on every card except `8-`, so they sit on Back 1 and 9.
Requiring every 2×2 block to sum to 130 and every row, column and broken diagonal to sum to 260 rules out the pairing 20↔9 / 26↔1.
With 20↔1 and 26↔9 it leaves **24** squares. Exactly **one** of those also has Franklin's own properties: half-rows and half-columns sum to 130, and bent diagonals sum to 260.
It is also one of only 3 that make an XOR shortcut possible:

```
41 64 17  8  9 32 49 40
19  6 43 62 51 38 11 30
48 57 24  1 16 25 56 33
22  3 46 59 54 35 14 27
45 60 21  4 13 28 53 36
23  2 47 58 55 34 15 26
44 61 20  5 12 29 52 37
18  7 42 63 50 39 10 31
```

## The hidden message (image 9)

Image 9 is a character grid laid out like the Back card. Reading its cells in Back-card order 1 → 64 gives:

> 8964天安門的坦克鎮壓屠殺，彼時台灣不流血的典範轉型。兩岸殊途，藏富於民，儼然東升西降。為中國人計，民主自由如操刀必割，不可畏首畏尾，台灣可以攻錯。

> June 4, 1989: the tank crackdown and massacre at Tiananmen. Meanwhile, Taiwan made its bloodless, model transition. The two sides of the Strait went separate ways.
> [Taiwan] keeps wealth with the people, and it really looks like "the East rises, the West declines". For the sake of the Chinese people: with democracy and freedom, once you hold the knife you
> must cut. Do not be timid. Taiwan can be the whetstone (他山之石，可以攻錯: learn from its example).

Every comma and full stop in the grid falls at the end of a clause, which independently confirms the Back card. The phrase "the East rises, the West declines" (東升西降) is a Beijing slogan.
Here it appears to be turned around, with Taiwan, to the east, rising.

## Run it

```
pip install numpy ortools
python3 solve.py
```
