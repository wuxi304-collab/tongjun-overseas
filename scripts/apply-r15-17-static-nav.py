from pathlib import Path
import re

ROOT = Path('.')
RUNTIME_VERSION = '20260921-r15-17'


def fail(message):
    raise SystemExit('ERROR: ' + message)


def replace_once(text, old, new, page):
    count = text.count(old)
    if count != 1:
        fail(f'{page}: expected exactly one occurrence of {old!r}, found {count}')
    return text.replace(old, new, 1)


def main():
    htmls = sorted(ROOT.glob('*.html'))
    if len(htmls) != 50:
        fail(f'expected 50 root HTML pages, found {len(htmls)}')

    changed = 0
    for page in htmls:
        if page.name == '404.html':
            continue
        text = page.read_text(encoding='utf-8')

        text = replace_once(
            text,
            '<a href="/capabilities">Capabilities</a>',
            '<a href="/quality">Quality</a>',
            page.name,
        )
        text = replace_once(
            text,
            '<a href="/resources">Resources</a>',
            '<a href="/technical-data">Technical Data</a>',
            page.name,
        )

        cta_pattern = re.compile(
            r'<a class="cta nav-cta" href="/rfq">[^<]*(?:<span>[^<]*</span>)?</a>'
        )
        updated, count = cta_pattern.subn(
            '<a class="cta nav-cta" href="/rfq">Request a Quote <span>→</span></a>',
            text,
            count=1,
        )
        if count != 1:
            fail(f'{page.name}: expected exactly one nav CTA, found {count}')
        text = updated

        runtime_pattern = re.compile(r'(assets/brand-v34\.152\.js)(?:\?v=[A-Za-z0-9._-]+)?')
        text, count = runtime_pattern.subn(rf'\1?v={RUNTIME_VERSION}', text)
        if count != 1:
            fail(f'{page.name}: expected exactly one brand runtime reference, found {count}')

        page.write_text(text, encoding='utf-8')
        changed += 1

    print(
        f'PASS: R15.17 static navigation overlay — {changed} full-shell pages now render final '
        f'Quality / Technical Data / Request a Quote navigation before JS; runtime cache {RUNTIME_VERSION}.'
    )


if __name__ == '__main__':
    main()
