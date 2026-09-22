from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
MANIFEST = Path('VISUAL_MANIFEST_R15_7.json')
MIN_LONG_EDGE = 2048
VERSION = '20260922-r15-24'
RASTER = {'.webp', '.jpg', '.jpeg', '.png', '.avif'}
LOGO_EXEMPT = {'columbus-logo-v2.webp', 'columbus-mark.webp'}

def fail(message):
    raise SystemExit('ERROR: ' + message)

def webp_dimensions(path: Path):
    data = path.read_bytes()
    if len(data) < 30 or data[:4] != b'RIFF' or data[8:12] != b'WEBP':
        fail(f'invalid WebP: {path}')
    pos = 12
    while pos + 8 <= len(data):
        fourcc = data[pos:pos+4]
        size = int.from_bytes(data[pos+4:pos+8], 'little')
        payload = data[pos+8:pos+8+size]
        if fourcc == b'VP8X' and len(payload) >= 10:
            return 1 + int.from_bytes(payload[4:7], 'little'), 1 + int.from_bytes(payload[7:10], 'little')
        if fourcc == b'VP8 ' and len(payload) >= 10 and payload[3:6] == b'\x9d\x01\x2a':
            return int.from_bytes(payload[6:8], 'little') & 0x3fff, int.from_bytes(payload[8:10], 'little') & 0x3fff
        if fourcc == b'VP8L' and len(payload) >= 5 and payload[0] == 0x2f:
            bits = int.from_bytes(payload[1:5], 'little')
            return (bits & 0x3fff) + 1, ((bits >> 14) & 0x3fff) + 1
        pos += 8 + size + (size & 1)
    fail(f'WebP dimensions unavailable: {path}')


def dimensions(path: Path):
    if path.suffix.lower() == '.webp':
        return webp_dimensions(path)
    fail(f'R15.7 visual gate only permits shipped content WebP rasters: {path.name}')

def collect_refs():
    refs = set()
    candidates = list(ROOT.glob('*.html'))
    for rel in ('assets/brand-v34.152-r14.css','assets/site.css','assets/brand-v34.152.js'):
        path = ROOT / rel
        if path.is_file():
            candidates.append(path)
    pattern = re.compile(r'assets/images/([A-Za-z0-9._-]+)')
    for path in candidates:
        refs.update(pattern.findall(path.read_text(encoding='utf-8')))
    return refs

def main():
    refs = collect_refs()
    raster_refs = sorted(name for name in refs if Path(name).suffix.lower() in RASTER and name not in LOGO_EXEMPT)
    if not raster_refs:
        fail('no content raster references found')

    bad = []
    for name in raster_refs:
        path = ROOT / 'assets' / 'images' / name
        if not path.is_file():
            bad.append((name, 'missing'))
            continue
        w, h = dimensions(path)
        minimum = 1440 if name == 'hero-special-metals-r15-24-mobile.webp' else MIN_LONG_EDGE
        if max(w, h) < minimum:
            bad.append((name, f'{w}x{h}'))
    if bad:
        fail(f'content raster(s) below 2K or missing: {bad}')

    if not MANIFEST.is_file():
        fail('R15.7 visual manifest missing')
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    hero_meta = manifest['hero']
    hero_path = ROOT / 'assets' / 'images' / hero_meta['file']
    if hashlib.sha256(hero_path.read_bytes()).hexdigest() != hero_meta['sha256']:
        fail('frozen homepage hero SHA256 drifted')

    index = (ROOT / 'index.html').read_text(encoding='utf-8')
    hero = index.split('<section class="hero">',1)[1].split('</section>',1)[0]
    if hero_meta['file'] not in hero or 'hero-special-metals.webp' in hero:
        fail('homepage hero reference changed')
    if f"{hero_meta['file']}?v={VERSION}" not in hero:
        fail('homepage hero cache key missing')
    for name, expected in {
        'hero-special-metals-r15-24-4k.webp': (3840, 2160),
        'hero-special-metals-r15-24-mobile.webp': (1440, 1800),
    }.items():
        path = ROOT / 'assets' / 'images' / name
        if not path.is_file():
            fail(f'R15.24 HERO variant missing: {name}')
        if dimensions(path) != expected:
            fail(f'R15.24 HERO variant dimensions drifted: {name} {dimensions(path)}')
        if name not in index:
            fail(f'R15.24 HERO variant is not referenced by homepage: {name}')

    w, h = dimensions(hero_path)
    print(
        f'PASS: R15.7 visual gate — {len(raster_refs)} shipped content rasters >=2K; '
        f'homepage hero binary frozen by SHA256 ({w}x{h}).'
    )

if __name__ == '__main__':
    main()
