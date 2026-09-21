from pathlib import Path
import re

ROOT = Path('.')
RUNTIME_VERSION = '20260921-r15-17'


def fail(message):
    raise SystemExit('ERROR: ' + message)


def ensure_transition(text: str, old: str, new: str, page: str, label: str) -> str:
    old_count = text.count(old)
    new_count = text.count(new)
    if old_count == 1 and new_count == 0:
        return text.replace(old, new, 1)
    if old_count == 0 and new_count == 1:
        return text
    fail(
        f'{page}: invalid {label} transition state; '
        f'old={old_count}, final={new_count}'
    )


def ensure_nav_cta(text: str, page: str) -> str:
    final = '<a class="cta nav-cta" href="/rfq">Request a Quote <span>→</span></a>'
    if text.count(final) == 1:
        # Final first-frame CTA already present.
        return text

    pattern = re.compile(
        r'<a class="cta nav-cta" href="/rfq">[^<]*(?:<span>[^<]*</span>)?</a>'
    )
    matches = pattern.findall(text)
    if len(matches) != 1:
        fail(f'{page}: expected one legacy/final nav CTA, found {len(matches)}')
    return pattern.sub(final, text, count=1)


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
        text = original

        text = ensure_transition(
            text,
            '<a href="/capabilities">Capabilities</a>',
            '<a href="/quality">Quality</a>',
            page.name,
            'Quality nav link',
        )
        text = ensure_transition(
            text,
            '<a href="/resources">Resources</a>',
            '<a href="/technical-data">Technical Data</a>',
            page.name,
            'Technical Data nav link',
        )
        text = ensure_nav_cta(text, page.name)

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

        # Final first-frame contract: one direct Quality, one direct Technical Data,
        # one quote CTA. Mega-menu occurrences are intentionally excluded by exact
        # top-level markup matching.
        final_checks = {
            '<a href="/quality">Quality</a>': 'Quality',
            '<a href="/technical-data">Technical Data</a>': 'Technical Data',
            '<a class="cta nav-cta" href="/rfq">Request a Quote <span>→</span></a>': 'Request a Quote',
        }
        for markup, label in final_checks.items():
            if text.count(markup) != 1:
                fail(
                    f'{page.name}: final first-frame {label} markup count '
                    f'is {text.count(markup)}, expected 1'
                )

        if text != original:
            page.write_text(text, encoding='utf-8')
            changed += 1
        else:
            already_final += 1

    print(
        f'PASS: R15.17 static navigation overlay — {changed} full-shell pages normalized, '
        f'{already_final} already-final page(s) accepted; final Quality / Technical Data / '
        f'Request a Quote navigation is idempotent; runtime cache {RUNTIME_VERSION}.'
    )


if __name__ == '__main__':
    main()
