from pathlib import Path
import re

ROOT = Path('.')
VERSION = '20260920-r15-6b'

MAP = {
    'about-engineering.webp': 'r15-6-about.webp',
    'engineering-discussion-v2.webp': 'r15-6-about.webp',
    'engineering-review-v2.webp': 'r15-6-quality.webp',
    'heavy-plate.webp': 'r15-6-heavy.webp',
    'hero-port-v2.webp': 'r15-6-materials.webp',
    'hero-special-metals.webp': 'r15-6-materials.webp',
    'invar-lng.webp': 'r15-6-lng.webp',
    'invar-tooling.webp': 'r15-6-tooling.webp',
    # Homepage logistics-stock.webp is intentionally NOT replaced.
    'materials-r8.webp': 'r15-6-materials.webp',
    'materials-warehouse-v2.webp': 'r15-6-materials.webp',
    'nickel-alloys.webp': 'r15-6-process.webp',
    'og-cover.webp': 'r15-6-materials.webp',
    'precision-strip.webp': 'r15-6-precision.webp',
    'quality-inspection.webp': 'r15-6-quality.webp',
    'quality-lab-v2.webp': 'r15-6-quality.webp',
    'quality-r8.webp': 'r15-6-quality.webp',
    'resources-metal.webp': 'r15-6-resources.webp',
    'standards-rfq.webp': 'r15-6-resources.webp',
    'titanium-zirconium.webp': 'r15-6-titanium.webp',
}

TARGETS = [
    *ROOT.glob('*.html'),
    ROOT / 'assets' / 'brand-v34.152-r14.css',
    ROOT / 'assets' / 'site.css',
    ROOT / 'assets' / 'brand-v34.152.js',
]

def rewrite(text: str) -> str:
    for old, new in MAP.items():
        pattern = re.compile(rf'assets/images/{re.escape(old)}(?:\?v=[A-Za-z0-9._-]+)?')
        text = pattern.sub(f'assets/images/{new}?v={VERSION}', text)
    return text

def main():
    changed = 0
    for path in TARGETS:
        if not path.is_file():
            continue
        text = path.read_text(encoding='utf-8')
        updated = rewrite(text)
        if updated != text:
            path.write_text(updated, encoding='utf-8')
            changed += 1

    index = (ROOT / 'index.html').read_text(encoding='utf-8')
    if '<section class="hero">' not in index:
        raise SystemExit('ERROR: homepage hero section missing')
    hero = index.split('<section class="hero">', 1)[1].split('</section>', 1)[0]
    if 'logistics-stock.webp' not in hero:
        raise SystemExit('ERROR: frozen homepage hero path changed')
    if 'r15-6-' in hero:
        raise SystemExit('ERROR: R15.6 attempted to replace the frozen homepage hero')

    legacy_refs = []
    for path in TARGETS:
        if not path.is_file():
            continue
        text = path.read_text(encoding='utf-8')
        for old in MAP:
            if f'assets/images/{old}' in text:
                legacy_refs.append((str(path), old))
    if legacy_refs:
        raise SystemExit(f'ERROR: legacy soft visual reference(s) remain after R15.6 rewrite: {legacy_refs[:20]}')

    print(f'PASS: R15.6 native visual overlay — {changed} text assets updated; homepage hero kept frozen; all mapped content visuals now point to optimized high-resolution photography.')

if __name__ == '__main__':
    main()
