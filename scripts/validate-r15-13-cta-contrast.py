from html.parser import HTMLParser
from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
HERO_CLASSES = {'pagehero', 'landinghero', 'articlehero', 'tech-hero'}
EXPECTED_GHOST_CTAS = 19


def fail(message):
    raise SystemExit('ERROR: ' + message)


class HeroGhostParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.hero_depth = 0
        self.count = 0

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        classes = set((data.get('class') or '').split())
        is_hero = bool(classes & HERO_CLASSES)
        self.stack.append(is_hero)
        if is_hero:
            self.hero_depth += 1
        if tag == 'a' and self.hero_depth:
            if {'cta', 'ghost'} <= classes:
                self.count += 1

    def handle_startendtag(self, tag, attrs):
        data = dict(attrs)
        classes = set((data.get('class') or '').split())
        if tag == 'a' and self.hero_depth and {'cta', 'ghost'} <= classes:
            self.count += 1

    def handle_endtag(self, tag):
        if self.stack:
            is_hero = self.stack.pop()
            if is_hero:
                self.hero_depth -= 1


def main():
    htmls = sorted(ROOT.glob('*.html'))
    if len(htmls) != 50:
        fail(f'expected 50 root HTML pages, found {len(htmls)}')

    total = 0
    pages = []
    for page in htmls:
        parser = HeroGhostParser()
        parser.feed(page.read_text(encoding='utf-8'))
        if parser.count:
            total += parser.count
            pages.append((page.name, parser.count))

    if total != EXPECTED_GHOST_CTAS:
        fail(f'expected {EXPECTED_GHOST_CTAS} light-hero ghost CTAs, found {total}: {pages}')

    css_path = ROOT / 'assets' / 'brand-v34.152-r14.css'
    if not css_path.is_file():
        fail('consolidated stylesheet missing')
    css = css_path.read_text(encoding='utf-8')
    markers = (
        'V34.152 R15.13',
        ':where(.pagehero,.landinghero,.articlehero,.tech-hero) .cta.ghost',
        'background:#fff!important',
        'color:#10263c!important',
        'border-color:#7b8997!important',
        'background:#10263c!important',
    )
    for marker in markers:
        if marker not in css:
            fail(f'R15.13 CTA contrast CSS marker missing: {marker}')

    # R15.13 must never change the approved dark homepage hero ghost treatment.
    tail = ROOT / 'assets' / 'brand-v34.152-r15-13-tail.css'
    if tail.is_file():
        tail_text = tail.read_text(encoding='utf-8')
        if 'body.brand-v34 .hero .cta.ghost' in tail_text:
            fail('R15.13 must not override the dark homepage hero ghost CTA')

    print(
        f'PASS: R15.13 hero CTA contrast gate — {total} secondary CTAs across {len(pages)} light technical-hero pages '
        'use scoped dark-on-white treatment; dark homepage hero remains untouched.'
    )


if __name__ == '__main__':
    main()
