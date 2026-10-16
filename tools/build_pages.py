"""Generate the about page, privacy policy and case studies for noveragroup.uz.

Run after tools/build_locales.py and tools/build_services.py. Shared chrome comes
from the translated home pages (build_services.home_parts). Footer links authored
with Uzbek URLs are localized in every generated page, a work section is injected
into the home pages when content/cases.json has entries, and the sitemap is
rewritten with every route.
"""
from html import escape
from pathlib import Path
import json
import os
import re
import shutil

from build_services import DIST, HOME, OG_LOCALE, ORIGIN, home_parts

ROOT = Path(__file__).resolve().parents[1]
CASE_BASE = {'uz': '/ishlar/', 'en': '/en/work/', 'ru': '/ru/raboty/'}
OG_IMAGE = f'{ORIGIN}/assets/digital-products.jpg'


def e(text):
    return escape(text, quote=True)


def case_slugs(case):
    return {lang: CASE_BASE[lang] + case['slug'][lang].strip('/') + '/' for lang in HOME}


def document(lang, slugs, title, description, nodes, crumbs, body, parts, label):
    url = ORIGIN + slugs[lang]
    header = parts['header']
    for code, path in slugs.items():  # language switcher points to this page in each language
        header = re.sub(rf'href="[^"]*"([^>]*data-lang="{code}")', f'href="{path}"\\1', header)
    alternates = '\n'.join(f'  <link rel="alternate" hreflang="{l}" href="{ORIGIN}{p}">' for l, p in slugs.items())
    alternates += f'\n  <link rel="alternate" hreflang="x-default" href="{ORIGIN}{slugs["uz"]}">'
    graph = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'Organization', '@id': f'{ORIGIN}/#organization', 'name': 'Novera', 'url': f'{ORIGIN}/',
         'email': 'main@noveragroup.uz', 'telephone': '+998998112829'},
        {'@type': 'BreadcrumbList', '@id': url + '#breadcrumb', 'itemListElement': [
            {'@type': 'ListItem', 'position': i, 'name': name, 'item': ORIGIN + link}
            for i, (name, link) in enumerate(crumbs, 1)]},
        *nodes]}
    ld = json.dumps(graph, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    crumb_items = ''.join(f'<li><a href="{link}">{e(name)}</a></li>' if i < len(crumbs) - 1
                          else f'<li><span aria-current="page">{e(name)}</span></li>' for i, (name, link) in enumerate(crumbs))
    return f'''<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
{parts["head"]}
  <title>{e(title)}</title>
  <meta name="description" content="{e(description)}">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="{url}">
{alternates}
  <meta property="og:type" content="website"><meta property="og:site_name" content="Novera">
  <meta property="og:locale" content="{OG_LOCALE[lang]}">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(description)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{OG_IMAGE}">
  <meta name="twitter:card" content="summary_large_image">
  <script type="application/ld+json">{ld}</script>
</head>
<body>
  {parts["skip"]}
  {parts["progress"]}
  {header}
  <main id="main" tabindex="-1">
    <nav class="crumbs wrap" aria-label="{e(label)}"><ol>{crumb_items}</ol></nav>
{body}
  </main>
  {parts["footer"]}
</body>
</html>
'''


def cta(services, lang):
    ui = services['ui'][lang]
    return f'''    <section class="contact wrap svc-cta" aria-labelledby="cta-title">
      <div><h2 id="cta-title">{e(ui["cta_h"])}</h2><p>{e(ui["cta_p"])}</p></div>
      <div class="svc-cta-actions"><a class="button" href="{HOME[lang]}#boshlash">{e(ui["cta_btn"])} <span aria-hidden="true">↗</span></a>
        <a class="text-link" href="mailto:main@noveragroup.uz">main@noveragroup.uz</a></div>
    </section>'''


def about(data, services, lang, parts):
    page, ui = data['about'], data['ui'][lang]
    slugs, url = page['slug'], ORIGIN + page['slug'][lang]
    crumbs = [(ui['home'], HOME[lang]), (page['name'][lang], slugs[lang])]
    principles = ''.join(f'<article><h3>{e(h)}</h3><p>{e(p)}</p></article>' for h, p in page['principles'][lang])
    links = ''.join(f'<li><a href="{s["slug"][lang]}">{e(s[lang]["name"])} <span aria-hidden="true">↗</span></a></li>'
                    for s in services['services'])
    team = ''
    if page['team']:
        people = ''.join(f'<li class="team-card"><img src="/{m["photo"]}" width="600" height="750" alt="" loading="lazy" decoding="async">'
                         f'<h3>{e(m["name"])}</h3><p>{e(m["role"][lang])}</p></li>' for m in page['team'])
        team = f'''
    <section class="section wrap" aria-labelledby="team-title">
      <div class="section-head"><h2 id="team-title">{e(page["team_label"][lang])}</h2></div>
      <ul class="team-grid">{people}</ul>
    </section>'''
    body = f'''    <section class="svc-hero page-hero wrap">
      <div class="svc-hero-copy">
        <p class="eyebrow">{e(page["name"][lang])}</p>
        <h1>{e(page["headline"][lang])}</h1>
        <p class="lead">{e(page["lead"][lang])}</p>
      </div>
    </section>
    <section class="statement"><div class="wrap statement-inner">
      <p class="eyebrow">{e(page["principles_label"][lang])}</p>
      <h2>{e(page["principles_title"][lang])}</h2>
      <div class="principles">{principles}</div>
    </div></section>
    <section class="engagement section wrap" aria-labelledby="formats-title">
      <div class="section-head"><h2 id="formats-title">{e(page["formats_label"][lang])}</h2></div>
      {parts["formats"]}
    </section>
    <nav class="svc-others wrap" aria-labelledby="services-title">
      <h2 id="services-title">{e(page["services_label"][lang])}</h2>
      <ul>{links}</ul>
    </nav>{team}
{cta(services, lang)}'''
    node = {'@type': 'AboutPage', '@id': url + '#webpage', 'url': url, 'name': page['title'][lang],
            'description': page['description'][lang], 'inLanguage': lang,
            'about': {'@id': f'{ORIGIN}/#organization'}, 'breadcrumb': {'@id': url + '#breadcrumb'}}
    return document(lang, slugs, page['title'][lang], page['description'][lang], [node], crumbs, body, parts, ui['breadcrumb'])


def privacy(data, lang, parts):
    page, ui = data['privacy'], data['ui'][lang]
    slugs, url = page['slug'], ORIGIN + page['slug'][lang]
    crumbs = [(ui['home'], HOME[lang]), (page['name'][lang], slugs[lang])]
    sections = ''.join(f'<section class="legal-section"><h2>{e(h)}</h2>' + ''.join(f'<p>{e(p)}</p>' for p in paras) + '</section>'
                       for h, paras in page['sections'][lang])
    body = f'''    <article class="legal wrap">
      <h1>{e(page["name"][lang])}</h1>
      <p class="legal-updated">{e(ui["updated"])}</p>
      <div class="legal-body">{sections}</div>
    </article>'''
    node = {'@type': 'WebPage', '@id': url + '#webpage', 'url': url, 'name': page['title'][lang],
            'description': page['description'][lang], 'inLanguage': lang, 'dateModified': '2026-10-16',
            'breadcrumb': {'@id': url + '#breadcrumb'}}
    return document(lang, slugs, page['title'][lang], page['description'][lang], [node], crumbs, body, parts, ui['breadcrumb'])


def case_page(cases, i, services, data, lang, parts):
    case, ui, base = cases['cases'][i], cases['ui'][lang], data['ui'][lang]
    slugs, url = case_slugs(case), ORIGIN + case_slugs(case)[lang]
    crumbs = [(base['home'], HOME[lang]), (ui['crumb'], HOME[lang] + '#ishlar'), (case['title'][lang], slugs[lang])]
    names = {s['id']: s for s in services['services']}
    service_links = ', '.join(f'<a href="{names[k]["slug"][lang]}">{e(names[k][lang]["name"])}</a>' for k in case['services'])
    facts = (f'<div><dt>{e(ui["client"])}</dt><dd>{e(case["client"])}</dd></div>'
             f'<div><dt>{e(ui["sector"])}</dt><dd>{e(case["sector"][lang])}</dd></div>'
             f'<div><dt>{e(ui["services"])}</dt><dd>{service_links}</dd></div>'
             f'<div><dt>{e(ui["year"])}</dt><dd>{case["year"]}</dd></div>')
    story = ''.join(f'<section><h2>{e(ui[part])}</h2>' + ''.join(f'<p>{e(p)}</p>' for p in case[part][lang]) + '</section>'
                    for part in ('challenge', 'solution', 'result'))
    gallery = ''.join(f'<figure><img src="/{g["src"]}" width="1600" height="1000" alt="{e(g["alt"][lang])}" loading="lazy" decoding="async"></figure>'
                      for g in case.get('gallery', []))
    quote = ''
    if case.get('quote'):
        q = case['quote']
        quote = (f'\n    <figure class="case-quote wrap"><blockquote><p>{e(q["text"][lang])}</p></blockquote>'
                 f'<figcaption>{e(q["author"])}, {e(q["role"][lang])}</figcaption></figure>')
    body = f'''    <section class="svc-hero page-hero wrap">
      <div class="svc-hero-copy">
        <p class="eyebrow">{e(case["client"])}</p>
        <h1>{e(case["title"][lang])}</h1>
        <p class="lead">{e(case["summary"][lang])}</p>
      </div>
    </section>
    <dl class="page-facts wrap">{facts}</dl>
    <figure class="case-cover wrap"><img src="/{case["cover"]}" width="1600" height="1000" alt="" decoding="async" fetchpriority="high"></figure>
    <div class="case-story section wrap">{story}</div>{quote}
    <div class="case-gallery wrap">{gallery}</div>
{cta(services, lang)}'''
    node = {'@type': 'CreativeWork', '@id': url + '#case', 'url': url, 'name': case['title'][lang],
            'abstract': case['summary'][lang], 'inLanguage': lang, 'dateCreated': str(case['year']),
            'creator': {'@id': f'{ORIGIN}/#organization'}, 'image': f'{ORIGIN}/{case["cover"]}',
            'breadcrumb': {'@id': url + '#breadcrumb'}}
    return document(lang, slugs, f'{case["title"][lang]} — Novera', case['summary'][lang], [node], crumbs, body, parts, base['breadcrumb'])


def work_section(cases, lang):
    ui = cases['ui'][lang]
    cards = ''.join(f'<li><a class="work-card" href="{case_slugs(c)[lang]}"><span class="work-card-media">'
                    f'<img src="/{c["cover"]}" width="1600" height="1000" alt="" loading="lazy" decoding="async"></span>'
                    f'<span class="work-card-client">{e(c["client"])}</span><strong>{e(c["title"][lang])}</strong></a></li>'
                    for c in cases['cases'])
    return (f'<section id="ishlar" class="section wrap" aria-labelledby="work-title"><div class="section-head">'
            f'<p class="eyebrow">{e(ui["label"])}</p><h2 id="work-title">{e(ui["title"])}</h2></div>'
            f'<ul class="work-grid">{cards}</ul></section>\n    ')


def main():
    data = json.loads((ROOT / 'content/pages.json').read_text(encoding='utf-8'))
    services = json.loads((ROOT / 'content/services.json').read_text(encoding='utf-8'))
    cases = json.loads(Path(os.environ.get('NOVERA_CASES', ROOT / 'content/cases.json')).read_text(encoding='utf-8'))
    # dist/ is not wiped between builds: drop case pages that are no longer in cases.json.
    for base in CASE_BASE.values():
        shutil.rmtree(DIST / base.strip('/'), ignore_errors=True)
    for lang, route in HOME.items():
        if cases['cases']:
            path = DIST / route.strip('/') / 'index.html'
            html = path.read_text(encoding='utf-8')
            html = html.replace('<section id="yechimlar"', work_section(cases, lang) + '<section id="yechimlar"', 1)
            path.write_text(html, encoding='utf-8')
    # Localize footer links everywhere before copying chrome into the new pages.
    targets = [data['about']['slug'], data['privacy']['slug']]
    for path in DIST.rglob('index.html'):
        html = path.read_text(encoding='utf-8')
        lang = re.search(r'<html lang="(\w+)"', html)[1]
        for slugs in targets:
            html = html.replace(f'href="{slugs["uz"]}"', f'href="{slugs[lang]}"')
        path.write_text(html, encoding='utf-8')
    parts = {lang: home_parts(lang) for lang in HOME}
    groups = targets + [case_slugs(c) for c in cases['cases']]
    for lang in HOME:
        outputs = {data['about']['slug'][lang]: about(data, services, lang, parts[lang]),
                   data['privacy']['slug'][lang]: privacy(data, lang, parts[lang])}
        for i, case in enumerate(cases['cases']):
            outputs[case_slugs(case)[lang]] = case_page(cases, i, services, data, lang, parts[lang])
        for slug, html in outputs.items():
            dest = DIST / slug.strip('/') / 'index.html'
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(html, encoding='utf-8')

    all_groups = [HOME] + [s['slug'] for s in services['services']] + groups
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for g in all_groups:
        alt = ''.join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{ORIGIN}{p}"/>' for l, p in {**g, 'x-default': g['uz']}.items())
        xml += [f'<url><loc>{ORIGIN}{p}</loc>{alt}</url>' for p in g.values()]
    (DIST / 'sitemap.xml').write_text('\n'.join(xml) + '\n</urlset>\n', encoding='utf-8')
    print(f'Pages built: about, privacy, {len(cases["cases"])} case studies; sitemap: {len(all_groups) * 3} URLs')


if __name__ == '__main__':
    main()
