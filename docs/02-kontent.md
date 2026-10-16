# Kontent

Qoida: `dist/` dagi `.html` fayllarni qo‘lda tahrirlamang — keyingi buildda
o‘chib ketadi. Matn `content/` da o‘zgartiriladi.

## 1. Bosh sahifa matni

1. `content/index.html` da o‘zbekcha matnni o‘zgartiring.
2. `content/translations.json` ga kalit qo‘shing:
   `"O‘zbekcha matn": {"en": "...", "ru": "..."}`.
3. `python3 tools/build_locales.py` — yetishmagan tarjimalarni ro‘yxat qilib
   to‘xtaydi.

Kalit matn bilan aynan mos bo‘lishi kerak, jumladan yashirin defis `U+00AD`
(masalan "yengillash­tiradigan" — telefonda chiroyli bo‘linishi uchun).
Tarjima qilinmaydigan brend yorliqlari `build_locales.py` dagi `brand_labels`da.

Title/description: `content/seo.json`.

## 2. Xizmatlar (`content/services.json`)

`services` ro‘yxati, har element:

| Maydon | Ma’nosi |
|---|---|
| `id` | `web`, `mobile`, `integration`, `ai` kabi ichki nom |
| `slug` | `{uz, en, ru}` URL |
| `image` | Hero rasmi (`/assets/...`) |
| `uz` / `en` / `ru` | `name`, `title`, `description`, `h1`, `lead`, `kinds`, `scope`, `faq` |

`ui` — sahifa yorliqlari (bo‘lim nomlari, CTA). Bo‘lim ustidagi kichik yorliqlar
`eb_*` kalitlarida (raqamlar emas, matn).

Bosh sahifadagi xizmat havolalari uz slug bilan yoziladi; `build_locales.py`
ularni en/ru slugga avtomatik almashtiradi.

## 3. Biz haqimizda va maxfiylik (`content/pages.json`)

- `about.team` bo‘sh bo‘lsa jamoa bloki chiqmaydi.
- `privacy.sections` haqiqiy ma’lumot oqimiga mos: ariza → Telegram yopiq chat,
  AI baholashga faqat loyiha tavsifi (ism/kontakt emas) → Google Gemini,
  Cloudflare Web Analytics (cookie’siz), server loglari 14 kun. Backend yoki
  analitika o‘zgarsa, matnni va `ui.updated` sanasini yangilang.
- Shahar yoki manzil hozircha yozilmagan.

## 4. Case study (`content/cases.json`)

Hozir `cases: []` — hech narsa chiqmaydi (bosh sahifada "Ishlar" bloki ham yo‘q).
Faqat haqiqiy, mijoz tasdiqlagan loyihalar qo‘shiladi. Maydonlar ro‘yxati
faylning `_comment` qismida:

`slug`, `client`, `year`, `cover` (1600×1000 webp), `title`, `summary`, `sector`,
`services` (services.json `id`lari), `challenge`/`solution`/`result`
(paragraflar), ixtiyoriy `gallery` va `quote`.

Case bo‘lsa, bosh sahifada `#yechimlar` bo‘limidan oldin "Ishlar" setkasi paydo
bo‘ladi. Bu yerda `cover` majburiy (kartochka rasmi), `client` — oddiy matn.

Sinov: `NOVERA_CASES=/yo‘l/test.json python3 tools/build_pages.py`. Sinovdan
keyin oddiy build qiling — `build_pages.py` eski case papkalarini o‘zi o‘chiradi.
**Sinov dist’ini deploy qilmang.**

Case qo‘shilgach `check_seo.py` URL sonini avtomatik hisobga oladi.

## 5. Rasm

- `dist/assets/` ga qo‘ying, HTML’da aniq `width`/`height` bering.
- Yangi rasm g‘oyalari va avvalgi prompt: `ARTWORK.md`.
