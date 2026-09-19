from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import urlsplit

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
MIN_LONG_EDGE = 2048
VERSION = '20260919-r15-5'
RASTER = {'.webp', '.jpg', '.jpeg', '.png', '.avif'}
LOGO_EXEMPT = {'columbus-logo-v2.webp', 'columbus-mark.webp'}


def fail(message):
    raise SystemExit('ERROR: ' + message)


def ffprobe():
    tool = shutil.which('ffprobe')
    if not tool:
        fail('ffprobe is required for the R15.5 visual gate')
    return tool


FFPROBE = ffprobe()


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
    width, height = result.stdout.strip().split('x')
    return int(width), int(height)


def collect_refs():
    refs = set()
    # Scan shipped markup plus the active CSS/runtime surfaces that can select visuals.
    candidates = list(ROOT.glob('*.html'))
    for rel in (
        'assets/brand-v34.152-r14.css',
        'assets/site.css',
        'assets/brand-v34.152.js',
    ):
        path = ROOT / rel
        if path.is_file():
            candidates.append(path)
    pattern = re.compile(r'assets/images/([A-Za-z0-9._-]+)')
    for path in candidates:
        text = path.read_text(encoding='utf-8')
        refs.update(pattern.findall(text))
    return refs


def main():
    refs = collect_refs()
    raster_refs = sorted(
        name for name in refs
        if Path(name).suffix.lower() in RASTER and name not in LOGO_EXEMPT
    )
    if not raster_refs:
        fail('no content raster references found')

    bad = []
    for name in raster_refs:
        path = ROOT / 'assets' / 'images' / name
        if not path.is_file():
            bad.append((name, 'missing'))
            continue
        width, height = dimensions(path)
        if max(width, height) < MIN_LONG_EDGE:
            bad.append((name, f'{width}x{height}'))
    if bad:
        fail(f'content raster(s) below 2K or missing: {bad}')

    index = (ROOT / 'index.html').read_text(encoding='utf-8')
    if '<section class="hero">' not in index:
        fail('homepage hero section missing')
    hero = index.split('<section class="hero">', 1)[1].split('</section>', 1)[0]
    if hero.count('logistics-stock.webp') < 1:
        fail('homepage hero visual changed from frozen logistics-stock.webp')
    if 'hero-special-metals.webp' in hero:
        fail('homepage hero silently switched to hero-special-metals.webp')
    if f'logistics-stock.webp?v={VERSION}' not in hero:
        fail('homepage hero 2K cache key missing')

    width, height = dimensions(ROOT / 'assets' / 'images' / 'logistics-stock.webp')
    if max(width, height) < MIN_LONG_EDGE:
        fail(f'frozen homepage hero is below 2K: {width}x{height}')

    print(
        f'PASS: R15.5 visual gate — {len(raster_refs)} shipped content raster references are >=2K; '
        f'homepage hero frozen to logistics-stock.webp ({width}x{height}).'
    )


if __name__ == '__main__':
    main()
