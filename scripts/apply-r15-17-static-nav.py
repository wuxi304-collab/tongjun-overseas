from pathlib import Path
import re

ROOT = Path('.')
RUNTIME_VERSION = '20260921-r15-17'

NAV_TAIL = re.compile(
    r'<a href="/(?:capabilities|quality)">(?:Capabilities|Quality)</a>\s*'
    r'<a href="/(?:resources|technical-data)">(?:Resources|Technical Data)</a>\s*'
    r'<a href="/about">About</a>\s*</nav>'
)
FINAL_NAV_TAIL = (
    '<a href="/quality">Quality</a>\n'
    '<a href="/technical-data">Technical Data</a>\n'
    '<a href="/about">About</a>\n'
    '</nav>'
)
FINAL_CTA = '<a class="cta nav-cta" href="/rfq">Request a Quote <span>→</span></a>'


def fail(message):
    raise SystemExit('ERROR: ' + message)


def normalize_nav_tail(text: str, page: str) -> str:
    matches = list(NAV_TAIL.finditer(text))
    if len(matches) != 1:
        fail(f'{page}: expected exactly one primary-nav tail candidate, found {len(matches)}')
    return text[:matches[0].start()] + FINAL_NAV_TAIL + text[matches[0].end():]


def normalize_nav_cta(text: str, page: str) -> str:
    if text.count(FINAL_CTA) == 1:
        return text
    pattern = re.compile(
        r'<a class="cta nav-cta" href="/rfq">[^<]*(?:<span>[^<]*</span>)?</a>'
    )
    matches = pattern.findall(text)
    if len(matches) != 1:
        fail(f'{page}: expected exactly one nav CTA, found {len(matches)}')
    return pattern.sub(FINAL_CTA, text, count=1)


def main():
    htmls = sorted(ROOT.glob('*.html'))
    if len(htmls) != 50:
        fail(f'expected 50 root HTML pages, found {len(htmls)}')

    changed = 0
    already_final = 0

    for page in htmls:
        if page.name == '404.html':
            continue

        original = page.read_text(encoding='utf-8')
        text = normalize_nav_tail(original, page.name)
        text = normalize_nav_cta(text, page.name)

        runtime_pattern = re.compile(
            r'(assets/brand-v34\.152\.js)(?:\?v=[A-Za-z0-9._-]+)?'
        )
        text, count = runtime_pattern.subn(
            rf'\1?v={RUNTIME_VERSION}',
            text,
        )
        if count != 1:
            fail(
                f'{page.name}: expected exactly one brand runtime reference, found {count}'
            )

        # Verify the exact direct-nav tail after normalization.
        if text.count(FINAL_NAV_TAIL) != 1:
            fail(f'{page.name}: final primary-nav tail missing or duplicated')
        if text.count(FINAL_CTA) != 1:
            fail(f'{page.name}: final Request a Quote CTA missing or duplicated')

        if text != original:
            page.write_text(text, encoding='utf-8')
            changed += 1
        else:
            already_final += 1

    print(
        f'PASS: R15.17 static navigation overlay — {changed} full-shell pages normalized, '
        f'{already_final} already-final page(s) accepted; direct primary-nav tail is now '
        f'Quality / Technical Data / About with one Request a Quote CTA; runtime cache {RUNTIME_VERSION}.'
    )


if __name__ == '__main__':
    main()
