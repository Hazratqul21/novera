# Hozirgi holat (16.10.2026)

## Jonli saytda

- Bosh sahifa (uz/en/ru), 4 xizmat × 3 til, "Biz haqimizda", maxfiylik —
  21 URL sitemapda.
- Ariza formasi (Telegram) va AI taxminiy baho (Gemini).
- `main` = `develop` = `5113d13`.

## Tezlik (Lighthouse, mobil, 16.10.2026)

Bosh sahifa: 77 ball, LCP 4.5s, CLS 0.136. Accessibility/Best practices/SEO — 100.
Desktop 96–97.

Sabablar va reja (hali boshlanmagan):
- CLS: Unbounded shrifti almashganda matn siljiydi; `nav-js` klassi kech
  qo‘shiladi → `<head>`da erta qo‘yish, Unbounded subsetini tilga qarab preload.
- LCP: `novera-sculpture.jpg` (212 KB, 1200px) kech topiladi → WebP `srcset`
  va preload.
- Inter variable (352 KB) → latin va cyrillic bo‘laklarga subset.
- Nginx HTTP/2 va uzoqroq kesh — egasining ruxsati kerak.

## Kutilayotgan ma’lumotlar

- Haqiqiy loyihalar (case) — mijoz ruxsati bilan.
- Jamoa a’zolari (`pages.json` → `about.team`).
- Yangi Gemini kaliti va Telegram bot tokeni (eskisi oshkor bo‘lgan, almashtirish kerak).
