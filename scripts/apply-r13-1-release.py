from pathlib import Path
import re

ROOT = Path('.')
VERSION = '20260916-r13-1'
LOGO = f'/assets/images/logo-r13.avif?v={VERSION}'
HERO = f'/assets/images/hero-port-r13.avif?v={VERSION}'
STYLESHEET = f'/assets/brand-v34.152-r13-1.css?v={VERSION}'

LOGO_HTML = (
    f'<img class="tj-logo-img tj-logo-r13" src="{LOGO}" alt="Tongjun Metal Tech" '
    'width="1200" height="400" decoding="async" fetchpriority="high" />'
)
FOOTER_LOGO = (
    f'<img class="tj-footer-logo tj-logo-r13" src="{LOGO}" alt="Tongjun Metal Tech" '
    'width="1200" height="400" decoding="async" loading="lazy" />'
)
HERO_HTML = (
    f'<img class="hero-bg-r6 hero-bg-r13" src="{HERO}" '
    'alt="Special-metal coils prepared for international delivery at an industrial port" '
    'width="1280" height="720" decoding="async" fetchpriority="high" />'
)

changed = []
for p in ROOT.glob('*.html'):
    if p.name == '404.html':
        continue
    s = p.read_text(encoding='utf-8')
    old = s

    # Corporate history is kept factual. R13 experimental branches used an unsupported 2010 date.
    s = s.replace('SINCE 2010', 'EST. 2026').replace('Since 2010', 'Est. 2026').replace('since 2010', 'est. 2026')

    s = re.sub(
        r'(<a[^>]*class="brand"[^>]*>).*?(</a>)',
        lambda m: m.group(1) + LOGO_HTML + m.group(2),
        s,
        count=1,
        flags=re.S,
    )
    s = re.sub(
        r'(<div class="footer-brand"><div class="brand[^>]*>).*?(</div>)',
        lambda m: '<div class="footer-brand"><div class="brand tj-footer-brand">' + FOOTER_LOGO + m.group(2),
        s,
        count=1,
        flags=re.S,
    )

    # Promote only the two R13 assets that actually exist and have been materialized.
    if p.name == 'index.html':
        if re.search(r'<img class="hero-bg-r6[^\"]*"[^>]*>', s):
            s = re.sub(r'<img class="hero-bg-r6[^\"]*"[^>]*>', HERO_HTML, s, count=1)
        else:
            s = s.replace('<section class="hero">', '<section class="hero">' + HERO_HTML, 1)

        absolute_hero = 'https://exoticalloycn.com/assets/images/hero-port-r13.avif'
        s = re.sub(r'<meta content="[^"]*" property="og:image"\s*/?>', f'<meta content="{absolute_hero}" property="og:image"/>', s, count=1)
        s = re.sub(r'<meta content="[^"]*" name="twitter:image"\s*/?>', f'<meta content="{absolute_hero}" name="twitter:image"/>', s, count=1)

        # Remove stale hero preloads and add exactly one R13 preload.
        s = re.sub(r'<link rel="preload" as="image" href="/assets/images/(?:hero-port-v2\.webp|logistics-stock\.webp)[^"]*" fetchpriority="high">', '', s)
        r13_preload = f'<link rel="preload" as="image" href="{HERO}" fetchpriority="high">'
        if r13_preload not in s:
            s = s.replace('</head>', r13_preload + '</head>', 1)

    # Advance only the brand stylesheet. R12 JS remains unchanged for this imagery-only release.
    s = re.sub(
        r'/assets/brand-v34\.152-r12\.css\?v=[^"\']+',
        STYLESHEET,
        s,
    )

    if s != old:
        p.write_text(s, encoding='utf-8')
        changed.append(p.name)

print(f'PASS: R13.1 validated logo + homepage hero overlay applied to {len(changed)} HTML files.')
