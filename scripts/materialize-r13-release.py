from pathlib import Path
import base64

ROOT = Path('.')
OUT = ROOT / 'assets' / 'images'
OUT.mkdir(parents=True, exist_ok=True)


def is_complete_avif(raw: bytes) -> bool:
    """Validate the top-level ISO-BMFF box chain, not just the AVIF magic bytes."""
    if len(raw) < 1024 or b'ftypavif' not in raw[:64]:
        return False

    pos = 0
    box_types = []
    total = len(raw)
    while pos < total:
        if pos + 8 > total:
            return False
        size = int.from_bytes(raw[pos:pos + 4], 'big')
        box_type = raw[pos + 4:pos + 8]
        header_size = 8

        if size == 1:
            if pos + 16 > total:
                return False
            size = int.from_bytes(raw[pos + 8:pos + 16], 'big')
            header_size = 16
        elif size == 0:
            size = total - pos

        if size < header_size or pos + size > total:
            return False

        box_types.append(box_type)
        pos += size

    return (
        pos == total
        and b'ftyp' in box_types
        and b'meta' in box_types
        and b'mdat' in box_types
    )


def clean_text(path: Path) -> str:
    return ''.join(path.read_text(encoding='utf-8').split())


def candidate_streams(parts):
    texts = [clean_text(p) for p in parts]

    # Strategy A: chunks are slices of one continuous base64 stream.
    try:
        yield 'joined-base64', base64.b64decode(''.join(texts), validate=True)
    except Exception as exc:
        print(f'INFO: joined-base64 rejected: {exc}')

    # Strategy B: each upload chunk is an independently padded base64 payload
    # representing a consecutive binary segment.
    try:
        decoded = [base64.b64decode(text, validate=True) for text in texts]
        yield 'per-part-base64', b''.join(decoded)
    except Exception as exc:
        print(f'INFO: per-part-base64 rejected: {exc}')


def decode_payload(parts, filename):
    parts = list(parts)
    if not parts:
        raise SystemExit(f'ERROR: no source chunks found for {filename}')

    tried = []
    for strategy, raw in candidate_streams(parts):
        tried.append(f'{strategy}:{len(raw)}')
        if not is_complete_avif(raw):
            print(f'INFO: {filename} candidate {strategy} decoded but failed AVIF box validation ({len(raw)} bytes)')
            continue

        target = OUT / filename
        target.write_bytes(raw)
        print(
            f'PASS: materialized {target} ({len(raw)} bytes) '
            f'with {strategy} from {len(parts)} source file(s)'
        )
        return

    raise SystemExit(
        f"ERROR: no structurally complete AVIF reconstruction for {filename}; "
        f"candidates={','.join(tried) or 'none'}"
    )


# The trusted deploy upload contains a complete, padded AVIF logo in one base64 file.
# Do not concatenate it with later experimental fragments from the R13 upload attempts.
decode_payload(
    [ROOT / '.sync' / 'r13-logo-release' / 'logo-r13.full.b64'],
    'logo-r13.avif',
)

# R13 hero went through more than one upload path. Accept only a reconstruction
# whose entire ISO-BMFF box chain closes exactly at EOF.
hero_parts = sorted((ROOT / '.sync' / 'r13-release').glob('hero-port-r13.part*'))
decode_payload(hero_parts, 'hero-port-r13.avif')
