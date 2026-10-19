"""Reproduce every calibration point from the public sources (run fetch_sources.py first).

1. Stage One from Hal Finney's post with the plain rule (flip paragraphs whose first letter is
   not I/T/A/S/M, join "\\n\\n", single <br /> -> "\\n") -> MD5 9dd2efb9... -> 19TbyN5K... index 0.
2. Grycoin Chain Block 1: "Still 21st Century" -> 18EpYz5q... index 0.
3. Grycoin Block 2 base text MD5 starts 7759227 (the digits the author confirmed on 2019-08-03).
4. Wattpad data-p-id is the MD5 of each paragraph's stored HTML; the one mismatch (the second
   '"What?"') is Wattpad's duplicate scheme md5(md5(text) + "1"), not a hidden message.
"""
import hashlib
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fastoracle as fo  # noqa: E402

CACHE = os.path.join(HERE, '..', 'cache')
md5 = lambda s: hashlib.md5(s.encode()).hexdigest()  # noqa: E731

body = open(os.path.join(CACHE, 'finney_body.html'), encoding='latin-1').read()
paras = [html.unescape(p).replace('<br />', '\n') for p in body.split('<br /><br />')]
flip = lambda p: p if p[0] in 'ITASM' else __import__('chapter').flip(p)  # noqa: E731
t = '\n\n'.join(flip(p) for p in paras)
h = hashlib.md5(t.encode('latin-1')).hexdigest()
print('1. Stage One', h, fo.check_entropy(bytes.fromhex(h)))
assert h == '9dd2efb9bc976c2095bd534d7b8d431c'

fo.add_target('18EpYz5qB3XoxZWouJF3KdEp3E2nfv9FgP', 'Grycoin Chain Block 1')
print('2. Grycoin Block 1', fo.check_text('Still 21st Century'))

q = open(os.path.join(CACHE, 'gry2_base.txt')).read()
print('3. Grycoin Block 2 base', md5(q))

raw = open(os.path.join(CACHE, 'storytext.html'), encoding='utf-8').read()
ps = re.findall(r'<p data-p-id="([0-9a-f]{32})">(.*?)</p>', raw, re.S)
seen, explained = {}, 0
for pid, inner in ps:
    forms = {inner, html.unescape(re.sub(r'<[^>]+>', '', inner)),
             html.unescape(re.sub(r'<(?!br)[^>]+>', '', inner)).replace('<br>', '\n')}
    ok = pid in {md5(f) for f in forms}
    if not ok:  # duplicate paragraph: md5(md5(text) + str(k))
        ok = any(pid == md5(md5(f) + str(k)) for f in forms for k in range(1, 5))
    explained += ok
print(f'4. data-p-id explained for {explained}/{len(ps)} paragraphs')
