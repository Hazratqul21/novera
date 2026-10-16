# Server va infratuzilma

## Umumiy

| Narsa | Qiymat |
|---|---|
| Statik sayt | `/var/www/innovera` |
| Nginx | `/etc/nginx/sites-available/innovera` |
| SSL | Let’s Encrypt: `noveragroup.uz` va `innovera.uz` sertifikatlari (certbot, webroot `/var/www/certbot`) |
| CDN/himoya | Cloudflare (noveragroup.uz) |
| Backend | `~/apps/novera/backend`, konteyner `backend-api-1`, `127.0.0.1:8010` |
| Zaxiralar | `~/backups/innovera/` |

Serverda boshqa loyihalar ham bor — ularga tegilmaydi. Nginx va Docker umumiy,
global o‘zgarish faqat egasining roziligi bilan.

## Nginx

- `http://*`, `www.noveragroup.uz`, `innovera.uz`, `www.innovera.uz` →
  `https://noveragroup.uz$request_uri` (301).
- `root /var/www/innovera`; `/api/` → `http://127.0.0.1:8010`.
- CSP: `default-src 'self'`, skript faqat o‘zimiz va
  `static.cloudflareinsights.com`, `connect-src` o‘zimiz va
  `cloudflareinsights.com`. Inline skript/stil taqiqlangan.
- HTTP/2 yoqilgan. Kesh: shriftlar 365 kun, videolar va css/js/rasmlar 30 kun.
  HTML keshlanmaydi — CSS/JS o‘zgarsa `?v=` majburiy, rasm almashsa fayl nomini
  o‘zgartiring (Cloudflare ham shu muddatda saqlaydi).

Tahrir tartibi: nusxa (`~/backups/innovera/nginx-innovera.<sabab>.bak`) →
tahrir → `sudo nginx -t` → `sudo systemctl reload nginx`.

## Backend (`backend/main.py`)

| Endpoint | Vazifa |
|---|---|
| `GET /api/v1/health` | Holat |
| `POST /api/v1/lead` | Ariza: `name`, `contact`, `service`, `details`, `lang` → Telegram yopiq chat |
| `POST /api/v1/estimate` | Loyiha tavsifi (`description`, 10–1000 belgi) → Gemini → taxminiy baho JSON |

Himoya:
- Faqat loopback; tashqaridan nginx orqali. Haqiqiy IP `X-Real-IP` dan.
- Honeypot `website` maydoni.
- IP bo‘yicha limit: 10 daqiqada `lead` 5 ta, `estimate` 5 ta (pullik kvota).
- CORS faqat noveragroup.uz va innovera.uz domenlari.
- `/docs` va OpenAPI o‘chirilgan.
- Docker: `read_only`, `cap_drop: ALL`, `no-new-privileges`, 256 MB, log 3×5 MB.
- Gemini’ga ism va kontakt yuborilmaydi — faqat tavsif (maxfiylik siyosatida shunday yozilgan).

Sozlamalar (`backend/.env.example`): `GEMINI_API_KEY`, `GEMINI_MODEL`,
`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `PORT=8010`, ixtiyoriy `ALLOWED_ORIGINS`.

```bash
docker logs --tail 50 backend-api-1
cd ~/apps/novera/backend && docker compose restart
```

## Analitika

Cloudflare Web Analytics — cookie o‘rnatmaydi. Boshqa analitika yoki pixel
qo‘shilsa, CSP va maxfiylik siyosatini ham yangilash shart.
