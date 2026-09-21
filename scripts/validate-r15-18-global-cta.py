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
    for page in htmls:
        text = page.read_text(encoding='utf-8')
        if page.name == '404.html':
            if 'mobile-rfq' in text or 'rfq-btn' in text:
                bad.append((page.name, '404-global-cta-leak'))
            continue

        mobile = extract(text, 'mobile-rfq')
        sticky = extract(text, 'rfq-btn')
        expected = [('/rfq', FINAL_LABEL)]
        if mobile != expected:
            bad.append((page.name, 'mobile-rfq', mobile))
        if sticky != expected:
            bad.append((page.name, 'rfq-btn', sticky))

        # Header must remain aligned with the same commercial intent.
        if 'Request a Quote' not in text:
            bad.append((page.name, 'header-quote-label-missing'))

        # Context-specific technical CTAs remain allowed elsewhere.
        if 'Request Technical Review' not in text:
            bad.append((page.name, 'technical-review-prefooter-missing'))

    if bad:
        fail(f'R15.18 global CTA consistency mismatch: {bad[:20]}')

    print(
        'PASS: R15.18 global CTA consistency — 49 full-shell pages use Request a Quote '
        'for mobile-menu and sticky global actions, while technical-review CTAs remain '
        'available in contextual page content.'
    )


if __name__ == '__main__':
    main()
