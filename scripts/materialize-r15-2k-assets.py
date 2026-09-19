from pathlib import Path
import hashlib
import shutil
import subprocess

ROOT = Path('.')
IMAGES = ROOT / 'assets' / 'images'
VERSION = '20260919-r15-5'
MIN_LONG_EDGE = 2048

# Content imagery that may be reached by the shipped HTML/CSS/JS.
CONTENT_ASSETS = [
    'about-engineering.webp',
    'engineering-discussion-v2.webp',
    'engineering-review-v2.webp',
    'heavy-plate.webp',
    'hero-port-v2.webp',
    'hero-special-metals.webp',
    'invar-lng.webp',
    'invar-tooling.webp',
    'logistics-stock.webp',
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
]

# Three legacy files are irrecoverably truncated; other legacy references were
# never valid production assets. Keep their semantics conservative by deriving
# them from the closest existing industrial visual rather than inventing a new scene.
SOURCE_OVERRIDE = {
    'about-engineering.webp': 'resources-metal.webp',
    'engineering-discussion-v2.webp': 'titanium-zirconium.webp',
    'engineering-review-v2.webp': 'quality-r8.webp',
    'hero-port-v2.webp': 'logistics-stock.webp',
    'hero-special-metals.webp': 'logistics-stock.webp',
    'materials-warehouse-v2.webp': 'materials-r8.webp',
    'quality-lab-v2.webp': 'quality-r8.webp',
}

# Freeze the exact R15.4 hero source bytes. If anyone replaces the hero source,
# the build stops before it can silently ship a different visual.
HERO_SOURCE_SHA256 = '89961367b48e0d8a16df57739c34c4a572e4608968a6a45efcc94cc515327900'


def command(name):
    resolved = shutil.which(name)
    if not resolved:
        raise SystemExit(f'ERROR: required binary missing: {name}')
    return resolved


FFMPEG = command('ffmpeg')
FFPROBE = command('ffprobe')


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def dimensions(path: Path):
    result = subprocess.run(
        [
            FFPROBE, '-v', 'error', '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height', '-of', 'csv=s=x:p=0',
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    width, height = result.stdout.strip().split('x')
    return int(width), int(height)


def transcode_2k(source: Path, target: Path):
    tmp = target.with_name(target.stem + '.r15-2k-tmp.webp')
    if tmp.exists():
        tmp.unlink()
    subprocess.run(
        [
            FFMPEG, '-hide_banner', '-loglevel', 'error', '-err_detect', 'ignore_err',
            '-i', str(source), '-frames:v', '1',
            '-vf',
            "scale='if(gte(iw,ih),2048,-2)':'if(gte(iw,ih),-2,2048)':flags=lanczos,"
            "unsharp=5:5:0.35:5:5:0.0",
            '-c:v', 'libwebp', '-quality', '88', '-compression_level', '6',
            '-y', str(tmp),
        ],
        check=True,
    )
    width, height = dimensions(tmp)
    if max(width, height) < MIN_LONG_EDGE:
        raise SystemExit(f'ERROR: 2K transcode failed for {target.name}: {width}x{height}')
    # A second decode proves the generated file is not just header-readable.
    subprocess.run(
        [FFMPEG, '-hide_banner', '-loglevel', 'error', '-i', str(tmp), '-frames:v', '1', '-f', 'null', '-'],
        check=True,
    )
    tmp.replace(target)
    return width, height


def main():
    hero = IMAGES / 'logistics-stock.webp'
    if not hero.is_file():
        raise SystemExit('ERROR: frozen homepage hero source missing')
    actual = sha256(hero)
    if actual != HERO_SOURCE_SHA256:
        raise SystemExit(
            'ERROR: homepage hero source changed. '
            f'Expected {HERO_SOURCE_SHA256}, found {actual}. '
            'Hero replacement requires explicit visual approval.'
        )

    results = []
    for name in CONTENT_ASSETS:
        source_name = SOURCE_OVERRIDE.get(name, name)
        source = IMAGES / source_name
        target = IMAGES / name
        if not source.is_file():
            raise SystemExit(f'ERROR: source image missing for {name}: {source_name}')
        width, height = transcode_2k(source, target)
        results.append((name, width, height, source_name))

    print(f'PASS: R15.5 2K materialization — {len(results)} content rasters generated at long edge >= {MIN_LONG_EDGE}px.')
    for name, width, height, source_name in results:
        suffix = '' if source_name == name else f' <- {source_name}'
        print(f'  {name}: {width}x{height}{suffix}')


if __name__ == '__main__':
    main()
