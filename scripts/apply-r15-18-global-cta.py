from pathlib import Path
import re

ROOT = Path('.')
FINAL_LABEL = 'Request a Quote →'


def fail(message):
    raise SystemExit('ERROR: ' + message)


def normalize_link(text: str, class_name: str, page: str) -> str:
    pattern = re.compile(
        rf'<a class="{re.escape(class_name)}" href="/rfq">[^<]*</a>'
    )
    matches = pattern.findall(text)
    if len(matches) != 1:
        fail(f'{page}: expected one {class_name} RFQ link, found {len(matches)}')
    final = f'<a class="{class_name}" href="/rfq">{FINAL_LABEL}</a>'
    return pattern.sub(final, text, count=1)


def main():
    htmls = sorted(ROOT.glob('*.html'))
    if len(htmls) != 50:
        fail(f'expected 50 root HTML pages, found {len(htmls)}')

    changed = 0
    already = 0

    for page in htmls:
        if page.name == '404.html':
            continue

        original = page.read_text(encoding='utf-8')
        text = normalize_link(original, 'mobile-rfq', page.name)
        text = normalize_link(text, 'rfq-btn', page.name)

        if text.count(f'<a class="mobile-rfq" href="/rfq">{FINAL_LABEL}</a>') != 1:
            fail(f'{page.name}: final mobile-menu quote CTA missing or duplicated')
        if text.count(f'<a class="rfq-btn" href="/rfq">{FINAL_LABEL}</a>') != 1:
            fail(f'{page.name}: final sticky quote CTA missing or duplicated')

        if text != original:
            page.write_text(text, encoding='utf-8')
            changed += 1
        else:
            already += 1

    print(
        f'PASS: R15.18 global CTA overlay — {changed} full-shell pages normalized, '
        f'{already} already-final page(s); mobile menu and sticky action bar now use one '
        f'canonical buyer action: {FINAL_LABEL}.'
    )


if __name__ == '__main__':
    main()
