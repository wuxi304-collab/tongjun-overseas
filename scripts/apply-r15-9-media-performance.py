from pathlib import Path
import re

ROOT = Path('.')
HERO = 'logistics-stock.webp?v=20260919-r15-5'


def fail(message):
    raise SystemExit('ERROR: ' + message)


def add_attr(tag: str, name: str, value: str) -> str:
    if re.search(rf'\b{name}\s*=', tag, flags=re.I):
        return re.sub(
            rf'\b{name}\s*=\s*["\'][^"\']*["\']',
            f'{name}="{value}"',
            tag,
            count=1,
            flags=re.I,
        )
    return tag[:-1] + f' {name}="{value}">'


def main():
    path = ROOT / 'index.html'
    text = path.read_text(encoding='utf-8')
    match = re.search(r'(<section class="hero">)([\s\S]*?)(</section>)', text)
    if not match:
        fail('homepage hero section missing')

    inner = match.group(2)
    figures = re.findall(r'<figure\b[^>]*class=["\'][^"\']*\bhero-photo\b[^"\']*["\'][^>]*>[\s\S]*?</figure>', inner, flags=re.I)
    if len(figures) != 1:
        fail(f'expected exactly one legacy hero-photo figure before R15.9 cleanup, found {len(figures)}')
    inner = inner.replace(figures[0], '', 1)

    bg = re.search(r'<img\b[^>]*class=["\'][^"\']*\bhero-bg-r6\b[^"\']*["\'][^>]*>', inner, flags=re.I)
    if not bg:
        fail('homepage hero background image missing')
    tag = bg.group(0)
    tag = add_attr(tag, 'loading', 'eager')
    tag = add_attr(tag, 'fetchpriority', 'high')
    tag = add_attr(tag, 'decoding', 'async')
    inner = inner[:bg.start()] + tag + inner[bg.end():]

    if inner.count('logistics-stock.webp') != 1:
        fail(f'homepage hero must contain exactly one logistics-stock image after cleanup; found {inner.count("logistics-stock.webp")}')
    if f'/assets/images/{HERO}' not in inner:
        fail('frozen homepage hero URL/cache key changed')
    if 'hero-special-metals.webp' in inner or 'r15-6-' in inner:
        fail('homepage hero visual changed during R15.9 performance cleanup')

    updated = text[:match.start(2)] + inner + text[match.end(2):]
    preload_pattern = re.compile(r'<link\b[^>]*rel=["\'][^"\']*\bpreload\b[^"\']*["\'][^>]*>', re.I)
    preloads = []
    for link in preload_pattern.findall(updated):
        if re.search(r'\bas=["\']image["\']', link, flags=re.I):
            href = re.search(r'\bhref=["\']([^"\']+)["\']', link, flags=re.I)
            if href:
                preloads.append(href.group(1))
    expected = f'/assets/images/{HERO}'
    if preloads != [expected]:
        fail(f'homepage image preload mismatch after cleanup: {preloads}')

    path.write_text(updated, encoding='utf-8')
    print('PASS: R15.9 homepage media cleanup — one frozen hero image, eager/high LCP candidate, preload aligned; hidden duplicate removed.')


if __name__ == '__main__':
    main()
