# Qoidalar

## Brend

- Novera — mustaqil brend. Boshqa kompaniyalar saytlariga havola, logo yoki
  eslatma qo‘yilmaydi.
- Ranglar: deep green `#0e6444`, ink `#0d1a15`, fon `#f1f4f2`, tonal green
  `#d7ebe0`, gold `#c08a1e`. Hero — yashil-kumush skulptura.
- Shriftlar: Inter (matn), Unbounded (sarlavha). O‘z serverimizda.
- Native cursor va native scroll saqlanadi; scroll hijack, majburiy intro yo‘q.

## Kontent

- Faqat haqiqiy ma’lumot: o‘ylab topilgan mijoz, raqam, mukofot, sharh yo‘q.
- Case faqat mijoz tasdiqlagan loyihadan.
- Kontakt: `main@noveragroup.uz`, telefon `+998998112829` (telefon JSON-LD’da
  ham bor — `check_seo.py` buni talab qiladi).

## Xavfsizlik

- Repo public: `.env`, kalit, token, parol, server IP/login commit qilinmaydi.
- Oldin tarixdan `backend/.env` olib tashlangan (filter-branch). Unda bo‘lgan
  OpenAI, Gemini va Telegram kalitlari **egasi tomonidan almashtirilishi kerak**.
  Boshqa ishtirokchilar eski tarixni qayta push qilmasligi uchun:
  `git fetch && git reset --hard origin/develop`.
- CSP yumshatilmaydi; yangi kod alohida faylda.
- Deploydan oldin zaxira. Serverdagi boshqa loyihalarga tegilmaydi.

## Git

- Commit xabarlari oddiy, inglizcha, nima o‘zgarganini aytadi.
- Commit’larda avtomatik yaratuvchi yoki vosita imzolari (Co-Authored-By va
  shunga o‘xshash) qo‘yilmaydi.
- Push va deploy egasining roziligi bilan.
