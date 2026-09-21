from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')


def fail(message):
    raise SystemExit('ERROR: ' + message)


def main():
    standards = ROOT / 'standards.html'
    if not standards.is_file():
        fail('standards.html missing')
    text = standards.read_text(encoding='utf-8')
    if text.count('class="r15-12-table-scroll"') != 1:
        fail('R15.12 standards scroll wrapper missing or duplicated')
    if '<table class="data-table standards">' not in text:
        fail('standards table missing inside R15.12 wrapper')
    if 'tabindex="0"' not in text:
        fail('R15.12 standards scroll wrapper must remain keyboard focusable')

    css_path = ROOT / 'assets' / 'tongjun-site-r15-19.css'
    if not css_path.is_file():
        css_path = ROOT / 'assets' / 'brand-v34.152-r14.css'
    if not css_path.is_file():
        fail('release stylesheet missing')
    css = css_path.read_text(encoding='utf-8')
    markers = (
        'V34.152 R15.12',
        'data-page="about"] .visual-frame',
        'data-page="materials"] .visual-frame',
        'data-page="product-forms"] .visual-frame',
        '.r15-12-table-scroll',
        'min-height:0!important',
        'aspect-ratio:16/10!important',
        'overflow-x:auto',
    )
    for marker in markers:
        if marker not in css:
            fail(f'R15.12 mobile layout CSS marker missing: {marker}')

    print('PASS: R15.12 mobile layout gate — visual-frame overrides and local standards scroll region are present.')


if __name__ == '__main__':
    main()
