from pathlib import Path
import re

ROOT = Path('.')
SKIP = {'404.html'}
changed = []

PAGE_KEYS = {
    'index.html':'home','materials.html':'materials','product-forms.html':'product-forms','technical-data.html':'technical-data',
    'quality.html':'quality','about.html':'about','rfq.html':'rfq','resources.html':'resources','nickel-alloys.html':'nickel-alloys',
    'precision-strip.html':'precision-strip','heavy-plate.html':'heavy-plate','invar-36.html':'invar-36','titanium-zirconium.html':'titanium-zirconium',
    'industries.html':'industries','nickel-process-equipment.html':'nickel-process-equipment','titanium-heat-exchangers.html':'titanium-heat-exchangers',
    'heavy-plate-pressure-equipment.html':'heavy-plate-pressure-equipment','precision-strip-bellows.html':'precision-strip-bellows',
    'invar-lng.html':'invar-lng','invar-aerospace-tooling.html':'invar-aerospace-tooling'
}

VISUAL_INSERT = {
    'product-forms.html': ('/assets/images/materials-r8.webp?v=20260914-r8','Product geometry · process route · qualification evidence','Special metal product forms in controlled industrial storage'),
    'nickel-alloys.html': ('/assets/images/nickel-alloys.webp','Nickel alloys · corrosion service · product-form control','Nickel alloy flat products and controlled material forms'),
    'invar-36.html': ('/assets/images/invar-tooling.webp','Low expansion · thermal stability · route qualification','Low-expansion alloy prepared for precision tooling'),
    'heavy-plate.html': ('/assets/images/heavy-plate.webp','Heavy plate · width capability · inspection route','Heavy special-metal plate in an industrial processing environment'),
    'titanium-zirconium.html': ('/assets/images/titanium-zirconium.webp','Reactive metals · corrosion service · product-form evidence','Titanium and zirconium products for critical equipment'),
    'precision-strip.html': ('/assets/images/precision-strip.webp','Precision strip · dimensional control · coil repeatability','Precision metal strip coil with controlled dimensional geometry'),
}

for p in ROOT.glob('*.html'):
    if p.name in SKIP:
        continue
    s = p.read_text(encoding='utf-8')
    old = s

    # English-only brand normalization.
    s = s.replace('Tongjun Special Metals', 'Tongjun Metal Tech')
    s = s.replace('TONGJUN SPECIAL METALS', 'TONGJUN METAL TECH')
    s = s.replace('TONGJUN METALS · EST. 2026', 'TONGJUN METAL TECH · EST. 2026')

    # Static primary navigation must match visible labels and destinations.
    s = s.replace(
        '<a href="/capabilities">Capabilities</a>\n<a href="/resources">Resources</a>\n<a href="/about">About</a>',
        '<a href="/quality">Quality</a>\n<a href="/technical-data">Technical Data</a>\n<a href="/about">About</a>'
    )
    s = re.sub(r'<a class="cta nav-cta" href="/rfq">.*?</a>', '<a class="cta nav-cta" href="/rfq">Request a Quote <span>→</span></a>', s, count=1, flags=re.S)

    # Page identity hook for precise editorial styling.
    page_key = PAGE_KEYS.get(p.name, p.stem)
    if '<body' in s:
        m = re.search(r'<body([^>]*)>', s)
        if m:
            attrs = m.group(1)
            attrs = re.sub(r'\sdata-page="[^"]*"', '', attrs)
            s = s[:m.start()] + '<body' + attrs + f' data-page="{page_key}">' + s[m.end():]

    # Core module imagery.
    if p.name == 'materials.html':
        for src in ['/assets/images/resources-metal.webp','/assets/images/materials-overview-gen.webp','/assets/images/materials-overview-gen.jpg','/assets/images/materials-warehouse-v2.webp']:
            s = s.replace(src, '/assets/images/materials-r8.webp?v=20260914-r8')
        s = s.replace('>Material forms<', '>Material families · product forms · sourcing routes<')
    elif p.name == 'quality.html':
        for src in ['/assets/images/traceability-pmi.webp','/assets/images/quality-inspection.webp','/assets/images/quality-lab-v2.webp']:
            s = s.replace(src, '/assets/images/quality-r8.webp?v=20260914-r8')
        s = s.replace('>Quality inspection<', '>Inspection · traceability · release evidence<')
    elif p.name == 'technical-data.html':
        for src in ['/assets/images/resources-metal.webp','/assets/images/standards-rfq.webp','/assets/images/quality-inspection.webp','/assets/images/quality-lab-v2.webp']:
            s = s.replace(src, '/assets/images/technical-lab-r11.webp?v=20260914-r11')
        if 'technical-visual' not in s:
            visual = '<section class="visual-band technical-visual"><div class="wrap"><div class="visual-frame"><img alt="Metallurgical laboratory inspection and controlled technical data review" decoding="async" loading="eager" src="/assets/images/technical-lab-r11.webp?v=20260914-r11" width="1200" height="510"/><span class="visual-label">Material data · verification · controlled reference</span></div></div></section>'
            m = re.search(r'(<nav aria-label="Section navigation".*?</nav>)', s, re.S)
            if m: s = s[:m.end()] + visual + s[m.end():]
    elif p.name == 'about.html':
        for src in ['/assets/images/about-engineering.webp','/assets/images/resources-metal.webp','/assets/images/engineering-discussion-v2.webp']:
            s = s.replace(src, '/assets/images/engineering-review-r11.webp?v=20260914-r11')
        s = s.replace('>Engineering-led sourcing<', '>Requirement review · source role · evidence boundary<')
    elif p.name == 'rfq.html':
        for src in ['/assets/images/standards-rfq.webp','/assets/images/about-engineering.webp','/assets/images/engineering-review-v2.webp']:
            s = s.replace(src, '/assets/images/engineering-review-r11.webp?v=20260914-r11')
        if 'rfq-visual' not in s:
            visual = '<section class="visual-band rfq-visual"><div class="wrap"><div class="visual-frame"><img alt="Engineering and sourcing team reviewing a controlled special-metals requirement" decoding="async" loading="eager" src="/assets/images/engineering-review-r11.webp?v=20260914-r11" width="1200" height="510"/><span class="visual-label">Requirement review · route control · buyer release</span></div></div></section>'
            m = re.search(r'(<section class="pagehero[^>]*>.*?</section>)', s, re.S)
            if m: s = s[:m.end()] + visual + s[m.end():]

    # Insert/normalize visual bands for priority material pages.
    if p.name in VISUAL_INSERT:
        img, label, alt = VISUAL_INSERT[p.name]
        visual = f'<section class="visual-band page-specific-visual"><div class="wrap"><div class="visual-frame"><img alt="{alt}" decoding="async" loading="eager" src="{img}" width="1200" height="510"/><span class="visual-label">{label}</span></div></div></section>'
        if 'page-specific-visual' not in s and p.name != 'precision-strip.html':
            m = re.search(r'(<nav aria-label="Section navigation".*?</nav>)', s, re.S)
            if m: s = s[:m.end()] + visual + s[m.end():]
        elif p.name == 'precision-strip.html':
            s = re.sub(r'<section class="visual-band">.*?</section>', visual, s, count=1, flags=re.S)

    # Approved Columbus lockup as a real image node in header/footer.
    logo_html = '<img class="tj-logo-img" src="/assets/images/columbus-logo-r7.svg?v=20260914-r7" alt="Tongjun Metal Tech" width="1200" height="400" decoding="async" />'
    s = re.sub(r'(<a[^>]*class="brand"[^>]*>).*?(</a>)', lambda m: m.group(1) + logo_html + m.group(2), s, count=1, flags=re.S)
    footer_logo = '<img class="tj-footer-logo" src="/assets/images/columbus-logo-r7.svg?v=20260914-r7" alt="Tongjun Metal Tech" width="1200" height="400" decoding="async" loading="lazy" />'
    s = re.sub(r'(<div class="footer-brand"><div class="brand"[^>]*>).*?(</div>)', lambda m: '<div class="footer-brand"><div class="brand tj-footer-brand">' + footer_logo + m.group(2), s, count=1, flags=re.S)

    # Stable real-image homepage hero node.
    if p.name == 'index.html':
        hero = '<img class="hero-bg-r6" src="/assets/images/hero-port-r7.svg?v=20260914-r7" alt="Special metals prepared for international delivery at an industrial port" width="1916" height="821" decoding="async" fetchpriority="high" />'
        s = re.sub(r'<img class="hero-bg-r6"[^>]*>', hero, s, count=1)
        if 'hero-bg-r6' not in s:
            s = s.replace('<section class="hero">','<section class="hero">' + hero,1)

    # R11 delivers one consolidated brand stylesheet.
    s = re.sub(r'<link[^>]+href="/assets/brand-v34\.152[^\"]*"[^>]*>', '', s)
    s = re.sub(r'<script[^>]+src="/assets/brand-v34\.152\.js[^\"]*"[^>]*></script>', '', s)
    s = s.replace('</head>', '<link rel="stylesheet" href="/assets/brand-v34.152-r11.css?v=20260914-r11"><script defer src="/assets/brand-v34.152.js?v=20260914-r11"></script></head>')

    if '<body' in s and 'brand-v34' not in s.split('<body', 1)[1].split('>', 1)[0]:
        s = re.sub(r'<body([^>]*)>', lambda m: '<body' + m.group(1) + ' class="brand-v34">' if 'class=' not in m.group(1) else '<body' + re.sub(r'class="([^"]*)"', r'class="\1 brand-v34"', m.group(1)) + '>', s, count=1)

    if s != old:
        p.write_text(s, encoding='utf-8')
        changed.append(p.name)

print(f'Brand shell applied to {len(changed)} HTML files')
