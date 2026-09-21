from pathlib import Path
import base64
import shutil
import subprocess

ROOT = Path('.')
OUT = ROOT / '_prod'

CSS_PARTS = [
    'assets/brand-v34.152.css',
    'assets/brand-v34.152-r2.css',
    'assets/brand-v34.152-r4.css',
    'assets/brand-v34.152-r5.css',
    'assets/brand-v34.152-r6.css',
    'assets/brand-v34.152-r7.css',
    'assets/brand-v34.152-r8.css',
    'assets/brand-v34.152-r9-tail.css',
    'assets/brand-v34.152-r10-tail.css',
    'assets/brand-v34.152-r11-tail.css',
    'assets/brand-v34.152-r12-tail.css',
    'assets/brand-v34.152-r12-fix2.css',
    'assets/brand-v34.152-r13-1-tail.css',
    'assets/brand-v34.152-r14-tail.css',
    'assets/brand-v34.152-r15-tail.css',
    'assets/brand-v34.152-r15-12-tail.css',
    'assets/brand-v34.152-r15-13-tail.css',
    'assets/brand-v34.152-r15-15-tail.css',
]
OVERLAYS = [
    'scripts/apply-brand-shell-v34-152.py',
    'scripts/apply-home-visual-fix-r12.py',
    'scripts/apply-r13-1-release.py',
    'scripts/apply-r14-conversion.py',
    'scripts/apply-r14-runtime.py',
    'scripts/apply-r15-accessibility.py',
    'scripts/apply-r15-2k-visual-freeze.py',
    'scripts/apply-r15-6-native-visuals.py',
    'scripts/apply-r15-9-media-performance.py',
    'scripts/apply-r15-12-mobile-layout.py',
]
PUBLIC_ROOT_FILES = [
    'manifest.webmanifest',
    'robots.txt',
    'sitemap.xml',
    'llms.txt',
]
ASSET_EXTENSIONS = {
    '.css', '.js', '.svg', '.ico', '.png', '.jpg', '.jpeg', '.webp', '.avif',
    '.woff', '.woff2', '.ttf',
}


def materialize_split_image(name: str):
    target = ROOT / 'assets' / 'images' / f'{name}.webp'
    parts = sorted((ROOT / '.sync' / 'r8-modules').glob(f'{name}.part*'))
    if not parts:
        if target.is_file() and target.stat().st_size:
            return
        raise SystemExit(f'ERROR: no split source found for {name}.webp')
    encoded = ''.join(p.read_text(encoding='utf-8').replace('\r', '').replace('\n', '') for p in parts)
    try:
        data = base64.b64decode(encoded, validate=True)
    except Exception as exc:
        raise SystemExit(f'ERROR: invalid split image payload for {name}: {exc}')
    if not data.startswith(b'RIFF') or b'WEBP' not in data[:16]:
        raise SystemExit(f'ERROR: materialized {name}.webp is not a WebP')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


def build_css():
    chunks = []
    for rel in CSS_PARTS:
        path = ROOT / rel
        if not path.is_file():
            raise SystemExit(f'ERROR: production CSS source missing: {rel}')
        chunks.append(path.read_text(encoding='utf-8'))
    target = ROOT / 'assets' / 'brand-v34.152-r14.css'
    target.write_text('\n'.join(chunks) + '\n', encoding='utf-8')
    if 'V34.152 R14.1' not in target.read_text(encoding='utf-8'):
        raise SystemExit('ERROR: consolidated R14 stylesheet marker missing')


def run_overlays():
    for rel in OVERLAYS:
        path = ROOT / rel
        if not path.is_file():
            raise SystemExit(f'ERROR: production overlay missing: {rel}')
        subprocess.run(['python3', rel], check=True)


def copy_tree_filtered(src: Path, dest: Path):
    for path in src.rglob('*'):
        if not path.is_file():
            continue
        if path.suffix.lower() not in ASSET_EXTENSIONS:
            continue
        rel = path.relative_to(src)
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, out)


def build_output():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    htmls = sorted(ROOT.glob('*.html'))
    if len(htmls) != 50:
        raise SystemExit(f'ERROR: expected 50 root HTML pages, found {len(htmls)}')
    for page in htmls:
        shutil.copy2(page, OUT / page.name)

    copy_tree_filtered(ROOT / 'assets', OUT / 'assets')

    well_known = ROOT / '.well-known'
    if well_known.is_dir():
        for path in well_known.rglob('*'):
            if not path.is_file():
                continue
            rel = path.relative_to(well_known)
            out = OUT / '.well-known' / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, out)

    for rel in PUBLIC_ROOT_FILES:
        source = ROOT / rel
        if not source.is_file():
            raise SystemExit(f'ERROR: production public root file missing: {rel}')
        shutil.copy2(source, OUT / rel)

    # Explicitly prove internal/build files are not part of the static output.
    forbidden = ['CNAME', 'package.json', 'vercel.json', 'R7_TEST.txt', 'MINIMAX_ENV.example']
    for name in forbidden:
        if (OUT / name).exists():
            raise SystemExit(f'ERROR: build-only root file leaked to production static output: {name}')
    for dirname in ('api', 'lib', 'scripts', 'ops', 'tests', '.sync'):
        if (OUT / dirname).exists():
            raise SystemExit(f'ERROR: internal/server directory leaked to production static output: {dirname}')

    print(f'PASS: production static output materialized in {OUT} — 50 HTML pages; server/build sources excluded.')


def main():
    materialize_split_image('materials-r8')
    materialize_split_image('quality-r8')
    subprocess.run(['python3', 'scripts/materialize-r15-2k-assets.py'], check=True)
    subprocess.run(['python3', 'scripts/materialize-r15-6-native-assets.py'], check=True)
    build_css()
    run_overlays()
    build_output()
    subprocess.run(['python3', 'scripts/prune-public-raster-assets.py', str(OUT)], check=True)
    subprocess.run(['python3', 'scripts/write-release-metadata.py', str(OUT), 'production'], check=True)


if __name__ == '__main__':
    main()
