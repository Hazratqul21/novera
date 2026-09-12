# Novera QA — 2026-09-10

## Multilingual outsourcing expansion — 2026-09-12

- Added detailed deliverables to each of four services and three engagement models:
  end-to-end delivery, team extension and product evolution. No fabricated clients,
  awards, performance statistics or case studies added.
- Separate static UZ/EN/RU pages, shared template and checked translation dictionary.
  Localized SEO, image alt text, form labels, service values and runtime validation.
- Complete light/dark tokens, system initial preference, persistent manual toggle,
  localized accessible toggle label. Theme switching does not animate the full page.
- Real in-app browser: all 30 combinations (3 languages × 2 themes × widths
  360/390/768/1280/1440) had no horizontal overflow.
- Russian dark desktop hero and partnership section reviewed visually. English
  and Russian service selections and validation messages checked. Language switch
  retains theme. No console errors seen in these tested paths.
- Static asset/anchor checks now cover all three routes and representative dark
  text/button/focus contrast pairs. No native-device or Lighthouse score claimed.

## Implemented

- Two new generated conceptual service illustrations (not customer case studies).
  1200×800 JPEGs, lazy loading, fixed aspect ratio and explicit dimensions.
- Four consistent SVG service icons, compact service grid, quality criteria section.
- Sticky navigation, active section indication, reading progress and active process
  step. Native scrolling; event-driven single RAF, no perpetual animation loop.
- 600ms once-only transform/opacity reveals and 2.5% gated image hover zoom.
  Keyboard navigation bypasses reveals; motion preference changes cancel animation.
- Increased mobile text sizes, 44px footer email target, darker focus outline.
- Browser history now keeps anchor visits; modifier-click preserves browser defaults.
- Brif form hidden until JS initializes; direct phone/email usable without JS.
  Uzbek required/whitespace validation and local TXT download fallback for visitors
  without an email application. No automatic mail transmission or data persistence.

## Verified in the real in-app browser

- 360×800, 390×844, 768×1024, 1280×900, 1440×960: no horizontal overflow.
- Desktop hero, image stories, service grid and tablet process inspected visually.
- All three images loaded; no console errors seen in tested paths.
- 360px: visible links, buttons and summary controls all at least 44px high.
- Service link selected the corresponding mobile radio in the brief form.
- Empty required field focused; whitespace-only content rejected with Uzbek message.
- Non-sensitive test brief triggered download and accurate not-sent status.
- FAQ opens and closes with Enter; anchor navigation is keyboard-operable.
- Script-stripped local fixture: no scripts, form hidden, direct contact links intact.
- Reduced-motion local fixture: no progress bar, no image transition, reveal at rest.
  These two are controlled fixtures, not OS accessibility settings or screen-reader tests.

## Static checks

`python3 tools/check_site.py`, `node --check dist/assets/site.js`, `git diff --check`.
Checker covers assets, anchors, image alt/dimensions, sitemap, public boundaries,
and representative text/focus contrast pairs. It is not a complete WCAG audit.

## Still required before production release

Native Safari/Chrome and physical phone tests, screen-reader check, real email-client
handoff, slow-network/performance measurement, DNS/TLS and server configuration.
No server changes made. Public directory remains `dist/` only.
