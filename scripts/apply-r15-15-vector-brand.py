from pathlib import Path

ROOT = Path('.')


def fail(message):
    raise SystemExit('ERROR: ' + message)


def main():
    path = ROOT / 'products.html'
    if not path.is_file():
        fail('products.html missing')

    text = path.read_text(encoding='utf-8')
    old = '<div class="brand footer-brand"><span class="mark"></span><span>TONGJUN METAL TECH</span></div>'
    new = (
        '<div class="brand footer-brand tj-footer-brand">'
        '<span class="tj-brand-composite tj-brand-composite-footer">'
        '<img class="tj-brand-mark" src="/assets/tongjun-logo.svg?v=20260916-r13-1-safe" '
        'alt="" width="140" height="116" decoding="async" loading="lazy" />'
        '<span class="tj-brand-copy"><strong>TONGJUN</strong>'
        '<small>METAL TECH · EST. 2026</small></span>'
        '</span></div>'
    )

    if old in text:
        text = text.replace(old, new, 1)
    elif 'class="brand footer-brand tj-footer-brand"' not in text:
        fail('products.html legacy footer brand target missing')

    if text.count('class="brand footer-brand tj-footer-brand"') != 1:
        fail('products.html vector footer brand missing or duplicated')
    if 'assets/tongjun-logo.svg' not in text:
        fail('products.html native Tongjun SVG reference missing')

    path.write_text(text, encoding='utf-8')
    print('PASS: R15.15 products footer upgraded to native vector brand lockup.')


if __name__ == '__main__':
    main()
