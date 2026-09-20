from pathlib import Path

ROOT = Path('.')


def fail(message):
    raise SystemExit('ERROR: ' + message)


def main():
    path = ROOT / 'standards.html'
    text = path.read_text(encoding='utf-8')

    marker = '<table class="data-table standards">'
    if marker not in text:
        fail('standards table not found')

    if 'class="r15-12-table-scroll"' not in text:
        text = text.replace(
            marker,
            '<div class="r15-12-table-scroll" tabindex="0" aria-label="Standards table; scroll horizontally on smaller screens">' + marker,
            1,
        )
        close = '</tbody></table>'
        if close not in text:
            fail('standards table closing tag not found')
        text = text.replace(close, close + '</div>', 1)

    if text.count('class="r15-12-table-scroll"') != 1:
        fail('expected exactly one R15.12 standards scroll wrapper')
    if 'tabindex="0"' not in text or 'scroll horizontally' not in text:
        fail('standards scroll wrapper is missing keyboard/mobile affordance')

    path.write_text(text, encoding='utf-8')
    print('PASS: R15.12 mobile layout overlay — standards table wrapped in a keyboard-focusable local scroll region.')


if __name__ == '__main__':
    main()
