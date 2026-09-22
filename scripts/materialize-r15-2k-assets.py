from pathlib import Path
import hashlib

ROOT = Path('.')
IMAGES = ROOT / 'assets' / 'images'
HERO_FILE = 'hero-special-metals-r15-24.webp'
FROZEN_HERO_SHA256 = '883b9e4a14dc839a0f2516694a4826bf0094f30d8a2811b8f83719b2b2e5f45b'
FROZEN_SIZE = (2560, 1440)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def main():
    hero = IMAGES / HERO_FILE
    if not hero.is_file():
        raise SystemExit(f'ERROR: R15.24 homepage hero missing: {HERO_FILE}')
    dims = webp_dimensions(hero)
    digest = sha256(hero)
    if dims != FROZEN_SIZE:
        raise SystemExit(f'ERROR: R15.24 homepage hero dimensions drifted: {dims}')
    if digest != FROZEN_HERO_SHA256:
        raise SystemExit(f'ERROR: R15.24 homepage hero SHA256 drifted: {digest}')
    print(f'PASS: R15.24 homepage hero frozen — {dims[0]}x{dims[1]}, SHA256 locked.')


if __name__ == '__main__':
    main()
