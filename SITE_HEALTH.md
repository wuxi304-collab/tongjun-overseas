# SITE HEALTH — V23

Date: 2026-09-07

- Release: V23 — Visual Decision Hierarchy
- Validation: `npm run check` PASS (50 HTML files + RFQ V22 regression test; no API schema change in V23)
- Public technical sheets: 6 controlled references
- Flagship controlled references: 625 / 718 / C-276 / 36Ni-Fe remain REV 03; V23 changes are editorial / layout only
- Buyer release interface: Service Fit → Manufacturability → Evidence Readiness → Buyer Release
- Quality evidence console: Claim → Record → Link → Release
- Decision workflow: Perform → Make → Accept → Release
- Commercial handoff: Material identity → Supply route → Evidence scope → Logistics basis → Commercial assumptions
- RFQ input architecture: Contact → Material → Approval → Logistics → Application
- Evidence taxonomy: CORE / CONDITIONAL / PO-DRIVEN / BUYER-CONTROLLED / COMMERCIAL-BASIS
- Public/private deployment boundary: enforced by `.vercelignore` allowlist
- RFQ API: production webhook still requires `RFQ_WEBHOOK_URL`
- Canonical domain: `https://exoticalloycn.com`
- Vercel production binding: external launch task; not asserted by this release
- GitHub target: `wuxi304-collab/tongjun-overseas`

## V23 editorial note

V23 intentionally adds no new sourcing promise and no new technical value. It reduces visual density, aligns the flagship pages with the four-gate buyer release model, and improves the long-form RFQ experience on smaller screens.
