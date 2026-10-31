# Hozirgi holat (16.10.2026)

## Jonli saytda

- Bosh sahifa (uz/en/ru), 4 xizmat × 3 til, "Biz haqimizda", maxfiylik —
  21 URL sitemapda.
- Ariza formasi (Telegram) va AI taxminiy baho (Gemini).
- `main` = `develop` = `5113d13`.

## Tezlik (Lighthouse, mobil)

| | Oldin (16.10, jonli) | Keyin (lokal) | Keyin (jonli) |
|---|---|---|---|
| Bosh sahifa | 77, LCP 4.5s, CLS 0.136 | 98, LCP 2.3s | 92–93, LCP 2.5s, CLS 0 |
| /ru/ | — | 95 | 90 |
| Xizmat sahifasi | — | 99 | — |
| Desktop | 96–97 | 100 | — |

16.10.2026 serverga chiqdi.

Nima qilindi: Inter 352 KB → 45 KB lotin + 18 KB kirill subset; Unbounded va
Inter tilga mos subseti preload (ru — kirill); hero va xizmat rasmlari WebP
`srcset` (213 KB → 15–43 KB); `nav-js` klassi `theme.js`da birinchi paintdan oldin.

Nginx HTTP/2 va uzoq kesh yoqilgandan keyin (jonli, mobil): bosh sahifa va /ru/ —
100, LCP 1.5–1.6s, CLS 0.002.

## Kutilayotgan ma’lumotlar

- Haqiqiy loyihalar (case) — mijoz ruxsati bilan.
- Jamoa a’zolari (`pages.json` → `about.team`).
- Yangi Gemini kaliti va Telegram bot tokeni (eskisi oshkor bo‘lgan, almashtirish kerak).

## Redizayn (26.10.2026, jonli)

- Gibrid yo‘nalish: o‘rmon-yashil immersiv hero (haykal kursorga qarab buriladi) + yorug‘ editorial bo‘limlar.
- Shriftlar: Playfair Display (sarlavha), Onest (matn), Inter faqat "novera" wordmark harflari (`inter-wordmark.woff2`).
- Palitra: forest `#0B1F17`, brand `#0E6444`, mint `#8FE3B8` (faqat qorong‘i fonda), fon `#F1F4F0`.
- Yangi qatlam: `dist/assets/v2.css`, `dist/assets/v2.js` (site.css/site.js ustidan yuklanadi).
- Komponentlar: glass sticky header (qorong‘i bo‘limlar ustida `.is-dark`), Mega menyu (build_locales.mega_menu),
  Ctrl/⌘+K qidiruv (`dist/assets/search.json`, build_pages), jonli validatsiya + toast, marquee, tilt, split sarlavhalar,
  back-to-top, Toshkent soati, ovoz (sukut bo‘yicha o‘chiq), View Transitions, skeleton.
- Lighthouse (jonli): /ru/ mobil 95, desktop 99; / mobil 93; a11y/BP/SEO 100.

## Dizayn tanqidi va tuzatishlar (28.10.2026)

Tekshiruv mezoni: "andaza" alomatlari (har sarlavha ustidagi yorliq, tugmaga yopishtirilgan strelka,
sarlavhada bitta qatorni rang/kursiv bilan ajratish, bir xil kartochkalar to‘plami, har bo‘limda fade-up).

- Bo‘lim yorliqlari (eyebrow) olib tashlandi: sarlavha va menyu bo‘limni allaqachon nomlaydi.
- Tugma va havolalar matnidagi ↗ → ↓ strelkalar olib tashlandi; tugma shakli o‘zi harakatni bildiradi.
- Asosiy chaqiruv butun sahifada bir xil nomlandi ("Loyihani muhokama qilish").
- Harakat bitta joyda: hero (yuklanish ketma-ketligi). Har bo‘limdagi fade-up, har sarlavhadagi
  so‘zma-so‘z animatsiya va ko‘p kartochkalardagi tilt olib tashlandi.
- Raqamli markerlar faqat haqiqiy ketma-ketlikda qoldi (jarayon qadamlari).
- Keyingi qadamda qilmaslik kerak: yangi bo‘limga avtomatik eyebrow, strelka yoki scroll fade-up qo‘shish.
- Novera: xizmatlar kartochkalar o‘rniga editorial indeks qatorlari; sarlavhalarning ikkinchi qatori endi rangli kursiv aksent emas; haykal ustidagi qo‘shimcha shior olib tashlandi.

## Odoo website builder bilan qayta chizish (31.10.2026, lokal, deploy qilinmagan)

Dizayn Odoo website builder bloklari bilan chizildi; sayt avvalgidek statik, Odoo faqat lokal chizish quroli.

- Lokal Odoo 20: `novsite-odoo` (127.0.0.1:8078, baza `novsite`).
- Manba: `tools/odoo_site/` — `gen.py` (content/*.json va translations.json → 3 tilda 22 sahifa),
  `odoo.py setup|pages`, `custom.scss`, `static.css`, `export.py` (Odoo render → `dist/*.html`), `serve.py`.
- Yangi assetlar: `dist/assets/builder.css` (generatsiya), `builder.js`, `forms.js` (ariza → `/api/v1/lead`,
  AI baho → `/api/v1/estimate`, avvalgi format), `messages.js` saqlandi.
- URL’lar o‘zgarmadi (21 + 404). `check_site.py` va `check_seo.py` o‘tadi.
- Lighthouse (lokal, siqishsiz): Performance 93–96, Accessibility/Best Practices/SEO 100.
- Eski `build_locales.py` / `build_services.py` / `build_pages.py` endi ishlatilmaydi: ular yangi sahifalarni
  eski dizayn bilan qayta yozib yuboradi.

Ish tartibi: `python3 tools/odoo_site/odoo.py pages && python3 tools/odoo_site/export.py && python3 tools/check_site.py && python3 tools/check_seo.py`
