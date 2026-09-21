from html.parser import HTMLParser
from pathlib import Path
import re
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
EXPECTED_PAGES = 50
EXPECTED_HEADER_LOCKUPS = 50
EXPECTED_FOOTER_LOCKUPS_MIN = 49


def fail(message):
    raise SystemExit('ERROR: ' + message)


class BrandParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack=[]
        self.in_header=False
        self.in_footer=False
        self.header_lockups=0
        self.footer_lockups=0
        self.bad_srcs=[]
        self.header_text=[]

    def handle_starttag(self, tag, attrs):
        data=dict(attrs)
        classes=set((data.get('class') or '').split())
        if tag=='header':
            self.in_header=True
        if tag=='footer':
            self.in_footer=True

        if tag=='span' and 'tj-brand-composite' in classes:
            if self.in_header:
                self.header_lockups += 1
            if self.in_footer:
                self.footer_lockups += 1

        if tag=='img' and 'tj-brand-mark' in classes:
            src=data.get('src','')
            if 'assets/tongjun-logo.svg' not in src:
                self.bad_srcs.append(src)

        self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag=='header':
            self.in_header=False
        if tag=='footer':
            self.in_footer=False
        if self.stack:
            self.stack.pop()


def main():
    htmls=sorted(ROOT.glob('*.html'))
    if len(htmls)!=EXPECTED_PAGES:
        fail(f'expected {EXPECTED_PAGES} root HTML pages, found {len(htmls)}')

    header_total=0
    footer_total=0
    bad=[]
    text_fail=[]
    for page in htmls:
        parser=BrandParser()
        text=page.read_text(encoding='utf-8')
        parser.feed(text)
        header_total += parser.header_lockups
        footer_total += parser.footer_lockups
        if parser.bad_srcs:
            bad.append((page.name, parser.bad_srcs))
        if page.name!='404.html':
            if '<strong>TONGJUN</strong>' not in text or 'METAL TECH · EST. 2026' not in text:
                text_fail.append(page.name)

    if header_total!=EXPECTED_HEADER_LOCKUPS:
        fail(f'expected {EXPECTED_HEADER_LOCKUPS} header vector lockups, found {header_total}')
    if footer_total<EXPECTED_FOOTER_LOCKUPS_MIN:
        fail(f'expected at least {EXPECTED_FOOTER_LOCKUPS_MIN} footer vector lockups, found {footer_total}')
    if bad:
        fail(f'brand mark image does not use native SVG: {bad[:10]}')
    if text_fail:
        fail(f'brand copy missing on page(s): {text_fail}')

    css_path=ROOT/'assets'/'brand-v34.152-r14.css'
    if not css_path.is_file():
        fail('consolidated stylesheet missing')
    css=css_path.read_text(encoding='utf-8')
    for marker in (
        'V34.152 R15.15',
        '.navin>.brand>span.tj-brand-composite',
        'display:inline-flex!important',
        '.navin>.brand .tj-brand-mark',
        '.tj-footer-brand .tj-brand-composite',
    ):
        if marker not in css:
            fail(f'R15.15 vector brand CSS marker missing: {marker}')

    searchable=[]
    for path in list(ROOT.glob('*.html')) + list((ROOT/'assets').rglob('*.css')) + list((ROOT/'assets').rglob('*.js')):
        if not path.is_file():
            continue
        try:
            searchable.append((str(path.relative_to(ROOT)), path.read_text(encoding='utf-8')))
        except UnicodeDecodeError:
            pass
    legacy=[name for name,text in searchable if 'columbus-logo-v2.webp' in text or 'columbus-mark.webp' in text]
    if legacy:
        fail(f'legacy raster brand reference(s) remain: {legacy}')

    svg=ROOT/'assets'/'tongjun-logo.svg'
    if not svg.is_file() or svg.stat().st_size < 1000:
        fail('native Tongjun SVG brand asset missing or unexpectedly small')
    svg_text=svg.read_text(encoding='utf-8')
    if '<svg' not in svg_text or 'viewBox=' not in svg_text:
        fail('native Tongjun SVG is malformed')

    print(
        f'PASS: R15.15 vector brand gate — {header_total} header lockups and {footer_total} footer lockups '
        'use native Tongjun SVG + live HTML brand copy; no legacy raster logo references remain.'
    )


if __name__ == '__main__':
    main()
