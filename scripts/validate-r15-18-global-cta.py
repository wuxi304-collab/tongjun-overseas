from pathlib import Path
import re
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
BASE_PREFIX = '/tongjun-overseas'
FINAL_LABEL = 'Request a Quote →'


def fail(message):
    raise SystemExit('ERROR: ' + message)


def normalize_href(value: str) -> str:
    if value == BASE_PREFIX:
        return '/'
    if value.startswith(BASE_PREFIX + '/'):
        return value[len(BASE_PREFIX):]
    return value


def extract(text: str, class_name: str):
    pattern = re.compile(
        rf'<a class="{re.escape(class_name)}" href="([^"]+)">([^<]*)</a>'
    )
    return [
        (normalize_href(href), ' '.join(label.split()))
        for href, label in pattern.findall(text)
    ]


def main():
    htmls = sorted(ROOT.glob('*.html'))
    if len(htmls) != 50:
        fail(f'expected 50 root HTML pages, found {len(htmls)}')

    bad = []
    mobile_total = 0
    sticky_total = 0

    for page in htmls:
        text = page.read_text(encoding='utf-8')
        mobile = extract(text, 'mobile-rfq')
        sticky = extract(text, 'rfq-btn')

        mobile_total += len(mobile)
        sticky_total += len(sticky)

        for label, rows in (('mobile-rfq', mobile), ('rfq-btn', sticky)):
            if len(rows) > 1:
                bad.append((page.name, label, 'duplicate', rows))
                continue
            if rows and rows != [('/rfq', FINAL_LABEL)]:
                bad.append((page.name, label, rows))

        if page.name != '404.html' and 'Request a Quote' not in text:
            bad.append((page.name, 'header-quote-label-missing'))

    if mobile_total != 48:
        bad.append(('site', 'mobile-rfq-total', mobile_total))
    if sticky_total != 48:
        bad.append(('site', 'rfq-btn-total', sticky_total))

    if bad:
        fail(f'R15.18 global CTA consistency mismatch: {bad[:20]}')

    print(
        'PASS: R15.18 global CTA consistency — 48 mobile-menu and 48 sticky global '
        'quote actions use Request a Quote → where those controls exist; structural '
        'exceptions remain intact and full-shell header CTAs stay aligned.'
    )


if __name__ == '__main__':
    main()
