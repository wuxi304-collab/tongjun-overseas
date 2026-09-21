from pathlib import Path
import re

ROOT = Path('.')
FINAL_LABEL = 'Request a Quote →'


def fail(message):
    raise SystemExit('ERROR: ' + message)


def normalize_optional_link(text: str, class_name: str, page: str):
    pattern = re.compile(
        rf'<a class="{re.escape(class_name)}" href="/rfq">[^<]*</a>'
    )
    matches = pattern.findall(text)
    if len(matches) > 1:
        fail(f'{page}: expected at most one {class_name} RFQ link, found {len(matches)}')
    if not matches:
        return text, False
    final = f'<a class="{class_name}" href="/rfq">{FINAL_LABEL}</a>'
    return pattern.sub(final, text, count=1), True


def main():
    htmls = sorted(ROOT.glob('*.html'))
    if len(htmls) != 50:
        fail(f'expected 50 root HTML pages, found {len(htmls)}')

    changed = 0
    mobile_count = 0
    sticky_count = 0

    for page in htmls:
        original = page.read_text(encoding='utf-8')
        text, mobile_present = normalize_optional_link(original, 'mobile-rfq', page.name)
        text, sticky_present = normalize_optional_link(text, 'rfq-btn', page.name)

        mobile_count += int(mobile_present)
        sticky_count += int(sticky_present)

        if mobile_present and text.count(
            f'<a class="mobile-rfq" href="/rfq">{FINAL_LABEL}</a>'
        ) != 1:
            fail(f'{page.name}: canonical mobile-menu quote CTA missing or duplicated')

        if sticky_present and text.count(
            f'<a class="rfq-btn" href="/rfq">{FINAL_LABEL}</a>'
        ) != 1:
            fail(f'{page.name}: canonical sticky quote CTA missing or duplicated')

        if text != original:
            page.write_text(text, encoding='utf-8')
            changed += 1

    if mobile_count != 48:
        fail(f'expected 48 mobile-rfq nodes, found {mobile_count}')
    if sticky_count != 48:
        fail(f'expected 48 rfq-btn nodes, found {sticky_count}')

    print(
        f'PASS: R15.18 global CTA overlay — {changed} page(s) normalized; '
        f'{mobile_count} mobile-menu + {sticky_count} sticky quote actions now use '
        f'one canonical buyer label: {FINAL_LABEL}; structural exceptions preserved.'
    )


if __name__ == '__main__':
    main()
