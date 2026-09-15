from pathlib import Path
import re

ROOT = Path('.')
VERSION = '20260915-r13'
LOGO = f'/assets/images/logo-r13.avif?v={VERSION}'
HERO = f'/assets/images/hero-port-r13.avif?v={VERSION}'
QUALITY = f'/assets/images/quality-lab-r13.avif?v={VERSION}'
ENGINEERING = f'/assets/images/engineering-team-r13.avif?v={VERSION}'
TECHNICAL = f'/assets/images/technical-lab-r13.avif?v={VERSION}'

LOGO_HTML = f'<img class="tj-logo-img tj-logo-r13" src="{LOGO}" alt="Tongjun Metal Tech · Since 2010" width="1200" height="400" decoding="async" fetchpriority="high" />'
FOOTER_LOGO = f'<img class="tj-footer-logo tj-logo-r13" src="{LOGO}" alt="Tongjun Metal Tech · Since 2010" width="1200" height="400" decoding="async" loading="lazy" />'
HERO_HTML = f'<img class="hero-bg-r6 hero-bg-r13" src="{HERO}" alt="Tongjun Metal Tech special-metal coils prepared for international delivery at an industrial port" width="1280" height="720" decoding="async" fetchpriority="high" />'

PEOPLE_ASSET_REPLACEMENTS = {
    '/assets/images/engineering-discussion-v2.webp': ENGINEERING,
    '/assets/images/engineering-review-v2.webp': ENGINEERING,
    '/assets/images/about-engineering.webp': ENGINEERING,
    '/assets/images/quality-lab-v2.webp': QUALITY,
    '/assets/images/quality-inspection.webp': QUALITY,
    '/assets/images/traceability-pmi.webp': QUALITY,
}

PAGE_VISUALS = {
    'quality.html': (QUALITY, 'Inspection · traceability · release evidence', 'Tongjun Metal Tech engineer performing precision material inspection'),
    'technical-data.html': (TECHNICAL, 'Material data · verification · controlled reference', 'Tongjun Metal Tech materials engineer reviewing metallurgical evidence and technical data'),
    'about.html': (ENGINEERING, 'Requirement review · source role · evidence boundary', 'Tongjun Metal Tech engineering team reviewing a special-metals sourcing requirement'),
    'rfq.html': (ENGINEERING, 'Requirement review · route control · buyer release', 'Tongjun Metal Tech engineering team reviewing a controlled special-metals requirement'),
    'problem-order.html': (ENGINEERING, 'Problem order · technical recovery · evidence review', 'Tongjun Metal Tech engineering review of a special-metals order requiring technical recovery'),
}

def replace_visual(s: str, page_name: str) -> str:
    if page_name not in PAGE_VISUALS:
        return s
    img, label, alt = PAGE_VISUALS[page_name]
    visual = ('<section class="visual-band page-specific-visual"><div class="wrap"><div class="visual-frame">'
              f'<img alt="{alt}" decoding="async" loading="eager" fetchpriority="high" src="{img}" width="1280" height="720"/>'
              f'<span class="visual-label">{label}</span></div></div></section>')
    if re.search(r'<section class="visual-band[^>]*>.*?</section>', s, flags=re.S):
        s = re.sub(r'<section class="visual-band[^>]*>.*?</section>', visual, s, count=1, flags=re.S)
    absolute = 'https://exoticalloycn.com' + img.split('?')[0]
    s = re.sub(r'<meta content="[^"]*" property="og:image"\s*/?>', f'<meta content="{absolute}" property="og:image"/>', s, count=1)
    s = re.sub(r'<meta content="[^"]*" name="twitter:image"\s*/?>', f'<meta content="{absolute}" name="twitter:image"/>', s, count=1)
    return s

changed = []
for p in ROOT.glob('*.html'):
    if p.name == '404.html':
        continue
    s = p.read_text(encoding='utf-8')
    old = s
    s = s.replace('EST. 2026', 'SINCE 2010').replace('Est. 2026', 'Since 2010').replace('est. 2026', 'since 2010')
    s = re.sub(r'(<a[^>]*class="brand"[^>]*>).*?(</a>)', lambda m: m.group(1) + LOGO_HTML + m.group(2), s, count=1, flags=re.S)
    s = re.sub(r'(<div class="footer-brand"><div class="brand[^>]*>).*?(</div>)', lambda m: '<div class="footer-brand"><div class="brand tj-footer-brand">' + FOOTER_LOGO + m.group(2), s, count=1, flags=re.S)
    for old_path, new_path in PEOPLE_ASSET_REPLACEMENTS.items():
        s = re.sub(re.escape(old_path) + r'(?:\?[^\"\']*)?', new_path, s)
    if p.name == 'index.html':
        if re.search(r'<img class="hero-bg-r6[^\"]*"[^>]*>', s):
            s = re.sub(r'<img class="hero-bg-r6[^\"]*"[^>]*>', HERO_HTML, s, count=1)
        else:
            s = s.replace('<section class="hero">', '<section class="hero">' + HERO_HTML, 1)
        s = re.sub(r'<link rel="preload" as="image" href="[^"]*" fetchpriority="high">', '', s)
        s = s.replace('</head>', f'<link rel="preload" as="image" href="{HERO}" fetchpriority="high"></head>', 1)
    s = replace_visual(s, p.name)
    if s != old:
        p.write_text(s, encoding='utf-8')
        changed.append(p.name)
print(f'PASS: R13 AVIF logo, SINCE 2010 brand date, hero and branded-workwear imagery applied to {len(changed)} HTML files.')
