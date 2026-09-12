"""Generate indexable language pages from a single authored template."""
from pathlib import Path
from html import escape, unescape
import json
import re

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'content/index.html').read_text()
dictionary = json.loads((ROOT / 'content/translations.json').read_text())
brand_labels = {'novera','Novera','UZ','EN','RU','NOVERA / DIGITAL ENGINEERING',
                'CONNECTED BY DESIGN','01 / NOVERA','01 — DIGITAL PRODUCTS',
                '02 — CONNECTED SYSTEMS','01 / END-TO-END','02 / TEAM EXTENSION','03 / EVOLUTION'}
missing = {unescape(t.strip()) for t in re.findall(r'>([^<>]+)<', source)
           if re.search(r'[A-Za-z]', t) and unescape(t.strip()) not in dictionary
           and t.strip() not in brand_labels and 'info@innovera.uz' not in t}
if missing:
    raise SystemExit('Missing translations: '+repr(sorted(missing)))
routes = {'uz':'/', 'en':'/en/', 'ru':'/ru/'}
alternates = '\n'.join(f'<link rel="alternate" hreflang="{lang}" href="https://innovera.uz{route}">' for lang,route in routes.items())
alternates += '\n<link rel="alternate" hreflang="x-default" href="https://innovera.uz/">'

for lang, route in routes.items():
    def translate(value):
        key = unescape(value.strip())
        if lang == 'uz' or key not in dictionary: return value
        return value.replace(value.strip(), escape(dictionary[key][lang], quote=True))
    output = re.sub(r'>([^<>]+)<', lambda m:'>'+translate(m[1])+'<', source)
    output = re.sub(r'(alt|aria-label|placeholder|content|value|data-service)="([^"]*)"', lambda m:m[1]+'="'+translate(m[2])+'"', output)
    output = output.replace('lang="uz"', f'lang="{lang}"', 1)
    output = output.replace('content="uz_UZ"', 'content="'+{'uz':'uz_UZ','en':'en_US','ru':'ru_RU'}[lang]+'"')
    output = output.replace('href="https://innovera.uz/"', f'href="https://innovera.uz{route}"')
    output = output.replace('content="https://innovera.uz/"', f'content="https://innovera.uz{route}"')
    output = output.replace('</head>', alternates+'\n</head>')
    output = output.replace(f'data-lang="{lang}"',f'data-lang="{lang}" aria-current="page"')
    destination = ROOT / 'dist' / route.strip('/') / 'index.html'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(output)

sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
sitemap += ''.join(f'<url><loc>https://innovera.uz{route}</loc></url>' for route in routes.values())
(ROOT/'dist/sitemap.xml').write_text(sitemap+'</urlset>\n')
print('Built: /, /en/, /ru/')
