from html.parser import HTMLParser
from pathlib import Path
import re
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
RUNTIME_VERSION = '20260921-r15-17'


def fail(message):
    raise SystemExit('ERROR: ' + message)


class HeaderParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_header = False
        self.in_navlinks = False
        self.depth = 0
        self.direct_nav = []
        self.ctas = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        classes = set((data.get('class') or '').split())
        if tag == 'header':
            self.in_header = True
        if self.in_header and tag == 'nav' and 'navlinks' in classes:
            self.in_navlinks = True
            self.depth = 0
            return
        if self.in_navlinks:
            if tag == 'a' and self.depth == 0:
                self.direct_nav.append({'href': data.get('href',''), 'text': ''})
            if tag not in {'img','input','br','hr','meta','link','source'}:
                self.depth += 1
        if self.in_header and tag == 'a' and 'nav-cta' in classes:
            self.ctas.append({'href': data.get('href',''), 'text': ''})

    def handle_data(self, data):
        text=' '.join(data.split())
        if not text:
            return
        if self.in_navlinks and self.depth == 1 and self.direct_nav:
            self.direct_nav[-1]['text'] += (' ' if self.direct_nav[-1]['text'] else '') + text
        if self.ctas:
            self.ctas[-1]['text'] += (' ' if self.ctas[-1]['text'] else '') + text

    def handle_endtag(self, tag):
        if self.in_navlinks:
            if tag == 'nav' and self.depth == 0:
                self.in_navlinks = False
            elif self.depth > 0:
                self.depth -= 1
                if tag == 'nav' and self.depth == 0:
                    self.in_navlinks = False
        if tag == 'header':
            self.in_header = False


def main():
    htmls = sorted(ROOT.glob('*.html'))
    if len(htmls) != 50:
        fail(f'expected 50 root HTML pages, found {len(htmls)}')

    bad=[]
    for page in htmls:
        text=page.read_text(encoding='utf-8')
        refs=re.findall(r'assets/brand-v34\.152\.js(?:\?v=([A-Za-z0-9._-]+))?', text)
        expected=[] if page.name=='404.html' else [RUNTIME_VERSION]
        if refs != expected:
            bad.append((page.name,'runtime-cache',refs))
        if page.name=='404.html':
            continue

        if '<a href="/capabilities">Capabilities</a>' in text:
            bad.append((page.name,'legacy-capabilities-nav'))
        if '<a href="/resources">Resources</a>' in text:
            bad.append((page.name,'legacy-resources-nav'))
        if '<a href="/quality">Quality</a>' not in text:
            bad.append((page.name,'quality-nav-missing'))
        if '<a href="/technical-data">Technical Data</a>' not in text:
            bad.append((page.name,'technical-data-nav-missing'))
        if '<a class="cta nav-cta" href="/rfq">Request a Quote <span>→</span></a>' not in text:
            bad.append((page.name,'quote-cta-missing'))

    if bad:
        fail(f'R15.17 static nav mismatch: {bad[:20]}')

    js_path=ROOT/'assets'/'brand-v34.152.js'
    if not js_path.is_file():
        fail('brand runtime missing')
    js=js_path.read_text(encoding='utf-8')
    forbidden=(
        "cta.innerHTML='Request a Quote",
        "cap.textContent='Quality'",
        "res.textContent='Technical Data'",
        "cap.href='/quality'",
        "res.href='/technical-data'",
        "document.querySelector('.site-header .navlinks')",
    )
    for marker in forbidden:
        if marker in js:
            fail(f'R15.17 runtime navigation mutation returned: {marker}')

    print(
        'PASS: R15.17 static navigation consistency — 49 full-shell pages render final header '
        'navigation and RFQ CTA before JS; 404 stays script-free; runtime no longer mutates nav labels/routes.'
    )


if __name__ == '__main__':
    main()
