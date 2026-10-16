"""Generate service pages (4 services x uz/en/ru) for noveragroup.uz.

Header, footer, process steps, collaboration formats and the general FAQ are taken
from the already translated home pages in dist/, so copy and translations live in
one place. Run after tools/build_locales.py; it also rewrites dist/sitemap.xml.
"""
from html import escape
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
ORIGIN = 'https://noveragroup.uz'
HOME = {'uz': '/', 'en': '/en/', 'ru': '/ru/'}
OG_LOCALE = {'uz': 'uz_UZ', 'en': 'en_US', 'ru': 'ru_RU'}
IMG = {'/assets/digital-products.jpg': (1200, 800), '/assets/connected-systems.jpg': (1200, 800)}


def element(html, start_pattern):
    """Return the balanced element whose opening tag matches start_pattern."""
    m = re.search(start_pattern, html)
    if not m:
        raise SystemExit(f'not found: {start_pattern}')
    tag = re.match(r'<(\w+)', m.group(0)).group(1)
    depth, i = 0, m.start()
    for t in re.finditer(rf'<(/?){tag}\b[^>]*>', html[m.start():]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return html[m.start():m.start() + t.end()]
    raise SystemExit(f'unbalanced: {start_pattern}')


def home_parts(lang):
    page = (DIST / HOME[lang].strip('/') / 'index.html').read_text(encoding='utf-8')
    head = page[page.find('<head>') + 6:page.find('</head>')]
    keep = [l for l in head.splitlines() if re.search(r'theme-color|rel="preload"|rel="icon"|rel="stylesheet"|<script src=', l)]
    home = HOME[lang]

    def link_home(fragment):
        fragment = re.sub(r'href="#"', f'href="{home}"', fragment)
        return re.sub(r'href="#(?!main")([^"]+)"', lambda m: f'href="{home}#{m[1]}"', fragment)

    return {
        'head': '\n'.join(keep),
        'skip': re.search(r'<a class="skip"[^>]*>[^<]*</a>', page).group(0),
        'progress': re.search(r'<div class="reading-progress"[^>]*></div>', page).group(0),
        'header': link_home(element(page, r'<header class="header wrap">')),
        'footer': link_home(element(page, r'<footer class="wrap">')),
        'steps': element(page, r'<ol class="steps">'),
        'formats': link_home(element(page, r'<div class="engagement-grid">')),
        'faq': re.findall(r'<details>.*?</details>', element(page, r'<section id="savollar"'), re.S),
    }


def page(service, lang, data, parts):
    ui, s, home = data['ui'][lang], service[lang], HOME[lang]
    url = ORIGIN + service['slug'][lang]
    others = [x for x in data['services'] if x['id'] != service['id']]
    w, h = IMG[service['image']]
    header = parts['header']
    for code, path in service['slug'].items():  # language switcher points to this service in each language
        header = re.sub(rf'href="[^"]*"([^>]*data-lang="{code}")', f'href="{path}"\\1', header)
    alternates = '\n'.join(f'  <link rel="alternate" hreflang="{l}" href="{ORIGIN}{p}">' for l, p in service['slug'].items())
    alternates += f'\n  <link rel="alternate" hreflang="x-default" href="{ORIGIN}{service["slug"]["uz"]}">'
    graph = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'Organization', '@id': f'{ORIGIN}/#organization', 'name': 'Novera', 'url': f'{ORIGIN}/',
         'email': 'main@noveragroup.uz', 'telephone': '+998998112829'},
        {'@type': 'Service', '@id': f'{url}#service', 'name': s['name'], 'description': s['description'],
         'url': url, 'provider': {'@id': f'{ORIGIN}/#organization'}},
        {'@type': 'WebPage', '@id': f'{url}#webpage', 'url': url, 'name': s['title'], 'description': s['description'],
         'inLanguage': lang, 'about': {'@id': f'{url}#service'}, 'isPartOf': {'@id': f'{ORIGIN}/#website'}},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': ui['home'], 'item': ORIGIN + home},
            {'@type': 'ListItem', 'position': 2, 'name': ui['services'], 'item': f'{ORIGIN}{home}#yechimlar'},
            {'@type': 'ListItem', 'position': 3, 'name': s['name'], 'item': url}]},
        {'@type': 'FAQPage', '@id': f'{url}#faq', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in s['faq']]}]}
    ld = json.dumps(graph, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    e = lambda x: escape(x, quote=True)
    kinds = ''.join(f'<article class="svc-kind"><h3>{e(t)}</h3><p>{e(d)}</p></article>' for t, d in s['kinds'])
    scope = ''.join(f'<li><strong>{e(t)}</strong><span>{e(d)}</span></li>' for t, d in s['scope'])
    own_faq = ''.join(f'<details><summary>{e(q)}<span aria-hidden="true">+</span></summary><p>{e(a)}</p></details>' for q, a in s['faq'])
    other_links = ''.join(f'<li><a href="{x["slug"][lang]}">{e(x[lang]["name"])} <span aria-hidden="true">↗</span></a></li>' for x in others)
    return f'''<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
{parts["head"]}
  <title>{e(s["title"])}</title>
  <meta name="description" content="{e(s["description"])}">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="{url}">
{alternates}
  <meta property="og:type" content="website"><meta property="og:site_name" content="Novera">
  <meta property="og:locale" content="{OG_LOCALE[lang]}">
  <meta property="og:title" content="{e(s["title"])}">
  <meta property="og:description" content="{e(s["description"])}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{ORIGIN}{service["image"]}">
  <meta name="twitter:card" content="summary_large_image">
  <script type="application/ld+json">{ld}</script>
</head>
<body>
  {parts["skip"]}
  {parts["progress"]}
  {header}
  <main id="main" tabindex="-1">
    <nav class="crumbs wrap" aria-label="{e(ui["breadcrumb"])}"><ol>
      <li><a href="{home}">{e(ui["home"])}</a></li>
      <li><a href="{home}#yechimlar">{e(ui["services"])}</a></li>
      <li><span aria-current="page">{e(s["name"])}</span></li>
    </ol></nav>
    <section class="svc-hero wrap">
      <div class="svc-hero-copy">
        <p class="eyebrow">{e(ui["eyebrow"])}</p>
        <h1>{e(s["h1"])}</h1>
        <p class="lead">{e(s["lead"])}</p>
        <div class="hero-actions"><a class="button" href="{home}#boshlash">{e(ui["cta_btn"])} <span aria-hidden="true">↗</span></a></div>
      </div>
      <figure class="svc-hero-art"><img src="{service["image"]}" alt="" width="{w}" height="{h}" decoding="async" fetchpriority="high"></figure>
    </section>
    <section class="section wrap" aria-labelledby="svc-build">
      <div class="section-head"><p class="eyebrow">{e(ui["eb_build"])}</p><h2 id="svc-build">{e(ui["build"])}</h2></div>
      <div class="svc-kinds">{kinds}</div>
    </section>
    <section class="section wrap" aria-labelledby="svc-scope">
      <div class="section-head"><p class="eyebrow">{e(ui["eb_scope"])}</p><h2 id="svc-scope">{e(ui["scope"])}</h2></div>
      <ul class="svc-scope">{scope}</ul>
    </section>
    <section class="section wrap process" aria-labelledby="svc-process">
      <div class="process-intro"><p class="eyebrow">{e(ui["eb_process"])}</p><h2 id="svc-process">{e(ui["process"])}</h2></div>
      {parts["steps"]}
    </section>
    <section class="engagement section wrap" aria-labelledby="svc-formats">
      <div class="section-head"><p class="eyebrow">{e(ui["eb_formats"])}</p><h2 id="svc-formats">{e(ui["formats"])}</h2></div>
      {parts["formats"]}
    </section>
    <section class="section wrap faq" aria-labelledby="svc-faq">
      <div><p class="eyebrow">{e(ui["eb_faq"])}</p><h2 id="svc-faq">{e(ui["faq"])}</h2></div>
      <div>{own_faq}{"".join(parts["faq"])}</div>
    </section>
    <section class="contact wrap svc-cta" aria-labelledby="svc-cta-title">
      <div><h2 id="svc-cta-title">{e(ui["cta_h"])}</h2><p>{e(ui["cta_p"])}</p></div>
      <div class="svc-cta-actions"><a class="button" href="{home}#boshlash">{e(ui["cta_btn"])} <span aria-hidden="true">↗</span></a>
        <a class="text-link" href="mailto:main@noveragroup.uz">main@noveragroup.uz</a></div>
    </section>
    <nav class="svc-others wrap" aria-labelledby="svc-others-title">
      <h2 id="svc-others-title">{e(ui["other"])}</h2>
      <ul>{other_links}</ul>
    </nav>
  </main>
  {parts["footer"]}
</body>
</html>
'''


def main():
    data = json.loads((ROOT / 'content/services.json').read_text(encoding='utf-8'))
    parts = {lang: home_parts(lang) for lang in HOME}
    built = []
    for service in data['services']:
        for lang in HOME:
            dest = DIST / service['slug'][lang].strip('/') / 'index.html'
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(page(service, lang, data, parts[lang]), encoding='utf-8')
            built.append(service['slug'][lang])

    groups = [HOME] + [s['slug'] for s in data['services']]
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for g in groups:
        alt = ''.join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{ORIGIN}{p}"/>' for l, p in {**g, 'x-default': g['uz']}.items())
        xml += [f'<url><loc>{ORIGIN}{p}</loc>{alt}</url>' for p in g.values()]
    (DIST / 'sitemap.xml').write_text('\n'.join(xml) + '\n</urlset>\n', encoding='utf-8')
    print(f'Services built: {len(built)} pages; sitemap: {3 + len(built)} URLs')


if __name__ == '__main__':
    main()
