from pathlib import Path
import re

ROOT = Path('.')
BUNDLE = ROOT / 'assets' / 'tongjun-site-r15-19.css'
VERSION = '20260921-r15-19'

PARTS = [
    'assets/site.css',
    'assets/thank-you.css',
    'assets/polish.css',
    'assets/polish-v34.139.css',
    'assets/polish-v34.139-fix.css',
    'assets/brand-v34.152-r14.css',
    'assets/r15-20-visual-density.css',
]
TARGET_NAMES = {Path(p).name for p in PARTS}
LINK_RE = re.compile(r'<link\b[^>]*>', re.I)
HREF_RE = re.compile(r'\bhref=["\']([^"\']+)["\']', re.I)
REL_RE = re.compile(r'\brel=["\']([^"\']+)["\']', re.I)


def fail(message):
    raise SystemExit('ERROR: ' + message)


def is_target_stylesheet(tag: str) -> bool:
    href = HREF_RE.search(tag)
    rel = REL_RE.search(tag)
    if not href or not rel or 'stylesheet' not in rel.group(1).lower().split():
        return False
    path = href.group(1).split('?', 1)[0].split('#', 1)[0]
    return Path(path).name in TARGET_NAMES


def build_bundle():
    chunks = [
        '/* V34.152 R15.19 base + V34.152 R15.20 visual candidate — production CSS bundle. Source order is release-critical. */\n'
    ]
    for rel in PARTS:
        path = ROOT / rel
        if not path.is_file():
            fail(f'CSS bundle source missing: {rel}')
        chunks.append(f'\n/* R15.19 SOURCE: {rel} */\n')
        chunks.append(path.read_text(encoding='utf-8').rstrip() + '\n')
    BUNDLE.write_text(''.join(chunks), encoding='utf-8')
    size = BUNDLE.stat().st_size
    if not (220 * 1024 <= size <= 360 * 1024):
        fail(f'CSS bundle size outside expected release range: {size} bytes')
    return size


def rewrite_html():
    htmls = sorted(ROOT.glob('*.html'))
    if len(htmls) != 50:
        fail(f'expected 50 root HTML pages, found {len(htmls)}')

    bundle_tag = f'<link href="/assets/tongjun-site-r15-19.css?v={VERSION}" rel="stylesheet"/>'
    counts = []
    for page in htmls:
        text = page.read_text(encoding='utf-8')
        text, footer_fixes = FOOTER_BRAND_FIX_RE.subn(r'\\1\\2', text, count=1)
        tags = list(LINK_RE.finditer(text))
        targets = [m for m in tags if is_target_stylesheet(m.group(0))]
        expected = 6 if page.name == 'thank-you.html' else 5
        if len(targets) != expected:
            fail(f'{page.name}: expected {expected} source stylesheet links before bundling, found {len(targets)}')

        first = targets[0]
        pieces = []
        cursor = 0
        inserted = False
        target_spans = {(m.start(), m.end()) for m in targets}
        for m in tags:
            span = (m.start(), m.end())
            if span not in target_spans:
                continue
            pieces.append(text[cursor:m.start()])
            if not inserted:
                pieces.append(bundle_tag)
                inserted = True
            cursor = m.end()
        pieces.append(text[cursor:])
        updated = ''.join(pieces)

        if updated.count('tongjun-site-r15-19.css') != 1:
            fail(f'{page.name}: bundle link count is not exactly one')
        for name in TARGET_NAMES:
            if re.search(rf'<link\b[^>]*href=["\'][^"\']*{re.escape(name)}', updated, re.I):
                fail(f'{page.name}: source stylesheet link survived bundling: {name}')

        page.write_text(updated, encoding='utf-8')
        counts.append((page.name, len(targets)))

    print(f'PASS: R15.19 CSS bundle overlay — 50 pages now load one release stylesheet; replaced {sum(c for _, c in counts)} source stylesheet links; malformed footer-brand closure normalized where present.')


def main():
    size = build_bundle()
    rewrite_html()
    print(f'PASS: R15.20 visual candidate bundle materialized — {BUNDLE.name}, {size // 1024} KB, {len(PARTS)} ordered source parts.')


if __name__ == '__main__':
    main()
