# SITE HEALTH — V26

Date: 2026-09-07

- Release: V26 — Canonical Source Mirror Convergence
- Package version: 26.0.0
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

## V26 source-mirror note

The validated public behavior remains the V25 launch baseline. V26 advances GitHub source convergence but does not declare production readiness until the remote tree is complete, Vercel ownership is established, RFQ webhook delivery is verified, branded mail is closed and a live-domain browser crawl passes.
