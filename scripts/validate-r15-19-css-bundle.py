from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
BUNDLE = ROOT / 'assets' / 'tongjun-site-r15-19.css'
VERSION = '20260921-r15-19'
PARTS = [
    'assets/site.css',
    'assets/thank-you.css',
    'assets/polish.css',
    'assets/polish-v34.139.css',
    'assets/polish-v34.139-fix.css',
    'assets/brand-v34.152-r14.css',
]


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stylesheets = []

    def handle_starttag(self, tag, attrs):
        self._read(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self._read(tag, attrs)

    def _read(self, tag, attrs):
        if tag != 'link':
            return
        data = dict(attrs)
        rel = set((data.get('rel') or '').lower().split())
        if 'stylesheet' in rel and data.get('href'):
            self.stylesheets.append(data['href'])


def fail(message):
    raise SystemExit('ERROR: ' + message)


def main():
    htmls = sorted(ROOT.glob('*.html'))
    if len(htmls) != 50:
        fail(f'expected 50 root HTML pages, found {len(htmls)}')
    if not BUNDLE.is_file():
        fail('R15.19 CSS bundle missing')

    css = BUNDLE.read_text(encoding='utf-8')
    previous = -1
    for rel in PARTS:
        marker = f'R15.19 SOURCE: {rel}'
        pos = css.find(marker)
        if pos < 0:
            fail(f'CSS bundle source marker missing: {rel}')
        if pos <= previous:
            fail(f'CSS bundle source order drifted at: {rel}')
        previous = pos

    required_markers = (
        'V34.152 R15.19',
        'V34.152 R15.12',
        'V34.152 R15.13',
        'body.brand-v34 .skip-link',
        ':focus-visible',
        'prefers-reduced-motion: reduce',
        '.r15-12-table-scroll',
        ':where(.pagehero,.landinghero,.articlehero,.tech-hero) .cta.ghost',
    )
    for marker in required_markers:
        if marker not in css:
            fail(f'R15.19 bundle lost release CSS marker: {marker}')

    for page in htmls:
        parser = Parser()
        parser.feed(page.read_text(encoding='utf-8'))
        if len(parser.stylesheets) != 1:
            fail(f'{page.name}: expected one stylesheet request, found {parser.stylesheets}')
        href = parser.stylesheets[0]
        if Path(urlsplit(href).path).name != BUNDLE.name or f'v={VERSION}' not in href:
            fail(f'{page.name}: wrong R15.19 stylesheet href: {href}')

    strict_artifact = not (ROOT / 'scripts').is_dir()
    if strict_artifact:
        public_css = sorted(p.name for p in (ROOT / 'assets').glob('*.css'))
        if public_css != [BUNDLE.name]:
            fail(f'R15.19 final artifact must ship exactly one CSS file: {public_css}')

    print(
        f'PASS: R15.19 CSS bundle gate — 50 pages use one versioned stylesheet; six source layers preserve release order'
        + ('; final artifact contains no source-only CSS.' if strict_artifact else '.')
    )


if __name__ == '__main__':
    main()
