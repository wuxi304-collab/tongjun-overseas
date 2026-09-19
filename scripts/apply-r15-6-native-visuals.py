from pathlib import Path
import re

ROOT = Path('.')
VERSION = '20260919-r15-6'

MAP = {
    'about-engineering.webp': 'r15-6-about.jpg',
    'engineering-discussion-v2.webp': 'r15-6-about.jpg',
    'engineering-review-v2.webp': 'r15-6-quality.jpg',
    'heavy-plate.webp': 'r15-6-heavy.jpg',
    'hero-port-v2.webp': 'r15-6-materials.jpg',
    'hero-special-metals.webp': 'r15-6-materials.jpg',
    'invar-lng.webp': 'r15-6-lng.jpg',
    'invar-tooling.webp': 'r15-6-tooling.jpg',
    # Homepage logistics-stock.webp is intentionally NOT replaced.
    'materials-r8.webp': 'r15-6-materials.jpg',
    'materials-warehouse-v2.webp': 'r15-6-materials.jpg',
    'nickel-alloys.webp': 'r15-6-process.jpg',
    'og-cover.webp': 'r15-6-materials.jpg',
    'precision-strip.webp': 'r15-6-precision.jpg',
    'quality-inspection.webp': 'r15-6-quality.jpg',
    'quality-lab-v2.webp': 'r15-6-quality.jpg',
    'quality-r8.webp': 'r15-6-quality.jpg',
    'resources-metal.webp': 'r15-6-resources.jpg',
    'standards-rfq.webp': 'r15-6-resources.jpg',
    'titanium-zirconium.webp': 'r15-6-titanium.jpg',
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

    print(f'PASS: R15.6 native visual overlay — {changed} text assets updated; homepage hero kept frozen; all mapped content visuals now point to native high-resolution photography.')

if __name__ == '__main__':
    main()
