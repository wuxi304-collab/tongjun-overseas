from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
BASE_PREFIX = '/tongjun-overseas'
FINAL_LABEL = 'Request a Quote →'

MOBILE_RFQ = re.compile(
    r'<a class="mobile-rfq" href="([^"]+)">([^<]*)</a>'
)
ACTIONBAR = re.compile(
    r'<div aria-label="Quick actions" class="mobile-actionbar">[\s\S]*?</div>'
)
RFQ_BTN = re.compile(
    r'<a class="rfq-btn" href="([^"]+)">([^<]*)</a>'
)


def fail(message):
    raise SystemExit('ERROR: ' + message)


def normalize_href(value: str) -> str:
    path = urlsplit(value).path
    if path == BASE_PREFIX:
        return '/'
    if path.startswith(BASE_PREFIX + '/'):
        return path[len(BASE_PREFIX):]
    return path


def normalize_label(value: str) -> str:
    return ' '.join(value.split())


def main():
    htmls = sorted(ROOT.glob('*.html'))
    if len(htmls) != 50:
        fail(f'expected 50 root HTML pages, found {len(htmls)}')

    bad = []
    mobile_total = 0
    actionbar_total = 0

    for page in htmls:
        text = page.read_text(encoding='utf-8')

        mobile = [
            (normalize_href(href), normalize_label(label))
            for href, label in MOBILE_RFQ.findall(text)
        ]
        if len(mobile) > 1:
            bad.append((page.name, 'mobile-rfq-duplicate', mobile))
        elif mobile and mobile != [('/rfq', FINAL_LABEL)]:
            bad.append((page.name, 'mobile-rfq', mobile))
        mobile_total += len(mobile)

        bars = ACTIONBAR.findall(text)
        if len(bars) > 1:
            bad.append((page.name, 'mobile-actionbar-duplicate', len(bars)))
        elif bars:
            buttons = [
                (normalize_href(href), normalize_label(label))
                for href, label in RFQ_BTN.findall(bars[0])
            ]
            if buttons != [('/rfq', FINAL_LABEL)]:
                bad.append((page.name, 'mobile-actionbar-rfq', buttons))
        actionbar_total += len(bars)

        if page.name != '404.html' and 'Request a Quote' not in text:
            bad.append((page.name, 'header-quote-label-missing'))

    if mobile_total != 48:
        bad.append(('site', 'mobile-rfq-total', mobile_total))
    if actionbar_total != 48:
        bad.append(('site', 'mobile-actionbar-total', actionbar_total))

    if bad:
        fail(f'R15.18 global CTA consistency mismatch: {bad[:20]}')

    print(
        'PASS: R15.18 global CTA consistency — 48 mobile-menu and 48 sticky global '
        'quote controls use Request a Quote →; Resources has one mobile actionbar; '
        'structural exceptions remain intact.'
    )


if __name__ == '__main__':
    main()
