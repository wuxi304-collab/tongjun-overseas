from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
MANIFEST = Path('VISUAL_MANIFEST_R15_7.json')
VERSION = '20260920-r15-6b'
MIN_DELIVERY_LONG_EDGE = 2048
MAX_DELIVERY_BYTES = 590 * 1024
LEGACY_FORBIDDEN = {
    'about-engineering.webp','engineering-discussion-v2.webp','engineering-review-v2.webp',
    'heavy-plate.webp','hero-port-v2.webp','hero-special-metals.webp','invar-lng.webp',
    'invar-tooling.webp','materials-r8.webp','materials-warehouse-v2.webp','nickel-alloys.webp',
    'og-cover.webp','precision-strip.webp','quality-inspection.webp','quality-lab-v2.webp',
    'quality-r8.webp','resources-metal.webp','standards-rfq.webp','titanium-zirconium.webp',
}

def fail(msg):
    raise SystemExit('ERROR: ' + msg)

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
        if fourcc == b'VP8 ' and len(payload) >= 10 and payload[3:6] == b'\\x9d\\x01\\x2a':
            return int.from_bytes(payload[6:8], 'little') & 0x3fff, int.from_bytes(payload[8:10], 'little') & 0x3fff
        if fourcc == b'VP8L' and len(payload) >= 5 and payload[0] == 0x2f:
            bits = int.from_bytes(payload[1:5], 'little')
            return (bits & 0x3fff) + 1, ((bits >> 14) & 0x3fff) + 1
        pos += 8 + size + (size & 1)
    fail(f'WebP dimensions unavailable: {path}')


def sha256(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load_manifest():
    if not MANIFEST.is_file():
        fail('R15.7 visual manifest missing')
    doc = json.loads(MANIFEST.read_text(encoding='utf-8'))
    if doc.get('release') != 'V34.152 R15.7':
        fail('unexpected R15.7 manifest release')
    return doc

def text_surfaces():
    items = list(ROOT.glob('*.html'))
    for rel in ('assets/brand-v34.152-r14.css','assets/site.css','assets/brand-v34.152.js'):
        p = ROOT / rel
        if p.is_file():
            items.append(p)
    return items

def main():
    manifest = load_manifest()
    expected = manifest['assets']
    native = set(expected)
    used = set()
    legacy_hits = []
    for path in text_surfaces():
        text = path.read_text(encoding='utf-8')
        used.update(re.findall(r'assets/images/(r15-6-[A-Za-z0-9._-]+\\.webp)', text))
        for old in LEGACY_FORBIDDEN:
            if f'assets/images/{old}' in text:
                legacy_hits.append((path.name, old))
    if legacy_hits:
        fail(f'legacy soft-image references returned: {legacy_hits[:20]}')
    if used != native:
        fail(f'R15.7 visual reference set mismatch; used={sorted(used)} expected={sorted(native)}')

    total = 0
    for name, meta in sorted(expected.items()):
        path = ROOT / 'assets' / 'images' / name
        if not path.is_file():
            fail(f'R15.7 frozen visual missing: {name}')
        dims = webp_dimensions(path)
        size = path.stat().st_size
        digest = sha256(path)
        total += size
        if dims != (meta['width'], meta['height']):
            fail(f'R15.7 visual dimensions drifted: {name} {dims}')
        if max(dims) < MIN_DELIVERY_LONG_EDGE:
            fail(f'R15.7 visual below 2K: {name} {dims}')
        if size != meta['bytes'] or size > MAX_DELIVERY_BYTES:
            fail(f'R15.7 visual byte budget drifted: {name} {size}')
        if digest != meta['sha256']:
            fail(f'R15.7 visual SHA256 drifted: {name} {digest}')

    hero_meta = manifest['hero']
    hero_path = ROOT / 'assets' / 'images' / hero_meta['file']
    if not hero_path.is_file():
        fail('frozen homepage hero missing')
    if webp_dimensions(hero_path) != (hero_meta['width'], hero_meta['height']):
        fail('frozen homepage hero dimensions drifted')
    if hero_path.stat().st_size != hero_meta['bytes'] or sha256(hero_path) != hero_meta['sha256']:
        fail('frozen homepage hero binary drifted')

    index = (ROOT / 'index.html').read_text(encoding='utf-8')
    hero = index.split('<section class="hero">',1)[1].split('</section>',1)[0]
    if hero_meta['file'] not in hero or 'r15-6-' in hero:
        fail('homepage hero reference changed')
    all_text = '\n'.join(p.read_text(encoding='utf-8') for p in text_surfaces())
    if f'?v={VERSION}' not in all_text:
        fail('R15.6 delivery cache version missing')

    print(
        f'PASS: R15.7 content-addressed visual gate — {len(expected)} frozen inner-page WebPs + '
        f'1 frozen hero verified by dimensions, bytes and SHA256; aggregate inner visuals {total // 1024} KB.'
    )

if __name__ == '__main__':
    main()
