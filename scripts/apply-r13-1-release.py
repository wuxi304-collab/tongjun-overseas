from pathlib import Path
import re

ROOT = Path('.')
VERSION = '20260916-r13-1-safe'
MARK = f'/assets/tongjun-logo.svg?v={VERSION}'
STYLESHEET = f'/assets/brand-v34.152-r13-1.css?v={VERSION}'
HERO = '/assets/images/logistics-stock.webp?v=20260915-r12fix2'

BRAND_HTML = (
    '<span class="tj-brand-composite">'
    f'<img class="tj-brand-mark" src="{MARK}" alt="" width="140" height="116" decoding="async" />'
    '<span class="tj-brand-copy"><strong>TONGJUN</strong><small>METAL TECH · EST. 2026</small></span>'
    '</span>'
)
FOOTER_BRAND_HTML = (
    '<span class="tj-brand-composite tj-brand-composite-footer">'
    f'<img class="tj-brand-mark" src="{MARK}" alt="" width="140" height="116" decoding="async" loading="lazy" />'
    '<span class="tj-brand-copy"><strong>TONGJUN</strong><small>METAL TECH · EST. 2026</small></span>'
    '</span>'
)

changed = []
for p in ROOT.glob('*.html'):
    if p.name == '404.html':
        continue
    s = p.read_text(encoding='utf-8')
    old = s

    # Keep corporate history factual. The experimental R13 branch introduced an unsupported 2010 date.
    s = s.replace('SINCE 2010', 'EST. 2026').replace('Since 2010', 'Est. 2026').replace('since 2010', 'est. 2026')

    # Replace the fallback text-only wordmark with the repository-native Tongjun portrait mark + type.
    s = re.sub(
        r'(<a[^>]*class="brand"[^>]*>).*?(</a>)',
        lambda m: m.group(1) + BRAND_HTML + m.group(2),
        s,
        count=1,
        flags=re.S,
    )
    s = re.sub(
        r'(<div class="footer-brand"><div class="brand[^>]*>).*?(</div>)',
        lambda m: '<div class="footer-brand"><div class="brand tj-footer-brand">' + FOOTER_BRAND_HTML + m.group(2),
        s,
        count=1,
        flags=re.S,
    )

    # Migrate stale image paths to assets that are present and validated in the release branch.
    s = s.replace(
        '/assets/images/supply-route.webp',
        '/assets/images/logistics-stock.webp?v=20260915-r12',
    )
    s = re.sub(
        r'/assets/images/hero-special-metals\.webp(?:\?[^"\']*)?',
        HERO,
        s,
    )

    if p.name == 'index.html':
        # Keep the validated R12 logistics hero until a complete next-gen binary asset exists.
        absolute_hero = 'https://exoticalloycn.com/assets/images/logistics-stock.webp'
        s = re.sub(r'<meta content="[^"]*" property="og:image"\s*/?>', f'<meta content="{absolute_hero}" property="og:image"/>', s, count=1)
        s = re.sub(r'<meta content="[^"]*" name="twitter:image"\s*/?>', f'<meta content="{absolute_hero}" name="twitter:image"/>', s, count=1)

        # Remove every image preload irrespective of attribute order, then add exactly one canonical hero preload.
        s = re.sub(r'<link\b(?=[^>]*\brel=["\']preload["\'])(?=[^>]*\bas=["\']image["\'])[^>]*>', '', s, flags=re.I)
        preload = f'<link rel="preload" as="image" href="{HERO}" fetchpriority="high">'
        s = s.replace('</head>', preload + '</head>', 1)

    # Advance CSS only. R12 JS stays unchanged for this visual-system release.
    s = re.sub(
        r'/assets/brand-v34\.152-r12\.css\?v=[^"\']+',
        STYLESHEET,
        s,
    )

    if s != old:
        p.write_text(s, encoding='utf-8')
        changed.append(p.name)

print(f'PASS: R13.1 safe brand overlay applied to {len(changed)} HTML files; stale image references migrated.')
