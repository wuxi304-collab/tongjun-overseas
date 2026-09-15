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

    if 'class="field full r14-rfq-optional"' not in s:
        group3 = '<div class="rfq-group-label field full"><span>03 · Qualification / release</span>'
        group5 = '<div class="rfq-group-label field full"><span>05 · Application / notes</span>'
        review_marker = '<div class="field full"><section class="v34-152-review"'
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

    if 'class="field full r14-rfq-advanced"' not in s:
        outer_marker = '<div class="field full"><section class="v34-152-review"'
        outer_start = s.find(outer_marker)
        if outer_start < 0:
            raise SystemExit('ERROR: RFQ technical review control wrapper not found')
        section_start = s.find('<section class="v34-152-review"', outer_start)
        if section_start < 0:
            raise SystemExit('ERROR: RFQ technical review section not found')
        end_marker = '</section></div>'
        outer_end = s.find(end_marker, section_start)
        if outer_end < 0:
            raise SystemExit('ERROR: RFQ technical review control closing marker not found')
        review_section = s[section_start:outer_end + len('</section>')]
        advanced_details = (
            '<details class="field full r14-rfq-advanced">'
            '<summary><span>Advanced qualification controls</span><small>Buyer governance · deviations · release basis</small></summary>'
            + review_section +
            '</details>'
        )
        s = s[:outer_start] + advanced_details + s[outer_end + len(end_marker):]

    return s


def associate_form_labels(s: str, form_id: str, prefix: str) -> str:
    """Add stable ids and label[for] links to visible named controls in one form."""
    form_match = re.search(rf'<form\b[^>]*\bid="{re.escape(form_id)}"[^>]*>.*?</form>', s, flags=re.S)
    if not form_match:
        raise SystemExit(f'ERROR: form #{form_id} not found for semantic labelling')
    segment = form_match.group(0)
    names = []
    for m in re.finditer(r'<(?:input|select|textarea)\b[^>]*\bname="([^"]+)"[^>]*>', segment, flags=re.I):
        name = m.group(1)
        if name not in names:
            names.append(name)

    for name in names:
        control_re = re.compile(
            rf'<(?:input|select|textarea)\b(?=[^>]*\bname="{re.escape(name)}")[^>]*>',
            flags=re.I,
        )
        m = control_re.search(segment)
        if not m:
            continue
        tag = m.group(0)
        lower = tag.lower()
        if 'type="hidden"' in lower or 'aria-hidden="true"' in lower:
            continue
        if re.search(r'\bid="[^"]+"', tag, flags=re.I):
            continue

        stable = f'{prefix}-{re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")}'
        new_tag = tag[:-1] + f' id="{stable}">' if tag.endswith('>') else tag
        control_start = m.start()
        segment = segment[:m.start()] + new_tag + segment[m.end():]

        # Existing forms place the visible label immediately before the control.
        # Associate only that nearest label; do not guess across another HTML element.
        label_end = segment.rfind('</label>', 0, control_start)
        if label_end < 0:
            continue
        between = segment[label_end + len('</label>'):control_start]
        if '<' in between:
            continue
        label_start = segment.rfind('<label', 0, label_end)
        if label_start < 0:
            continue
        label_open_end = segment.find('>', label_start, label_end)
        if label_open_end < 0:
            continue
        label_open = segment[label_start:label_open_end + 1]
        if re.search(r'\bfor="', label_open, flags=re.I):
            continue
        new_label_open = label_open[:-1] + f' for="{stable}">'
        segment = segment[:label_start] + new_label_open + segment[label_open_end + 1:]

    return s[:form_match.start()] + segment + s[form_match.end():]


changed = []
for p in ROOT.glob('*.html'):
    s = p.read_text(encoding='utf-8')
    old = s

    s = s.replace(R13, R14)
    s = re.sub(r'/assets/brand-v34\.152-r13-1\.css\?v=[^"\']+', R14, s)
    s = re.sub(r'/assets/brand-v34\.152-r14\.css\?v=[^"\']+', R14, s)

    if p.name == 'technical-data.html':
        s = re.sub(
            r'(<section class="pagehero tech-center-hero"[^>]*>.*?<h1>).*?(</h1>)',
            r'\1Technical data for sourcing decisions.\2',
            s,
            count=1,
            flags=re.S,
        )

    if p.name == 'industries.html':
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
        m = re.search(r'(<main\b[^>]*>\s*<section\b[^>]*class="[^"]*pagehero[^"]*"[^>]*>.*?</section>)', s, flags=re.S)
        if not m:
            raise SystemExit(f'ERROR: page hero not found for R14 rail in {p.name}')
        s = s[:m.end()] + rail + s[m.end():]

    if p.name == 'rfq.html':
        s = simplify_rfq(s)
        s = associate_form_labels(s, 'rfqForm', 'rfq')
    elif p.name == 'supply-route.html':
        s = associate_form_labels(s, 'routeForm', 'route')
    elif p.name == 'problem-order.html':
        s = associate_form_labels(s, 'problemOrderForm', 'problem')

    if s != old:
        p.write_text(s, encoding='utf-8')
        changed.append(p.name)

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
if 'id="technicalReviewControl"' not in rfq:
    raise SystemExit('ERROR: advanced technical review controls were lost')
for marker in ('id="rfq-name"', 'for="rfq-name"', 'id="rfq-grade"', 'for="rfq-grade"'):
    if marker not in rfq:
        raise SystemExit(f'ERROR: RFQ label association missing: {marker}')

print(f'PASS: R14.1 conversion overlay applied to {len(changed)} HTML files; RFQ progressive disclosure and buyer-form label semantics installed.')
