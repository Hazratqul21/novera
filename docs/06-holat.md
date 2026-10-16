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
