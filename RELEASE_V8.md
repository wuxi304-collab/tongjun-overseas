# Release V8 — Deployment hardening & account-attribution layer

## Highlights
- Fixed canonical and sitemap URLs for Vercel `cleanUrls` deployment.
- Added missing favicon, PWA manifest, security.txt and dedicated 1200×630 OG image.
- Added RFQ confirmation page and server-success redirect.
- Added RFQ API input limits, origin checks, request IDs, timeout and optional webhook secret.
- Expanded campaign attribution with anonymous account code (`ac`), persona and wedge parameters.
- Added homepage sourcing-answer workflow and RFQ trust copy.
- Added Service schema to seven high-intent SEO pages.
- Hardened Vercel headers and www → apex redirect.

## Production environment
- `RFQ_WEBHOOK_URL` (required for server-side delivery)
- `RFQ_SHARED_SECRET` (recommended)
- `RFQ_ALLOWED_ORIGINS` (optional comma-separated override)
