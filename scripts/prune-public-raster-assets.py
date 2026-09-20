from pathlib import Path
import re
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
RASTER = {'.webp', '.jpg', '.jpeg', '.png', '.avif'}
TEXT_EXT = {'.html', '.css', '.js', '.json', '.xml', '.txt', '.webmanifest', '.svg'}
REF_RE = re.compile(r'assets/images/([A-Za-z0-9._-]+)')


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


def main():
    images = ROOT / 'assets' / 'images'
    if not images.is_dir():
        fail(f'public image directory missing: {images}')

    refs = collect_refs()
    missing = sorted(
        name for name in refs
        if Path(name).suffix.lower() in RASTER and not (images / name).is_file()
    )
    if missing:
        fail(f'referenced raster(s) missing before prune: {missing}')

    removed = []
    kept = []
    for path in sorted(images.iterdir()):
        if not path.is_file() or path.suffix.lower() not in RASTER:
            continue
        if path.name in refs:
            kept.append(path.name)
        else:
            removed.append(path.name)
            path.unlink()

    remaining = sorted(
        p.name for p in images.iterdir()
        if p.is_file() and p.suffix.lower() in RASTER
    )
    if set(remaining) != set(kept):
        fail('public raster prune produced an unexpected remaining set')

    print(
        f'PASS: public raster prune — kept {len(kept)} referenced raster(s), '
        f'removed {len(removed)} unreferenced legacy raster(s).'
    )
    if removed:
        print('Removed legacy raster(s): ' + ', '.join(removed))


if __name__ == '__main__':
    main()
