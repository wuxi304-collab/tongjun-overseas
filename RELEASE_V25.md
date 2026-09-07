# Release V25 — Launch Gate & Production Hardening

Date: 2026-09-07

V25 is a launch-control release. It does not expand the material portfolio or add a new buyer workflow. It closes production-readiness gaps that could undermine an otherwise credible technical site.

## Launch-gate changes

- Added Privacy and Terms access to the global footer on every HTML page.
- Tightened long / weak SEO titles and descriptions and completed Open Graph / Twitter metadata on the remaining indexable routes.
- Added valid JSON-LD to every indexable page that previously had no structured-data object.
- Corrected the Technical Data Center directory so Alloy 625, 718, C-276 and 36Ni-Fe display **REV 03**, matching the controlled sheets and Document Center; Alloy 825 and Super Duplex 2507 remain REV 02.
- Cleaned public Privacy / Terms wording, added explicit legal-entity / last-updated context and removed deployment-scaffolding language.
- Added an RFQ no-JavaScript email fallback notice and a privacy-processing notice near submission.
- Added a lightweight per-instance RFQ rate gate while retaining the origin allowlist, honeypot, payload limits and fail-closed webhook behavior.
- Extended RFQ regression tests to cover the `503 → browser email fallback` path and rate-limit rejection.
- Replaced one-year immutable caching on mutable shared assets with a short revalidation policy so CSS / JS updates cannot remain stale for a year.
- Added Content-Security-Policy and Cross-Origin-Opener-Policy response headers.
- Aligned `llms.txt` and the web manifest with the current source-role / buyer-release model.
- Added V25 launch assertions to the site validator: metadata range, schema validity, exact sitemap parity, legal links, technical revision parity and deployment hardening.

## Validation

`npm run check` → PASS

- 50 HTML files passed structural / route / image / canonical validation.
- RFQ V25 regression passed payload, origin, fail-closed fallback path and rate-gate tests.
- Local clean-route crawl: **46 / 46** indexable canonical routes served HTTP 200 and contained the expected production canonical.

## Controlled-document boundary

V25 corrects directory revision labels only. It does **not** change chemistry, mechanical properties, density, CTE, product-form standards or sourcing qualification values. Controlled technical sheets therefore keep their existing revisions.

## Remaining launch blockers

- Vercel production project / team is not discoverable through the currently connected Vercel account.
- `RFQ_WEBHOOK_URL` has not been confirmed in production.
- Domain DNS does not yet resolve to a live production site from the current environment.
- Branded-domain email and SPF / DKIM / DMARC remain operational tasks.
- GitHub `main` is still not a complete production-source mirror.
- Browser screenshot-level visual QA remains uncompleted because the execution environment blocks local browser navigation.
