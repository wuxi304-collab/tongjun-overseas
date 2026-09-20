from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
VERSION = '20260920-r15-6b'
MIN_DELIVERY_LONG_EDGE = 2048
MAX_DELIVERY_BYTES = 590 * 1024
NATIVE = {
    'r15-6-materials.webp',
    'r15-6-quality.webp',
    'r15-6-process.webp',
    'r15-6-precision.webp',
    'r15-6-heavy.webp',
    'r15-6-lng.webp',
    'r15-6-tooling.webp',
    'r15-6-titanium.webp',
    'r15-6-resources.webp',
    'r15-6-about.webp',
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

FFPROBE = shutil.which('ffprobe')
FFMPEG = shutil.which('ffmpeg')
if not FFPROBE or not FFMPEG:
    fail('ffprobe/ffmpeg required for R15.6 delivery validation')

def dimensions(path: Path):
    result = subprocess.run(
        [
            FFPROBE, '-v', 'error', '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height', '-of', 'csv=s=x:p=0',
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or 'x' not in result.stdout:
        fail(f'cannot decode image dimensions: {path}')
    w, h = result.stdout.strip().split('x')
    return int(w), int(h)

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
        used.update(re.findall(r'assets/images/(r15-6-[A-Za-z0-9._-]+\.webp)', text))
        for old in LEGACY_FORBIDDEN:
            if f'assets/images/{old}' in text:
                legacy_hits.append((path.name, old))
    if legacy_hits:
        fail(f'legacy soft-image references returned: {legacy_hits[:20]}')
    if used != NATIVE:
        fail(f'native visual reference set mismatch; used={sorted(used)} expected={sorted(NATIVE)}')

    total = 0
    for name in sorted(NATIVE):
        path = ROOT / 'assets' / 'images' / name
        if not path.is_file():
            fail(f'R15.6 delivery visual missing: {name}')
        w, h = dimensions(path)
        size = path.stat().st_size
        total += size
        if max(w, h) < MIN_DELIVERY_LONG_EDGE:
            fail(f'R15.6 delivery visual below 2K gate: {name} {w}x{h}')
        if size > MAX_DELIVERY_BYTES:
            fail(f'R15.6 delivery visual over byte budget: {name} {size // 1024} KB')
        subprocess.run(
            [FFMPEG, '-hide_banner', '-loglevel', 'error', '-i', str(path), '-frames:v', '1', '-f', 'null', '-'],
            check=True,
        )

    index = (ROOT / 'index.html').read_text(encoding='utf-8')
    hero = index.split('<section class="hero">',1)[1].split('</section>',1)[0]
    if 'logistics-stock.webp' not in hero:
        fail('frozen homepage hero changed')
    if 'r15-6-' in hero:
        fail('R15.6 rewrite touched frozen homepage hero')

    all_text = '\n'.join(p.read_text(encoding='utf-8') for p in text_surfaces())
    if f'?v={VERSION}' not in all_text:
        fail('R15.6 delivery cache version missing')

    print(
        f'PASS: R15.6 delivery gate — {len(NATIVE)} optimized real-photo WebPs, each >=2K and '
        f'<=590 KB; aggregate {total // 1024} KB; mapped soft images eliminated; homepage hero remains frozen.'
    )

if __name__ == '__main__':
    main()
