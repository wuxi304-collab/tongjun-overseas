from pathlib import Path
import re

ROOT = Path('.')
SKIP = {'404.html'}
changed = []


def insert_visual(s, marker, src, alt, label):
    """Insert one deterministic editorial visual after section nav, else after page hero."""
    if marker in s:
        return s
    visual = (
        f'<section class="visual-band {marker}"><div class="wrap"><div class="visual-frame">'
        f'<img alt="{alt}" decoding="async" loading="eager" src="{src}" width="1400" height="788"/>'
        f'<span class="visual-label">{label}</span></div></div></section>'
    )
    m = re.search(r'(<nav aria-label="Section navigation".*?</nav>)', s, re.S)
    if not m:
        m = re.search(r'(<section class="pagehero[^>]*>.*?</section>)', s, re.S)
    if m:
        s = s[:m.end()] + visual + s[m.end():]
    return s


for p in ROOT.glob('*.html'):
    if p.name in SKIP:
        continue

    s = p.read_text(encoding='utf-8')
    old = s
    page_key = p.stem

    # English-only brand normalization.
    s = s.replace('Tongjun Special Metals', 'Tongjun Metal Tech')
    s = s.replace('TONGJUN SPECIAL METALS', 'TONGJUN METAL TECH')
    s = s.replace('TONGJUN METALS · EST. 2026', 'TONGJUN METAL TECH · EST. 2026')

    # Static primary navigation must match its visible labels and destinations.
    s = s.replace(
        '<a href="/capabilities">Capabilities</a>\n<a href="/resources">Resources</a>\n<a href="/about">About</a>',
        '<a href="/quality">Quality</a>\n<a href="/technical-data">Technical Data</a>\n<a href="/about">About</a>'
    )
    s = re.sub(
        r'<a class="cta nav-cta" href="/rfq">.*?</a>',
        '<a class="cta nav-cta" href="/rfq">Request a Quote <span>→</span></a>',
        s,
        count=1,
        flags=re.S
    )

    # Module-specific visual system.
    if p.name == 'materials.html':
        for src in [
            '/assets/images/resources-metal.webp',
            '/assets/images/materials-overview-gen.webp',
            '/assets/images/materials-overview-gen.jpg',
            '/assets/images/materials-warehouse-v2.webp'
        ]:
            s = s.replace(src, '/assets/images/materials-r8.webp?v=20260914-r8')
        s = s.replace('>Material forms<', '>Material families · product forms · sourcing routes<')

    elif p.name == 'quality.html':
        for src in [
            '/assets/images/traceability-pmi.webp',
            '/assets/images/quality-inspection.webp',
            '/assets/images/quality-lab-v2.webp'
        ]:
            s = s.replace(src, '/assets/images/quality-r8.webp?v=20260914-r8')
        s = s.replace('>Quality inspection<', '>Inspection · traceability · release evidence<')

    elif p.name == 'technical-data.html':
        # Keep the current local laboratory image until the dedicated R10 binary is promoted.
        s = re.sub(
            r'(<section class="visual-band technical-visual".*?<img[^>]+src=")[^"]+("[^>]*>)',
            r'\1/assets/images/quality-lab-v2.webp?v=20260914-r10\2',
            s,
            count=1,
            flags=re.S
        )
        s = insert_visual(
            s,
            'technical-visual',
            '/assets/images/quality-lab-v2.webp?v=20260914-r10',
            'Metallurgical inspection and controlled technical data review',
            'Technical data · verification · document control'
        )

    elif p.name == 'about.html':
        for src in ['/assets/images/about-engineering.webp', '/assets/images/resources-metal.webp']:
            s = s.replace(src, '/assets/images/engineering-discussion-v2.webp?v=20260914-r10')
        s = s.replace('<section class="visual-band">', '<section class="visual-band about-visual">', 1)
        s = s.replace('>Engineering-led sourcing<', '>Engineering review · sourcing control · route ownership<')

    elif p.name == 'rfq.html':
        for src in ['/assets/images/standards-rfq.webp', '/assets/images/about-engineering.webp']:
            s = s.replace(src, '/assets/images/engineering-review-v2.webp?v=20260914-r10')
        s = s.replace('<section class="visual-band">', '<section class="visual-band rfq-visual">', 1)
        s = insert_visual(
            s,
            'rfq-visual',
            '/assets/images/engineering-review-v2.webp?v=20260914-r10',
            'Engineering and sourcing team reviewing a controlled special-metals requirement',
            'Requirement review · route control · buyer release'
        )

    elif p.name == 'product-forms.html':
        s = insert_visual(
            s,
            'product-forms-visual',
            '/assets/images/materials-warehouse-v2.webp?v=20260914-r10',
            'Special-metal product forms staged in an industrial warehouse',
            'Strip · sheet · plate · bar · forging · components'
        )
        # Use engineering imagery only where the page discusses secondary conversion / forging route.
        s = s.replace('/assets/images/about-engineering.webp', '/assets/images/engineering-discussion-v2.webp?v=20260914-r10')

    elif p.name == 'nickel-alloys.html':
        s = insert_visual(
            s,
            'material-detail-visual nickel-visual',
            '/assets/images/nickel-alloys.webp?v=20260914-r10',
            'Nickel alloy flat products and engineered special-metal forms',
            'Nickel alloys · corrosion service · product-form qualification'
        )

    elif p.name == 'invar-36.html':
        s = insert_visual(
            s,
            'material-detail-visual invar-visual',
            '/assets/images/invar-tooling.webp?v=20260914-r10',
            'Low-expansion alloy material prepared for precision tooling applications',
            'Low expansion · dimensional stability · application-specific route'
        )

    elif p.name == 'heavy-plate.html':
        s = insert_visual(
            s,
            'material-detail-visual heavy-plate-visual',
            '/assets/images/heavy-plate.webp?v=20260914-r10',
            'Heavy special-metal plate prepared for project supply',
            'Heavy plate · width capability · heat treatment · inspection'
        )

    # Approved Columbus lockup in the header as a real image node.
    logo_html = '<img class="tj-logo-img" src="/assets/images/columbus-logo-r7.svg?v=20260914-r7" alt="Tongjun Metal Tech" width="1200" height="400" decoding="async" />'
    s = re.sub(
        r'(<a[^>]*class="brand"[^>]*>).*?(</a>)',
        lambda m: m.group(1) + logo_html + m.group(2),
        s,
        count=1,
        flags=re.S
    )

    # Keep the same approved lockup in the footer; no duplicate pseudo-wordmark.
    footer_logo = '<img class="tj-footer-logo" src="/assets/images/columbus-logo-r7.svg?v=20260914-r7" alt="Tongjun Metal Tech" width="1200" height="400" decoding="async" loading="lazy" />'
    s = re.sub(
        r'(<div class="footer-brand"><div class="brand"[^>]*>).*?(</div>)',
        lambda m: '<div class="footer-brand"><div class="brand tj-footer-brand">' + footer_logo + m.group(2),
        s,
        count=1,
        flags=re.S
    )

    # Stable real-image homepage hero node.
    if p.name == 'index.html':
        s = re.sub(
            r'<img class="hero-bg-r6"[^>]*>',
            '<img class="hero-bg-r6" src="/assets/images/hero-port-r7.svg?v=20260914-r7" alt="Special metals prepared for international delivery at an industrial port" width="1916" height="821" decoding="async" fetchpriority="high" />',
            s,
            count=1
        )
        if 'hero-bg-r6' not in s:
            s = s.replace(
                '<section class="hero">',
                '<section class="hero"><img class="hero-bg-r6" src="/assets/images/hero-port-r7.svg?v=20260914-r7" alt="Special metals prepared for international delivery at an industrial port" width="1916" height="821" decoding="async" fetchpriority="high" />',
                1
            )

    # Page identity hook for deterministic page-level styling.
    def body_hook(m):
        attrs = m.group(1)
        if 'data-page=' not in attrs:
            attrs += f' data-page="{page_key}"'
        if 'class=' not in attrs:
            attrs += ' class="brand-v34"'
        elif 'brand-v34' not in attrs:
            attrs = re.sub(r'class="([^"]*)"', r'class="\1 brand-v34"', attrs, count=1)
        return '<body' + attrs + '>'
    s = re.sub(r'<body([^>]*)>', body_hook, s, count=1)

    # R10 keeps one deploy-time stylesheet and one brand script in the HTML.
    s = re.sub(r'<link[^>]+href="/assets/brand-v34\.152[^\"]*"[^>]*>', '', s)
    s = re.sub(r'<script[^>]+src="/assets/brand-v34\.152\.js[^\"]*"[^>]*></script>', '', s)
    s = s.replace(
        '</head>',
        '<link rel="stylesheet" href="/assets/brand-v34.152-r10.css?v=20260914-r10"><script defer src="/assets/brand-v34.152.js?v=20260914-r10"></script></head>'
    )

    if s != old:
        p.write_text(s, encoding='utf-8')
        changed.append(p.name)

print(f'Brand shell applied to {len(changed)} HTML files')
