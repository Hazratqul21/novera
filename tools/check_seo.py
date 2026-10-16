#!/usr/bin/env python3
"""Check generated metadata, reciprocal language links and truthful JSON-LD."""
import json
from html.parser import HTMLParser
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://noveragroup.uz'
ROUTES = {'uz': '/', 'en': '/en/', 'ru': '/ru/'}
EXPECTED = {lang: ORIGIN + route for lang, route in {**ROUTES, 'x-default': '/'}.items()}


class Head(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.meta, self.title, self.schema = [], {}, '', ''
        self.in_title = self.in_schema = False
        self.lang = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html': self.lang = a.get('lang')
        if tag == 'link': self.links.append(a)
        if tag == 'meta': self.meta[a.get('name', a.get('property'))] = a.get('content', '')
        if tag == 'title': self.in_title = True
        if tag == 'script' and a.get('type') == 'application/ld+json': self.in_schema = True

    def handle_endtag(self, tag):
        if tag == 'title': self.in_title = False
        if tag == 'script': self.in_schema = False

    def handle_data(self, data):
        if self.in_title: self.title += data
        if self.in_schema: self.schema += data


def main():
    metadata = json.loads((ROOT / 'content/seo.json').read_text())
    for lang, route in ROUTES.items():
        page = Head()
        page.feed((ROOT / 'dist' / route.strip('/') / 'index.html').read_text())
        assert page.lang == lang, f'{lang}: wrong document language'
        assert [a['href'] for a in page.links if a.get('rel') == 'canonical'] == [ORIGIN + route]
        alternates = [a for a in page.links if a.get('rel') == 'alternate']
        assert len(alternates) == 4
        assert {a['hreflang']: a['href'] for a in alternates} == EXPECTED
        assert page.title == metadata[lang]['title'] == page.meta['og:title']
        assert page.meta['description'] == metadata[lang]['description'] == page.meta['og:description']
        assert page.meta['og:url'] == ORIGIN + route
        assert not any(token in page.meta.get('robots', '').lower() for token in ('noindex', 'none'))
        graph = json.loads(page.schema)
        assert graph['@context'] == 'https://schema.org'
        entities = {item['@type']: item for item in graph['@graph']}
        assert entities['WebPage']['url'] == ORIGIN + route
        assert entities['WebPage']['inLanguage'] == lang
        assert entities['Organization']['telephone'] == '+998998112829'
        assert entities['Organization']['email'] == 'main@noveragroup.uz'
        assert not {'review', 'aggregateRating', 'address'} & entities['Organization'].keys()
    ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9', 'x': 'http://www.w3.org/1999/xhtml'}
    urls = ET.parse(ROOT / 'dist/sitemap.xml').findall('s:url', ns)
    services = json.loads((ROOT / 'content/services.json').read_text())['services']
    pages = json.loads((ROOT / 'content/pages.json').read_text())
    cases = json.loads((ROOT / 'content/cases.json').read_text())['cases']
    case_base = {'uz': '/ishlar/', 'en': '/en/work/', 'ru': '/ru/raboty/'}
    groups = ([ROUTES] + [s['slug'] for s in services] + [pages['about']['slug'], pages['privacy']['slug']]
              + [{l: case_base[l] + c['slug'][l].strip('/') + '/' for l in ROUTES} for c in cases])
    assert len(urls) == sum(len(g) for g in groups), 'sitemap URL count'
    by_loc = {url.findtext('s:loc', namespaces=ns): url for url in urls}
    for group in groups:
        expected = {lang: ORIGIN + path for lang, path in {**group, 'x-default': group['uz']}.items()}
        for path in group.values():
            url = by_loc.get(ORIGIN + path)
            assert url is not None, f'sitemap missing {path}'
            links = url.findall('x:link', ns)
            assert {a.attrib['hreflang']: a.attrib['href'] for a in links} == expected, f'hreflang {path}'
            assert (ROOT / 'dist' / path.strip('/') / 'index.html').is_file(), f'page missing {path}'
    robots = (ROOT / 'dist/robots.txt').read_text()
    assert 'Sitemap: '+ORIGIN+'/sitemap.xml' in robots
    assert not any(line.strip().lower() == 'disallow: /' for line in robots.splitlines())
    print('SEO CHECK: OK — 3 locales + service, about, privacy and case pages, metadata, canonical, hreflang, JSON-LD, sitemap, robots')


if __name__ == '__main__':
    main()
