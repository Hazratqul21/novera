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
                target = ROOT / value.lstrip('/')
                if target.is_dir(): target /= 'index.html'
                if not target.is_file(): self.errors.append('Missing asset: ' + value)

check = Check()
check.feed((ROOT / 'index.html').read_text())
check.errors += ['Missing anchor: ' + item for item in check.anchors if item not in check.ids]
if check.headings != 1: check.errors.append('Expected one h1')
for locale in ('en','ru'):
    page = Check()
    document = (ROOT / locale / 'index.html').read_text()
    page.feed(document)
    page.errors += ['Missing anchor: '+a for a in page.anchors if a not in page.ids]
    if page.headings != 1: page.errors.append('Expected one h1')
    if f'lang="{locale}"' not in document: page.errors.append('Language missing')
    if f'href="https://innovera.uz/{locale}/"' not in document: page.errors.append('Canonical missing')
    check.errors += [locale+': '+error for error in page.errors]
for css in ROOT.glob('assets/*.css'):
    text = css.read_text()
    for url in re.findall(r'url\([\'"]?([^\)\'"\s]+)', text):
        if not (css.parent / url).is_file(): check.errors.append('Missing CSS asset: ' + url)
    if re.search(r'transition\s*:\s*all', text): check.errors.append('Avoid transition: all')
ET.parse(ROOT / 'sitemap.xml')
def luminance(color):
    values = [int(color[i:i+2],16)/255 for i in (1,3,5)]
    linear = [v/12.92 if v <= 0.04045 else ((v+0.055)/1.055)**2.4 for v in values]
    return sum(v*w for v,w in zip(linear,(0.2126,0.7152,0.0722)))

for foreground, background, minimum in (
    ('#5b6b64','#f1f4f2',4.5), ('#ffffff','#0e6444',4.5),
    ('#bbd2c5','#06291d',4.5), ('#375748','#d7ebe0',4.5),
    ('#9a6d13','#d7ebe0',3), ('#9a6d13','#f1f4f2',3),
    ('#b0c4b8','#101b16',4.5), ('#10251a','#96d5b2',4.5),
    ('#bdd2c5','#1e392c',4.5), ('#e6c773','#101b16',3),
):
    light, dark = sorted((luminance(foreground),luminance(background)), reverse=True)
    ratio = (light+0.05)/(dark+0.05)
    if ratio < minimum: check.errors.append(f'Contrast {foreground}/{background}: {ratio:.2f}')
for name in ('references', '.git', '.env', 'tools'):
    if (ROOT / name).exists(): check.errors.append('Private file in public output: ' + name)
if check.errors: raise SystemExit('\n'.join(check.errors))
print('SITE CHECK: OK — anchors, assets, image dimensions, sitemap, public boundaries')
