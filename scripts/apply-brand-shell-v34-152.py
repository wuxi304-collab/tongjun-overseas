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
    if p.name=='materials.html':
        s=s.replace('/assets/images/resources-metal.webp','/assets/images/materials-overview-gen.jpg')
        s=s.replace('/assets/images/materials-overview-gen.webp','/assets/images/materials-overview-gen.jpg')
    if 'brand-v34.152.css' not in s:
        s=s.replace('</head>','<link rel="stylesheet" href="/assets/brand-v34.152.css"><script defer src="/assets/brand-v34.152.js"></script></head>')
    if 'brand-v34.152-r2.css' not in s:
        s=s.replace('</head>','<link rel="stylesheet" href="/assets/brand-v34.152-r2.css"></head>')
    if 'brand-v34.152-r4.css' not in s:
        s=s.replace('</head>','<link rel="stylesheet" href="/assets/brand-v34.152-r4.css"></head>')
    if '<body' in s and 'brand-v34' not in s.split('<body',1)[1].split('>',1)[0]:
        s=re.sub(r'<body([^>]*)>',lambda m:'<body'+m.group(1)+' class="brand-v34">' if 'class=' not in m.group(1) else '<body'+re.sub(r'class="([^"]*)"',r'class="\1 brand-v34"',m.group(1))+'>',s,count=1)
    if s!=old:
        p.write_text(s,encoding='utf-8');changed.append(p.name)
print(f'Brand shell applied to {len(changed)} HTML files')
