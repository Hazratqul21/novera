# Novera / innovera.uz

Standalone corporate landing in Uzbek, English and Russian. No Node dependencies.
Template: `content/index.html`; translations: `content/translations.json`.
Styles and scripts: `dist/assets/`. Generated pages: `dist/index.html`,
`dist/en/index.html`, `dist/ru/index.html`. INNASOFT and Barter projects are untouched.

## Local preview

```sh
cd /Users/hazratqulabduraufov/Desktop/innovera
python3 -m http.server 8092 --bind 127.0.0.1 --directory dist
```

Open http://127.0.0.1:8092/. Refresh after editing files.

## Validate

```sh
python3 tools/check_site.py
node --check dist/assets/site.js
```

After changing text/template, regenerate all pages before preview/deployment:

```sh
python3 tools/build_locales.py
```

Do not edit generated HTML directly. The generator validates translation coverage,
creates per-language canonical/hreflang metadata and a three-route sitemap.
Dynamic form messages live in `dist/assets/messages.js`.
Theme initially follows the OS and then remembers the explicit choice in localStorage.

## Design

Read-only reference: Desktop/Barterapp/src/index.css. Deep green #0e6444,
ink #0d1a15, cool ground #f1f4f2, tonal green #d7ebe0 and gold #c08a1e.
Inter variable font is self-hosted; license included alongside the font.
Apple-design guidance informs type hierarchy and direct press feedback.
Material-inspired tonal surfaces and pill controls, not a replica of either brand.
Scroll reveals use WAAPI transform/opacity, 600ms strong ease-out, once per item.
Buttons use 160ms press feedback. Reduced motion removes movement. Native cursor
and native scrolling remain; no forced intro delay or scroll hijacking.

## Content and contact

Only supplied company scope is claimed; no invented clients, metrics or awards.
Confirmed contacts: info@innovera.uz and +998998112829.
The brief form opens a prefilled mailto draft, not a server submission. It does
not collect or persist user data. The visitor sends the draft themselves.
Without JS, direct email and phone links remain available.

## Deploy later

Deployment is intentionally deferred until the user supplies their SSH access.
Serve ONLY `dist/` as the HTTPS document root; do not upload project/private files.
Before replacing an existing site, inspect virtual-host configuration and back it
up. Configure innovera.uz DNS, TLS and www redirect. Test mailto on an actual device.
No credentials belong in this repository.

## Verification status

Local HTTP, static checks, and real in-app browser responsive/interaction checks
are complete. See QA-NOTES.md for tested paths and remaining release checks.
Native devices, Lighthouse, DNS/TLS and the receiving mailbox remain unchecked;
no full WCAG or performance score is claimed. New image prompts: ARTWORK.md.

## Generated asset

Built-in imagegen, one original render. Asset: `dist/assets/novera-sculpture.jpg`.
Prompt: square premium sculptural 3D studio render of two interlocking folded
ribbons forming an abstract forward bridge / N-like structure, not a literal
logo; connected systems and technology crafted carefully. Deep forest emerald
enamel #0e6444 / #127a52, brushed silver, subtle pale gold edging. Seamless cool
gray #f1f4f2 background, soft studio light and grounded shadow. Centered sculpture
occupies 75% of frame. No text, UI, logos, watermark, neon or background gradient.
