from pathlib import Path
import re

ROOT = Path('.')
VERSION = '20260916-r14'
R13 = '/assets/brand-v34.152-r13-1.css?v=20260916-r13-1-safe'
R14 = f'/assets/brand-v34.152-r14.css?v={VERSION}'

RAILS = {
    'technical-data.html': (
        '<nav class="r14-action-rail" aria-label="Technical data quick actions"><div class="wrap">'
        '<a href="/material-compare">Compare materials</a>'
        '<a href="/standards-matrix">Standards matrix</a>'
        '<a href="/rfq">Technical RFQ</a>'
        '</div></nav>'
    ),
    'quality.html': (
        '<nav class="r14-action-rail" aria-label="Quality quick actions"><div class="wrap">'
        '<a href="/document-center">Document center</a>'
        '<a href="/technical-data">Technical data</a>'
        '<a href="/rfq">Send requirement</a>'
        '</div></nav>'
    ),
    'rfq.html': (
        '<nav class="r14-action-rail" aria-label="RFQ quick actions"><div class="wrap">'
        '<a href="#rfqForm">Open RFQ form</a>'
        '<a href="/document-center">Document center</a>'
        '<a href="mailto:ask2205@outlook.com">Email requirement</a>'
        '</div></nav>'
    ),
}

changed = []
for p in ROOT.glob('*.html'):
    s = p.read_text(encoding='utf-8')
    old = s

    # Advance every customer-facing page to the R14 stylesheet after the R13 baseline has been applied.
    s = s.replace(R13, R14)
    s = re.sub(r'/assets/brand-v34\.152-r13-1\.css\?v=[^"\']+', R14, s)

    if p.name == 'technical-data.html':
        # Restore the action-first headline that was lost during later visual consolidation.
        s = re.sub(
            r'(<section class="pagehero tech-center-hero"[^>]*>.*?<h1>).*?(</h1>)',
            r'\1Technical data for sourcing decisions.\2',
            s,
            count=1,
            flags=re.S,
        )

    if p.name == 'industries.html':
        # Global Markets navigation has long linked to these fragments. Make the destinations real.
        s = s.replace(
            '<div class="industry"><h3>Energy &amp; Power</h3>',
            '<div class="industry" id="energy"><h3>Energy &amp; Power</h3>',
        )
        s = s.replace(
            '<div class="industry"><h3>Marine &amp; Offshore</h3>',
            '<div class="industry" id="marine"><h3>Marine &amp; Offshore</h3>',
        )

    rail = RAILS.get(p.name)
    if rail and 'class="r14-action-rail"' not in s:
        # Insert immediately after the page hero, before a visual band or any long-form content.
        m = re.search(r'(<main\b[^>]*>\s*<section\b[^>]*class="[^"]*pagehero[^"]*"[^>]*>.*?</section>)', s, flags=re.S)
        if not m:
            raise SystemExit(f'ERROR: page hero not found for R14 rail in {p.name}')
        s = s[:m.end()] + rail + s[m.end():]

    if s != old:
        p.write_text(s, encoding='utf-8')
        changed.append(p.name)

# Hard assertions: conversion pages must carry the new rail and critical deep links must resolve.
for name in RAILS:
    text = (ROOT / name).read_text(encoding='utf-8')
    if text.count('class="r14-action-rail"') != 1:
        raise SystemExit(f'ERROR: expected exactly one R14 action rail in {name}')

tech = (ROOT / 'technical-data.html').read_text(encoding='utf-8')
if 'Technical data for sourcing decisions.' not in tech:
    raise SystemExit('ERROR: Technical Data action-first headline missing')

industries = (ROOT / 'industries.html').read_text(encoding='utf-8')
for anchor in ('id="energy"', 'id="marine"'):
    if anchor not in industries:
        raise SystemExit(f'ERROR: Industries deep-link target missing: {anchor}')

print(f'PASS: R14 conversion overlay applied to {len(changed)} HTML files; action rails and Markets deep links installed.')
