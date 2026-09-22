from pathlib import Path
import re
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
RASTER = {'.webp', '.jpg', '.jpeg', '.png', '.avif'}
TEXT_EXT = {'.html', '.css', '.js', '.json', '.xml', '.txt', '.webmanifest', '.svg'}
REF_RE = re.compile(r'assets/images/([A-Za-z0-9._-]+)')
MIN_CONTENT_LONG_EDGE = 2048


def fail(message):
    raise SystemExit('ERROR: ' + message)


def collect_refs():
    refs = set()
    for path in ROOT.rglob('*'):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXT:
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue
        refs.update(REF_RE.findall(text))
    return refs


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


def main():
    images = ROOT / 'assets' / 'images'
    if not images.is_dir():
        fail(f'public image directory missing: {images}')

    refs = collect_refs()
    all_files = sorted(p for p in images.iterdir() if p.is_file())
    rasters = [p for p in all_files if p.suffix.lower() in RASTER]
    names = {p.name for p in all_files}

    referenced_assets = {name for name in refs if (images / name).is_file()}
    missing = sorted(name for name in refs if not (images / name).is_file())
    if missing:
        fail(f'referenced public image asset(s) missing: {missing}')

    dead = sorted(names - referenced_assets)
    if dead:
        fail(f'unreferenced file(s) leaked into public image directory: {dead}')

    non_raster = sorted(name for name in names if Path(name).suffix.lower() not in RASTER)
    if non_raster:
        fail(f'R15.16 public image directory must contain only referenced 2K raster delivery assets: {non_raster}')

    bad = []
    content = []
    for path in rasters:
        if path.suffix.lower() != '.webp':
            bad.append((path.name, 'non-WebP content raster'))
            continue
        w, h = webp_dimensions(path)
        content.append((path.name, w, h))
        minimum = 1440 if path.name == 'hero-special-metals-r15-24-mobile.webp' else MIN_CONTENT_LONG_EDGE
        if max(w, h) < minimum:
            bad.append((path.name, f'{w}x{h}'))

    if bad:
        fail(f'public raster(s) below 2K or invalid: {bad}')
    required_hero = {
        'hero-special-metals-r15-24.webp',
        'hero-special-metals-r15-24-4k.webp',
        'hero-special-metals-r15-24-mobile.webp',
    }
    if not required_hero.issubset(names):
        fail(f'R15.24 HERO delivery set incomplete: {sorted(required_hero - names)}')

    total = sum(p.stat().st_size for p in rasters)
    print(
        f'PASS: R15.16 public image hygiene — {len(rasters)} referenced public raster(s) only; '
        f'{len(content)} public raster images satisfy release dimension gates; zero raster-logo exemptions; '
        f'aggregate raster payload {total // 1024} KB.'
    )


if __name__ == '__main__':
    main()
