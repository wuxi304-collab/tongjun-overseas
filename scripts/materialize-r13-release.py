from pathlib import Path
import base64

ROOT = Path('.')
SRC = ROOT / '.sync' / 'r13-release'
OUT = ROOT / 'assets' / 'images'
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = {
    'logo-r13.avif': 'logo-r13.part*',
    'hero-port-r13.avif': 'hero-port-r13.part*',
}

for filename, pattern in TARGETS.items():
    parts = sorted(SRC.glob(pattern))
    if not parts:
        raise SystemExit(f'ERROR: no chunks found for {filename}')
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
    print(f'PASS: materialized {target} ({len(raw)} bytes) from {len(parts)} chunks')
