# Build, tekshiruv va deploy

## 1. Build

```bash
cd ~/Desktop/innovera
python3 tools/build_locales.py    # /, /en/, /ru/
python3 tools/build_services.py   # 12 xizmat sahifasi
python3 tools/build_pages.py      # about, maxfiylik, case’lar, sitemap
python3 tools/check_site.py
python3 tools/check_seo.py
node --check dist/assets/site.js
python3 -m http.server 8092 --bind 127.0.0.1 --directory dist
```

`dist/` butunlay o‘chirilmaydi (u yerda manba assets bor), generatorlar faqat
o‘z HTML fayllarini qayta yozadi.

## 2. Deploydan oldin

- [ ] Uchala tekshiruv o‘tdi.
- [ ] `/`, `/en/`, `/ru/` va o‘zgargan sahifalar; 360px va desktop; light/dark.
- [ ] Klaviatura, fokus, reduced-motion.
- [ ] Konsolda xato va CSP buzilishi yo‘q.
- [ ] CSS/JS o‘zgargan bo‘lsa `?v=` oshirildi.
- [ ] `dist/` da sinov case’lari yoki keraksiz fayl qolmagan
      (`ls dist/ishlar dist/en/work 2>/dev/null` bo‘sh bo‘lishi kerak, toki
      haqiqiy case yo‘q ekan).

## 3. Serverga joylash

Server manzili va kirish ma’lumotlari repoda saqlanmaydi (sayt Cloudflare
ortida, origin IP oshkor qilinmasligi kerak) — egasidan oling. Quyida
`$SERVER` — `foydalanuvchi@host`.

Statik sayt papkasi: `/var/www/innovera`.

```bash
# 1) zaxira
ssh $SERVER 'tar -czf ~/backups/innovera/pre-<nom>-$(date +%Y%m%d-%H%M%S).tgz -C /var/www/innovera .'

# 2) yuklash (macOS ._* fayllarisiz)
COPYFILE_DISABLE=1 tar --no-xattrs -czf - -C dist . | \
  ssh $SERVER 'tar -xzf - -m -C /var/www/innovera && find /var/www/innovera -name "._*" -delete'

# 3) tekshirish
curl -sI https://noveragroup.uz/ | head -5
```

Bu usul serverdagi ortiqcha fayllarni o‘chirmaydi. Sahifa olib tashlansa,
serverdagi papkani ham alohida o‘chiring (zaxiradan keyin).

Cloudflare keshi: HTML odatda keshlanmaydi; CSS/JS uchun `?v=` yetarli. Kerak
bo‘lsa Cloudflare panelida "Purge cache".

Qaytarish:

```bash
ssh $SERVER 'rm -rf /var/www/innovera/* && tar -xzf ~/backups/innovera/<zaxira>.tgz -C /var/www/innovera'
```

## 4. Backend

Serverdagi nusxa: `~/apps/novera/backend` (Docker Compose, konteyner `backend-api-1`).

```bash
COPYFILE_DISABLE=1 tar --no-xattrs --exclude=.env --exclude=__pycache__ -czf - -C backend . | \
  ssh $SERVER 'tar -xzf - -C ~/apps/novera/backend'
ssh $SERVER 'cd ~/apps/novera/backend && docker compose up -d --build'
curl -s https://noveragroup.uz/api/v1/health
```

Serverdagi `.env` ustidan yozilmaydi.

## 5. Git

- Repo **public**. Hech qachon `.env`, kalit, token, server IP yoki parol
  commit qilinmaydi. `.gitignore` `.env` va `backend/.env` ni bloklaydi,
  faqat `.env.example` ruxsat etilgan.
- `main` va `develop` sinxron saqlanadi.
- Push faqat egasining roziligi bilan.
