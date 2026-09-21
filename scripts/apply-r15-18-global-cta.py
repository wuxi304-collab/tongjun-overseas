from pathlib import Path
import re

ROOT = Path('.')
FINAL_LABEL = 'Request a Quote →'

MOBILE_RFQ = re.compile(
    r'<a class="mobile-rfq" href="/rfq">[^<]*</a>'
)
ACTIONBAR = re.compile(
    r'<div aria-label="Quick actions" class="mobile-actionbar">[\s\S]*?</div>'
)
RFQ_BTN = re.compile(
    r'<a class="rfq-btn" href="/rfq">[^<]*</a>'
)


def fail(message):
    raise SystemExit('ERROR: ' + message)


def normalize_optional_mobile(text: str, page: str):
    matches = MOBILE_RFQ.findall(text)
    if len(matches) > 1:
        fail(f'{page}: expected at most one mobile-rfq link, found {len(matches)}')
    if not matches:
        return text, False
    final = f'<a class="mobile-rfq" href="/rfq">{FINAL_LABEL}</a>'
    return MOBILE_RFQ.sub(final, text, count=1), True


def normalize_actionbars(text: str, page: str):
    bars = ACTIONBAR.findall(text)

    # resources.html carried a legacy contextual quick-action bar immediately
    # before </main> plus the normal global bar after the footer. Remove only
    # the legacy in-main duplicate and keep the global shell consistent.
    if page == 'resources.html' and len(bars) == 2:
        legacy = bars[0]
        marker = legacy + '</main>'
        if marker not in text:
            fail('resources.html: duplicate actionbar is not the expected in-main legacy bar')
        text = text.replace(marker, '</main>', 1)
        bars = ACTIONBAR.findall(text)

    if len(bars) > 1:
        fail(f'{page}: expected at most one global mobile-actionbar after cleanup, found {len(bars)}')
    if not bars:
        return text, False

    bar = bars[0]
    buttons = RFQ_BTN.findall(bar)
    if len(buttons) != 1:
        fail(f'{page}: expected exactly one rfq-btn inside mobile-actionbar, found {len(buttons)}')

    final_btn = f'<a class="rfq-btn" href="/rfq">{FINAL_LABEL}</a>'
    normalized_bar = RFQ_BTN.sub(final_btn, bar, count=1)
    text = text.replace(bar, normalized_bar, 1)
    return text, True


def main():
    htmls = sorted(ROOT.glob('*.html'))
    if len(htmls) != 50:
        fail(f'expected 50 root HTML pages, found {len(htmls)}')

    changed = 0
    mobile_count = 0
    actionbar_count = 0

    for page in htmls:
        original = page.read_text(encoding='utf-8')
        text, mobile_present = normalize_optional_mobile(original, page.name)
        text, actionbar_present = normalize_actionbars(text, page.name)

        mobile_count += int(mobile_present)
        actionbar_count += int(actionbar_present)

        if text != original:
            page.write_text(text, encoding='utf-8')
            changed += 1

    if mobile_count != 48:
        fail(f'expected 48 mobile-rfq controls, found {mobile_count}')
    if actionbar_count != 48:
        fail(f'expected 48 global mobile-actionbar controls, found {actionbar_count}')

    print(
        f'PASS: R15.18 global CTA overlay — {changed} page(s) normalized; '
        f'{mobile_count} mobile-menu and {actionbar_count} sticky quote actions now use '
        f'{FINAL_LABEL}; duplicate Resources mobile actionbar removed.'
    )


if __name__ == '__main__':
    main()
