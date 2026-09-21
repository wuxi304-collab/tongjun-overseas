from pathlib import Path
import os
import re
import shutil
import subprocess

ROOT = Path('.')
OUT = Path('_site')
BASE = os.environ.get('BASE_PATH', '/tongjun-overseas').rstrip('/')

# Pages is a temporary public mirror. Keep internal sales/ops, server-only
# material and build metadata out of the artifact even when present in source.
SKIP_TOP_LEVEL = {
    '.git', '.github', '.sync', '.vercel', 'node_modules', 'scripts', 'tests',
    'api', 'ops', 'lib', '_site',
}
SKIP_NAMES = {'CNAME', 'R7_TEST.txt', 'package.json', 'vercel.json', 'VISUAL_MANIFEST_R15_7.json', 'RELEASE_R15_18.json'}
TEXT_EXT = {'.html', '.css', '.js', '.json', '.xml', '.txt', '.webmanifest', '.svg'}
KEEP_EXT = TEXT_EXT | {'.ico', '.png', '.jpg', '.jpeg', '.webp', '.avif', '.woff', '.woff2', '.ttf'}
KEEP_NAMES = {'robots.txt', 'sitemap.xml', 'manifest.webmanifest', 'llms.txt'}

ATTR_ROOT = re.compile(r"(\b(?:href|src|action|poster|content|data-src|data-href)=[\"'])/(?!/)", re.I)
QUOTED_ROOT = re.compile(r"([\"'])/(?=[A-Za-z0-9])")
CSS_ROOT = re.compile(r"url\(([\"']?)/(?!/)")
ROBOTS_META = re.compile(
    r'<meta\b(?=[^>]*\bname=[\"\']robots[\"\'])[^>]*>',
    re.I,
)
PAGES_ROBOTS = '<meta content="noindex,nofollow,noarchive" name="robots"/>'


def rewrite_text(path: Path, text: str) -> str:
    suffix = path.suffix.lower()
    if suffix in {'.html', '.xml', '.svg'}:
        text = ATTR_ROOT.sub(lambda m: m.group(1) + BASE + '/', text)
        text = CSS_ROOT.sub(lambda m: 'url(' + m.group(1) + BASE + '/', text)
    elif suffix == '.css':
        text = CSS_ROOT.sub(lambda m: 'url(' + m.group(1) + BASE + '/', text)
    elif suffix in {'.js', '.json', '.webmanifest'}:
        text = QUOTED_ROOT.sub(lambda m: m.group(1) + BASE + '/', text)

    if suffix == '.html':
        if ROBOTS_META.search(text):
            text = ROBOTS_META.sub(PAGES_ROBOTS, text, count=1)
        else:
            text = re.sub(r'<head>', '<head>' + PAGES_ROBOTS, text, count=1, flags=re.I)
        if text.count('name="robots"') != 1:
            raise SystemExit(f'ERROR: expected exactly one robots meta after Pages rewrite: {path}')
    return text


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    copied = 0
    for path in ROOT.rglob('*'):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if rel.parts and rel.parts[0] in SKIP_TOP_LEVEL:
            continue
        if path.name in SKIP_NAMES:
            continue
        if path.suffix.lower() not in KEEP_EXT and path.name not in KEEP_NAMES:
            continue

        dest = OUT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        suffix = path.suffix.lower()
        if suffix in TEXT_EXT or path.name in KEEP_NAMES:
            try:
                text = path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                shutil.copy2(path, dest)
            else:
                dest.write_text(rewrite_text(path, text), encoding='utf-8')
        else:
            shutil.copy2(path, dest)
        copied += 1

    # Do not allow the temporary mirror to compete with the production domain.
    (OUT / 'robots.txt').write_text('User-agent: *\nDisallow: /\n', encoding='utf-8')
    (OUT / '.nojekyll').write_text('', encoding='utf-8')

    forbidden_roots = {'ops', 'api', 'scripts', 'tests', 'lib'}
    leaked = [p for p in OUT.rglob('*') if p.is_file() and p.relative_to(OUT).parts[0] in forbidden_roots]
    if leaked:
        raise SystemExit(f'ERROR: internal/server files leaked into Pages artifact: {leaked[:10]}')
    stray = [name for name in SKIP_NAMES if (OUT / name).exists()]
    if stray:
        raise SystemExit(f'ERROR: build metadata leaked into Pages artifact: {stray}')

    subprocess.run(['python3', 'scripts/prune-public-raster-assets.py', str(OUT)], check=True)
    subprocess.run(['python3', 'scripts/prune-public-css-assets.py', str(OUT)], check=True)
    subprocess.run(['python3', 'scripts/write-release-metadata.py', str(OUT), 'github-pages-mirror'], check=True)

    html_count = len(list(OUT.glob('*.html')))
    if html_count != 50:
        raise SystemExit(f'ERROR: expected 50 root HTML pages, found {html_count}')

    print(f'PASS: R15 Pages mirror built — {html_count} root pages, noindex enforced, internal/build-only paths excluded, {copied} public files copied.')


if __name__ == '__main__':
    main()
