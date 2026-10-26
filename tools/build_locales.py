"""Generate indexable language pages from a single authored template."""
from pathlib import Path
from html import escape, unescape
import json
import re

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'content/index.html').read_text(encoding='utf-8')
dictionary = json.loads((ROOT / 'content/translations.json').read_text(encoding='utf-8'))
seo = json.loads((ROOT / 'content/seo.json').read_text(encoding='utf-8'))
# Service page URLs per language: uz slugs in the template are swapped for en/ru slugs.
services_data = json.loads((ROOT / 'content/services.json').read_text(encoding='utf-8'))
service_links = [s['slug'] for s in services_data['services']]


def mega_menu(lang):
    """Desktop mega menu for the services link: picture, name and one line each.
    It lives in the header, so build_services copies it into every inner page."""
    items = ''.join(
        f'<li><a class="mega__item" href="{s["slug"][lang]}"><img src="{s["image"].removesuffix(".jpg")}-600.webp" width="96" height="64" alt="" loading="lazy" decoding="async">'
        f'<span><b>{escape(s[lang]["name"])}</b><small>{escape(s[lang]["lead"].split("—")[0].split(". ")[0].rstrip(" ,."))}</small></span></a></li>'
        for s in services_data['services'])
    return f'<div class="mega" id="mega-services" hidden><div class="wrap mega__inner"><ul class="mega__list">{items}</ul></div></div>'
brand_labels = {'novera','Novera','UZ','EN','RU','NOVERA / DIGITAL ENGINEERING',
                'CONNECTED BY DESIGN','01 / NOVERA','01 — DIGITAL PRODUCTS',
                '02 — CONNECTED SYSTEMS','01 / END-TO-END','02 / TEAM EXTENSION','03 / EVOLUTION'}
missing = {unescape(t.strip()) for t in re.findall(r'>([^<>]+)<', source)
           if re.search(r'[A-Za-z]', t) and unescape(t.strip()) not in dictionary
           and t.strip() not in brand_labels and 'main@noveragroup.uz' not in t}
if missing:
    raise SystemExit('Missing translations: '+repr(sorted(missing)))
routes = {'uz':'/', 'en':'/en/', 'ru':'/ru/'}
alternates = '\n'.join(f'<link rel="alternate" hreflang="{lang}" href="https://noveragroup.uz{route}">' for lang,route in routes.items())
alternates += '\n<link rel="alternate" hreflang="x-default" href="https://noveragroup.uz/">'

for lang, route in routes.items():
    def translate(value):
        key = unescape(value.strip())
        if lang == 'uz' or key not in dictionary: return value
        return value.replace(value.strip(), escape(dictionary[key][lang], quote=True))
    output = re.sub(r'>([^<>]+)<', lambda m:'>'+translate(m[1])+'<', source)
    output = re.sub(r'(alt|aria-label|placeholder|content|value|data-service)="([^"]*)"', lambda m:m[1]+'="'+translate(m[2])+'"', output)
    for links in service_links:
        output = output.replace(f'href="{links["uz"]}"', f'href="{links[lang]}"')
    output = output.replace('lang="uz"', f'lang="{lang}"', 1)
    if lang == 'ru':  # Russian pages render mostly Cyrillic: preload those font subsets instead.
        output = output.replace('/assets/playfair-latin.woff2', '/assets/playfair-cyrillic.woff2').replace('/assets/onest-latin.woff2', '/assets/onest-cyrillic.woff2')
    output = output.replace('content="uz_UZ"', 'content="'+{'uz':'uz_UZ','en':'en_US','ru':'ru_RU'}[lang]+'"')
    output = output.replace('href="https://noveragroup.uz/"', f'href="https://noveragroup.uz{route}"')
    output = output.replace('content="https://noveragroup.uz/"', f'content="https://noveragroup.uz{route}"')
    metadata = seo[lang]
    output = re.sub(r'<title>.*?</title>', '<title>'+escape(metadata['title'])+'</title>', output)
    for attribute, key, value in (
        ('name', 'description', metadata['description']),
        ('property', 'og:title', metadata['title']),
        ('property', 'og:description', metadata['description']),
    ):
        output = re.sub(r'<meta '+attribute+'="'+key+r'" content="[^"]*">',
                        '<meta '+attribute+'="'+key+'" content="'+escape(value, quote=True)+'">', output)
    graph = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'Organization', '@id': 'https://noveragroup.uz/#organization',
         'name': 'Novera', 'url': 'https://noveragroup.uz/',
         'email': 'main@noveragroup.uz', 'telephone': '+998998112829'},
        {'@type': 'WebSite', '@id': 'https://noveragroup.uz/#website',
         'name': 'Novera', 'url': 'https://noveragroup.uz/', 'inLanguage': list(routes),
         'publisher': {'@id': 'https://noveragroup.uz/#organization'}},
        {'@type': 'WebPage', '@id': f'https://noveragroup.uz{route}#webpage',
         'url': f'https://noveragroup.uz{route}', 'name': metadata['title'],
         'description': metadata['description'], 'inLanguage': lang,
         'isPartOf': {'@id': 'https://noveragroup.uz/#website'},
         'about': {'@id': 'https://noveragroup.uz/#organization'}}
    ]}
    structured = json.dumps(graph, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    output = output.replace('</head>', alternates+'\n<meta property="og:site_name" content="Novera">\n'
                            +'<script type="application/ld+json">'+structured+'</script>\n</head>')
    output = output.replace(f'data-lang="{lang}"',f'data-lang="{lang}" aria-current="page"')
    output = output.replace('<a href="#yechimlar">', '<a href="#yechimlar" data-mega="mega-services">', 1)
    output = output.replace('</header>', mega_menu(lang) + '\n  </header>', 1)
    destination = ROOT / 'dist' / route.strip('/') / 'index.html'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(output, encoding='utf-8')

sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
xml_alternates = ''.join(f'<xhtml:link rel="alternate" hreflang="{lang}" href="https://noveragroup.uz{route}"/>'
                         for lang, route in {**routes, 'x-default':'/'}.items())
sitemap += ''.join(f'<url><loc>https://noveragroup.uz{route}</loc>{xml_alternates}</url>\n' for route in routes.values())
(ROOT/'dist/sitemap.xml').write_text(sitemap+'</urlset>\n', encoding='utf-8')
print('Built: /, /en/, /ru/')