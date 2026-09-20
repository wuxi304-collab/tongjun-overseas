from pathlib import Path
from urllib.parse import urlsplit
import re
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')

IMG_TAG = re.compile(r'<img\b[^>]*>', re.I)
LINK_TAG = re.compile(r'<link\b[^>]*>', re.I)
ATTR = re.compile(r'([A-Za-z_:][-A-Za-z0-9_:.]*)\s*=\s*(["\'])(.*?)\2', re.S)
MALFORMED_SLASH_ATTR = re.compile(
    r'<(?:img|link|source)\b[^>]*?/\s+[A-Za-z_:][-A-Za-z0-9_:.]*\s*=',
    re.I,
)


def fail(message):
    raise SystemExit('ERROR: ' + message)


def attrs(tag):
    out = {}
    dup = set()
    for name, _, value in ATTR.findall(tag):
        key = name.lower()
        if key in out:
            dup.add(key)
        out[key] = value
    return out, dup


def normalize_local(url):
    parsed = urlsplit(url)
    path = parsed.path
    prefix = '/tongjun-overseas'
    if path == prefix:
        path = '/'
    elif path.startswith(prefix + '/'):
        path = path[len(prefix):]
    query = f'?{parsed.query}' if parsed.query else ''
    return path + query


def main():
    if not ROOT.is_dir():
        fail(f'HTML root missing: {ROOT}')

    htmls = sorted(ROOT.glob('*.html'))
    if len(htmls) != 50:
        fail(f'expected 50 root HTML pages, found {len(htmls)}')

    total_images = 0
    preload_pages = 0
    eager_high = 0

    for page in htmls:
        text = page.read_text(encoding='utf-8')
        malformed = MALFORMED_SLASH_ATTR.findall(text)
        if malformed:
            fail(f'{page.name}: slash-before-attribute malformed void tag detected: {malformed[:3]}')

        images = []
        for tag in IMG_TAG.findall(text):
            data, dup = attrs(tag)
            if dup:
                fail(f'{page.name}: duplicate image attribute(s) {sorted(dup)} in {tag[:220]}')
            src = data.get('src', '')
            if not src:
                fail(f'{page.name}: img tag missing src')
            if src.startswith('/assets/images/') or src.startswith('/tongjun-overseas/assets/images/'):
                total_images += 1
                images.append((tag, data))
                width = data.get('width', '')
                height = data.get('height', '')
                if not width.isdigit() or not height.isdigit() or int(width) <= 0 or int(height) <= 0:
                    fail(f'{page.name}: local image lacks positive integer intrinsic dimensions: {src}')
                loading = data.get('loading', '').lower()
                if loading not in {'eager', 'lazy'}:
                    fail(f'{page.name}: local image missing explicit loading=eager|lazy: {src}')
                priority = data.get('fetchpriority', '').lower()
                if priority == 'high':
                    if loading != 'eager':
                        fail(f'{page.name}: fetchpriority=high image must also be loading=eager: {src}')
                    eager_high += 1

        image_preloads = []
        for tag in LINK_TAG.findall(text):
            data, dup = attrs(tag)
            if dup:
                fail(f'{page.name}: duplicate link attribute(s) {sorted(dup)} in {tag[:220]}')
            rel = set(data.get('rel', '').lower().split())
            if 'preload' in rel and data.get('as', '').lower() == 'image':
                href = data.get('href', '')
                if not href:
                    fail(f'{page.name}: image preload missing href')
                image_preloads.append(href)

        if len(image_preloads) > 1:
            fail(f'{page.name}: more than one image preload creates competing LCP candidates: {image_preloads}')
        if image_preloads:
            preload_pages += 1
            target = normalize_local(image_preloads[0])
            matching = []
            for tag, data in images:
                if normalize_local(data.get('src', '')) == target:
                    matching.append(data)
            if len(matching) != 1:
                fail(f'{page.name}: image preload must map to exactly one rendered local image: {image_preloads[0]} -> {len(matching)} matches')
            data = matching[0]
            if data.get('loading', '').lower() != 'eager' or data.get('fetchpriority', '').lower() != 'high':
                fail(f'{page.name}: preloaded image must be eager + fetchpriority=high: {image_preloads[0]}')

        if page.name == 'index.html':
            hero_match = re.search(r'<section class=["\']hero["\']>[\s\S]*?</section>', text, re.I)
            if not hero_match:
                fail('index.html: homepage hero section missing')
            hero = hero_match.group(0)
            if hero.count('logistics-stock.webp') != 1:
                fail(f'index.html: expected exactly one frozen hero image, found {hero.count("logistics-stock.webp")}')
            if re.search(r'class=["\'][^"\']*\bhero-photo\b', hero, re.I):
                fail('index.html: hidden legacy hero-photo figure returned')
            hero_tags = [
                (tag, attrs(tag)[0])
                for tag in IMG_TAG.findall(hero)
                if 'hero-bg-r6' in attrs(tag)[0].get('class', '').split()
            ]
            if len(hero_tags) != 1:
                fail(f'index.html: expected exactly one hero-bg-r6 image, found {len(hero_tags)}')
            _, data = hero_tags[0]
            if data.get('width') != '2048' or data.get('height') != '1154':
                fail('index.html: frozen hero intrinsic dimensions changed from 2048x1154')
            if data.get('loading', '').lower() != 'eager' or data.get('fetchpriority', '').lower() != 'high':
                fail('index.html: frozen hero must be eager + fetchpriority=high')

    print(
        f'PASS: R15.10 HTML/media conformance — {len(htmls)} pages, {total_images} local image nodes, '
        f'{preload_pages} image-preload pages, no malformed slash-before-attribute void tags, '
        f'no duplicate img/link attributes, and preload/LCP contracts aligned.'
    )


if __name__ == '__main__':
    main()
