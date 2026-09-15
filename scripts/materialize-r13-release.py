from pathlib import Path
import base64

ROOT = Path('.')
OUT = ROOT / 'assets' / 'images'
OUT.mkdir(parents=True, exist_ok=True)


def decode_payload(parts, filename):
    if not parts:
        raise SystemExit(f'ERROR: no source chunks found for {filename}')
    payload = ''.join(p.read_text(encoding='utf-8').strip() for p in parts)
    try:
        raw = base64.b64decode(payload, validate=True)
    except Exception as exc:
        raise SystemExit(f'ERROR: invalid base64 for {filename}: {exc}')
    if len(raw) < 1024:
        raise SystemExit(f'ERROR: {filename} is unexpectedly small ({len(raw)} bytes)')
    if b'ftypavif' not in raw[:64]:
        raise SystemExit(f'ERROR: {filename} is not an AVIF payload')
    target = OUT / filename
    target.write_bytes(raw)
    print(f'PASS: materialized {target} ({len(raw)} bytes) from {len(parts)} source file(s)')

# The trusted deploy upload contains a complete, padded AVIF logo in one base64 file.
# Do not concatenate it with later experimental fragments from the R13 upload attempts.
decode_payload(
    [ROOT / '.sync' / 'r13-logo-release' / 'logo-r13.full.b64'],
    'logo-r13.avif',
)

# The hero was intentionally split as one continuous base64 stream.
hero_parts = sorted((ROOT / '.sync' / 'r13-release').glob('hero-port-r13.part*'))
decode_payload(hero_parts, 'hero-port-r13.avif')
