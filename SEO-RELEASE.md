# Novera: Google indexing release checklist

## Public audit — 2026-09-12

- HTTPS `/`, `/en/`, `/ru/`: HTTP 200; HTML is available without JavaScript.
- `robots.txt` permits crawling and references the three-route sitemap.
- HTTP root redirects to HTTPS with 301.
- HTTPS `www.innovera.uz` returns 200 instead of redirecting to the canonical host.
- `/novera-seo-missing-page-check` incorrectly returns the homepage with HTTP 200.
- No `X-Robots-Tag` blocking directive observed on checked responses.
- Search Console ownership, Google's selected canonical and actual indexing status
  have NOT been verified. Public HTTP checks cannot establish indexing.

## Local changes ready to deploy

- Specific Uzbek, English and Russian titles/descriptions: `content/seo.json`.
- Organization, WebSite and localized WebPage JSON-LD with confirmed contacts only.
- Reciprocal language alternatives in both HTML and XML sitemap, including x-default.
- Automated metadata and sitemap regression checks: `python3 tools/check_seo.py`.
- No fabricated reviews, office address, results, keyword stuffing or doorway pages.
- Design, accessibility, motion and contact behavior are unchanged.

Only upload `dist/`. These changes are NOT deployed by this task.

## Server corrections before requesting indexing

Inspect and back up the existing nginx virtual host first. Adapt these rules to
its existing document root/TLS configuration; this is not a replacement config.

1. The HTTPS www virtual host should return
   `return 301 https://innovera.uz$request_uri;` (retain its valid TLS certificate).
2. The main static-site location should use `try_files $uri $uri/ =404;`, not a
   fallback to `/index.html`. Unknown paths must return an actual HTTP 404.
3. Redirect `/index.html`, `/en/index.html`, `/ru/index.html` to their respective
   directory URLs if the server exposes them; preserve language and query strings.
4. Keep HTML short-lived/revalidated. Do not apply immutable caching to unversioned
   CSS or JS. Do not block Googlebot or serve bots different content.
5. Validate with `nginx -t` before reload. Verify all three canonical pages and
   their assets return 200, variants redirect, and nonexistent URLs return 404.

## Search Console — owner action

1. Open https://search.google.com/search-console and add the Domain property
   `innovera.uz` (no protocol/path).
2. Add Google's exact supplied TXT verification record at the domain's DNS
   provider. Do not invent a verification value; keep the record after verification.
3. After deploying and verifying, submit `https://innovera.uz/sitemap.xml` in Sitemaps.
4. URL Inspection → Test live URL → Request indexing for `/`, `/en/`, `/ru/`.
5. Review Page indexing and Performance reports after Google processes the site.
   Do not repeatedly submit the same URLs; it does not accelerate crawling.

Indexing and top rankings cannot be guaranteed. Next content work should be
original detailed service pages based on actual capabilities, then approved real
case studies: problem, delivered scope and evidence. Avoid near-identical pages
for cities or keywords, bought links, and invented testimonials.

Official references:
- https://developers.google.com/search/docs/fundamentals/seo-starter-guide
- https://developers.google.com/search/docs/appearance/structured-data/organization
- https://developers.google.com/search/docs/specialty/international/localized-versions
- https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl
