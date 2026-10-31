#!/usr/bin/env python3
"""Export pages rendered by the local Odoo website builder as a static site.

The result follows the production rules in docs/05-qoidalar.md:
- no Odoo JavaScript and no inline <script>/style="" (CSP: script-src/style-src 'self');
  inline styles become generated classes, bundled into dist/assets/builder.css;
- the compiled Odoo theme CSS is saved once and trimmed to the selectors used;
- fonts, images and video come from this repo's assets/, nothing external.

    python3 tools/odoo_site/export.py            # writes the pages into dist/
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from html import escape
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from odoo import STATIC, URL  # noqa: E402
from gen import LANGS, UI, build, links  # noqa: E402

LOCALE = {'ru': 'ru_RU', 'uz': 'uz_UZ', 'en': 'en_US'}

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'dist'   # dist/assets is hand-written source; the .html pages are generated here
SITE = 'https://noveragroup.uz'
ORG = {'@type': 'Organization', 'name': 'Novera', 'url': SITE + '/', 'logo': SITE + '/assets/favicon.svg',
       'telephone': '+998998112829', 'email': 'main@noveragroup.uz'}
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
DROP_ATTRS = re.compile(r'^(data-oe-|data-website-id$|data-main-object$|onerror$|data-extra-items|contenteditable$)')
WORDMARK = '<span class="s_nv_word">novera<span aria-hidden="true">✳</span></span>'


def fetch(path: str) -> str:
    with urllib.request.urlopen(URL + path) as r:
        return r.read().decode('utf-8')


class Rewriter(HTMLParser):
    """Streams the Odoo page back out, dropping what production must not ship."""

    def __init__(self, styles: dict[str, str]):
        super().__init__(convert_charrefs=False)
        self.out: list[str] = []
        self.styles = styles
        self.skip = 0          # inside a dropped element
        self.skip_tag = ''
        self.in_brand = 0
        self.brands = 0

    # -- helpers ---------------------------------------------------------
    def style_class(self, css: str) -> str:
        decls = [d.strip() for d in css.split(';') if d.strip()]
        if not decls:
            return ''
        body = ';'.join(d if '!important' in d else d + ' !important' for d in decls)
        body = local_urls(body)
        name = 's-' + hashlib.sha1(body.encode()).hexdigest()[:7]
        self.styles[name] = body
        return name

    def attrs(self, tag, attrs):
        out, classes = [], None
        for k, v in attrs:
            if DROP_ATTRS.match(k):
                continue
            if k == 'style':
                extra = self.style_class(v or '')
                if extra:
                    out.append(('__style', extra))
                continue
            if k == 'class':
                classes = ' '.join(c for c in (v or '').split() if c != 'o_menu_loading')
                continue
            if k in ('href', 'src', 'srcset', 'poster', 'content', 'data-reel-src') and v:
                v = local_urls(v)
            if tag == 'html' and k == 'lang':
                v = v.split('-')[0]
            out.append((k, v))
        if tag == 'img' and not any(k == 'width' for k, _ in out):
            size = image_size(dict(out).get('src', ''))
            if size:
                out += [('width', str(size[0])), ('height', str(size[1]))]
        extra = [v for k, v in out if k == '__style']
        out = [(k, v) for k, v in out if k != '__style']
        if extra:
            classes = ' '.join(filter(None, [classes] + extra))
        if classes is not None:
            out.insert(0, ('class', classes.strip()))
        return ''.join(f' {k}' if v is None else f' {k}="{escape(v, quote=True)}"' for k, v in out)

    def drop(self, tag, attrs) -> bool:
        a = dict(attrs)
        if tag == 'script':
            return True  # Odoo runtime and its JSON-LD; export writes its own structured data
        if tag == 'link':
            href = a.get('href', '')
            return ('fonts.g' in href or href.startswith('/web/') or a.get('rel') in ('preload', 'preconnect', 'canonical', 'alternate')
                    or 'icon' in (a.get('rel') or ''))
        if tag == 'meta':
            return (a.get('name') in ('generator', 'twitter:card', 'twitter:image') or a.get('http-equiv') == 'X-UA-Compatible'
                    or (a.get('property') or '').startswith('og:'))
        return a.get('id') == 'o_fake_header_disclaimer' or 'o_brand_promotion' in (a.get('class') or '')

    # -- parser events ---------------------------------------------------
    def handle_decl(self, decl):
        self.out.append(f'<!{decl}>')

    def handle_starttag(self, tag, attrs):
        if self.skip:
            if tag == self.skip_tag:
                self.skip += 1
            return
        if self.drop(tag, attrs):
            if tag not in VOID:
                self.skip, self.skip_tag = 1, tag
            return
        if self.in_brand:  # logo <span><img></span> inside .navbar-brand is replaced
            if tag not in VOID:
                self.in_brand += 1
            return
        self.out.append(f'<{tag}{self.attrs(tag, attrs)}>')
        if tag == 'a' and 'navbar-brand' in (dict(attrs).get('class') or ''):
            self.brands += 1
            self.out.append(WORDMARK)
            self.in_brand = 1

    def handle_startendtag(self, tag, attrs):
        if self.skip or self.in_brand or self.drop(tag, attrs):
            return
        self.out.append(f'<{tag}{self.attrs(tag, attrs)}/>')

    def handle_endtag(self, tag):
        if self.skip:
            if tag == self.skip_tag:
                self.skip -= 1
            return
        if self.in_brand:
            if tag == 'a' and self.in_brand == 1:
                self.in_brand = 0
            elif tag not in VOID:
                self.in_brand -= 1
                return
            else:
                return
        if tag == 'head':  # after <meta charset>, which must stay first
            self.out.append('{HEADMETA}'
                            '\n        <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"/>'
                            '\n        <link rel="stylesheet" href="/assets/builder.css?v={css}"/>'
                            '\n        <script src="/assets/messages.js?v={messages}" defer="defer"></script>'
                            '\n        <script src="/assets/builder.js?v={js}" defer="defer"></script>'
                            '\n        <script src="/assets/forms.js?v={forms}" defer="defer"></script>\n    ')
        if tag not in VOID:
            self.out.append(f'</{tag}>')

    def handle_data(self, data):
        if self.skip:
            if self.skip_tag == 'script':
                return
            return
        if self.in_brand:
            return
        if self.out and self.out[-1].startswith('<script type="application/ld+json"'):
            data = local_urls(data)
        self.out.append(data)

    def handle_entityref(self, name):
        if not (self.skip or self.in_brand):
            self.out.append(f'&{name};')

    def handle_charref(self, name):
        if not (self.skip or self.in_brand):
            self.out.append(f'&#{name};')

    def handle_comment(self, data):
        pass


def image_size(src: str):
    """Intrinsic size of a local WebP/PNG/SVG, so the browser reserves the space (no layout shift)."""
    path = OUT / src.split('?')[0].lstrip('/')
    if not src.startswith('/assets/') or not path.is_file():
        return None
    data = path.read_bytes()[:4096]
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        kind = data[12:16]
        if kind == b'VP8X':
            return 1 + int.from_bytes(data[24:27], 'little'), 1 + int.from_bytes(data[27:30], 'little')
        if kind == b'VP8 ':
            return int.from_bytes(data[26:28], 'little') & 0x3fff, int.from_bytes(data[28:30], 'little') & 0x3fff
        if kind == b'VP8L':
            b = int.from_bytes(data[21:25], 'little')
            return 1 + (b & 0x3fff), 1 + ((b >> 14) & 0x3fff)
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return int.from_bytes(data[16:20], 'big'), int.from_bytes(data[20:24], 'big')
    m = re.search(rb'viewBox="0 0 ([\d.]+) ([\d.]+)"', data)
    return (round(float(m[1])), round(float(m[2]))) if m else None


def shape_file(match: re.Match) -> str:
    """Odoo builder background shapes are generated SVGs; ship them as files."""
    url = match.group(0).replace('&amp;', '&')
    name = 'assets/shapes/' + hashlib.sha1(url.encode()).hexdigest()[:10] + '.svg'
    target = OUT / name
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(fetch(url), encoding='utf-8')
    return '/' + name


def local_urls(value: str) -> str:
    value = value.replace(f'{STATIC}/assets/', '/assets/')
    value = re.sub(r'/html_editor/shape/[^)"\'\s]+', shape_file, value)
    for host in (URL, 'http://localhost:8069'):
        value = value.replace(host + '/', SITE + '/').replace(host, SITE)
    value = re.sub(re.escape(SITE) + r'/web/image/website/1/logo[^"\s]*', SITE + '/assets/novera-sculpture.jpg', value)
    return value


def export_css(page_html: str) -> str:
    href = re.search(r'href="(/web/assets/[^"]+web\.assets_frontend\.min\.css)"', page_html)[1]
    css = fetch(href)
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    css = re.sub(r'@font-face\s*\{[^}]*\}', '', css)              # Odoo icon fonts; real fonts are in site-static.css
    css = re.sub(r'[^{}]*\{[^{}]*url\(["\']?/(web|html_editor|website)/[^}]*\}', '', css)  # editor shapes/placeholders
    return css


def purge(css_path: Path, html_files: list[Path]):
    """Trim unused selectors with PurgeCSS when it is available (dev tool, not shipped)."""
    safelist = ['show', 'showing', 'hiding', 'offcanvas-backdrop', 'fade', 'o_animating', 'o_animated',
                'o_nv_visible', 'o_header_is_scrolled', 'is-open', 'is-success', 'is-error']
    config = css_path.parent / 'purgecss.config.cjs'
    config.write_text('module.exports = ' + json.dumps({
        'css': [str(css_path)], 'output': str(css_path.parent), 'keyframes': True, 'variables': True,
        'content': [*map(str, html_files), str(OUT / 'assets/builder.js'), str(OUT / 'assets/forms.js')],
        'safelist': {'standard': safelist, 'greedy': ['/s_nv_/']},
    }).replace('"/s_nv_/"', '/s_nv_/') + ';\n')
    cmd = ['npx', '--yes', 'purgecss@6.0.0', '--config', str(config)]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=300)
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print('purgecss skipped:', e, getattr(e, 'stderr', b'')[:400])
    finally:
        config.unlink(missing_ok=True)


def version(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()[:10]


def localize(html: str, page: dict, group: dict) -> str:
    """Header/footer are shared in Odoo (Russian); give each page its language."""
    lang, L, u = page['lang'], links(page['lang']), UI[page['lang']]
    html = re.sub(r'<html lang="[^"]*"', f'<html lang="{lang}"', html, count=1)
    keys = ['services', 'formats', 'approach', 'faq', 'about']
    for i, key in enumerate(keys):
        html = re.sub(rf'(href="/?#m-{key}"[^>]*>\s*<span>)[^<]*(</span>)', rf'\g<1>{u["menu"][i]}\g<2>', html)
    html = re.sub(r'href="/?#m-(\w+)"', lambda m: f'href="{L[m[1]]}"', html)
    html = re.sub(r'(class="[^"]*btn_cta[^"]*" href="[^"]*">)[^<]*', rf'\g<1>{u["cta"]}', html)
    strings = {**u, **{f'menu{i}': v for i, v in enumerate(u['menu'])}}
    html = re.sub(r'(<(\w+)[^>]*data-i18n="(\w+)"[^>]*>)[^<]*(</\2>)', lambda m: m[1] + escape(strings[m[3]], quote=False) + m[4], html)
    html = html.replace(' data-i18n="', ' data-t="')
    html = re.sub(r' data-t="\w+"', '', html)
    # language switch: desktop next to the CTA, mobile next to the burger
    switch = ''.join(
        f'<a href="{group[l]["path"]}" lang="{l}" hreflang="{l}" class="nav-link px-1{" fw-semibold active" if l == lang else ""}"'
        f'{" aria-current=\"true\"" if l == lang else ""}>{l.upper()}</a>' for l in LANGS if l in group)
    item = f'<li class="nav-item d-flex s_nv_lang" aria-label="Language">{switch}</li>'
    html = html.replace('justify-content-end ps-3">', 'justify-content-end ps-3">' + item, 1)
    html = html.replace('o_header_mobile_buttons_wrap navbar-nav d-flex flex-row align-items-center gap-2 mb-0 ms-auto">',
                        'o_header_mobile_buttons_wrap navbar-nav d-flex flex-row align-items-center gap-2 mb-0 ms-auto">' + item, 1)
    # head: canonical, alternates, social cards
    url = SITE + page['path']
    alts = ''.join(f'\n        <link rel="alternate" hreflang="{l}" href="{SITE + group[l]["path"]}"/>' for l in LANGS if l in group)
    if LANGS[0] in group:
        alts += f'\n        <link rel="alternate" hreflang="x-default" href="{SITE + group[LANGS[0]]["path"]}"/>'
    meta = (f'\n        <link rel="canonical" href="{url}"/>{alts}'
            f'\n        <meta property="og:type" content="website"/>'
            f'\n        <meta property="og:site_name" content="Novera"/>'
            f'\n        <meta property="og:locale" content="{LOCALE[lang]}"/>'
            f'\n        <meta property="og:title" content="{escape(page["title"])}"/>'
            f'\n        <meta property="og:description" content="{escape(page["description"])}"/>'
            f'\n        <meta property="og:url" content="{url}"/>'
            f'\n        <meta property="og:image" content="{SITE}/assets/novera-sculpture.jpg"/>'
            f'\n        <meta name="twitter:card" content="summary_large_image"/>')
    graph = {'@context': 'https://schema.org', '@graph': [
        ORG, {'@type': 'WebPage', 'url': url, 'name': page['title'], 'description': page['description'],
              'inLanguage': lang, 'isPartOf': {'@type': 'WebSite', 'name': ORG['name'], 'url': SITE + '/'}}]}
    meta += '\n        <script type="application/ld+json">' + json.dumps(graph, ensure_ascii=False).replace('</', '<\\/') + '</script>'
    poster = re.search(r'<video[^>]*poster="([^"]+)"', html)
    if poster:
        meta += f'\n        <link rel="preload" as="image" href="{poster[1]}" fetchpriority="high"/>'
    return html.replace('{HEADMETA}', meta if page['path'] != '/404.html' else '\n        <meta name="robots" content="noindex"/>', 1)


def sitemap(pages, groups) -> str:
    rows = []
    for p in pages:
        if p['path'] == '/404.html':
            continue
        g = groups[p['group']]
        alts = ''.join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{SITE + g[l]["path"]}"/>' for l in LANGS if l in g)
        if LANGS[0] in g:
            alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{SITE + g[LANGS[0]]["path"]}"/>'
        rows.append(f'<url><loc>{SITE + p["path"]}</loc>{alts}</url>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + '\n'.join(rows) + '\n</urlset>\n')


def main():
    shutil.rmtree(OUT / 'assets/shapes', ignore_errors=True)

    pages = build()
    groups: dict[str, dict] = {}
    for p in pages:
        groups.setdefault(p['group'], {})[p['lang']] = p

    styles: dict[str, str] = {}
    written, theme = [], ''
    for page in pages:
        raw = fetch(page['odoo'])
        theme = theme or export_css(raw)
        parser = Rewriter(styles)
        parser.feed(raw)
        html = re.sub(r'\n\s*\n+', '\n', ''.join(parser.out))
        html = localize(html, page, groups[page['group']])
        path = page['path']
        target = OUT / (path.strip('/') if path.endswith('.html') else (path.strip('/') + '/index.html').lstrip('/'))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding='utf-8')
        written.append(target)
    (OUT / 'sitemap.xml').write_text(sitemap(pages, groups), encoding='utf-8')
    css_dir = OUT / 'assets'
    (css_dir / 'site-theme.css').write_text(theme, encoding='utf-8')
    (css_dir / 'site-inline.css').write_text(
        ''.join(f'.{name}{{{body}}}\n' for name, body in sorted(styles.items())), encoding='utf-8')
    purge(css_dir / 'site-theme.css', written)

    # one render-blocking stylesheet: Odoo theme, former inline styles, static-export fixes
    parts = [(css_dir / 'site-theme.css').read_text(encoding='utf-8'), (css_dir / 'site-inline.css').read_text(encoding='utf-8'),
             (HERE / 'static.css').read_text(encoding='utf-8')]
    (css_dir / 'builder.css').write_text('\n'.join(parts), encoding='utf-8')
    for n in ('site-theme.css', 'site-inline.css'):
        (css_dir / n).unlink()
    versions = {'css': version(css_dir / 'builder.css'), 'js': version(OUT / 'assets/builder.js'),
                'forms': version(OUT / 'assets/forms.js'), 'messages': version(OUT / 'assets/messages.js')}
    for page in written:
        html = page.read_text(encoding='utf-8')
        for key, value in versions.items():
            html = html.replace('{' + key + '}', value)
        page.write_text(html, encoding='utf-8')
    size = (css_dir / 'builder.css').stat().st_size // 1024
    print(f'export: {len(written)} page(s), {len(styles)} inline styles, builder.css {size} KB -> {OUT}')
    print(json.dumps(versions))


if __name__ == '__main__':
    main()
