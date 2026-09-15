from pathlib import Path
import re

ROOT = Path('.')
VERSION = '20260916-r14-1'
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


def simplify_rfq(s: str) -> str:
    """Keep the first-pass RFQ short while preserving every advanced control."""
    if 'class="r14-rfq-fast-note"' not in s:
        s = s.replace(
            '<div class="formgrid">',
            '<p class="r14-rfq-fast-note">Required fields are marked *. Start with the technical core; add qualification, logistics and release controls only when they matter to the order.</p><div class="formgrid">',
            1,
        )

    # Move the optional qualification + logistics blocks behind the required application block.
    # They remain inside the same form and are fully submitted when the buyer opens/completes them.
    if 'class="field full r14-rfq-optional"' not in s:
        group3 = '<div class="rfq-group-label field full"><span>03 · Qualification / release</span>'
        group5 = '<div class="rfq-group-label field full"><span>05 · Application / notes</span>'
        review_marker = '<div class="field full"><section class="v34-152-review" id="technicalReviewControl">'
        opt_start = s.find(group3)
        app_start = s.find(group5)
        if opt_start < 0 or app_start < 0 or app_start <= opt_start:
            raise SystemExit('ERROR: RFQ qualification/logistics block markers not found')
        optional_chunk = s[opt_start:app_start]
        s = s[:opt_start] + s[app_start:]
        review_start = s.find(review_marker)
        if review_start < 0:
            raise SystemExit('ERROR: RFQ advanced review marker not found after block move')
        optional_details = (
            '<details class="field full r14-rfq-optional">'
            '<summary><span>Optional qualification + logistics</span><small>Improve offer readiness</small></summary>'
            '<div class="r14-rfq-optional-grid">' + optional_chunk + '</div>'
            '</details>'
        )
        s = s[:review_start] + optional_details + s[review_start:]

    # The governance/release console is valuable for controlled procurement, but it should not
    # confront every first-time buyer before they can send a technically useful requirement.
    if 'class="field full r14-rfq-advanced"' not in s:
        outer_start_marker = '<div class="field full"><section class="v34-152-review" id="technicalReviewControl">'
        outer_start = s.find(outer_start_marker)
        if outer_start < 0:
            raise SystemExit('ERROR: RFQ technical review control wrapper not found')
        inner_start = outer_start + len('<div class="field full">')
        end_marker = '</section></div>'
        outer_end = s.find(end_marker, inner_start)
        if outer_end < 0:
            raise SystemExit('ERROR: RFQ technical review control closing marker not found')
        review_section = s[inner_start:outer_end + len('</section>')]
        advanced_details = (
            '<details class="field full r14-rfq-advanced">'
            '<summary><span>Advanced qualification controls</span><small>Buyer governance · deviations · release basis</small></summary>'
            + review_section +
            '</details>'
        )
        s = s[:outer_start] + advanced_details + s[outer_end + len(end_marker):]

    return s


changed = []
for p in ROOT.glob('*.html'):
    s = p.read_text(encoding='utf-8')
    old = s

    # Advance every customer-facing page to the R14.1 stylesheet after the R13 baseline has been applied.
    s = s.replace(R13, R14)
    s = re.sub(r'/assets/brand-v34\.152-r13-1\.css\?v=[^"\']+', R14, s)
    s = re.sub(r'/assets/brand-v34\.152-r14\.css\?v=[^"\']+', R14, s)

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
        # Global Markets navigation links to these fragments. Make the destinations real.
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
        # Insert immediately after the page hero, before photography or long-form content.
        m = re.search(r'(<main\b[^>]*>\s*<section\b[^>]*class="[^"]*pagehero[^"]*"[^>]*>.*?</section>)', s, flags=re.S)
        if not m:
            raise SystemExit(f'ERROR: page hero not found for R14 rail in {p.name}')
        s = s[:m.end()] + rail + s[m.end():]

    if p.name == 'rfq.html':
        s = simplify_rfq(s)

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

rfq = (ROOT / 'rfq.html').read_text(encoding='utf-8')
for marker in (
    'class="r14-rfq-fast-note"',
    'class="field full r14-rfq-optional"',
    'class="field full r14-rfq-advanced"',
):
    if rfq.count(marker) != 1:
        raise SystemExit(f'ERROR: RFQ progressive-disclosure marker count wrong: {marker}')
if rfq.find('05 · Application / notes') > rfq.find('Optional qualification + logistics'):
    raise SystemExit('ERROR: required Application block must precede optional qualification/logistics')

print(f'PASS: R14.1 conversion overlay applied to {len(changed)} HTML files; buyer path and RFQ progressive disclosure installed.')
