from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path('.')
DESCRIPTOR = ROOT / 'RELEASE_R15_25.json'
VISUAL_MANIFEST = ROOT / 'VISUAL_MANIFEST_R15_7.json'


def fail(message):
    raise SystemExit('ERROR: ' + message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head() -> str:
    try:
        value = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except Exception:
        value = ''
    if not re.fullmatch(r'[0-9a-f]{40}', value):
        fail(f'cannot resolve a 40-character source commit SHA: {value or "(missing)"}')
    return value


def main():
    if len(sys.argv) != 3:
        fail('usage: write-release-metadata.py <output-root> <environment>')
    output = Path(sys.argv[1])
    environment = sys.argv[2].strip()
    if environment not in {'production', 'github-pages-mirror'}:
        fail(f'unsupported release environment: {environment}')
    if not output.is_dir():
        fail(f'output root missing: {output}')
    if not DESCRIPTOR.is_file():
        fail('release descriptor missing')
    if not VISUAL_MANIFEST.is_file():
        fail('visual manifest missing')

    descriptor = json.loads(DESCRIPTOR.read_text(encoding='utf-8'))
    visual = json.loads(VISUAL_MANIFEST.read_text(encoding='utf-8'))
    required = {
        'service': 'tongjun-overseas',
        'site_release': 'V34.152 R15.25',
        'source_branch': 'feat/v34.152-r15.25-prelaunch',
        'visual_release': 'V34.152 R15.7',
        'hero_release': 'V34.152 R15.24',
        'release_identity_version': 2,
    }
    for key, expected in required.items():
        if descriptor.get(key) != expected:
            fail(f'release descriptor mismatch for {key}: {descriptor.get(key)!r}')
    if visual.get('release') != descriptor['visual_release']:
        fail('release descriptor visual version does not match visual manifest')
    if visual.get('hero_release') != descriptor['hero_release']:
        fail('release descriptor HERO version does not match visual manifest')

    payload = {
        'service': descriptor['service'],
        'site_release': descriptor['site_release'],
        'source_branch': descriptor['source_branch'],
        'source_commit': git_head(),
        'visual_release': descriptor['visual_release'],
        'hero_release': descriptor['hero_release'],
        'visual_manifest_sha256': sha256(VISUAL_MANIFEST),
        'environment': environment,
        'canonical_origin': descriptor['canonical_origin'],
        'release_identity_version': descriptor['release_identity_version'],
    }
    target = output / '.well-known' / 'release.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(
        f"PASS: release identity written — {payload['site_release']} · {environment} · "
        f"{payload['source_commit'][:12]} · visuals {payload['visual_release']}."
    )


if __name__ == '__main__':
    main()
