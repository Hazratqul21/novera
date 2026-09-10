#!/usr/bin/env python3
"""Dependency-free checks for the exact public directory."""
from pathlib import Path
from html.parser import HTMLParser
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1] / 'dist'

class Check(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.anchors, self.errors = set(), [], []
        self.headings = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            if a['id'] in self.ids: self.errors.append('Duplicate id: ' + a['id'])
            self.ids.add(a['id'])
        if tag == 'h1': self.headings += 1
        if tag == 'img' and not all(k in a for k in ('alt', 'width', 'height')):
            self.errors.append('Image needs alt and dimensions')
        for key in ('src', 'href'):
            value = a.get(key, '')
            if value.startswith('#'):
                if len(value) > 1: self.anchors.append(value[1:])
            elif value and not value.startswith(('http:', 'https:', 'mailto:', 'tel:', 'data:')):
                if not (ROOT / value).is_file(): self.errors.append('Missing asset: ' + value)

check = Check()
check.feed((ROOT / 'index.html').read_text())
check.errors += ['Missing anchor: ' + item for item in check.anchors if item not in check.ids]
if check.headings != 1: check.errors.append('Expected one h1')
for css in ROOT.glob('assets/*.css'):
    text = css.read_text()
    for url in re.findall(r'url\([\'"]?([^\)\'"\s]+)', text):
        if not (css.parent / url).is_file(): check.errors.append('Missing CSS asset: ' + url)
    if re.search(r'transition\s*:\s*all', text): check.errors.append('Avoid transition: all')
ET.parse(ROOT / 'sitemap.xml')
for name in ('references', '.git', '.env', 'tools'):
    if (ROOT / name).exists(): check.errors.append('Private file in public output: ' + name)
if check.errors: raise SystemExit('\n'.join(check.errors))
print('SITE CHECK: OK — anchors, assets, image dimensions, sitemap, public boundaries')
