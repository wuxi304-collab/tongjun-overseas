from pathlib import Path
from urllib.request import Request, urlopen
import shutil
import subprocess
import time

ROOT = Path('.')
IMAGES = ROOT / 'assets' / 'images'
CACHE = ROOT / '.sync' / 'r15-6-native-src'
VERSION = '20260920-r15-6b'
MIN_SOURCE_LONG_EDGE = 3000
MIN_SOURCE_BYTES = 350_000
MIN_DELIVERY_LONG_EDGE = 2048
TARGET_MAX_BYTES = 590 * 1024

# Fixed, high-resolution real industrial photographs. Original JPEGs are used
# only as build-time source material. The browser receives local WebP derivatives.
SOURCES = {
    'r15-6-materials': 'https://images.pexels.com/photos/8940223/pexels-photo-8940223.jpeg?cs=srgb&fm=jpg',
    'r15-6-quality': 'https://images.pexels.com/photos/32845682/pexels-photo-32845682.jpeg?cs=srgb&fm=jpg',
    'r15-6-process': 'https://images.pexels.com/photos/5411674/pexels-photo-5411674.jpeg?cs=srgb&fm=jpg',
    'r15-6-precision': 'https://images.pexels.com/photos/8972008/pexels-photo-8972008.jpeg?cs=srgb&fm=jpg',
    'r15-6-heavy': 'https://images.pexels.com/photos/8973680/pexels-photo-8973680.jpeg?cs=srgb&fm=jpg',
    'r15-6-lng': 'https://images.pexels.com/photos/36778676/pexels-photo-36778676.jpeg?cs=srgb&fm=jpg',
    'r15-6-tooling': 'https://images.pexels.com/photos/10406128/pexels-photo-10406128.jpeg?cs=srgb&fm=jpg',
    'r15-6-titanium': 'https://images.pexels.com/photos/32845684/pexels-photo-32845684.jpeg?cs=tinysrgb&w=6129&fit=max&fm=jpg',
    'r15-6-resources': 'https://images.pexels.com/photos/3861938/pexels-photo-3861938.jpeg?cs=srgb&fm=jpg',
    'r15-6-about': 'https://images.pexels.com/photos/34054482/pexels-photo-34054482.jpeg?cs=srgb&fm=jpg',
}

def command(name):
    resolved = shutil.which(name)
    if not resolved:
        raise SystemExit(f'ERROR: required binary missing: {name}')
    return resolved

FFMPEG = command('ffmpeg')
FFPROBE = command('ffprobe')

def jpeg_dimensions(data: bytes):
    if len(data) < 4 or data[:2] != b'\xff\xd8':
        raise ValueError('not a JPEG')
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
    raise ValueError('JPEG dimensions not found')

def fetch(url: str) -> bytes:
    last = None
    for attempt in range(3):
        try:
            req = Request(url, headers={
                'User-Agent': 'TongjunVisualBuild/15.6 (+https://exoticalloycn.com)',
                'Accept': 'image/jpeg,image/*,*/*;q=0.8',
            })
            with urlopen(req, timeout=30) as response:
                return response.read()
        except Exception as exc:
            last = exc
            if attempt < 2:
                time.sleep(1 + attempt)
    raise SystemExit(f'ERROR: image download failed after retries: {url} ({last})')

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
    w, h = result.stdout.strip().split('x')
    return int(w), int(h)

def encode_derivative(source: Path, target: Path, source_width: int, source_height: int):
    # Start above 2K for sharper desktop delivery. If a detailed source cannot
    # satisfy the byte budget, reduce dimensions but never below 2048x1152.
    attempts = [
        (2560, 1440, 84), (2560, 1440, 80), (2560, 1440, 76),
        (2304, 1296, 82), (2304, 1296, 78), (2304, 1296, 74),
        (2048, 1152, 82), (2048, 1152, 78), (2048, 1152, 74), (2048, 1152, 70),
    ]
    tmp = target.with_suffix('.tmp.webp')
    for width, height, quality in attempts:
        # Never enlarge a source to satisfy the delivery target. Both target
        # dimensions must fit inside the native source before cover/crop.
        if width > source_width or height > source_height:
            continue
        if tmp.exists():
            tmp.unlink()
        vf = (
            f'scale={width}:{height}:force_original_aspect_ratio=increase:flags=lanczos,'
            f'crop={width}:{height}'
        )
        subprocess.run(
            [
                FFMPEG, '-hide_banner', '-loglevel', 'error',
                '-i', str(source), '-frames:v', '1',
                '-vf', vf,
                '-c:v', 'libwebp', '-preset', 'picture',
                '-quality', str(quality), '-compression_level', '6',
                '-y', str(tmp),
            ],
            check=True,
        )
        size = tmp.stat().st_size
        w, h = dimensions(tmp)
        if max(w, h) < MIN_DELIVERY_LONG_EDGE:
            continue
        # Decode once more so a merely header-readable file can never ship.
        subprocess.run(
            [FFMPEG, '-hide_banner', '-loglevel', 'error', '-i', str(tmp), '-frames:v', '1', '-f', 'null', '-'],
            check=True,
        )
        if size <= TARGET_MAX_BYTES:
            tmp.replace(target)
            return w, h, quality, size
    raise SystemExit(
        f'ERROR: unable to fit {target.name} within {TARGET_MAX_BYTES} bytes '
        f'without dropping below {MIN_DELIVERY_LONG_EDGE}px'
    )

def main():
    IMAGES.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)

    # Remove stale R15.6 public derivatives from previous failed builds.
    for stale in IMAGES.glob('r15-6-*'):
        if stale.is_file():
            stale.unlink()

    rows = []
    for stem, url in SOURCES.items():
        data = fetch(url)
        if len(data) < MIN_SOURCE_BYTES:
            raise SystemExit(f'ERROR: {stem} source unexpectedly small: {len(data)} bytes')
        try:
            sw, sh = jpeg_dimensions(data)
        except Exception as exc:
            raise SystemExit(f'ERROR: {stem} source is not a valid JPEG: {exc}')
        if max(sw, sh) < MIN_SOURCE_LONG_EDGE:
            raise SystemExit(f'ERROR: {stem} source below native gate: {sw}x{sh}')

        source = CACHE / f'{stem}.jpg'
        source.write_bytes(data)
        target = IMAGES / f'{stem}.webp'
        dw, dh, quality, size = encode_derivative(source, target, sw, sh)
        rows.append((stem, sw, sh, dw, dh, quality, size))

    print(
        f'PASS: R15.6 optimized native visuals — {len(rows)} real-photo sources validated at >= '
        f'{MIN_SOURCE_LONG_EDGE}px; local WebP delivery kept >= {MIN_DELIVERY_LONG_EDGE}px and <= '
        f'{TARGET_MAX_BYTES // 1024} KB each, with zero upsampling.'
    )
    for stem, sw, sh, dw, dh, quality, size in rows:
        print(
            f'  {stem}: source {sw}x{sh} -> delivery {dw}x{dh} '
            f'Q{quality}, {size // 1024} KB'
        )

if __name__ == '__main__':
    main()
