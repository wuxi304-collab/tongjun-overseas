from pathlib import Path
import re
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
VERSION = '20260919-r15-6'
MIN_LONG_EDGE = 3000
NATIVE = {
    'r15-6-materials.jpg',
    'r15-6-quality.jpg',
    'r15-6-process.jpg',
    'r15-6-precision.jpg',
    'r15-6-heavy.jpg',
    'r15-6-lng.jpg',
    'r15-6-tooling.jpg',
    'r15-6-titanium.jpg',
    'r15-6-resources.jpg',
    'r15-6-about.jpg',
}
LEGACY_FORBIDDEN = {
    'about-engineering.webp',
    'engineering-discussion-v2.webp',
    'engineering-review-v2.webp',
    'heavy-plate.webp',
    'hero-port-v2.webp',
    'hero-special-metals.webp',
    'invar-lng.webp',
    'invar-tooling.webp',
    'materials-r8.webp',
    'materials-warehouse-v2.webp',
    'nickel-alloys.webp',
    'og-cover.webp',
    'precision-strip.webp',
    'quality-inspection.webp',
    'quality-lab-v2.webp',
    'quality-r8.webp',
    'resources-metal.webp',
    'standards-rfq.webp',
    'titanium-zirconium.webp',
}

def fail(msg):
    raise SystemExit('ERROR: ' + msg)

def jpeg_dimensions(path: Path):
    data = path.read_bytes()
    if len(data) < 4 or data[:2] != b'\xff\xd8':
        fail(f'not a JPEG: {path}')
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        while i < len(data) and data[i] == 0xFF:
            i += 1
        if i >= len(data):
            break
        marker = data[i]
        i += 1
        if marker in (0xD8, 0xD9):
            continue
        if i + 2 > len(data):
            break
        seglen = int.from_bytes(data[i:i+2], 'big')
        if seglen < 2 or i + seglen > len(data):
            break
        if marker in {0xC0,0xC1,0xC2,0xC3,0xC5,0xC6,0xC7,0xC9,0xCA,0xCB,0xCD,0xCE,0xCF}:
            h = int.from_bytes(data[i+3:i+5], 'big')
            w = int.from_bytes(data[i+5:i+7], 'big')
            return w, h
        i += seglen
    fail(f'cannot read JPEG dimensions: {path}')

def text_surfaces():
    items = list(ROOT.glob('*.html'))
    for rel in ('assets/brand-v34.152-r14.css','assets/site.css','assets/brand-v34.152.js'):
        p = ROOT / rel
        if p.is_file():
            items.append(p)
    return items

def main():
    used = set()
    legacy_hits = []
    for path in text_surfaces():
        text = path.read_text(encoding='utf-8')
        used.update(re.findall(r'assets/images/(r15-6-[A-Za-z0-9._-]+\.jpg)', text))
        for old in LEGACY_FORBIDDEN:
            if f'assets/images/{old}' in text:
                legacy_hits.append((path.name, old))
    if legacy_hits:
        fail(f'legacy soft-image references returned: {legacy_hits[:20]}')
    if used != NATIVE:
        fail(f'native visual reference set mismatch; used={sorted(used)} expected={sorted(NATIVE)}')

    for name in sorted(NATIVE):
        path = ROOT / 'assets' / 'images' / name
        if not path.is_file():
            fail(f'native visual missing: {name}')
        w, h = jpeg_dimensions(path)
        if max(w, h) < MIN_LONG_EDGE:
            fail(f'native visual below 3K source gate: {name} {w}x{h}')
        if path.stat().st_size < 350_000:
            fail(f'native visual unexpectedly small: {name} {path.stat().st_size} bytes')

    index = (ROOT / 'index.html').read_text(encoding='utf-8')
    hero = index.split('<section class="hero">',1)[1].split('</section>',1)[0]
    if 'logistics-stock.webp' not in hero:
        fail('frozen homepage hero changed')
    if 'r15-6-' in hero:
        fail('native visual rewrite touched frozen homepage hero')

    all_text = '\n'.join(p.read_text(encoding='utf-8') for p in text_surfaces())
    if f'?v={VERSION}' not in all_text:
        fail('R15.6 cache version missing')

    print(f'PASS: R15.6 native visual gate — {len(NATIVE)} locally shipped real-photo masters, every source long edge >= {MIN_LONG_EDGE}px; mapped legacy soft images eliminated; homepage hero remains frozen.')

if __name__ == '__main__':
    main()
