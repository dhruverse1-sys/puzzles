# Zden — BTCrypto Puzzle Level HALV

* Puzzle page: <https://privatekeys.pw/puzzles/zden-level-halv-puzzle>
* Original image: <https://crypto.haluska.sk/cryptoHALV.png> (950×950 grayscale,
  SHA-256 `3a487eba…0e95`; identical to the image in the announcement tweet)
* Prize: 0.003125 BTC at `1crypto24HCr178iMcKd5iUi5D4rsg1nK`. It was still unspent on 2026-10-19.
* Author's hint: "This level is way easier than LVL 5. It shouldn't take long until it's solved."

**Status: not solved.** This folder records a pixel-exact reading of the waveform. It also
records the structure found in it, which goes well beyond the earlier public analyses
(those analyses count "59 lobes"). It ends with the one step that is still open.

## Files

| File | What it is |
|---|---|
| `extract.py` | Fits the polyline model to the image and writes `data/samples.json` and `data/frames.json` |
| `check.py` | Checks a 64-hex-digit key against the prize address (compressed and uncompressed) |
| `data/samples.json` | The 256 waveform samples, levels 0–3 |
| `data/frames.json` | The 66 reconstructed 4-sample source frames (`null` = sample that is never displayed) |

```
pip install numpy pillow coincurve base58
python3 extract.py cryptoHALV.png
python3 check.py <64 hex>
```

## What the image is

1. **Mirrored polyline.** The waveform is one polyline drawn together with its mirror image
   about y = 475. Top and bottom halves agree to within anti-aliasing. The only exceptions
   are the logo and a column of faint dots at x = 91 (see below). No line crosses the axis
   between two vertices, so the sign carries no information: only |value| matters.
2. **256 samples on a 3 px grid.** The vertices sit at x = 89 + 3k, k = 1…256 (x = 92…857).
   The fit was checked against other grids (pitches 2.5–3.25, every sub-pixel offset). The
   3 px grid at integer positions is clearly the best.
3. **Eight "halving" eras.** Each run of 32 samples is drawn at half the scale of the
   previous run: one level is 128, 64, 32, 16, 8, 4, 2, 1 px. Every sample is an integer
   level 0–3 of its era. A continuous re-fit of every vertex lands within ±0.15 level of an
   integer, and usually within ±0.05.
4. **Every line renders at the same peak brightness.** There is no hidden channel in line
   brightness or thickness.

The samples, one row per era:

```
era 1  21112330030002311012211013210032
era 2  22100300232223023302220223123202
era 3  30221022002230203020102020020020
era 4  00200003020202210200022000220020
era 5  02200030221022002200002020102000
era 6  03022100220023000200010201022100
era 7  00020002002010000002200230221000
era 8  02231120023301001113103112130100
```

## Hidden structure: a resampled stream of 4-sample frames

In eras 3–7 the samples follow a strict period-4 pattern:

```
frame = [a, b, c, 0]    with a ∈ {0,2}, b ∈ {0,2}, c ∈ {0,1,2,3}
```

The phase of this pattern slips by exactly one sample at every era boundary. That is what
you get when **display sample k shows source sample ⌊k·33/32⌋**. The source therefore has
264 samples (8 × 33). Its last sample in each era is never displayed, and the frames are
continuous across eras. With this mapping, all 160 samples of eras 3–7 fit the grammar with
**zero violations**. A dynamic-programming alignment allowing any skips finds nothing better.

There are 66 source frames (`?` marks a sample that is never displayed):

```
f0-7    2111 2330 0300 0231 1012 2110 1321 0032      <- era 1: does NOT follow the grammar
f8-15   ?221 0030 0232 2230 2330 2220 2231 2320      <- era 2: follows it, with 5 anomalies
f16-57  2?30 2210 2200 2230 2030 2010 2020 0200 20?0 0200 0030 2020 2210 2000 2200 0220
        020? 0220 0030 2210 2200 2200 0020 2010 2000 ?030 2210 0220 0230 0020 0010 2010
        2210 0?00 0200 0200 2010 0000 0220 0230 2210 00?0          <- clean
f58-65  2231 1200 2330 1001 1131 0311 2130 100?      <- era 8: does NOT follow the grammar
```

A clean frame carries 4 bits (A = a/2, B = b/2, c = 2 bits), giving 16 possible shapes.
15 of the 16 appear, and the all-zero frame is one of them. Read as nibble = 8A + 4B + c,
the clean region f16–f57 reads:

```
?dcfb9a4?43ad8c6463dcc298?d67219d?449067d?
```

The distribution is consistent with uniform random nibbles (χ² = 16.8, 15 d.o.f.), which is
what a private key would look like. The 66 frames are 2 more than the 64 nibbles of a key.

## The open problem: eras 1, 2 and 8

* **Eras 1 and 8** (f0–f7 and f58–f65) contain data that is not in this frame format. About
  50 % of their samples are odd. The frame stream can never exceed 25 % odd samples, so this
  cannot be a resampled view of the frame stream at any rate or offset. No periodic structure
  (periods 2–16), level relabelling, local filter, echo or overlap of the frame stream
  explains them. One consistent oddity: in these frames positions *a* and *d* never take the
  value 3, while *b* and *c* often do.
* **Era 2** follows the frame grammar but has five anomalies: d = 1, 2, 1 in f8, f10, f14
  and b = 3 in f12, f15. All its c values are 2 or 3. Read naively it gives `?37ffefe`. That
  value is suspiciously biased upwards, so era 2 looks perturbed rather than simply decoded.

The key needs 64 nibbles, but only 40–45 clean nibbles are readable. The rule for the dense
frames is therefore the missing step. Every reading tried so far has failed against the
address:

* The "noisy" frames read by dropping the low bits of a, b and d. All 24 bit orders, XOR and
  Gray variants, every 64-frame window, both directions, every choice for the never-displayed
  samples.
* The same, treating a = 1 and b = 1 as either 0 or 2.
* Eras 1, 2 and/or 8 read as raw base-4 key digits (2 bits per sample) plus 32 or 48 frames,
  in every order. All level relabellings, both digit orders within a pair, correct tail
  alignment.
* Dense frames read as bytes, as ASCII/Base58 text, or as a WIF payload. A double-SHA256
  checksum search over the 41-byte head + frames + tail layout found nothing.
* Era-wise XOR, sums, overlap-add with halving weights, and column sums across eras
  ("bit-plane" readings).
* SHA-256 of the sample, frame and nibble strings, and of the image file.
* EC "halving" of each candidate: multiplied by 2^±j mod n for j ≤ 8, plain shifts, and n − x.
* Era 1 read as raw digits plus frames f8–f55, with the five anomalous era-2 nibbles free
  (16⁵ values each; 33.5 M keys).
* Dense frames read as a nibble taken from any two of their four positions, under any level
  relabelling, combined with the clean nibbles (3.5 M keys).
* Dense frames as text: bytes with the clean nibble low and the extra bits (a₀, b₀, d) high,
  mixed-radix (3·4·4·3) ASCII, and Base58 / WIF prefixes. None gives readable output.
* Additive noise models: periodic saw or triangle "noise", local smoothing or echo filters,
  and the stream summed with a shifted copy of itself. None explains the dense eras.

## Side discovery: a second funded address

The funding transaction
[`30946152…5205`](https://mempool.space/tx/30946152b5f24ed975a26b28a46cb19d1ef2728159c5806544ffd0c2fb535205)
pays two addresses. One is the prize address. The other is 4 040 sats to the vanity address
**`1DoTPuzbAuLZHU4TodFrnMvZXBxAoBBcNv`** ("DoT Puz"), which was still unspent on 2026-10-19.

This is very likely a bonus puzzle tied to the faint column of dots at x = 91, y = 444–506.
That column is a 1-px vertical line whose brightness follows a sawtooth with a period of
about 7 rows (values ≈ 23, 47, 75, 107, 141, 178, 216). It is cut into nine segments, and
its two halves are near-mirror images about y = 475. The image's SHA-256 is not the key for
either address.
