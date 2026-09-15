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
    'invar-lng.html':'invar-lng','invar-aerospace-tooling.html':'invar-aerospace-tooling',
    'document-center.html':'document-center','standards-matrix.html':'standards-matrix','supply-route.html':'supply-route',
    'problem-order.html':'problem-order','material-compare.html':'material-compare','alloys.html':'alloys'
}

PAGE_VISUALS = {
    'materials.html': ('/assets/images/materials-r8.webp?v=20260915-r12','Material families · product forms · sourcing routes','Special-metal coils, sheet and plate in controlled industrial storage'),
    'product-forms.html': ('/assets/images/materials-r8.webp?v=20260915-r12','Product geometry · process route · qualification evidence','Special-metal product forms in controlled industrial storage'),
    'quality.html': ('/assets/images/quality-r8.webp?v=20260915-r12','Inspection · traceability · release evidence','Metallurgical inspection and controlled material verification'),
    'technical-data.html': ('/assets/images/quality-r8.webp?v=20260915-r12','Material data · verification · controlled reference','Metallurgical inspection and controlled technical-data review'),
    'about.html': ('/assets/images/engineering-discussion-v2.webp?v=20260915-r12','Requirement review · source role · evidence boundary','Engineering and sourcing specialists reviewing a special-metals requirement'),
    'rfq.html': ('/assets/images/engineering-review-v2.webp?v=20260915-r12','Requirement review · route control · buyer release','Engineering and sourcing team reviewing a controlled special-metals requirement'),
    'nickel-alloys.html': ('/assets/images/nickel-alloys.webp?v=20260915-r12','Nickel alloys · corrosion service · product-form control','Nickel alloy flat products and controlled material forms'),
    'nickel-process-equipment.html': ('/assets/images/nickel-alloys.webp?v=20260915-r12','Process service · corrosion environment · qualification route','Nickel alloys prepared for severe chemical and process-equipment service'),
    'invar-36.html': ('/assets/images/invar-tooling.webp?v=20260915-r12','Low expansion · thermal stability · route qualification','Low-expansion alloy prepared for precision tooling'),
    'invar-lng.html': ('/assets/images/invar-lng.webp?v=20260915-r12','Cryogenic control · LNG service · dimensional stability','Invar low-expansion material prepared for LNG and cryogenic service'),
    'invar-aerospace-tooling.html': ('/assets/images/invar-tooling.webp?v=20260915-r12','Tooling stability · thermal control · dimensional repeatability','Invar tooling material prepared for high-precision aerospace applications'),
    'heavy-plate.html': ('/assets/images/heavy-plate.webp?v=20260915-r12','Heavy plate · width capability · inspection route','Heavy special-metal plate in an industrial processing environment'),
    'heavy-plate-pressure-equipment.html': ('/assets/images/heavy-plate.webp?v=20260915-r12','Pressure equipment · thickness route · inspection control','Heavy special-metal plate prepared for pressure-equipment fabrication'),
    'titanium-zirconium.html': ('/assets/images/titanium-zirconium.webp?v=20260915-r12','Reactive metals · corrosion service · product-form evidence','Titanium and zirconium products for critical process equipment'),
    'titanium-heat-exchangers.html': ('/assets/images/titanium-zirconium.webp?v=20260915-r12','Heat exchangers · reactive metals · corrosion control','Titanium and zirconium material prepared for heat-exchanger service'),
    'precision-strip.html': ('/assets/images/precision-strip.webp?v=20260915-r12','Precision strip · dimensional control · coil repeatability','Precision metal strip coil with controlled dimensional geometry'),
    'precision-strip-bellows.html': ('/assets/images/precision-strip.webp?v=20260915-r12','Bellows · precision strip · repeatable forming route','Precision strip prepared for bellows and formed components'),
    'industries.html': ('/assets/images/logistics-stock.webp?v=20260915-r12','Markets · critical service · controlled supply routes','Special metals prepared for controlled international industrial supply'),
    'resources.html': ('/assets/images/resources-metal.webp?v=20260915-r12','Technical library · standards · sourcing evidence','Special metals technical resources and controlled reference material'),
    'document-center.html': ('/assets/images/standards-rfq.webp?v=20260915-r12','Documents · certificates · buyer evidence','Technical documentation and sourcing evidence under controlled review'),
    'standards-matrix.html': ('/assets/images/standards-rfq.webp?v=20260915-r12','Standards · product form · qualification basis','Standards and material requirements reviewed for sourcing decisions'),
    'supply-route.html': ('/assets/images/logistics-stock.webp?v=20260915-r12','Supply route · source control · delivery evidence','Special metals moving through a controlled sourcing and logistics route'),
    'problem-order.html': ('/assets/images/about-engineering.webp?v=20260915-r12','Problem order · technical recovery · evidence review','Engineering review of a special-metals order requiring technical recovery')
}


def apply_page_visual(s: str, page_name: str) -> str:
    if page_name not in PAGE_VISUALS:
        return s
    img, label, alt = PAGE_VISUALS[page_name]
    visual = (
        '<section class="visual-band page-specific-visual"><div class="wrap"><div class="visual-frame">'
        f'<img alt="{alt}" decoding="async" loading="eager" fetchpriority="high" src="{img}" width="1200" height="510"/>'
        f'<span class="visual-label">{label}</span></div></div></section>'
    )

    if re.search(r'<section class="visual-band[^>]*>.*?</section>', s, flags=re.S):
        s = re.sub(r'<section class="visual-band[^>]*>.*?</section>', visual, s, count=1, flags=re.S)
    else:
        m = re.search(r'(<nav aria-label="Section navigation".*?</nav>)', s, re.S)
        if m:
            s = s[:m.end()] + visual + s[m.end():]
        else:
            m = re.search(r'(<section class="pagehero[^>]*>.*?</section>)', s, re.S)
            if m:
                s = s[:m.end()] + visual + s[m.end():]

    absolute = 'https://exoticalloycn.com' + img.split('?')[0]
    s = re.sub(r'<meta content="[^"]*" property="og:image"\s*/?>', f'<meta content="{absolute}" property="og:image"/>', s, count=1)
    s = re.sub(r'<meta content="[^"]*" name="twitter:image"\s*/?>', f'<meta content="{absolute}" name="twitter:image"/>', s, count=1)

    preload = f'<link rel="preload" as="image" href="{img}" fetchpriority="high">'
    if preload not in s:
        s = s.replace('</head>', preload + '</head>', 1)
    return s


for p in ROOT.glob('*.html'):
    if p.name in SKIP:
        continue
    s = p.read_text(encoding='utf-8')
    old = s

    s = s.replace('Tongjun Special Metals', 'Tongjun Metal Tech')
    s = s.replace('TONGJUN SPECIAL METALS', 'TONGJUN METAL TECH')
    s = s.replace('TONGJUN METALS · EST. 2026', 'TONGJUN METAL TECH · EST. 2026')

    s = s.replace(
        '<a href="/capabilities">Capabilities</a>\n<a href="/resources">Resources</a>\n<a href="/about">About</a>',
        '<a href="/quality">Quality</a>\n<a href="/technical-data">Technical Data</a>\n<a href="/about">About</a>'
    )
    s = re.sub(r'<a class="cta nav-cta" href="/rfq">.*?</a>', '<a class="cta nav-cta" href="/rfq">Request a Quote <span>→</span></a>', s, count=1, flags=re.S)

    page_key = PAGE_KEYS.get(p.name, p.stem)
    if '<body' in s:
        m = re.search(r'<body([^>]*)>', s)
        if m:
            attrs = m.group(1)
            attrs = re.sub(r'\sdata-page="[^"]*"', '', attrs)
            s = s[:m.start()] + '<body' + attrs + f' data-page="{page_key}">' + s[m.end():]

    if p.name == 'materials.html':
        s = s.replace('>Material forms<', '>Material families · product forms · sourcing routes<')
    elif p.name == 'quality.html':
        s = s.replace('>Quality inspection<', '>Inspection · traceability · release evidence<')
    elif p.name == 'about.html':
        s = s.replace('>Engineering-led sourcing<', '>Requirement review · source role · evidence boundary<')

    s = apply_page_visual(s, p.name)

    logo_html = '<img class="tj-logo-img" src="/assets/images/columbus-logo-r7.svg?v=20260915-r12" alt="Tongjun Metal Tech" width="1200" height="400" decoding="async" />'
    s = re.sub(r'(<a[^>]*class="brand"[^>]*>).*?(</a>)', lambda m: m.group(1) + logo_html + m.group(2), s, count=1, flags=re.S)
    footer_logo = '<img class="tj-footer-logo" src="/assets/images/columbus-logo-r7.svg?v=20260915-r12" alt="Tongjun Metal Tech" width="1200" height="400" decoding="async" loading="lazy" />'
    s = re.sub(r'(<div class="footer-brand"><div class="brand"[^>]*>).*?(</div>)', lambda m: '<div class="footer-brand"><div class="brand tj-footer-brand">' + footer_logo + m.group(2), s, count=1, flags=re.S)

    if p.name == 'index.html':
        hero = '<img class="hero-bg-r6" src="/assets/images/hero-port-r7.svg?v=20260915-r12" alt="Special metals prepared for international delivery at an industrial port" width="1916" height="821" decoding="async" fetchpriority="high" />'
        s = re.sub(r'<img class="hero-bg-r6"[^>]*>', hero, s, count=1)
        if 'hero-bg-r6' not in s:
            s = s.replace('<section class="hero">','<section class="hero">' + hero,1)

    s = re.sub(r'<link[^>]+href="/assets/brand-v34\.152[^\"]*"[^>]*>', '', s)
    s = re.sub(r'<script[^>]+src="/assets/brand-v34\.152\.js[^\"]*"[^>]*></script>', '', s)
    s = s.replace('</head>', '<link rel="stylesheet" href="/assets/brand-v34.152-r12.css?v=20260915-r12"><script defer src="/assets/brand-v34.152.js?v=20260915-r12"></script></head>')

    if '<body' in s and 'brand-v34' not in s.split('<body', 1)[1].split('>', 1)[0]:
        s = re.sub(r'<body([^>]*)>', lambda m: '<body' + m.group(1) + ' class="brand-v34">' if 'class=' not in m.group(1) else '<body' + re.sub(r'class="([^"]*)"', r'class="\1 brand-v34"', m.group(1)) + '>', s, count=1)

    if s != old:
        p.write_text(s, encoding='utf-8')
        changed.append(p.name)

print(f'Brand shell applied to {len(changed)} HTML files')
