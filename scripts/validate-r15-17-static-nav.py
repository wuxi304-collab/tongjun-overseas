from html.parser import HTMLParser
from pathlib import Path
import re
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
RUNTIME_VERSION = '20260921-r15-17'
EXPECTED_NAV = [
    ('/quality', 'Quality'),
    ('/technical-data', 'Technical Data'),
    ('/about', 'About'),
]
EXPECTED_CTA = ('/rfq', 'Request a Quote →')
BASE_PREFIX = '/tongjun-overseas'


def normalize_href(value: str) -> str:
    if value == BASE_PREFIX:
        return '/'
    if value.startswith(BASE_PREFIX + '/'):
        return value[len(BASE_PREFIX):]
    return value
VOID = {'img','input','br','hr','meta','link','source','area','base','col','embed','param','track','wbr'}


def fail(message):
    raise SystemExit('ERROR: ' + message)


class HeaderParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_header = False
        self.in_nav = False
        self.nav_depth = 0
        self.current_direct = None
        self.direct_nav = []
        self.current_cta = None
        self.ctas = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        classes = set((data.get('class') or '').split())

        if tag == 'header':
            self.in_header = True

        if self.in_header and tag == 'nav' and 'navlinks' in classes:
            self.in_nav = True
            self.nav_depth = 0
            return

        if self.in_nav:
            if tag == 'a' and self.nav_depth == 0:
                self.current_direct = {
                    'href': data.get('href',''),
                    'text': '',
                }
                self.direct_nav.append(self.current_direct)
            if tag not in VOID:
                self.nav_depth += 1

        if self.in_header and tag == 'a' and 'nav-cta' in classes:
            self.current_cta = {
                'href': data.get('href',''),
                'text': '',
            }
            self.ctas.append(self.current_cta)

    def handle_data(self, data):
        text = ' '.join(data.split())
        if not text:
            return
        if self.current_direct is not None:
            self.current_direct['text'] += (
                (' ' if self.current_direct['text'] else '') + text
            )
        if self.current_cta is not None:
            self.current_cta['text'] += (
                (' ' if self.current_cta['text'] else '') + text
            )

    def handle_endtag(self, tag):
        if self.in_nav:
            if tag == 'nav' and self.nav_depth == 0:
                self.in_nav = False
                self.current_direct = None
                return
            if self.nav_depth > 0:
                self.nav_depth -= 1
            if tag == 'a' and self.current_direct is not None and self.nav_depth == 0:
                self.current_direct = None

        if tag == 'a' and self.current_cta is not None:
            self.current_cta = None
        if tag == 'header':
            self.in_header = False


def main():
    htmls = sorted(ROOT.glob('*.html'))
    if len(htmls) != 50:
        fail(f'expected 50 root HTML pages, found {len(htmls)}')

    bad = []

    for page in htmls:
        text = page.read_text(encoding='utf-8')
        refs = re.findall(
            r'assets/brand-v34\.152\.js(?:\?v=([A-Za-z0-9._-]+))?',
            text,
        )
        expected_refs = [] if page.name == '404.html' else [RUNTIME_VERSION]
        if refs != expected_refs:
            bad.append((page.name, 'runtime-cache', refs))

        if page.name == '404.html':
            continue

        parser = HeaderParser()
        parser.feed(text)
        nav = [(normalize_href(x['href']), x['text'].strip()) for x in parser.direct_nav]
        ctas = [(normalize_href(x['href']), x['text'].strip()) for x in parser.ctas]

        if nav != EXPECTED_NAV:
            bad.append((page.name, 'direct-primary-nav', nav))
        if ctas != [EXPECTED_CTA]:
            bad.append((page.name, 'nav-cta', ctas))

    if bad:
        fail(f'R15.17 static nav mismatch: {bad[:20]}')

    js_path = ROOT / 'assets' / 'brand-v34.152.js'
    if not js_path.is_file():
        fail('brand runtime missing')
    js = js_path.read_text(encoding='utf-8')
    forbidden = (
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
        'PASS: R15.17 static navigation consistency — 49 full-shell pages render exactly '
        'Quality / Technical Data / About as primary-nav direct links plus one Request a Quote CTA '
        'before JS; 404 stays script-free; runtime no longer mutates navigation.'
    )


if __name__ == '__main__':
    main()
