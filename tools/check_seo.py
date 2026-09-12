#!/usr/bin/env python3
"""Check generated metadata, reciprocal language links and truthful JSON-LD."""
import json
from html.parser import HTMLParser
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://innovera.uz'
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
        assert entities['Organization']['email'] == 'info@innovera.uz'
        assert not {'review', 'aggregateRating', 'address'} & entities['Organization'].keys()
    ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9', 'x': 'http://www.w3.org/1999/xhtml'}
    urls = ET.parse(ROOT / 'dist/sitemap.xml').findall('s:url', ns)
    assert len(urls) == 3
    assert {url.findtext('s:loc', namespaces=ns) for url in urls} == {ORIGIN + r for r in ROUTES.values()}
    for url in urls:
        links = url.findall('x:link', ns)
        assert len(links) == 4
        assert {a.attrib['hreflang']: a.attrib['href'] for a in links} == EXPECTED
    robots = (ROOT / 'dist/robots.txt').read_text()
    assert 'Sitemap: '+ORIGIN+'/sitemap.xml' in robots
    assert not any(line.strip().lower() == 'disallow: /' for line in robots.splitlines())
    print('SEO CHECK: OK — 3 locales, metadata, canonical, hreflang, JSON-LD, sitemap, robots')


if __name__ == '__main__':
    main()
