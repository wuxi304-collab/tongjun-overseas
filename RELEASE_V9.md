# Release V9 — Production Architecture & Account-Based Conversion

Date: 2026-09-06

## Core changes
- Externalized shared CSS and JavaScript into `/assets/site.css` and `/assets/site.js`.
- Added anonymous account/persona/wedge campaign context without exposing buyer identity.
- Added first-touch attribution: first landing path, referrer hostname and first-seen timestamp.
- RFQ API accepts bounded attribution fields and returns a request reference ID when secure delivery succeeds.
- Thank-you page displays the server-issued RFQ reference ID when available.
- Supply Route Builder preserves anonymous campaign attribution into the RFQ.
- Added BreadcrumbList structured data to public detail pages with breadcrumbs.
- Added sitemap `lastmod` for the V9 release date.
- Refined homepage positioning: route qualification before quotation; not a generic exporter.

## Privacy boundary
- `ac` is an anonymous account code only.
- No buyer legal name, personal email or identifiable contact information is stored in campaign query parameters.
- Referrer capture stores hostname only, not the full referring URL.

## Validation
- 37 HTML files / 34 public sitemap URLs.
- 0 inline style blocks / 0 inline executable scripts after shared-asset refactor.
- `npm run check` PASS.
- Clean-route smoke tests PASS for homepage, high-intent pages, RFQ, thank-you and shared assets.
