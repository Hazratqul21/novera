#!/usr/bin/env python3
"""Push the Novera design into a local, throwaway Odoo website builder.

Odoo is only the design tool: theme values, header/footer options and snippet
pages live in this folder, so the whole site can be recreated in a fresh
database at any time. tools/odoo_site/export.py turns the rendered pages into
the static, CSP-safe site that is deployed.

    python3 tools/odoo_site/odoo.py setup   # theme, header, footer, menu (once per DB)
    python3 tools/odoo_site/odoo.py pages   # (re)write every page built by gen.py
"""
from __future__ import annotations

import base64
import os
import subprocess
import sys
import xmlrpc.client
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
URL = os.environ.get('ODOO_URL', 'http://127.0.0.1:8078')
DB = os.environ.get('ODOO_DB', 'novsite')
LOGIN = os.environ.get('ODOO_LOGIN', 'admin')
PASSWORD = os.environ.get('ODOO_PASSWORD', 'admin')
CONTAINER = os.environ.get('ODOO_CONTAINER', 'novsite-odoo')
# Repo assets are mirrored here so pages can use their final /assets/... paths.
STATIC = '/website/static/src/img/nv'
STATIC_DIR = '/usr/lib/python3/dist-packages/odoo/addons' + STATIC

HOMEPAGE = '/s'

THEME_COLORS = {'o-color-1': '#0E6444', 'o-color-2': '#8FE3B8', 'o-color-3': '#F1F4F0',
                'o-color-4': '#FFFFFF', 'o-color-5': '#0B1F17'}
THEME_VALUES = {
    'font': "'Onest'", 'headings-font': "'Playfair Display'", 'navbar-font': "'Onest'",
    'buttons-font': "'Onest'", 'google-fonts': "('Playfair Display', 'Onest')",
    'header-bg-blur': '14px', 'logo-height': '2rem',
    'btn-border-radius': '4px', 'btn-border-radius-sm': '4px', 'btn-border-radius-lg': '4px',
    'btn-padding-y-lg': '0.95rem', 'btn-padding-x-lg': '1.75rem', 'btn-font-weight': '500',
    'headings-font-weight': '500', 'display-1-font-size': '5.5rem', 'h1-font-size': '3.75rem',
    'h2-font-size': '2.9rem', 'footer-template': "'descriptive'", 'footer': '5', 'copyright': '5',
    'footer-scrolltop': 'true',
}
VIEWS_OFF = ['website.header_search_box', 'website.header_text_element', 'website.header_visibility_standard',
             'website.footer_language_selector_inline', 'portal.user_sign_in', 'website.brand_promotion',
             'web.brand_promotion', 'web.brand_promotion_message']
VIEWS_ON = ['website.header_visibility_fixed', 'website.header_language_selector_code',
            'website.template_footer_descriptive']
# Menu targets are placeholders: export.py swaps in each language's label and URL.
MENU = [('Xizmatlar', '#m-services'), ('Formatlar', '#m-formats'), ('Yondashuv', '#m-approach'),
        ('Savollar', '#m-faq'), ('Biz haqimizda', '#m-about')]
FOOTER_ROWS = '''<div class="row">
<div class="col-lg-12 pt64 pb24"><p class="h3 mb-0 s_nv_word">novera<span aria-hidden="true">✳</span></p></div>
<div class="col-lg-5 pb48"><p data-i18n="footer">IT autsorsing va dasturlash: biznesingizning keyingi bosqichi uchun web, mobil va aqlli tizimlarni yaratamiz.</p>
<p><a href="#m-contact" class="btn btn-lg btn-secondary" data-i18n="cta">Loyihani muhokama qilish</a></p></div>
<div class="col-lg-3 offset-lg-1 pb48"><ul class="list-unstyled"><li><a href="#m-services" data-i18n="menu0">Xizmatlar</a></li><li><a href="#m-approach" data-i18n="menu2">Yondashuv</a></li><li><a href="#m-about" data-i18n="menu4">Biz haqimizda</a></li><li><a href="#m-privacy" data-i18n="privacy">Maxfiylik siyosati</a></li></ul></div>
<div class="col-lg-3 pb48"><p><b data-i18n="city">Toshkent, O‘zbekiston</b></p><ul class="list-unstyled mb-2"><li><a href="tel:+998998112829">+998 99 811 28 29</a></li><li><a href="mailto:main@noveragroup.uz">main@noveragroup.uz</a></li></ul></div>
</div></div>
            '''
LOGO = HERE / 'logo.svg'  # preview only; export.py swaps in the inline wordmark


class Odoo:
    def __init__(self):
        self.uid = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common').authenticate(DB, LOGIN, PASSWORD, {})
        if not self.uid:
            sys.exit(f'Odoo login failed at {URL} / {DB}')
        self.m = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object', allow_none=True)

    def __call__(self, model, method, *args, **kw):
        try:
            return self.m.execute_kw(DB, self.uid, PASSWORD, model, method, list(args), kw)
        except xmlrpc.client.Fault as e:
            if 'cannot marshal None' in str(e):  # method ran, it just returned None
                return None
            raise

    def views(self, keys):
        return self('ir.ui.view', 'search', [('key', 'in', keys)], context={'active_test': False})

    def view(self, key):
        return self('ir.ui.view', 'search_read', [('key', '=', key)], fields=['arch_db'])[0]


def to_odoo(arch: str) -> str:
    return (arch.replace('"/assets/', f'"{STATIC}/assets/').replace(', /assets/', f', {STATIC}/assets/')
            .replace("url('/assets/", f"url('{STATIC}/assets/"))


def mirror_assets():
    subprocess.run(['docker', 'exec', '-u', '0', CONTAINER, 'mkdir', '-p', STATIC_DIR], check=True)
    subprocess.run(['docker', 'cp', str(ROOT / 'dist/assets'), f'{CONTAINER}:{STATIC_DIR}/'], check=True,
                   stdout=subprocess.DEVNULL)


def setup(o: Odoo):
    ctx = {'website_id': 1}
    custom = lambda url, values: o('website.assets', 'make_scss_customization', url, values, context=ctx)
    custom('/website/static/src/scss/options/colors/user_color_palette.scss', THEME_COLORS)
    custom('/website/static/src/scss/options/user_values.scss', THEME_VALUES)
    o('website.assets', 'save_asset', '/website/static/src/scss/user_custom_rules.scss', 'web.assets_frontend',
      (HERE / 'custom.scss').read_text(), 'scss', context=ctx)
    o('ir.ui.view', 'write', o.views(VIEWS_OFF), {'active': False})
    o('ir.ui.view', 'write', o.views(VIEWS_ON), {'active': True})

    o('website', 'write', [1], {'name': 'Novera', 'logo': base64.b64encode(LOGO.read_bytes()).decode()})
    o('res.company', 'write', [1], {'name': 'Novera', 'email': 'main@noveragroup.uz', 'phone': '+998 99 811 28 29',
                                    'city': 'Toshkent'})

    cta = o.view('website.header_call_to_action')
    o('ir.ui.view', 'write', [cta['id']], {'arch_db': cta['arch_db'].replace('href="/contactus"', 'href="#m-contact"').replace('href="#aloqa"', 'href="#m-contact"')
                                           .replace('>Contact Us<', '>Loyihani muhokama qilish<')})
    footer = o.view('website.template_footer_descriptive')
    arch = footer['arch_db']
    arch = arch[:arch.index('<div class="row">')] + FOOTER_ROWS + arch[arch.index('</section>'):]
    if True:
        o('ir.ui.view', 'write', [footer['id']], {'arch_db': arch})

    root = o('website.menu', 'search', [('website_id', '=', 1), ('parent_id', '=', False)])[0]
    o('website.menu', 'unlink', o('website.menu', 'search', [('parent_id', '=', root)]))
    for seq, (name, url) in enumerate(MENU):
        o('website.menu', 'create', {'name': name, 'url': url, 'parent_id': root, 'website_id': 1, 'sequence': seq})


def pages(o: Odoo):
    from gen import build
    mirror_assets()
    for p in build():
        arch = to_odoo(p['arch'])
        meta = {'website_meta_title': p['title'], 'website_meta_description': p['description']}
        found = o('website.page', 'search', [('url', '=', p['odoo'])])
        if found:
            view = o('website.page', 'read', found, fields=['view_id'])[0]['view_id'][0]
            o('ir.ui.view', 'write', [view], {'arch_db': arch})
            o('website.page', 'write', found, meta)
        else:
            view = o('ir.ui.view', 'create', {'name': p['path'], 'type': 'qweb', 'arch_db': arch, 'key': p['key'], 'website_id': 1})
            o('website.page', 'create', {'view_id': view, 'url': p['odoo'], 'website_published': True, 'website_id': 1,
                                         'name': p['title'], **meta})
    o('website', 'write', [1], {'homepage_url': HOMEPAGE})


if __name__ == '__main__':
    command = sys.argv[1] if len(sys.argv) > 1 else 'pages'
    client = Odoo()
    {'setup': setup, 'pages': pages}[command](client)
    print(f'odoo {command}: ok ({URL})')
