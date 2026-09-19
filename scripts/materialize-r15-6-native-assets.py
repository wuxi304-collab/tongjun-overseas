from pathlib import Path
from urllib.request import Request, urlopen
import time

ROOT = Path('.')
IMAGES = ROOT / 'assets' / 'images'
VERSION = '20260919-r15-6'
MIN_LONG_EDGE = 3000
MIN_BYTES = 350_000

# Fixed, high-resolution real industrial photographs. The website ships local
# copies, so the browser never depends on Pexels at runtime.
SOURCES = {
    'r15-6-materials.jpg': 'https://images.pexels.com/photos/8940223/pexels-photo-8940223.jpeg?cs=srgb&fm=jpg',
    'r15-6-quality.jpg': 'https://images.pexels.com/photos/32845682/pexels-photo-32845682.jpeg?cs=srgb&fm=jpg',
    'r15-6-process.jpg': 'https://images.pexels.com/photos/5411674/pexels-photo-5411674.jpeg?cs=srgb&fm=jpg',
    'r15-6-precision.jpg': 'https://images.pexels.com/photos/8972008/pexels-photo-8972008.jpeg?cs=srgb&fm=jpg',
    'r15-6-heavy.jpg': 'https://images.pexels.com/photos/8973680/pexels-photo-8973680.jpeg?cs=srgb&fm=jpg',
    'r15-6-lng.jpg': 'https://images.pexels.com/photos/36778676/pexels-photo-36778676.jpeg?cs=srgb&fm=jpg',
    'r15-6-tooling.jpg': 'https://images.pexels.com/photos/10406128/pexels-photo-10406128.jpeg?cs=srgb&fm=jpg',
    'r15-6-titanium.jpg': 'https://images.pexels.com/photos/32845684/pexels-photo-32845684.jpeg?cs=tinysrgb&w=6129&fit=max&fm=jpg',
    'r15-6-resources.jpg': 'https://images.pexels.com/photos/3861938/pexels-photo-3861938.jpeg?cs=srgb&fm=jpg',
    'r15-6-about.jpg': 'https://images.pexels.com/photos/34054482/pexels-photo-34054482.jpeg?cs=srgb&fm=jpg',
}

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
        if marker in {
            0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
            0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF,
        }:
            if seglen < 7:
                raise ValueError('invalid SOF segment')
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
                'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            })
            with urlopen(req, timeout=30) as response:
                data = response.read()
            return data
        except Exception as exc:
            last = exc
            if attempt < 2:
                time.sleep(1 + attempt)
    raise SystemExit(f'ERROR: image download failed after retries: {url} ({last})')

def main():
    IMAGES.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, url in SOURCES.items():
        data = fetch(url)
        if len(data) < MIN_BYTES:
            raise SystemExit(f'ERROR: {name} source is unexpectedly small: {len(data)} bytes')
        try:
            w, h = jpeg_dimensions(data)
        except Exception as exc:
            raise SystemExit(f'ERROR: {name} is not a valid JPEG: {exc}')
        if max(w, h) < MIN_LONG_EDGE:
            raise SystemExit(f'ERROR: {name} source below native visual gate: {w}x{h}')
        target = IMAGES / name
        target.write_bytes(data)
        rows.append((name, w, h, len(data)))
    print(f'PASS: R15.6 native visual materialization — {len(rows)} real-photo assets downloaded locally; all source long edges >= {MIN_LONG_EDGE}px.')
    for name, w, h, size in rows:
        print(f'  {name}: {w}x{h}, {size} bytes')

if __name__ == '__main__':
    main()
