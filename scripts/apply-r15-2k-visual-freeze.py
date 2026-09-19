from pathlib import Path
import re

ROOT = Path('.')
VERSION = '20260919-r15-5'
CONTENT_ASSETS = [
    'about-engineering.webp',
    'engineering-discussion-v2.webp',
    'engineering-review-v2.webp',
    'heavy-plate.webp',
    'hero-port-v2.webp',
    'hero-special-metals.webp',
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
            # The R15.4 homepage visual remains frozen: no silent hero substitution.
            if '<section class="hero">' not in updated:
                raise SystemExit('ERROR: homepage hero section missing')
            hero_section = updated.split('<section class="hero">', 1)[1].split('</section>', 1)[0]
            if 'hero-special-metals.webp' in hero_section:
                raise SystemExit('ERROR: homepage hero regressed to hero-special-metals.webp')
            if hero_section.count('logistics-stock.webp') < 1:
                raise SystemExit('ERROR: frozen homepage hero logistics-stock.webp is missing')
            # Intrinsic ratio now matches the generated 2K hero asset.
            hero_section_new = re.sub(
                r'(class="hero-bg-r6"[^>]*\bwidth=")\d+("[^>]*\bheight=")\d+(")',
                r'\g<1>2048\g<2>1154\g<3>',
                hero_section,
                count=1,
            )
            updated = updated.replace(hero_section, hero_section_new, 1)
        if updated != text:
            path.write_text(updated, encoding='utf-8')
            changed += 1

    index = (ROOT / 'index.html').read_text(encoding='utf-8')
    hero = index.split('<section class="hero">', 1)[1].split('</section>', 1)[0]
    if f'logistics-stock.webp?v={VERSION}' not in hero:
        raise SystemExit('ERROR: R15.5 frozen hero cache key missing')
    print(f'PASS: R15.5 visual freeze overlay — cache-busted 2K imagery across {changed} text assets; homepage hero path frozen.')


if __name__ == '__main__':
    main()
