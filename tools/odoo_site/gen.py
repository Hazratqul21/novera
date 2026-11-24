"""Build Odoo snippet pages for every route of noveragroup.uz from content/*.json.

Pages are website-builder markup (s_split_intro, s_text_highlight, s_cards_grid,
s_comparisons, s_timeline, s_features, s_faq_collapse, s_website_form_cover ...)
so they can be opened and adjusted in the Odoo editor. odoo.py pushes them and
export.py publishes them into dist/.

Home page copy comes from content/translations.json (Uzbek source -> en/ru),
so the wording stays the one already approved for the live site.
Published paths stay as before: uz at /, en at /en/, ru at /ru/.
In Odoo a page lives at '/s' + its published path.
"""
from __future__ import annotations

import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LANGS = ('uz', 'en', 'ru')
TR = json.loads((ROOT / 'content/translations.json').read_text())
SERVICES = json.loads((ROOT / 'content/services.json').read_text())
PAGES_JSON = json.loads((ROOT / 'content/pages.json').read_text())
SEO = json.loads((ROOT / 'content/seo.json').read_text())

HOME = {'uz': '/', 'en': '/en/', 'ru': '/ru/'}
SVC = {s['id']: s for s in SERVICES['services']}
SVC_ORDER = ('web', 'mobile', 'integration', 'ai')


def T(uz: str, lang: str) -> str:
    if lang == 'uz':
        return uz
    try:
        return TR[uz][lang]
    except KeyError:
        raise SystemExit(f'translation missing for {lang}: {uz!r}')


def t(s) -> str:
    return escape(str(s), quote=False)


def a(s) -> str:
    return escape(str(s), quote=True)


def odoo_url(path: str) -> str:
    return '/s' + path.rstrip('/') if path != '/' else '/s'


UI = {
    'uz': {'open': 'Loyihani ko‘rish', 'visit': 'Saytni ochish', 'gallery': 'Ekranlar', 'work_p': 'Biz loyihalab, ishga tushirgan haqiqiy tizimlar: vazifa, yechim va natija.', 'menu': ['Ishlar', 'Xizmatlar', 'Formatlar', 'Yondashuv', 'Savollar', 'Biz haqimizda'], 'cta': 'Loyihani muhokama qilish',
           'footer': T('IT autsorsing va dasturlash: biznesingizning keyingi bosqichi uchun web, mobil va aqlli tizimlarni yaratamiz.', 'uz'),
           'city': 'Toshkent, O‘zbekiston', 'privacy': 'Maxfiylik siyosati', 'legal': '«NOVERA» MCHJ', 'tin': 'STIR 313 278 248', 'more': 'Batafsil',
           'nf_h': 'Sahifa topilmadi', 'nf_p': 'Havola eskirgan bo‘lishi mumkin. Bosh sahifadan boshlang.', 'nf_btn': 'Bosh sahifaga'},
    'en': {'open': 'View project', 'visit': 'Visit the site', 'gallery': 'Screens', 'work_p': 'Real systems we designed and launched: the challenge, the solution and the result.', 'menu': ['Work', 'Services', 'Formats', 'Approach', 'Questions', 'About'], 'cta': T('Loyihani muhokama qilish', 'en'),
           'footer': T('IT autsorsing va dasturlash: biznesingizning keyingi bosqichi uchun web, mobil va aqlli tizimlarni yaratamiz.', 'en'),
           'city': 'Tashkent, Uzbekistan', 'privacy': T('Maxfiylik siyosati', 'en'), 'legal': 'NOVERA LLC', 'tin': 'TIN 313 278 248', 'more': 'Learn more',
           'nf_h': 'Page not found', 'nf_p': 'The link may be out of date. Start from the home page.', 'nf_btn': 'Home page'},
    'ru': {'open': 'Смотреть проект', 'visit': 'Открыть сайт', 'gallery': 'Экраны', 'work_p': 'Реальные системы, которые мы спроектировали и запустили: задача, решение и результат.', 'menu': ['Работы', 'Услуги', 'Форматы', 'Подход', 'Вопросы', 'О нас'], 'cta': T('Loyihani muhokama qilish', 'ru'),
           'footer': T('IT autsorsing va dasturlash: biznesingizning keyingi bosqichi uchun web, mobil va aqlli tizimlarni yaratamiz.', 'ru'),
           'city': 'Ташкент, Узбекистан', 'privacy': T('Maxfiylik siyosati', 'ru'), 'legal': 'ООО «NOVERA»', 'tin': 'ИНН 313 278 248', 'more': 'Подробнее',
           'nf_h': 'Страница не найдена', 'nf_p': 'Возможно, ссылка устарела. Начните с главной страницы.', 'nf_btn': 'На главную'},
}

ICONS = {
    'screen': '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="2.5" y="4" width="13" height="10" rx="1.5"/><rect x="17" y="8" width="4.5" height="12" rx="1"/><path d="M6 19h6"/></svg>',
    'eye': '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M2 12s3.6-6.5 10-6.5S22 12 22 12s-3.6 6.5-10 6.5S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>',
    'bolt': '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M13 2L4 14h7l-1 8 9-12h-7z"/></svg>',
    'layers': '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/></svg>',
    'check': '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
}


def links(lang):
    home = HOME[lang]
    return {'work': home + '#ishlar', 'services': home + '#yechimlar', 'formats': home + '#hamkorlik', 'approach': home + '#yondashuv',
            'faq': home + '#savollar', 'about': PAGES_JSON['about']['slug'][lang], 'contact': home + '#boshlash',
            'privacy': PAGES_JSON['privacy']['slug'][lang], 'home': home}


def page(key, body):
    return f'<t t-name="{key}"><t t-call="website.layout"><div id="wrap" class="oe_structure">\n{body}\n</div></t></t>'


def srcset(name):
    return ', '.join(f'/assets/{name}-{w}.webp {w}w' for w in (600, 900, 1200))


def hero_band(title, lead='', crumbs=(), extra=''):
    nav = ''
    if crumbs:
        items = ''.join(f'<li class="breadcrumb-item"><a href="{a(u)}" class="text-reset">{t(n)}</a></li>' for n, u in crumbs)
        nav = f'<nav aria-label="breadcrumb"><ol class="breadcrumb mb-4 small">{items}</ol></nav>'
    lead_html = f'<p class="lead mb-0 s_nv_measure">{t(lead)}</p>' if lead else ''
    return f'''<section class="s_title s_nv_pagehead o_cc o_cc5 pt128 pb96" data-snippet="s_title" data-name="Title">
  <div class="container">{nav}<h1 class="display-3 mb-4 s_nv_measure_h" id="hero-title">{t(title)}</h1>{lead_html}{extra}</div>
</section>'''


def cta_band(lang):
    ui = SERVICES['ui'][lang]
    return f'''<section class="s_cta_box o_cc o_cc5 pt128 pb128 mx-finale s_nv_mist" data-snippet="s_cta_box" data-name="Call to Action"><div class="container">
<h2 class="mx-finale-title">{t(ui['cta_h'])}</h2><div class="mx-finale-row"><p class="lead">{t(ui['cta_p'])}</p>{eye_btn(links(lang)['contact'], ui['cta_btn'], light=True)}</div></div></section>'''


def faq(title, items, anchor=''):
    rows = ''.join(f'''<details class="accordion-item s_nv_faq"><summary class="accordion-button collapsed h6-fs mb-0">{t(q)}</summary>
<div class="accordion-body"><p class="mb-0">{t(ans)}</p></div></details>''' for q, ans in items)
    ident = f' id="{anchor}"' if anchor else ''
    return f'''<section class="s_faq_collapse pt96 pb96"{ident} data-snippet="s_faq_collapse" data-name="FAQ">
  <div class="container"><div class="row align-items-start s_nb_column_fixed">
    <div class="col-lg-4 pt16"><h2 class="display-5-fs">{title}</h2></div>
    <div class="col-lg-7 offset-lg-1"><div class="accordion accordion-flush">{rows}</div></div>
  </div></div>
</section>'''


def cards(title, items, cc='o_cc2', cols=3, inner='o_cc1'):
    width = {2: 'col-lg-6', 3: 'col-lg-4', 4: 'col-lg-3'}[cols]
    body = ''.join(f'''<div class="{width} col-md-6 pt16 pb16"><div class="s_card card o_cc {inner} h-100 border-0" data-snippet="s_card">
<div class="card-body p-4"><h3 class="card-title h5-fs">{t(h)}</h3><p class="card-text mb-0">{t(p)}</p></div></div></div>''' for h, p in items)
    return f'''<section class="s_cards_grid o_cc {cc} pt96 pb80" data-snippet="s_cards_grid" data-name="Cards Grid">
  <div class="container"><h2 class="display-5-fs mb-4">{title}</h2><div class="row">{body}</div></div>
</section>'''


def two_lines(first, second, lang):
    return f'{t(T(first, lang))}<br/>{t(T(second, lang))}'


STEPS = [('Tushunish', 'Maqsad, auditoriya va mavjud jarayonlarni o‘rganamiz. Vazifa chegarasi va ustuvorliklarni belgilaymiz.', 'NATIJA / Aniq loyiha brifi'),
         ('Loyihalash', 'Foydalanuvchi yo‘li, interfeys va texnik arxitektura. Kod yozishdan oldin yechimni birgalikda ko‘ramiz.', 'NATIJA / Dizayn va loyiha rejasi'),
         ('Yaratish', 'Yechimni bosqichma-bosqich quramiz. Har iteratsiyada natijani ko‘rsatib, fikringizni olamiz.', 'NATIJA / Sinovdan o‘tgan mahsulot'),
         ('Ishga tushirish', 'Yakuniy tekshiruv, joylashtirish va topshirish. Keyingi rivojlantirish rejasi alohida kelishiladi.', 'NATIJA / Ishga tayyor yechim')]


def timeline(lang, title_html, lead='', anchor='', cta=''):
    rows = ''
    for i, (h, p, res) in enumerate(STEPS):
        label, _, value = T(res, lang).partition(' / ')
        rows += f'''<div class="row border-top pt32 pb32 s_nv_step">
<div class="col-3 col-lg-2"><span class="display-5-fs s_nv_num">0{i + 1}</span></div>
<div class="col-9 col-lg-5"><h3 class="h4-fs">{t(T(h, lang))}</h3><p class="mb-0">{t(T(p, lang))}</p></div>
<div class="col-9 offset-3 col-lg-4 offset-lg-1 pt16 pt-lg-0"><p class="small text-uppercase mb-1 s_nv_muted">{t(label.capitalize())}</p><p class="mb-0 fw-medium">{t(value)}</p></div></div>'''
    ident = f' id="{anchor}"' if anchor else ''
    lead_html = f'<p class="lead s_nv_measure">{t(lead)}</p>' if lead else ''
    return f'''<section class="s_timeline pt96 pb80"{ident} data-snippet="s_timeline" data-name="Timeline">
  <div class="container"><div class="row mb-5"><div class="col-lg-7"><h2 class="display-4-fs">{title_html}</h2>{lead_html}</div>
  <div class="col-lg-4 offset-lg-1 d-flex align-items-end justify-content-lg-end">{cta}</div></div>{rows}</div>
</section>'''


# -- projects and interactive pieces ------------------------------------------------
CASES = json.loads((ROOT / 'content/cases.json').read_text())
CASE_BASE = {'ru': '/ru/raboty/', 'uz': '/ishlar/', 'en': '/en/work/'}
FEATURED = ('ijara-tolovlari', 'inna-ai', 'hubfield', 'ohma-katalog', 'gofrokarton-erp', 'kiberqalqon', 'barter-marketpleysi', 'cad-ai')
TONE = {'ijara-tolovlari': 'ijara', 'inna-ai': 'inna', 'gofrokarton-erp': 'erp', 'kiberqalqon': 'kiber',
        'barter-marketpleysi': 'barter', 'cad-ai': 'cad', 'ohma-katalog': 'ohma', 'hubfield': 'hub'}
SPARKLE = 'M12 1.8C14.2 8.7 15.3 9.8 22.2 12 15.3 14.2 14.2 15.3 12 22.2 9.8 15.3 8.7 14.2 1.8 12 8.7 9.8 9.8 8.7 12 1.8Z'

STAR = 'M30.00 2.00L34.78 18.45L49.80 10.20L41.55 25.22L58.00 30.00L41.55 34.78L49.80 49.80L34.78 41.55L30.00 58.00L25.22 41.55L10.20 49.80L18.45 34.78L2.00 30.00L18.45 25.22L10.20 10.20L25.22 18.45z'


def preloader():
    """Opening scene: the star spins in, then becomes a window the camera flies through (CSS in fx.css)."""
    word = ''.join(f'<b>{ch}</b>' for ch in 'novera')
    return (f'<div class="fx-preloader" aria-hidden="true"><svg viewBox="0 0 60 60"><g class="fx-in-zoom">'
            f'<path class="fx-in-wall" fill-rule="evenodd" d="M-1500-1500h3000v3000h-3000z{STAR}"/></g>'
            f'<path class="fx-in-fill" d="{STAR}"/><path class="fx-in-star" d="{STAR}"/></svg><div class="fx-in-word">{word}</div></div>')


def case_url(case, lang):
    return CASE_BASE[lang] + case['slug'][lang] + '/'


def metal_btn(href, label):
    """Liquid Metal Button+: chrome ring medallion, flowing chrome edge, frosted face."""
    stops = ''.join(f'<stop offset="{o}%" stop-color="{c}"/>' for o, c in
                    ((0, '#FFFFFF'), (28, '#7A879B'), (43, '#D7E4F5'), (54, '#FFFFFF'), (65, '#FFFFFF'), (84, '#7A879B'), (100, '#FFFFFF')))
    return f'''<a href="{a(href)}" class="mo-orbit fx-metal" data-hover-tone="light">
<svg class="fx-defs" width="0" height="0" aria-hidden="true"><defs><linearGradient id="fx-orbit-icon" x1="0" y1="0" x2="1" y2="0" gradientTransform="rotate(45 .5 .5)">{stops}</linearGradient></defs></svg>
<span class="orb-face"><span class="orb-decoration orb-wake fx-layer" aria-hidden="true"/><span class="orb-decoration fx-layer fx-metal-glass" aria-hidden="true"/>
<span class="orb-decoration orb-edge orb-edge-glow fx-layer" aria-hidden="true"/><span class="orb-decoration orb-edge fx-layer" aria-hidden="true"/>
<span class="orb-decoration orb-edge orb-edge-ridge fx-layer" aria-hidden="true"/><span class="orb-decoration orb-hover-edge fx-layer" aria-hidden="true"/>
<span class="orb-medallion" aria-hidden="true"><span class="orb-disc"/><span class="orb-decoration orb-fallback"/><canvas class="orb-decoration fx-metal-canvas"/>
<span class="orb-glyph"><svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><path d="{SPARKLE}" fill="url(#fx-orbit-icon)"/></svg></span></span>
<span class="orb-label">{t(label)}</span></span></a>'''


def glass_btn(href, label):
    """Liquid Glass Buttons, clear material on a dark surface, chevron icon."""
    return f'''<a href="{a(href)}" class="ml-optical-button fx-glass" data-material="clear" data-surface="dark">
<span class="ml-optical-face"><span class="ml-optical-body" aria-hidden="true"><span class="ml-optical-surface"><span class="ml-optical-tint"/><span class="ml-optical-shoulder"/>
<span class="ml-optical-reflection"/><span class="ml-optical-caustic"/><span class="ml-optical-pointer-light"/></span>
<span class="ml-optical-rim"/><span class="ml-optical-rim ml-optical-edge-light"/><span class="ml-optical-rim ml-optical-counter-light"/><span class="ml-optical-bottom"/></span>
<span class="ml-optical-label">{t(label)}</span><span class="ml-optical-icon" aria-hidden="true"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.25" stroke-linecap="round" stroke-linejoin="round"><path d="m9.5 6.5 5.5 5.5-5.5 5.5"/></svg></span></span></a>'''


def eye_btn(href, label, light=False):
    """Eye Follow Button: two eyes that follow the pointer and blink."""
    eye = '<span class="fx-eye-ball"><span class="fx-eye-pupil"/></span>'
    return (f'<a href="{a(href)}" class="fx-eye{" fx-eye--light" if light else ""}" data-magnetic="0.25"><span>{t(label)}</span>'
            f'<span class="fx-eyes" aria-hidden="true">{eye}{eye}</span></a>')


def tone(c):
    return 'sh-t-' + TONE.get(c['slug']['uz'], 'plain')


def framed(c, shots, lang, zoom=False, lazy=True):
    """Screenshots in a browser window, or in phones for mobile products."""
    cls, out = ('sh-phone', '') if c.get('device') == 'phone' else ('sh-frame', '')
    for src, alt in shots:
        img = f'<img src="/{a(src)}" alt="{a(alt[lang])}"{" loading=" + chr(34) + "lazy" + chr(34) if lazy else ""}/>'
        out += (f'<a class="{cls} sh-zoom" href="/{a(src)}" data-lightbox="1">{img}</a>' if zoom else f'<span class="{cls}">{img}</span>')
    return f'<span class="sh-phones">{out}</span>' if cls == 'sh-phone' else out


def shots_of(c):
    cover = [(c['cover'], c['cover_alt'])] if c.get('cover') else []
    return cover + [(g['src'], g['alt']) for g in c.get('gallery') or []]


def project_card(c, lang):
    shots = shots_of(c)
    art = framed(c, shots if c.get('device') == 'phone' else shots[:1], lang)
    facts = ''.join(f'<li>{t(h[0])}</li>' for h in c['highlights'][lang][:3])
    return f'''<a href="{a(case_url(c, lang))}" class="sh-card {tone(c)}"><span class="sh-card-text"><h3>{t(c['title'][lang])}</h3>
<p>{t(c['summary'][lang])}</p><ul class="sh-facts">{facts}</ul><span class="sh-more">{t(UI[lang]['open'])}</span></span><span class="sh-card-art">{art}</span></a>'''


def case(c, lang, nxt):
    u, ui = UI[lang], CASES['ui'][lang]
    meta = [(ui['client'], c['client'][lang]), (ui['sector'], c['sector'][lang]),
            (ui['status'], c['status'][lang]), (ui['year'], c['year'])]
    meta_html = '<dl class="row mt-5 mb-0 s_nv_meta">' + ''.join(
        f'<div class="col-6 col-lg-3 pt16"><dt class="small fw-normal">{t(k)}</dt><dd class="mb-0">{t(v)}</dd></div>' for k, v in meta) + '</dl>'
    shots = shots_of(c)
    phone = c.get('device') == 'phone'
    art = f'<div class="sh-hero-art">{framed(c, shots if phone else shots[:1], lang, zoom=True, lazy=False)}</div>' if shots else ''
    visit = f'<p class="mt-4 mb-0"><a class="sh-visit" href="{a(c["url"])}" target="_blank" rel="noopener">{t(u["visit"])}</a></p>' if c.get('url') else ''
    body = f'''<section class="sh-hero {tone(c)}" data-snippet="s_title" data-name="Title"><div class="container">
<nav aria-label="breadcrumb"><ol class="breadcrumb mb-4 small"><li class="breadcrumb-item"><a href="{a(links(lang)['work'])}">{t(u['menu'][0])}</a></li></ol></nav>
<h1 id="hero-title">{t(c['title'][lang])}</h1><p class="lead mb-0">{t(c['summary'][lang])}</p>{visit}{meta_html}{art}</div></section>'''
    for label, key in ((ui['challenge'], 'challenge'), (ui['solution'], 'solution'), (ui['result'], 'result')):
        paras = ''.join(f'<p class="lead">{t(p)}</p>' for p in c[key][lang])
        body += f'''<section class="s_title_split pt64 pb32" data-snippet="s_title_split" data-name="Title Split"><div class="container"><div class="row border-top pt48">
<div class="col-lg-4"><h2 class="h3-fs">{t(label)}</h2></div><div class="col-lg-7 offset-lg-1">{paras}</div></div></div></section>'''
    points = ''.join(f'<li><h3>{t(h)}</h3><p>{t(p)}</p></li>' for h, p in c['highlights'][lang])
    more = [] if phone else shots[1:]
    if more:
        figs = ''.join(f'<figure class="{tone(c)}">{framed(c, [x], lang, zoom=True)}<figcaption>{t(x[1][lang])}</figcaption></figure>' for x in more)
        body += f'''<section class="sh-scroll o_cc o_cc1" data-snippet="s_features"><div class="container"><div class="row">
<div class="col-lg-4 sh-points-col mb-5"><h2 class="display-5-fs mb-4">{t(c['highlights_title'][lang])}</h2><ul class="sh-points">{points}</ul></div>
<div class="col-lg-8 ps-lg-5"><div class="sh-shots">{figs}</div></div></div></div></section>'''
    else:
        body += cards(c['highlights_title'][lang], c['highlights'][lang])
    badges = ''.join(f'<span class="s_badge badge s_nv_badge me-2 mb-2 fw-normal">{t(s)}</span>' for s in c['stack'])
    body += f'''<section class="s_text_block pt64 pb32" data-snippet="s_text_block"><div class="container"><div class="row border-top pt48">
<div class="col-lg-4"><h2 class="h3-fs">{t(ui['stack'])}</h2></div><div class="col-lg-7 offset-lg-1 fs-5">{badges}</div></div></div></section>
<section class="s_projects_list pt48 pb96" data-snippet="s_projects_list"><div class="container">
<a href="{a(case_url(nxt, lang))}" class="sh-next {tone(nxt)}"><span><small>{t(ui['next'])}</small><b>{t(nxt['title'][lang])}</b></span><span class="sh-next-art">{framed(nxt, shots_of(nxt)[:1], lang)}</span></a></div></section>'''
    body += cta_band(lang)
    return body, f"{c['title'][lang]} — Novera", c['summary'][lang]


# -- home --------------------------------------------------------------------
def home(lang):
    L, u = links(lang), UI[lang]
    tr = lambda s: T(s, lang)
    directions = ''.join(f'<span class="s_badge badge s_nv_chip me-2 mb-2 fw-normal">{t(tr(d))}</span>'
                         for d in ('Web platformalar', 'Mobil ilovalar', 'Biznes tizimlari', 'AI & Data', 'Integratsiya'))
    bullets = {'web': ('UX/UI va interaktiv prototip', 'Frontend, backend va CMS', 'SEO asoslari va ishga tushirish'),
               'mobile': ('iOS va Android ilovalari', 'API va bildirishnomalar', 'Relizga tayyorlash va sinov'),
               'integration': ('CRM, ERP va to‘lov integratsiyasi', 'Botlar va ichki ish oqimlari', 'Ma’lumotlarni sinxronlash'),
               'ai': ('Bilim bazasiga ulangan yordamchi', 'Tahlil va hisobotlar', 'Inson nazorati va sifat baholash')}
    leads = {'web': 'Brendingizni ifodalaydigan saytlar. Mijozlaringiz qaytib keladigan web-ilovalar.',
             'mobile': 'iOS va Android uchun qulay, ravon va biznesingiz bilan birga o‘sadigan ilovalar.',
             'integration': 'Tarqoq tizimlarni bog‘laymiz. Takroriy ishlarni aniq jarayonga aylantiramiz.',
             'ai': 'Ma’lumotlardan foydali xulosalar. Jamoangiz vazifalariga mos AI yordamchilar.'}
    images = {'web': 'digital-products', 'mobile': 'digital-products', 'integration': 'connected-systems', 'ai': 'connected-systems'}
    svc_cards = ''
    for i, k in enumerate(SVC_ORDER):
        s = SVC[k]
        items = ''.join(f'<li class="d-flex gap-2 py-1"><span class="text-o-color-1">{ICONS["check"]}</span>{t(tr(b))}</li>' for b in bullets[k])
        img = (f'<figure class="o_card_img_wrapper ratio ratio-16x9 mb-0"><img class="o_card_img card-img-top" src="/assets/{images[k]}-900.webp" '
               f'srcset="{srcset(images[k])}" sizes="(min-width: 992px) 50vw, 100vw" alt="" loading="lazy"/></figure>') if i in (0, 2) else ''
        svc_cards += f'''<div class="col-lg-6 pt16 pb16"><a href="{a(s['slug'][lang])}" class="s_card card o_cc o_cc1 h-100 text-reset text-decoration-none s_nv_card" data-snippet="s_card">{img}
<div class="card-body p-4 p-lg-5"><h3 class="card-title h3-fs">{t(s[lang]['name'])}</h3><p class="card-text">{t(tr(leads[k]))}</p><ul class="list-unstyled mb-4">{items}</ul>
<span class="s_nv_link">{t(u['more'])}</span></div></a></div>'''
    formats = [('To‘liq loyiha', 'G‘oyadan dizayn, dasturlash va ishga tushirishgacha bitta hamkor bilan.', 'Yangi mahsulot yoki platformani yaratishda.', 'Kelishilgan hajm, bosqichlar va qabul mezonlari.', 'Loyihani muhokama qilish'),
               ('Jamoani kuchaytirish', 'Mavjud jamoangizga kerakli texnik kompetensiya va qo‘shimcha ishlab chiqish quvvati.', 'Ichki jamoa bor, lekin resurs yoki tajriba yetishmaydi.', 'Birgalikdagi backlog, rollar va muntazam natija ko‘rigi.', 'Jamoa ehtiyojini muhokama qilish'),
               ('Rivojlantirish', 'Mavjud mahsulotni audit qilish, integratsiya qo‘shish va texnik qarzni kamaytirish.', 'Tizim ishlayapti, keyingi bosqichga tayyorlash kerak.', 'Texnik audit, ustuvor vazifalar va bosqichli yaxshilash.', 'Tizimni muhokama qilish')]
    fmt = ''.join(f'''<div class="col-lg-4 pt16 pb16"><div class="s_card card o_cc {'o_cc5' if i == 0 else 'o_cc1'} h-100 border-0" data-snippet="s_card"><div class="card-body p-4 p-lg-5 d-flex flex-column">
<h3 class="card-title h3-fs">{t(tr(n))}</h3><p class="card-text">{t(tr(d))}</p>
<dl class="mt-2 mb-4"><dt class="small s_nv_muted fw-normal">{t(tr('Qachon mos?'))}</dt><dd>{t(tr(w))}</dd><dt class="small s_nv_muted fw-normal">{t(tr('Ishlash tartibi'))}</dt><dd class="mb-0">{t(tr(h))}</dd></dl>
<a href="#boshlash" class="btn {'btn-secondary' if i == 0 else 'btn-outline-primary'} mt-auto align-self-start">{t(tr(c))}</a></div></div></div>''' for i, (n, d, w, h, c) in enumerate(formats))
    principles = ''.join(f'<div class="col-lg-4 pt24"><h3 class="h4-fs">{t(tr(h))}</h3><p class="mb-0">{t(tr(p))}</p></div>' for h, p in (
        ('Biznesdan boshlaymiz', 'Avval maqsad va jarayon. Keyin texnologiya va kod.'),
        ('Inson uchun yaratamiz', 'Murakkab tizim ortida ham tushunarli tajriba bo‘lishi kerak.'),
        ('Kelajakni hisobga olamiz', 'Yangi vazifalar uchun kengaytiriladigan arxitektura.')))
    quality = ''.join(f'''<div class="col-lg-3 col-md-6 pt16 pb16"><span class="s_nv_icon rounded mb-3" aria-hidden="true">{ICONS[ic]}</span>
<h3 class="h5-fs">{t(tr(h))}</h3><p class="mb-0">{t(tr(p))}</p></div>''' for ic, h, p in (
        ('screen', 'Har ekranga mos', 'Telefon, planshet va desktop uchun alohida o‘ylangan tajriba.'),
        ('eye', 'Qulay va tushunarli', 'Aniq navigatsiya, o‘qiladigan matn va klaviatura bilan boshqarish.'),
        ('bolt', 'Yengil va tezkor', 'Optimallashtirilgan media va vazifaga mos texnik yechimlar.'),
        ('layers', 'Davom ettirishga tayyor', 'Tushunarli kod va kelishilgan topshirish hujjatlari.')))
    qa = [(tr(q), tr(x)) for q, x in (
        ('Loyiha narxi qanday aniqlanadi?', 'Vazifalar, integratsiyalar va hajmni aniqlagandan keyin taklif tayyorlaymiz. Narx hamda ish tarkibi boshlashdan oldin kelishiladi.'),
        ('Faqat g‘oya bo‘lsa ham murojaat qilsam bo‘ladimi?', 'Albatta. Dastlabki suhbatda g‘oyani foydalanuvchi ehtiyoji, asosiy funksiyalar va birinchi bosqichga ajratamiz.'),
        ('Mavjud tizimni rivojlantirasizmi?', 'Ha. Avval mavjud kod va arxitekturani o‘rganib, takomillashtirish yoki integratsiya yo‘lini taklif qilamiz.'),
        ('Qancha vaqtda tayyor bo‘ladi?', 'Muddat loyiha hajmiga bog‘liq. Brifdan so‘ng bosqichlar, topshirish mezonlari va vaqt rejasini kelishamiz.'))]
    radios = ''.join(f'''<div class="form-check form-check-inline me-3 mb-2"><input class="form-check-input" type="radio" name="service" id="svc-{i}" value="{a(v)}"{' checked="checked"' if i == 0 else ''}/>
<label class="form-check-label" for="svc-{i}">{t(tr(v))}</label></div>''' for i, v in enumerate(('Web platforma', 'Mobil ilova', 'Integratsiya', 'AI va data', 'Boshqa')))
    steps_cta = f'<a href="#boshlash" class="btn btn-lg btn-primary">{t(tr("Birinchi qadamni qo‘yamiz"))}</a>'
    cases = {c['slug']['uz']: c for c in CASES['cases']}
    stack = ''.join(project_card(cases[k], lang) for k in FEATURED)
    rows = ''.join(f'''<div class="col-lg-12 pt32 pb24 border-bottom"><a href="{a(case_url(c, lang))}" class="row text-reset text-decoration-none align-items-baseline s_nv_row">
<div class="col-12 col-lg-8"><h3 class="display-5-fs mb-0">{t(c['short'][lang])}</h3></div><div class="col-12 col-lg-4 text-lg-end"><span class="s_nv_muted">{t(c['sector'][lang])}</span></div></a></div>''' for c in CASES['cases'] if c['slug']['uz'] not in FEATURED)
    body = preloader() + f'''
<section class="s_split_intro o_cc o_cc5 pt128 pb96 s_nv_hero" data-snippet="s_split_intro" data-name="Split Intro">
  <div class="container"><div class="row align-items-center">
    <div class="col-lg-6 pb48 o_animate o_anim_fade_in o_anim_from_bottom">
      <h1 class="display-1 mb-4" id="hero-title">{two_lines('Katta g‘oyalar.', 'Aniq yechimlar.', lang)}</h1>
      <p class="lead mb-5 s_nv_measure">{t(tr('IT autsorsing va dasturlash: biznesingizning keyingi bosqichi uchun web, mobil va aqlli tizimlarni yaratamiz.'))}</p>
      <div class="d-flex flex-wrap align-items-center gap-3">{metal_btn('#boshlash', u['cta'])}{glass_btn('#ishlar', u['menu'][0])}</div>
    </div>
    <div class="col-lg-6 o_animate o_anim_fade_in">
      <img src="/assets/novera-sculpture-900.webp" srcset="{srcset('novera-sculpture')}" sizes="(min-width: 992px) 50vw, 100vw" class="img img-fluid s_nv_sculpture" alt="{a(tr('Bog‘langan tizimlarni ifodalovchi yashil va kumush rangli abstrakt haykal'))}" fetchpriority="high"/>
    </div>
  </div></div>
</section>
<section class="s_text_highlight o_cc o_cc2 pt64 pb64" data-snippet="s_text_highlight" data-name="Text Highlight">
  <div class="container"><div class="row align-items-center">
    <div class="col-lg-6"><p class="h2-fs mb-3 mb-lg-0 s_nv_serif">{two_lines('Strategiya. Dizayn. Dasturlash.', 'Bitta yaxlit yondashuv.', lang)}</p></div>
    <div class="col-lg-6 text-lg-end">{directions}</div>
  </div></div>
</section>
<section class="s_title_split pt128 pb48" id="ishlar" data-snippet="s_title_split" data-name="Title Split"><div class="container"><div class="row"><div class="col-lg-7"><h2 class="display-3-fs">{t(CASES['ui'][lang]['title'])}</h2></div>
<div class="col-lg-4 offset-lg-1 d-flex align-items-end"><p class="lead mb-0">{t(u['work_p'])}</p></div></div></div></section>
<section class="s_projects_grid pb48" data-snippet="s_projects_grid" data-name="Projects Grid"><div class="container"><div class="sh-stack">{stack}</div></div></section>
<section class="s_projects_list pt32 pb64" data-snippet="s_projects_list" data-name="Projects List"><div class="container"><div class="row">{rows}</div></div></section>
<section class="s_cards_grid pt96 pb80" id="yechimlar" data-snippet="s_cards_grid" data-name="Cards Grid">
  <div class="container">
    <div class="row mb-4"><div class="col-lg-7"><h2 class="display-4-fs">{two_lines('Vazifa sizniki.', 'Yechim — birgalikda.', lang)}</h2></div>
    <div class="col-lg-4 offset-lg-1 d-flex align-items-end"><p class="lead mb-0">{t(tr('Bir sahifali saytdan murakkab platformagacha. Texnologiyani vazifangizga qarab tanlaymiz.'))}</p></div></div>
    <div class="row">{svc_cards}</div>
  </div>
</section>
<section class="s_comparisons o_cc o_cc2 pt96 pb96" id="hamkorlik" data-snippet="s_comparisons" data-name="Comparisons">
  <div class="container">
    <div class="row mb-4"><div class="col-lg-7"><h2 class="display-4-fs">{two_lines('Jamoangizga mos.', 'Maqsadingizga yo‘naltirilgan.', lang)}</h2></div>
    <div class="col-lg-4 offset-lg-1 d-flex align-items-end"><p class="lead mb-0">{t(tr('Qayerdan boshlayotganingizdan qat’i nazar, mas’uliyat va ish chegarasini avval kelishamiz.'))}</p></div></div>
    <div class="row">{fmt}</div>
  </div>
</section>
<section class="s_text_cover o_cc o_cc5 pt128 pb128 s_nv_mist" data-snippet="s_text_cover" data-name="Text Cover">
  <div class="container"><h2 class="display-3-fs s_nv_measure_h">{two_lines('Shunchaki ishlaydigan emas.', 'Ishingizni yengillash\xadtiradigan.', lang)}</h2>
  <div class="row mt-4">{principles}</div></div>
</section>
{timeline(lang, two_lines('Har bosqichda', 'ravshanlik.', lang), tr('Nima qilinayotgani, nima uchun va keyingi qadam qanday — birgalikda aniqlaymiz.'), 'yondashuv', steps_cta)}
<section class="s_features o_cc o_cc2 pt96 pb80" data-snippet="s_features" data-name="Features">
  <div class="container"><h2 class="display-4-fs mb-4">{two_lines('Faqat tashqi', 'ko‘rinish emas.', lang)}</h2><div class="row">{quality}</div></div>
</section>
<section class="s_cta_box pt96 pb48" id="ai-estimator" data-snippet="s_cta_box" data-name="AI Estimate">
  <div class="container"><div class="s_card card o_cc o_cc5 border-0 s_nv_ctacard" data-snippet="s_card"><div class="card-body p-4 p-lg-5">
    <div class="row"><div class="col-lg-5"><h2 class="display-5-fs" id="ai-estimator-title">{t(tr('Loyihani AI yordamida baholash.'))}</h2>
      <p class="lead">{t(tr("Maqsadingizni yozing. Bizning sun'iy intellekt tizimimiz real vaqt rejimida texnologiyalar stekini va taxminiy byudjetni hisoblab beradi."))}</p></div>
    <div class="col-lg-6 offset-lg-1">
      <form id="ai-calc-form" aria-labelledby="ai-estimator-title">
        <div class="d-none" aria-hidden="true"><input type="text" name="website" tabindex="-1" autocomplete="off"/></div>
        <label class="form-label" for="ai-description">{t(tr('Loyiha tafsilotlari'))}</label>
        <textarea id="ai-description" name="description" rows="4" class="form-control mb-3" required="required" minlength="10" placeholder="{a(tr('Masalan: Logistika kompaniyasi uchun haydovchilarni kuzatish tizimi va CRM kerak...'))}"/>
        <button type="submit" class="btn btn-lg btn-secondary">{t(tr('Loyihani tahlil qilish'))}</button>
      </form>
      <div id="ai-calc-result" class="s_nv_result mt-4" aria-live="polite" hidden="hidden"/>
    </div></div>
  </div></div></div>
</section>
{faq(two_lines('Boshlashdan', 'oldin.', lang), qa, 'savollar')}
<section class="s_website_form_cover o_cc o_cc2" id="boshlash" data-snippet="s_website_form_cover">
  <div class="container-fluid"><div class="row s_nb_column_fixed">
    <div class="col-lg-5 oe_img_bg o_bg_img_center pt128 pb128 s_nv_formimg" style="background-image: url('/assets/novera-sculpture-1200.webp');"/>
    <div class="col-lg-7 pt80 pb80 px-4 px-lg-5">
      <h2 class="display-4-fs">{two_lines('G‘oyangiz bor.', 'Endi unga yo‘l ochamiz.', lang)}</h2>
      <p class="lead">{t(tr('Qisqacha vazifangizni yozing. Birinchi suhbatdan yechim yo‘lini birgalikda aniqlaymiz.'))}</p>
      <p class="mb-4"><a href="mailto:main@noveragroup.uz" class="text-decoration-underline me-4">main@noveragroup.uz</a><a href="tel:+998998112829" class="text-decoration-underline">+998 99 811 28 29</a></p>
      <form id="brief-form" class="s_website_form" novalidate="novalidate">
        <div class="d-none" aria-hidden="true"><input type="text" name="website" tabindex="-1" autocomplete="off"/></div>
        <fieldset class="mb-3"><legend class="form-label fs-6">{t(tr('Qaysi yo‘nalish sizga kerak?'))}</legend>{radios}</fieldset>
        <div class="row"><div class="col-md-6 mb-3"><label class="form-label" for="brief-name">{t(tr('Ismingiz yoki kompaniya nomi'))} *</label><input id="brief-name" type="text" class="form-control" required="required" autocomplete="name"/></div>
        <div class="col-md-6 mb-3"><label class="form-label" for="brief-contact">{t(tr("Aloqa ma'lumotlari"))} *</label><input id="brief-contact" type="text" class="form-control" required="required" placeholder="{a(tr('Telefon raqami yoki Email'))}"/></div></div>
        <div class="mb-3"><label class="form-label" for="brief">{t(tr('Nima yaratmoqchisiz?'))} *</label><textarea id="brief" rows="4" class="form-control" required="required" placeholder="{a(tr('G‘oyangiz, mavjud muammo yoki kerakli yechim…'))}"/></div>
        <button type="submit" class="btn btn-lg btn-primary">{t(tr('Arizani yuborish'))}</button>
        <p id="form-status" class="mt-3 mb-0" role="status" aria-live="polite"/>
        <p class="small s_nv_muted mt-3 mb-0">{t(tr("Ma'lumotlaringiz faqat arizangizga javob berish uchun ishlatiladi."))}</p>
      </form>
    </div>
  </div></div>
</section>'''
    return body, SEO[lang]['title'], SEO[lang]['description']


# -- service -------------------------------------------------------------------
def service(s, lang):
    ui, d = SERVICES['ui'][lang], s[lang]
    image = 'digital-products' if s['id'] in ('web', 'mobile') else 'connected-systems'
    body = hero_band(d['h1'], d['lead'], ((ui['home'], HOME[lang]), (ui['services'], links(lang)['services'])),
                     f'<p class="mt-5 mb-0"><a href="{a(links(lang)["contact"])}" class="btn btn-lg btn-secondary">{t(UI[lang]["cta"])}</a></p>')
    body += f'''<section class="s_picture o_cc o_cc5 pb96" data-snippet="s_picture"><div class="container">
<img src="/assets/{image}-1200.webp" srcset="{srcset(image)}" sizes="100vw" alt="" class="img img-fluid rounded w-100 s_nv_artwork"/></div></section>'''
    body += cards(t(ui['build']), d['kinds'], cc='o_cc1', inner='o_cc2')
    body += cards(t(ui['scope']), d['scope'], cc='o_cc2')
    body += timeline(lang, t(ui['process']))
    if d.get('faq'):
        body += faq(t(ui['faq']), d['faq'])
    others = [SVC[k] for k in SVC_ORDER if k != s['id']]
    rows = ''.join(f'''<div class="col-lg-4 pt16 pb16"><a href="{a(o['slug'][lang])}" class="s_card card o_cc o_cc2 h-100 border-0 text-reset text-decoration-none s_nv_card" data-snippet="s_card">
<div class="card-body p-4"><h3 class="h5-fs">{t(o[lang]['name'])}</h3><p class="mb-0">{t(o[lang]['lead'])}</p></div></a></div>''' for o in others)
    body += f'<section class="s_three_columns pt48 pb16" data-snippet="s_three_columns"><div class="container"><h2 class="h3-fs">{t(ui["other"])}</h2><div class="row">{rows}</div></div></section>'
    body += cta_band(lang)
    return body, d['title'], d['description']


# -- about, privacy, 404 -------------------------------------------------------
def about(lang):
    p, ui = PAGES_JSON['about'], PAGES_JSON['ui'][lang]
    body = hero_band(p['headline'][lang], p['lead'][lang], ((ui['home'], HOME[lang]),))
    body += cards(t(p['principles_title'][lang]), p['principles'][lang], cc='o_cc1', inner='o_cc2')
    svc = ''.join(f'''<div class="col-lg-3 col-md-6 pt16 pb16"><a href="{a(SVC[k]['slug'][lang])}" class="s_card card o_cc o_cc1 h-100 border-0 text-reset text-decoration-none s_nv_card" data-snippet="s_card">
<div class="card-body p-4"><h3 class="h5-fs">{t(SVC[k][lang]['name'])}</h3><p class="mb-0">{t(SVC[k][lang]['lead'])}</p></div></a></div>''' for k in SVC_ORDER)
    body += f'<section class="s_cards_grid o_cc o_cc2 pt96 pb80" data-snippet="s_cards_grid"><div class="container"><h2 class="display-5-fs mb-4">{t(p["services_label"][lang])}</h2><div class="row">{svc}</div></div></section>'
    body += timeline(lang, t(SERVICES['ui'][lang]['process']))
    body += cta_band(lang)
    return body, p['title'][lang], p['description'][lang]


def privacy(lang):
    p, ui = PAGES_JSON['privacy'], PAGES_JSON['ui'][lang]
    body = hero_band(p['name'][lang], ui['updated'], ((ui['home'], HOME[lang]),))
    sections = ''.join(f'''<div class="row border-top pt32 pb16"><div class="col-lg-4"><h2 class="h4-fs">{t(h)}</h2></div>
<div class="col-lg-7 offset-lg-1">{''.join(f'<p>{t(x)}</p>' for x in (paras if isinstance(paras, list) else [paras]))}</div></div>''' for h, paras in p['sections'][lang])
    body += f'<section class="s_text_block pt64 pb96" data-snippet="s_text_block"><div class="container">{sections}</div></section>'
    return body, p['title'][lang], p['description'][lang]


def not_found(lang):
    u = UI[lang]
    body = hero_band(u['nf_h'], u['nf_p'], (), f'<p class="mt-5 mb-0"><a href="{a(HOME[lang])}" class="btn btn-lg btn-secondary">{t(u["nf_btn"])}</a></p>')
    return body, u['nf_h'] + ' — Novera', u['nf_p']


def build():
    out = []

    def add(path, lang, group, result):
        body, title, description = result
        key = 'website.nv' + odoo_url(path).replace('/', '_').replace('-', '_').replace('.', '_')
        out.append({'path': path, 'lang': lang, 'group': group, 'title': title, 'description': description,
                    'odoo': odoo_url(path), 'arch': page(key, body), 'key': key})

    for lang in LANGS:
        add(HOME[lang], lang, 'home', home(lang))
        for i, c in enumerate(CASES['cases']):
            add(case_url(c, lang), lang, 'case:' + c['slug']['uz'], case(c, lang, CASES['cases'][(i + 1) % len(CASES['cases'])]))
        for k in SVC_ORDER:
            add(SVC[k]['slug'][lang], lang, 'svc:' + k, service(SVC[k], lang))
        add(PAGES_JSON['about']['slug'][lang], lang, 'about', about(lang))
        add(PAGES_JSON['privacy']['slug'][lang], lang, 'privacy', privacy(lang))
    add('/404.html', 'uz', '404', not_found('uz'))
    return out


if __name__ == '__main__':
    pages = build()
    print(len(pages), 'pages')
