from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
BUNDLE = 'tongjun-site-r15-19.css'


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
        href = data.get('href') or ''
        if 'stylesheet' in rel and href:
            self.stylesheets.append(href)


def fail(message):
    raise SystemExit('ERROR: ' + message)


def main():
    if not ROOT.is_dir():
        fail(f'public root missing: {ROOT}')
    htmls = sorted(ROOT.glob('*.html'))
    if len(htmls) != 50:
        fail(f'expected 50 root HTML pages, found {len(htmls)}')

    for page in htmls:
        parser = Parser()
        parser.feed(page.read_text(encoding='utf-8'))
        if len(parser.stylesheets) != 1:
            fail(f'{page.name}: expected exactly one public stylesheet link, found {parser.stylesheets}')
        if Path(urlsplit(parser.stylesheets[0]).path).name != BUNDLE:
            fail(f'{page.name}: unexpected public stylesheet: {parser.stylesheets[0]}')

    assets = ROOT / 'assets'
    bundle = assets / BUNDLE
    if not bundle.is_file():
        fail('R15.19 CSS bundle missing before prune')

    removed = []
    for path in sorted(assets.glob('*.css')):
        if path.name == BUNDLE:
            continue
        removed.append((path.name, path.stat().st_size))
        path.unlink()

    remaining = sorted(p.name for p in assets.glob('*.css'))
    if remaining != [BUNDLE]:
        fail(f'unexpected public CSS set after prune: {remaining}')

    print(
        f'PASS: R15.19 public CSS hygiene — one shipped stylesheet; removed {len(removed)} source-only CSS file(s) / '
        f'{sum(size for _, size in removed) // 1024} KB.'
    )


if __name__ == '__main__':
    main()
