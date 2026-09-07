# SITE HEALTH — V25

Date: 2026-09-07

- Release: V25 — Launch Gate & Production Hardening
- Package version: 25.0.0
- `npm run check`: PASS
- HTML pages: 50
- Indexable canonical routes: 46
- Local clean-route crawl: 46 / 46 PASS
- Sitemap parity: exact match to indexable canonical set
- Structured data: valid JSON-LD present on every indexable page
- Social metadata: Open Graph + Twitter image/card present on every indexable page
- Legal navigation: Privacy + Terms linked from every global footer
- Controlled technical sheets: 6 references
- Flagship revision state: 625 / 718 / C-276 / 36Ni-Fe → REV 03; 825 / 2507 → REV 02
- RFQ safeguards: origin allowlist + payload limits + honeypot + fail-closed webhook + email fallback + lightweight per-instance rate gate
- Shared-asset caching: short revalidation policy; no one-year immutable cache on mutable CSS / JS
- Security headers: HSTS + nosniff + frame deny + referrer + permissions + CSP + COOP
- Canonical domain: `https://exoticalloycn.com`
- Production RFQ webhook: still requires `RFQ_WEBHOOK_URL`
- Vercel production binding: not established / not asserted
- GitHub target: `wuxi304-collab/tongjun-overseas`
- Screenshot-level browser QA: NOT completed; local navigation is blocked by the execution environment

## V25 launch note

The site is structurally ready for a controlled production deployment, but production is not declared ready until DNS, Vercel ownership, RFQ webhook delivery, branded mail and a live-domain browser crawl are all closed.
