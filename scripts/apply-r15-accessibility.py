from pathlib import Path
import re

ROOT = Path('.')
HTMLS = sorted(ROOT.glob('*.html'))

BODY_OPEN = re.compile(r'(<body\b[^>]*>)', re.I)
MAIN_OPEN = re.compile(r'<main\b([^>]*)>', re.I)
NAV_OPEN = re.compile(r'<nav\b([^>]*)>', re.I)
CSS_OLD = 'brand-v34.152-r14.css?v=20260916-r14-1'
CSS_NEW = 'brand-v34.152-r14.css?v=20260916-r15-4'


def patch_page(path: Path) -> bool:
    text = path.read_text(encoding='utf-8')
    original = text

    # R15.4 changes focus/reduced-motion CSS, so every page must move to a fresh
    # cache key after the R14 overlay has normalized the stylesheet reference.
    if CSS_OLD in text:
        text = text.replace(CSS_OLD, CSS_NEW)
    elif CSS_NEW not in text:
        raise SystemExit(f'ERROR: expected brand stylesheet reference missing in {path.name}')

    if 'class="skip-link"' not in text and "class='skip-link'" not in text:
        m = BODY_OPEN.search(text)
        if not m:
            raise SystemExit(f'ERROR: body element missing in {path.name}')
        skip = '<a class="skip-link" href="#main-content">Skip to content</a>'
        text = text[:m.end()] + skip + text[m.end():]

    main = MAIN_OPEN.search(text)
    if not main:
        raise SystemExit(f'ERROR: main landmark missing in {path.name}')
    main_tag = main.group(0)
    if not re.search(r'\bid=["\']main-content["\']', main_tag, re.I):
        if re.search(r'\bid=["\'][^"\']+["\']', main_tag, re.I):
            # Preserve an existing main id and make the skip link target it rather than creating duplicate semantics.
            existing = re.search(r'\bid=["\']([^"\']+)["\']', main_tag, re.I).group(1)
            text = text.replace('href="#main-content"', f'href="#{existing}"', 1)
        else:
            replacement = '<main id="main-content"' + main.group(1) + '>'
            text = text[:main.start()] + replacement + text[main.end():]

    navs = list(NAV_OPEN.finditer(text))
    if navs and not any(re.search(r'\b(?:aria-label|aria-labelledby)=', n.group(0), re.I) for n in navs):
        first = navs[0]
        replacement = '<nav aria-label="Primary navigation"' + first.group(1) + '>'
        text = text[:first.start()] + replacement + text[first.end():]

    # Release assertions.
    if text.count(CSS_NEW) != 1:
        raise SystemExit(f'ERROR: expected exactly one R15.4 stylesheet cache reference in {path.name}')
    if 'class="skip-link"' not in text and "class='skip-link'" not in text:
        raise SystemExit(f'ERROR: skip link missing after R15 accessibility patch in {path.name}')
    main = MAIN_OPEN.search(text)
    if not main or not re.search(r'\bid=["\'][^"\']+["\']', main.group(0), re.I):
        raise SystemExit(f'ERROR: named main landmark missing after R15 accessibility patch in {path.name}')
    navs = list(NAV_OPEN.finditer(text))
    if navs and not any(re.search(r'\b(?:aria-label|aria-labelledby)=', n.group(0), re.I) for n in navs):
        raise SystemExit(f'ERROR: accessible navigation name missing after R15 patch in {path.name}')

    if text != original:
        path.write_text(text, encoding='utf-8')
        return True
    return False


def main():
    if len(HTMLS) != 50:
        raise SystemExit(f'ERROR: expected 50 root HTML files, found {len(HTMLS)}')
    changed = sum(1 for page in HTMLS if patch_page(page))
    print(f'PASS: R15.4 accessibility normalization applied to {changed} page(s); 50-page landmark and cache-version gate satisfied.')


if __name__ == '__main__':
    main()
