from pathlib import Path
import re

ROOT = Path('.')
VERSION = '20260922-r15-24'
BASE = f'/assets/images/hero-special-metals-r15-24.webp?v={VERSION}'
MOBILE = f'/assets/images/hero-special-metals-r15-24-mobile.webp?v={VERSION}'
FOUR_K = f'/assets/images/hero-special-metals-r15-24-4k.webp?v={VERSION}'


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
    match = re.search(r'(\s*/?>)\s*$', tag)
    if not match:
        fail(f'cannot append {name}: malformed tag boundary: {tag}')
    closing = ' />' if '/' in match.group(1) else '>'
    body = tag[:match.start()].rstrip()
    return body + f' {name}="{value}"' + closing


def attr(tag: str, name: str) -> str:
    match = re.search(rf'\b{name}\s*=\s*["\']([^"\']*)["\']', tag, flags=re.I)
    return match.group(1) if match else ''


def main():
    path = ROOT / 'index.html'
    text = path.read_text(encoding='utf-8')
    match = re.search(r'(<section class="hero">)([\s\S]*?)(</section>)', text)
    if not match:
        fail('homepage hero section missing')

    inner = match.group(2)

    # Idempotent cleanup: legacy figure may already have been removed by R13.1.
    inner = re.sub(
        r'<figure\b[^>]*class=["\'][^"\']*\bhero-photo\b[^"\']*["\'][^>]*>[\s\S]*?</figure>',
        '',
        inner,
        flags=re.I,
    )

    if 'hero-picture-r15-24' not in inner:
        fail('R15.24 responsive HERO picture missing before media cleanup')

    bg = re.search(
        r'<img\b[^>]*class=["\'][^"\']*\bhero-bg-r6\b[^"\']*["\'][^>]*>',
        inner,
        flags=re.I,
    )
    if not bg:
        fail('R15.24 homepage HERO image missing')

    tag = bg.group(0)
    for name, value in (
        ('loading', 'eager'),
        ('fetchpriority', 'high'),
        ('decoding', 'async'),
        ('width', '2560'),
        ('height', '1440'),
        ('sizes', '100vw'),
    ):
        tag = add_attr(tag, name, value)

    if BASE not in attr(tag, 'src'):
        fail(f'R15.24 homepage HERO base source changed: {attr(tag, "src")}')
    srcset = attr(tag, 'srcset')
    if BASE not in srcset or FOUR_K not in srcset:
        fail(f'R15.24 desktop srcset changed: {srcset}')

    inner = inner[:bg.start()] + tag + inner[bg.end():]

    for required in (BASE, MOBILE, FOUR_K):
        if required not in inner:
            fail(f'R15.24 HERO delivery source missing after cleanup: {required}')
    if 'hero-special-metals.webp' in inner or 'r15-6-' in inner or 'logistics-stock.webp' in inner:
        fail('legacy homepage HERO reference returned during R15.9 cleanup')

    updated = text[:match.start(2)] + inner + text[match.end(2):]

    image_preloads = []
    for link in re.findall(r'<link\b[^>]*>', updated, flags=re.I):
        rel = attr(link, 'rel').lower().split()
        if 'preload' not in rel or attr(link, 'as').lower() != 'image':
            continue
        image_preloads.append((attr(link, 'href'), attr(link, 'media')))

    expected = {
        (MOBILE, '(max-width:860px)'),
        (BASE, '(min-width:861px)'),
    }
    if set(image_preloads) != expected or len(image_preloads) != 2:
        fail(f'R15.24 responsive HERO preload mismatch: {image_preloads}')

    malformed = re.findall(
        r'<img\b[^>]*?/\s+[A-Za-z_:][-A-Za-z0-9_:.]*\s*=',
        updated,
        flags=re.I,
    )
    if malformed:
        fail(f'non-conforming slash-before-attribute image tag(s) remain: {malformed[:3]}')

    path.write_text(updated, encoding='utf-8')
    print(
        'PASS: R15.24 homepage media cleanup — responsive picture preserved; '
        '2K/4K/mobile sources and mutually-exclusive preloads aligned.'
    )


if __name__ == '__main__':
    main()
