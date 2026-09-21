from pathlib import Path
import re

ROOT = Path('.')
VERSION = '20260921-r15-16'


def fail(message):
    raise SystemExit('ERROR: ' + message)


def main():
    htmls = sorted(ROOT.glob('*.html'))
    if len(htmls) != 50:
        fail(f'expected 50 root HTML pages, found {len(htmls)}')

    changed = 0
    pattern = re.compile(r'(assets/brand-v34\.152\.js)(?:\?v=[A-Za-z0-9._-]+)?')
    for page in htmls:
        text = page.read_text(encoding='utf-8')
        updated, count = pattern.subn(rf'\1?v={VERSION}', text)
        expected = 0 if page.name == '404.html' else 1
        if count != expected:
            fail(f'{page.name}: expected {expected} brand runtime reference(s), found {count}')
        if updated != text:
            page.write_text(updated, encoding='utf-8')
            changed += 1

    print(f'PASS: R15.16 runtime cache overlay — {changed} page(s) updated to brand runtime {VERSION}.')


if __name__ == '__main__':
    main()
