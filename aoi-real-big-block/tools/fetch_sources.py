"""Fetch the public sources into ./cache (git-ignored; the texts are not redistributed here).

  cache/storytext.html     Wattpad "Second" chapter (part 720888559), raw storytext HTML
  cache/paras_text.json    its 273 paragraphs: tags stripped, <br> -> "\\n", entities unescaped
  cache/finney_body.html   bitcointalk topic 155054, first post body (latin-1)
  cache/aoi_posts.json     all of AoiNakamoto's Reddit submissions (arctic-shift)
  cache/gry2_base.txt      Grycoin Block 2 question text (MD5 must start 7759227)
"""
import gzip
import hashlib
import html
import json
import os
import re
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, '..', 'cache')
UA = {'User-Agent': 'Mozilla/5.0'}


def get(url, tries=5):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            return gzip.decompress(data) if data[:2] == b'\x1f\x8b' else data
        except urllib.error.HTTPError as e:
            if e.code not in (422, 429, 503) or k == tries - 1:
                raise
            time.sleep(5 * (k + 1))  # arctic-shift answers 422 when polled too fast


def main():
    os.makedirs(CACHE, exist_ok=True)
    raw = get('https://www.wattpad.com/apiv2/storytext?id=720888559').decode('utf-8')
    open(os.path.join(CACHE, 'storytext.html'), 'w', encoding='utf-8').write(raw)
    ps = re.findall(r'<p data-p-id="([0-9a-f]{32})">(.*?)</p>', raw, re.S)
    text = [html.unescape(re.sub(r'<br>', '\n', re.sub(r'<(?!br)[^>]+>', '', p))) for _, p in ps]
    json.dump(text, open(os.path.join(CACHE, 'paras_text.json'), 'w'), ensure_ascii=False)
    assert len(text) == 273 and len('\n\n'.join(text) + '\n') == 45451, 'chapter changed since 2026-10'

    page = get('https://bitcointalk.org/index.php?topic=155054.0').decode('latin-1')
    body = re.search(r'<div class="post">(.*?)</div>', page, re.S).group(1)
    open(os.path.join(CACHE, 'finney_body.html'), 'w', encoding='latin-1').write(body)

    posts, after = {}, 1546300800  # 2019-01-01
    for _ in range(5):
        j = json.loads(get('https://arctic-shift.photon-reddit.com/api/posts/search'
                           f'?author=AoiNakamoto&limit=100&sort=asc&after={after}'))
        if not j['data']:
            break
        for p in j['data']:
            posts[p['id']] = p
        after = int(j['data'][-1]['created_utc']) + 1
        time.sleep(1)
    json.dump(list(posts.values()), open(os.path.join(CACHE, 'aoi_posts.json'), 'w'))

    st = posts['cleczc']['selftext']
    q = st[st.index('I thought I would write'):]
    q = q[:q.index('thinking only method.') + len('thinking only method.')]
    assert hashlib.md5(q.encode()).hexdigest().startswith('7759227')
    open(os.path.join(CACHE, 'gry2_base.txt'), 'w').write(q)
    print('ok:', len(text), 'paragraphs;', len(posts), 'posts')


if __name__ == '__main__':
    main()
