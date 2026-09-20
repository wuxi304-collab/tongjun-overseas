from pathlib import Path
import hashlib
import shutil
import subprocess

ROOT = Path('.')
IMAGES = ROOT / 'assets' / 'images'
MIN_LONG_EDGE = 2048
LEGACY_HERO_SHA256 = '89961367b48e0d8a16df57739c34c4a572e4608968a6a45efcc94cc515327900'
FROZEN_HERO_SHA256 = '8692b9d723a0c27dd6776e38c7fb33c3179eaaafafaf7e13637591a857b32a14'
FROZEN_SIZE = (2048, 1154)


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
            w = 1 + int.from_bytes(payload[4:7], 'little')
            h = 1 + int.from_bytes(payload[7:10], 'little')
            return w, h
        if fourcc == b'VP8 ' and len(payload) >= 10 and payload[3:6] == b'\x9d\x01\x2a':
            w = int.from_bytes(payload[6:8], 'little') & 0x3fff
            h = int.from_bytes(payload[8:10], 'little') & 0x3fff
            return w, h
        if fourcc == b'VP8L' and len(payload) >= 5 and payload[0] == 0x2f:
            bits = int.from_bytes(payload[1:5], 'little')
            return (bits & 0x3fff) + 1, ((bits >> 14) & 0x3fff) + 1
        pos += 8 + size + (size & 1)
    raise SystemExit(f'ERROR: WebP dimensions unavailable: {path}')


def main():
    hero = IMAGES / 'logistics-stock.webp'
    if not hero.is_file():
        raise SystemExit('ERROR: frozen homepage hero missing')

    actual = sha256(hero)
    if actual == FROZEN_HERO_SHA256:
        dims = webp_dimensions(hero)
        if dims != FROZEN_SIZE:
            raise SystemExit(f'ERROR: frozen hero dimensions changed: {dims}')
        print(f'PASS: R15.7 frozen hero already materialized — {dims[0]}x{dims[1]}, SHA256 locked.')
        return

    if actual != LEGACY_HERO_SHA256:
        raise SystemExit(
            'ERROR: homepage hero bytes changed without approval. '
            f'Expected legacy {LEGACY_HERO_SHA256} or frozen {FROZEN_HERO_SHA256}, found {actual}.'
        )

    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        raise SystemExit('ERROR: ffmpeg required only for the one-time R15.7 hero freeze')

    tmp = hero.with_name('logistics-stock.r15-7-freeze.webp')
    subprocess.run([
        ffmpeg, '-hide_banner', '-loglevel', 'error', '-err_detect', 'ignore_err',
        '-i', str(hero), '-frames:v', '1',
        '-vf', "scale='if(gte(iw,ih),2048,-2)':'if(gte(iw,ih),-2,2048)':flags=lanczos,unsharp=5:5:0.35:5:5:0.0",
        '-c:v', 'libwebp', '-quality', '88', '-compression_level', '6',
        '-y', str(tmp),
    ], check=True)
    tmp.replace(hero)

    dims = webp_dimensions(hero)
    frozen = sha256(hero)
    if dims != FROZEN_SIZE or frozen != FROZEN_HERO_SHA256:
        raise SystemExit(
            f'ERROR: one-time hero freeze is not deterministic: dims={dims}, sha256={frozen}'
        )
    print(f'PASS: R15.7 hero frozen deterministically — {dims[0]}x{dims[1]}, SHA256 {frozen}.')


if __name__ == '__main__':
    main()
