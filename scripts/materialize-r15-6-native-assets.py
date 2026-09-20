from pathlib import Path
from urllib.request import Request, urlopen
import hashlib
import json
import shutil
import subprocess
import time

ROOT = Path('.')
IMAGES = ROOT / 'assets' / 'images'
CACHE = ROOT / '.sync' / 'r15-6-native-src'
MANIFEST = ROOT / 'VISUAL_MANIFEST_R15_7.json'
VERSION = '20260920-r15-6b'
MIN_SOURCE_LONG_EDGE = 3000
MIN_SOURCE_BYTES = 350_000
MIN_DELIVERY_LONG_EDGE = 2048
TARGET_MAX_BYTES = 590 * 1024

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


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def webp_dimensions(path: Path):
    data = path.read_bytes()
    if len(data) < 30 or data[:4] != b'RIFF' or data[8:12] != b'WEBP':
        raise SystemExit(f'ERROR: invalid WebP: {path}')
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
    raise SystemExit(f'ERROR: WebP dimensions unavailable: {path}')


def load_manifest():
    if not MANIFEST.is_file():
        raise SystemExit('ERROR: R15.7 visual manifest missing')
    doc = json.loads(MANIFEST.read_text(encoding='utf-8'))
    if doc.get('release') != 'V34.152 R15.7':
        raise SystemExit('ERROR: unexpected visual manifest release')
    return doc


def validate_frozen_asset(path: Path, meta: dict):
    if not path.is_file():
        return False
    dims = webp_dimensions(path)
    actual_sha = sha256(path)
    if dims != (meta['width'], meta['height']):
        raise SystemExit(f'ERROR: frozen visual dimensions drifted: {path.name} {dims}')
    if path.stat().st_size != meta['bytes']:
        raise SystemExit(f'ERROR: frozen visual byte size drifted: {path.name}')
    if actual_sha != meta['sha256']:
        raise SystemExit(f'ERROR: frozen visual SHA256 drifted: {path.name} {actual_sha}')
    return True


def command(name):
    resolved = shutil.which(name)
    if not resolved:
        raise SystemExit(f'ERROR: required binary missing for one-time R15.7 freeze: {name}')
    return resolved


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
                'User-Agent': 'TongjunVisualBuild/15.7 (+https://exoticalloycn.com)',
                'Accept': 'image/jpeg,image/*,*/*;q=0.8',
            })
            with urlopen(req, timeout=30) as response:
                return response.read()
        except Exception as exc:
            last = exc
            if attempt < 2:
                time.sleep(1 + attempt)
    raise SystemExit(f'ERROR: image download failed after retries: {url} ({last})')


def ff_dimensions(ffprobe: str, path: Path):
    result = subprocess.run([
        ffprobe, '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height', '-of', 'csv=s=x:p=0', str(path)
    ], check=True, capture_output=True, text=True)
    w, h = result.stdout.strip().split('x')
    return int(w), int(h)


def encode_derivative(ffmpeg: str, ffprobe: str, source: Path, target: Path, source_width: int, source_height: int):
    attempts = [
        (2560, 1440, 84), (2560, 1440, 80), (2560, 1440, 76),
        (2304, 1296, 82), (2304, 1296, 78), (2304, 1296, 74),
        (2048, 1152, 82), (2048, 1152, 78), (2048, 1152, 74), (2048, 1152, 70),
    ]
    tmp = target.with_suffix('.tmp.webp')
    for width, height, quality in attempts:
        if width > source_width or height > source_height:
            continue
        if tmp.exists():
            tmp.unlink()
        vf = f'scale={width}:{height}:force_original_aspect_ratio=increase:flags=lanczos,crop={width}:{height}'
        subprocess.run([
            ffmpeg, '-hide_banner', '-loglevel', 'error', '-i', str(source), '-frames:v', '1',
            '-vf', vf, '-c:v', 'libwebp', '-preset', 'picture', '-quality', str(quality),
            '-compression_level', '6', '-y', str(tmp)
        ], check=True)
        size = tmp.stat().st_size
        w, h = ff_dimensions(ffprobe, tmp)
        if max(w, h) >= MIN_DELIVERY_LONG_EDGE and size <= TARGET_MAX_BYTES:
            tmp.replace(target)
            return
    raise SystemExit(f'ERROR: cannot derive compliant visual for {target.name}')


def main():
    manifest = load_manifest()
    expected = manifest['assets']

    present = [validate_frozen_asset(IMAGES / name, meta) for name, meta in expected.items()]
    if all(present):
        total = sum((IMAGES / name).stat().st_size for name in expected)
        print(
            f'PASS: R15.7 frozen visual assets already present — {len(expected)} binaries, '
            f'aggregate {total // 1024} KB; no network or image encoder used.'
        )
        return
    if any(present):
        raise SystemExit('ERROR: partial R15.7 frozen visual set detected; refusing silent rebuild')

    ffmpeg = command('ffmpeg')
    ffprobe = command('ffprobe')
    CACHE.mkdir(parents=True, exist_ok=True)
    IMAGES.mkdir(parents=True, exist_ok=True)

    for stem, url in SOURCES.items():
        name = f'{stem}.webp'
        meta = expected[name]
        data = fetch(url)
        if len(data) < MIN_SOURCE_BYTES:
            raise SystemExit(f'ERROR: {stem} source unexpectedly small')
        sw, sh = jpeg_dimensions(data)
        if max(sw, sh) < MIN_SOURCE_LONG_EDGE:
            raise SystemExit(f'ERROR: {stem} source below native gate: {sw}x{sh}')
        source = CACHE / f'{stem}.jpg'
        source.write_bytes(data)
        target = IMAGES / name
        encode_derivative(ffmpeg, ffprobe, source, target, sw, sh)
        validate_frozen_asset(target, meta)

    print(
        f'PASS: R15.7 one-time visual materialization reproduced all {len(expected)} pinned binaries exactly; '
        'ready to freeze into the release branch.'
    )


if __name__ == '__main__':
    main()
