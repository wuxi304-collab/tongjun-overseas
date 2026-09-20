from html.parser import HTMLParser
from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
HERO_CLASSES = {'pagehero', 'landinghero', 'articlehero', 'tech-hero'}
VOID_TAGS = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
EXPECTED_GHOST_CTAS = 19
TEXT_HEX = '#10263c'
BG_HEX = '#ffffff'


def luminance(hex_color: str) -> float:
    value = hex_color.lstrip('#')
    rgb = [int(value[i:i+2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(a: str, b: str) -> float:
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


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
        if tag == 'a' and self.hero_depth and {'cta', 'ghost'} <= classes:
            self.count += 1

        if tag in VOID_TAGS:
            return
        is_hero = bool(classes & HERO_CLASSES)
        self.stack.append((tag, is_hero))
        if is_hero:
            self.hero_depth += 1

    def handle_startendtag(self, tag, attrs):
        data = dict(attrs)
        classes = set((data.get('class') or '').split())
        if tag == 'a' and self.hero_depth and {'cta', 'ghost'} <= classes:
            self.count += 1

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] != tag:
                continue
            closing = self.stack[index:]
            self.stack = self.stack[:index]
            for _, is_hero in closing:
                if is_hero:
                    self.hero_depth -= 1
            return


def main():
    htmls = sorted(ROOT.glob('*.html'))
    if len(htmls) != 50:
        fail(f'expected 50 root HTML pages, found {len(htmls)}')

    total = 0
    pages = []
    for page in htmls:
        parser = HeroGhostParser()
        parser.feed(page.read_text(encoding='utf-8'))
        if parser.hero_depth != 0:
            fail(f'{page.name}: unbalanced technical-hero nesting after parse')
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

    ratio = contrast_ratio(TEXT_HEX, BG_HEX)
    if ratio < 4.5:
        fail(f'R15.13 secondary CTA text contrast below WCAG AA: {ratio:.2f}:1')

    tail = ROOT / 'assets' / 'brand-v34.152-r15-13-tail.css'
    if tail.is_file():
        tail_text = tail.read_text(encoding='utf-8')
        if 'body.brand-v34 .hero .cta.ghost' in tail_text:
            fail('R15.13 must not override the dark homepage hero ghost CTA')

    print(
        f'PASS: R15.13 hero CTA contrast gate — {total} secondary CTAs across {len(pages)} light technical-hero pages '
        f'use scoped dark-on-white treatment at {ratio:.2f}:1 contrast; dark homepage hero remains untouched.'
    )


if __name__ == '__main__':
    main()
