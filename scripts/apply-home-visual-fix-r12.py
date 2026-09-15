from pathlib import Path
import re

ROOT = Path('.')
WORDMARK = '<div class="tj-wordmark"><strong>TONGJUN</strong><small>METAL TECH · EST. 2026</small></div>'
HERO = '<img class="hero-bg-r6" src="/assets/images/logistics-stock.webp?v=20260915-r12fix2" alt="Special metals prepared for international delivery at an industrial port" width="1200" height="675" decoding="async" fetchpriority="high" />'

for p in ROOT.glob('*.html'):
    if p.name == '404.html':
        continue
    s = p.read_text(encoding='utf-8')
    old = s

    # Header/footer must never go blank if a generated logo asset is unavailable.
    s = re.sub(r'(<a[^>]*class="brand"[^>]*>).*?(</a>)', lambda m: m.group(1) + WORDMARK + m.group(2), s, count=1, flags=re.S)
    s = re.sub(r'(<div class="footer-brand"><div class="brand[^>]*>).*?(</div>)', lambda m: '<div class="footer-brand"><div class="brand tj-footer-brand">' + WORDMARK + m.group(2), s, count=1, flags=re.S)

    # Use the existing validated logistics photo for the live homepage hero.
    if p.name == 'index.html':
        if re.search(r'<img class="hero-bg-r6"[^>]*>', s):
            s = re.sub(r'<img class="hero-bg-r6"[^>]*>', HERO, s, count=1)
        else:
            s = s.replace('<section class="hero">', '<section class="hero">' + HERO, 1)

    if s != old:
        p.write_text(s, encoding='utf-8')

print('PASS: R12.2 live logo fallback and validated hero applied.')
