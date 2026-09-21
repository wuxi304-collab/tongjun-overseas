from pathlib import Path
import re
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
VERSION = '20260921-r15-16'


def fail(message):
    raise SystemExit('ERROR: ' + message)


def main():
    js_path = ROOT / 'assets' / 'brand-v34.152.js'
    if not js_path.is_file():
        fail('brand runtime missing')
    js = js_path.read_text(encoding='utf-8')

    required = (
        "const BRAND_MAIN='TONGJUN'",
        "const BRAND_SUB='METAL TECH · EST. 2026'",
        'function normalizeBrandLockup(root)',
        "root.querySelector(':scope > .tj-brand-composite')",
        "composite.querySelector('.tj-brand-copy strong')",
        "composite.querySelector('.tj-brand-copy small')",
        "span:last-child:not(.tj-brand-composite)",
    )
    for marker in required:
        if marker not in js:
            fail(f'R15.16 runtime brand marker missing: {marker}')

    forbidden = (
        'hero-port-r7.svg',
        "'logistics-stock.webp':",
        "'hero-special-metals.webp':",
        'label.textContent=BRAND;',
        "const BRAND='TONGJUN METAL TECH'",
    )
    for marker in forbidden:
        if marker in js:
            fail(f'R15.16 destructive/hero-swap runtime marker returned: {marker}')

    htmls = sorted(ROOT.glob('*.html'))
    if len(htmls) != 50:
        fail(f'expected 50 root HTML pages, found {len(htmls)}')

    bad_cache = []
    missing_brand = []
    for page in htmls:
        text = page.read_text(encoding='utf-8')
        refs = re.findall(r'assets/brand-v34\.152\.js(?:\?v=([A-Za-z0-9._-]+))?', text)
        expected_refs = [] if page.name == '404.html' else [VERSION]
        if refs != expected_refs:
            bad_cache.append((page.name, refs))

        if page.name != '404.html':
            header = text.split('<header',1)[1].split('</header>',1)[0] if '<header' in text and '</header>' in text else ''
            if header.count('tj-brand-composite') < 1 or 'assets/tongjun-logo.svg' not in header:
                missing_brand.append((page.name, 'header'))
        footer = text.split('<footer',1)[1].split('</footer>',1)[0] if '<footer' in text and '</footer>' in text else ''
        if footer.count('tj-brand-composite') < 1 or 'assets/tongjun-logo.svg' not in footer:
            missing_brand.append((page.name, 'footer'))

    if bad_cache:
        fail(f'R15.16 brand runtime cache key mismatch: {bad_cache[:10]}')
    if missing_brand:
        fail(f'R15.16 live vector brand shell missing: {missing_brand[:10]}')

    index = (ROOT / 'index.html').read_text(encoding='utf-8')
    hero = index.split('<section class="hero">',1)[1].split('</section>',1)[0]
    if hero.count('logistics-stock.webp') != 1:
        fail('R15.16 frozen homepage hero reference changed')

    print(
        'PASS: R15.16 runtime brand integrity — vector lockup survives runtime normalization on all '
        'applicable headers/footers, destructive composite text replacement is absent, hero fallback '
        f'swap is disabled, and all 49 runtime-bearing pages use cache key {VERSION}; 404 remains script-free.'
    )


if __name__ == '__main__':
    main()
