from pathlib import Path
import re
ROOT=Path('.')
SKIP={'404.html'}
changed=[]
for p in ROOT.glob('*.html'):
    if p.name in SKIP: continue
    s=p.read_text(encoding='utf-8')
    old=s
    s=s.replace('Tongjun Special Metals','Tongjun Metal Tech')

    # Module-specific visual system. Keep imagery semantically tied to the page.
    if p.name=='materials.html':
        s=s.replace('/assets/images/resources-metal.webp','/assets/images/materials-warehouse-v2.webp')
        s=s.replace('/assets/images/materials-overview-gen.webp','/assets/images/materials-warehouse-v2.webp')
        s=s.replace('/assets/images/materials-overview-gen.jpg','/assets/images/materials-warehouse-v2.webp')
    elif p.name=='quality.html':
        s=s.replace('/assets/images/traceability-pmi.webp','/assets/images/quality-lab-v2.webp')
        s=s.replace('/assets/images/quality-inspection.webp','/assets/images/quality-lab-v2.webp')
    elif p.name=='technical-data.html':
        s=s.replace('/assets/images/resources-metal.webp','/assets/images/quality-lab-v2.webp')
        s=s.replace('/assets/images/standards-rfq.webp','/assets/images/quality-lab-v2.webp')
        s=s.replace('/assets/images/quality-inspection.webp','/assets/images/quality-lab-v2.webp')
        if 'visual-band' not in s:
            visual='<section class="visual-band technical-visual"><div class="wrap"><div class="visual-frame"><img alt="Metallurgical inspection and controlled technical data review" decoding="async" loading="eager" src="/assets/images/quality-lab-v2.webp" width="1200" height="675"/><span class="visual-label">Technical review · material data · verification</span></div></div></section>'
            m=re.search(r'(<nav aria-label="Section navigation".*?</nav>)',s,re.S)
            if m: s=s[:m.end()]+visual+s[m.end():]
    elif p.name=='about.html':
        s=s.replace('/assets/images/about-engineering.webp','/assets/images/engineering-discussion-v2.webp')
        s=s.replace('/assets/images/resources-metal.webp','/assets/images/engineering-discussion-v2.webp')
    elif p.name=='rfq.html':
        s=s.replace('/assets/images/standards-rfq.webp','/assets/images/engineering-review-v2.webp')
        s=s.replace('/assets/images/about-engineering.webp','/assets/images/engineering-review-v2.webp')
        if 'visual-band' not in s:
            visual='<section class="visual-band rfq-visual"><div class="wrap"><div class="visual-frame"><img alt="Engineering and sourcing team reviewing a controlled special-metals requirement" decoding="async" loading="eager" src="/assets/images/engineering-review-v2.webp" width="1200" height="675"/><span class="visual-label">Requirement review · route control · buyer release</span></div></div></section>'
            m=re.search(r'(<section class="pagehero[^>]*>.*?</section>)',s,re.S)
            if m: s=s[:m.end()]+visual+s[m.end():]

    # R7: real image node for the approved Columbus lockup.
    logo_html='<img class="tj-logo-img" src="/assets/images/columbus-logo-r7.svg?v=20260914-r7" alt="Tongjun Metal Tech" width="1200" height="400" decoding="async" />'
    s=re.sub(r'(<a[^>]*class="brand"[^>]*>).*?(</a>)',lambda m:m.group(1)+logo_html+m.group(2),s,count=1,flags=re.S)

    # R7: hard-render homepage hero image instead of CSS background.
    if p.name=='index.html':
        s=re.sub(r'<img class="hero-bg-r6"[^>]*>', '<img class="hero-bg-r6" src="/assets/images/hero-port-r7.svg?v=20260914-r7" alt="Special metals prepared for international delivery at an industrial port" width="1916" height="821" decoding="async" fetchpriority="high" />', s, count=1)
        if 'hero-bg-r6' not in s:
            s=s.replace('<section class="hero">','<section class="hero"><img class="hero-bg-r6" src="/assets/images/hero-port-r7.svg?v=20260914-r7" alt="Special metals prepared for international delivery at an industrial port" width="1916" height="821" decoding="async" fetchpriority="high" />',1)

    if 'brand-v34.152.css' not in s:
        s=s.replace('</head>','<link rel="stylesheet" href="/assets/brand-v34.152.css"><script defer src="/assets/brand-v34.152.js"></script></head>')
    if 'brand-v34.152-r2.css' not in s:
        s=s.replace('</head>','<link rel="stylesheet" href="/assets/brand-v34.152-r2.css"></head>')
    if 'brand-v34.152-r4.css' not in s:
        s=s.replace('</head>','<link rel="stylesheet" href="/assets/brand-v34.152-r4.css"></head>')
    if 'brand-v34.152-r5.css' not in s:
        s=s.replace('</head>','<link rel="stylesheet" href="/assets/brand-v34.152-r5.css"></head>')
    if 'brand-v34.152-r6.css' not in s:
        s=s.replace('</head>','<link rel="stylesheet" href="/assets/brand-v34.152-r6.css?v=20260913-r6"></head>')
    if 'brand-v34.152-r7.css' not in s:
        s=s.replace('</head>','<link rel="stylesheet" href="/assets/brand-v34.152-r7.css?v=20260914-r7"></head>')
    if 'brand-v34.152-r8.css' not in s:
        s=s.replace('</head>','<link rel="stylesheet" href="/assets/brand-v34.152-r8.css?v=20260914-r8"></head>')
    if '<body' in s and 'brand-v34' not in s.split('<body',1)[1].split('>',1)[0]:
        s=re.sub(r'<body([^>]*)>',lambda m:'<body'+m.group(1)+' class="brand-v34">' if 'class=' not in m.group(1) else '<body'+re.sub(r'class="([^"]*)"',r'class="\1 brand-v34"',m.group(1))+'>',s,count=1)
    if s!=old:
        p.write_text(s,encoding='utf-8');changed.append(p.name)
print(f'Brand shell applied to {len(changed)} HTML files')
