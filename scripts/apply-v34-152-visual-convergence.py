from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
CSS='<link rel="stylesheet" href="/assets/visual-v34.152.css">'
count=0
index_changed=False

for p in sorted(ROOT.glob('*.html')):
    text=p.read_text(encoding='utf-8')
    original=text
    if CSS not in text:
        if '</head>' in text:
            text=text.replace('</head>',CSS+'</head>',1)
        else:
            raise SystemExit(f'{p.name}: missing </head>')

    if p.name=='index.html':
        # Remove the fabricated student/portrait SVG mark. The approved frozen logo asset
        # is not yet mounted in the repository, so the page must not invent a substitute.
        text=re.sub(r'\s*<span class="portrait"[^>]*>.*?</span>\s*', '\n      ', text, count=1, flags=re.S)
        # Keep the existing wordmark hidden by the convergence stylesheet; this avoids
        # inventing new graphic art while retaining semantic brand text in the document.
        index_changed = text != original

    if text!=original:
        p.write_text(text,encoding='utf-8')
        count+=1

# Explicit verification: every indexable/root HTML gets the same convergence layer.
html=list(ROOT.glob('*.html'))
missing=[p.name for p in html if CSS not in p.read_text(encoding='utf-8')]
if missing:
    raise SystemExit('Missing visual convergence stylesheet: '+', '.join(missing))

idx=(ROOT/'index.html').read_text(encoding='utf-8')
if '<span class="portrait"' in idx:
    raise SystemExit('Fabricated homepage portrait mark still present')
if 'visual-v34.152.css' not in idx:
    raise SystemExit('Homepage convergence CSS missing')

print(f'V34.152 visual convergence applied to {count}/{len(html)} root HTML files; fake portrait removed={index_changed}.')
