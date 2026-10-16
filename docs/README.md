# Novera sayti — hujjatlar

noveragroup.uz saytining tuzilishi va ish tartibi. Yangi ishni boshlashdan
oldin shu yerdan o‘qing.

| Fayl | Nima haqida |
|---|---|
| [01-tuzilma.md](01-tuzilma.md) | Papkalar, fayllar, sahifalar xaritasi |
| [02-kontent.md](02-kontent.md) | Matn, xizmat, case, sahifa va tarjima qo‘shish |
| [03-build-va-deploy.md](03-build-va-deploy.md) | Build, tekshiruv, deploy, qaytarish |
| [04-server.md](04-server.md) | Nginx, Cloudflare, Docker backend, forma va AI baholash |
| [05-qoidalar.md](05-qoidalar.md) | Brend, xavfsizlik, git qoidalari |
| [06-holat.md](06-holat.md) | Hozirgi holat va ochiq vazifalar |

## Bir qarashda

- **Nima:** Novera — IT autsorsing kompaniyasining korporativ sayti.
- **Domen:** https://noveragroup.uz (asosiy). `innovera.uz` va `www.` → 301 bilan
  noveragroup.uz ga.
- **Texnologiya:** framework yo‘q. HTML shablon + Python generatorlar, qo‘lda
  yozilgan CSS/JS. Node kerak emas.
- **Tillar:** o‘zbek (`/`), ingliz (`/en/`), rus (`/ru/`).
- **Backend:** FastAPI (`backend/`): ariza → Telegram, loyiha tavsifi → Gemini
  orqali taxminiy baho.
- **Repo:** `Hazratqul21/novera` (**public**), `main` va `develop` bir xil.

## Eng ko‘p ishlatiladigan buyruqlar

```bash
python3 tools/build_locales.py && python3 tools/build_services.py && python3 tools/build_pages.py
python3 tools/check_site.py && python3 tools/check_seo.py
python3 -m http.server 8092 --bind 127.0.0.1 --directory dist
```
