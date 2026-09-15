from pathlib import Path
from html.parser import HTMLParser
import re
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
RFQ = ROOT / 'rfq.html'
SITE_JS = ROOT / 'assets' / 'site.js'
# API source lives in the repository root even when validating a built _site artifact.
API_JS = Path('api/rfq.js')


class RfqFormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_form = False
        self.depth = 0
        self.fields = []
        self.required = []
        self.visible = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == 'form':
            if self.in_form:
                self.depth += 1
            elif data.get('id') == 'rfqForm':
                self.in_form = True
                self.depth = 1
            return
        if not self.in_form or tag not in {'input', 'select', 'textarea'}:
            return
        name = data.get('name')
        if not name:
            return
        if name not in self.fields:
            self.fields.append(name)
        input_type = (data.get('type') or '').lower()
        hidden = input_type in {'hidden', 'button', 'submit', 'reset', 'image'} or (data.get('aria-hidden') or '').lower() == 'true'
        if not hidden and name not in self.visible:
            self.visible.append(name)
        if 'required' in data and name not in self.required:
            self.required.append(name)

    def handle_endtag(self, tag):
        if self.in_form and tag == 'form':
            self.depth -= 1
            if self.depth <= 0:
                self.in_form = False
                self.depth = 0


def parse_api_contract(text: str):
    limits_match = re.search(r'const\s+LIMITS\s*=\s*\{(.*?)\};', text, flags=re.S)
    if not limits_match:
        raise SystemExit('ERROR: API LIMITS object not found')
    limit_keys = set(re.findall(r'\b([A-Za-z_][A-Za-z0-9_]*)\s*:', limits_match.group(1)))

    required_match = re.search(r"const\s+required\s*=\s*\[(.*?)\];", text, flags=re.S)
    if not required_match:
        raise SystemExit('ERROR: API required field list not found')
    required = set(re.findall(r"['\"]([^'\"]+)['\"]", required_match.group(1)))
    return limit_keys, required


def parse_fallback_fields(text: str):
    block = re.search(r'const\s+buildPayload\s*=\s*\(\)\s*=>\s*\{(.*?)return\s+\{subject,body\};', text, flags=re.S)
    if not block:
        raise SystemExit('ERROR: buildPayload() block not found in site.js')
    return set(re.findall(r"f\.get\(['\"]([^'\"]+)['\"]\)", block.group(1)))


def main():
    for path in (RFQ, SITE_JS, API_JS):
        if not path.is_file():
            raise SystemExit(f'ERROR: contract source missing: {path}')

    form_parser = RfqFormParser()
    form_parser.feed(RFQ.read_text(encoding='utf-8'))
    if not form_parser.fields:
        raise SystemExit('ERROR: #rfqForm has no named fields')

    api_limits, api_required = parse_api_contract(API_JS.read_text(encoding='utf-8'))
    fallback_fields = parse_fallback_fields(SITE_JS.read_text(encoding='utf-8'))

    form_fields = set(form_parser.fields)
    form_required = set(form_parser.required)
    visible_fields = set(form_parser.visible)

    missing_api = sorted(form_fields - api_limits)
    if missing_api:
        raise SystemExit(f'ERROR: RFQ form fields missing from API LIMITS: {missing_api}')

    if form_required != api_required:
        only_form = sorted(form_required - api_required)
        only_api = sorted(api_required - form_required)
        raise SystemExit(
            f'ERROR: frontend/backend required fields diverged; form_only={only_form}, api_only={only_api}'
        )

    # Email fallback must preserve every customer-facing field plus attribution/product context.
    fallback_required = (form_fields - {'website'})
    missing_fallback = sorted(fallback_required - fallback_fields)
    if missing_fallback:
        raise SystemExit(f'ERROR: fields missing from structured email fallback: {missing_fallback}')

    js_text = SITE_JS.read_text(encoding='utf-8')
    runtime_markers = (
        "fetch('/api/rfq'",
        'Product Context:',
        'First Seen:',
        "setStore('tj_last_rfq','email_fallback')",
        'Copy Structured RFQ',
        'mailto:ask2205@outlook.com',
    )
    # In a GitHub Pages artifact, the safe base-path rewrite changes /api/rfq to /tongjun-overseas/api/rfq.
    if "fetch('/api/rfq'" not in js_text and "fetch('/tongjun-overseas/api/rfq'" not in js_text:
        raise SystemExit('ERROR: RFQ secure POST endpoint missing from runtime')
    for marker in runtime_markers[1:]:
        if marker not in js_text:
            raise SystemExit(f'ERROR: RFQ runtime/fallback marker missing: {marker}')

    print(
        'PASS: RFQ contract aligned — '
        f'{len(form_fields)} form fields covered by API, '
        f'{len(form_required)} required fields match backend, '
        f'{len(fallback_required)} non-honeypot fields preserved in email fallback, '
        f'{len(visible_fields)} visible buyer fields audited.'
    )


if __name__ == '__main__':
    main()
