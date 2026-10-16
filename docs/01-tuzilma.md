# Tuzilma

## Papkalar

```
innovera/
├── content/               Manba: shablon va matnlar
│   ├── index.html         Bosh sahifa shabloni (o‘zbekcha)
│   ├── translations.json  O‘zbekcha matn → {en, ru}
│   ├── seo.json           Bosh sahifa title/description
│   ├── services.json      4 xizmat sahifasi
│   ├── pages.json         "Biz haqimizda" va maxfiylik
│   └── cases.json         Case study’lar (hozir bo‘sh)
├── dist/                  Public papka — serverga aynan shu yuklanadi
│   ├── assets/            ⚠ MANBA: site.css, site.js, theme.js, messages.js, shrift, rasm
│   └── *.html, sitemap    Generatsiya qilinadi (qo‘lda tahrirlanmaydi)
├── tools/                 Generator va tekshiruvlar
├── backend/               FastAPI + Docker (ariza va AI baholash)
└── docs/                  Shu hujjatlar
```

**Diqqat:** bu yerda `dist/` git’da saqlanadi va
`dist/assets/` ichidagi CSS/JS — haqiqiy manba fayllar. Ularni to‘g‘ridan-to‘g‘ri
tahrirlash to‘g‘ri. `dist/` dagi `.html` fayllar esa generatsiya qilinadi.

## Assets (`dist/assets/`)

| Fayl | Vazifasi |
|---|---|
| `site.css` | Barcha stillar: tokenlar (`--green #0e6444` …), light/dark, bosh sahifa, xizmat, about, legal, case |
| `theme.js` | `<head>`da: tanlangan yoki tizim mavzusini darhol qo‘yadi (miltillash bo‘lmasligi uchun) |
| `site.js` | Menyu, reveal, forma yuborish (`/api/v1/lead`), AI baholash (`/api/v1/estimate`) |
| `messages.js` | Forma xabarlari uchala tilda |
| `inter-variable.woff2` | Inter (matn) |
| `unbounded-*.woff2` | Unbounded (sarlavhalar), latin / latin-ext / cyrillic bo‘laklari |
| `novera-sculpture.jpg` | Hero rasmi (yashil-kumush skulptura) |
| `digital-products.jpg`, `connected-systems.jpg` | Xizmat rasmlari |

CSS/JS o‘zgarganda `content/index.html`dagi `?v=` versiyasini oshiring
(masalan `site.css?v=20261016i`).

## Tools

| Skript | Vazifasi |
|---|---|
| `build_locales.py` | `content/index.html` → `dist/index.html`, `dist/en/`, `dist/ru/`. Tarjima yetishmasa to‘xtaydi |
| `build_services.py` | 4 xizmat × 3 til = 12 sahifa (header/footer bosh sahifadan olinadi) |
| `build_pages.py` | About, maxfiylik, case sahifalari; barcha sahifalarda footer havolalarini lokalizatsiya qiladi; eski case papkalarini o‘chiradi; `sitemap.xml` ni yozadi |
| `check_site.py` | Fayl va havolalar, kontrast juftliklari |
| `check_seo.py` | Har sahifa: lang, canonical, hreflang, JSON-LD to‘g‘riligi, sitemap URL soni |
| `qa_preview.py` | Lokal QA yordamchisi |

Tartib muhim: **locales → services → pages** (keyingisi oldingisi yasagan
bosh sahifadan header/footer oladi).

## Sahifalar xaritasi (21 URL)

| Sahifa | uz | en | ru |
|---|---|---|---|
| Bosh | `/` | `/en/` | `/ru/` |
| Web platformalar | `/xizmatlar/web-platformalar/` | `/en/services/web-platforms/` | `/ru/uslugi/veb-platformy/` |
| Mobil ilovalar | `/xizmatlar/mobil-ilovalar/` | `/en/services/mobile-apps/` | `/ru/uslugi/mobilnye-prilozheniya/` |
| Integratsiya | `/xizmatlar/integratsiya-avtomatlashtirish/` | `/en/services/integration-automation/` | `/ru/uslugi/integratsiya-avtomatizatsiya/` |
| AI va data | `/xizmatlar/ai-data/` | `/en/services/ai-data/` | `/ru/uslugi/ii-dannye/` |
| Biz haqimizda | `/biz-haqimizda/` | `/en/about/` | `/ru/o-nas/` |
| Maxfiylik | `/maxfiylik/` | `/en/privacy/` | `/ru/konfidentsialnost/` |
| Case (kelajakda) | `/ishlar/<slug>/` | `/en/work/<slug>/` | `/ru/raboty/<slug>/` |
