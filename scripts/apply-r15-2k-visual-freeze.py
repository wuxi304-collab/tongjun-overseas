from pathlib import Path
import re

ROOT = Path('.')
VERSION = '20260922-r15-24'
CONTENT_ASSETS = [
    'about-engineering.webp',
    'engineering-discussion-v2.webp',
    'engineering-review-v2.webp',
    'heavy-plate.webp',
    'hero-port-v2.webp',
    'hero-special-metals.webp',
    'hero-special-metals-r15-24.webp',
    'hero-special-metals-r15-24-4k.webp',
    'hero-special-metals-r15-24-mobile.webp',
    'invar-lng.webp',
    'invar-tooling.webp',
    'logistics-stock.webp',
    'materials-r8.webp',
    'materials-warehouse-v2.webp',
    'nickel-alloys.webp',
    'og-cover.webp',
    'precision-strip.webp',
    'quality-inspection.webp',
    'quality-lab-v2.webp',
    'quality-r8.webp',
    'resources-metal.webp',
    'standards-rfq.webp',
    'titanium-zirconium.webp',
]


def bust(text: str) -> str:
    for name in CONTENT_ASSETS:
        # Preserve absolute/relative path shape; replace any legacy image cache token.
        pattern = re.compile(rf'(assets/images/{re.escape(name)})(?:\?v=[A-Za-z0-9._-]+)?')
        text = pattern.sub(rf'\1?v={VERSION}', text)
    return text


def main():
    changed = 0
    targets = list(ROOT.glob('*.html')) + [
        ROOT / 'assets' / 'brand-v34.152-r14.css',
        ROOT / 'assets' / 'site.css',
        ROOT / 'assets' / 'brand-v34.152.js',
    ]
    for path in targets:
        if not path.is_file():
            continue
        text = path.read_text(encoding='utf-8')
        updated = bust(text)
        if path.name == 'index.html':
            if '<section class="hero">' not in updated:
                raise SystemExit('ERROR: homepage hero section missing')
            hero_section = updated.split('<section class="hero">', 1)[1].split('</section>', 1)[0]
            required = (
                'hero-picture-r15-24',
                'hero-special-metals-r15-24.webp',
                'hero-special-metals-r15-24-4k.webp',
                'hero-special-metals-r15-24-mobile.webp',
            )
            for marker in required:
                if marker not in hero_section:
                    raise SystemExit(f'ERROR: R15.24 homepage HERO contract missing: {marker}')
            if 'hero-special-metals.webp' in hero_section:
                raise SystemExit('ERROR: homepage hero regressed to legacy hero-special-metals.webp')
            if 'width="2560"' not in hero_section or 'height="1440"' not in hero_section:
                raise SystemExit('ERROR: R15.24 homepage HERO intrinsic dimensions drifted')
        if updated != text:
            path.write_text(updated, encoding='utf-8')
            changed += 1

    index = (ROOT / 'index.html').read_text(encoding='utf-8')
    hero = index.split('<section class="hero">', 1)[1].split('</section>', 1)[0]
    for name in (
        'hero-special-metals-r15-24.webp',
        'hero-special-metals-r15-24-4k.webp',
        'hero-special-metals-r15-24-mobile.webp',
    ):
        if f'{name}?v={VERSION}' not in hero:
            raise SystemExit(f'ERROR: R15.24 HERO cache key missing: {name}')
    print(f'PASS: R15.24 visual freeze overlay — cache-busted release imagery across {changed} text assets; responsive homepage HERO locked.')


if __name__ == '__main__':
    main()
