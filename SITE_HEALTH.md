# SITE HEALTH — V22

Date: 2026-09-07

- Release: V22 — Qualified Offer System
- Validation: `npm run check` PASS (50 HTML files + RFQ V22 regression test)
- Public technical sheets: 6 controlled references
- Flagship controlled references: 625 / 718 / C-276 / 36Ni-Fe remain REV 03 (no technical-data change in V22)
- Technical tools: Material Compare, Standards Matrix, Document Center, Supply Route, Technical RFQ
- Procurement workflow: Requirement → Route → Evidence → Trial / Scale
- Decision workflow: Perform → Make → Accept → Release
- Commercial handoff: Material identity → Supply route → Evidence scope → Logistics basis → Commercial assumptions
- Buyer gates: Service Fit → Manufacturability → Evidence Readiness → Buyer Acceptance
- RFQ buyer context: Procurement Stage + Buyer Release Gate + Decision Reference
- RFQ offer context: Incoterm + Destination + Delivery Target + Packing + Offer Reference
- Evidence taxonomy: CORE / CONDITIONAL / PO-DRIVEN / BUYER-CONTROLLED / COMMERCIAL-BASIS
- Public/private deployment boundary: enforced by `.vercelignore` allowlist
- RFQ API: production webhook still requires `RFQ_WEBHOOK_URL`
- Canonical domain: `https://exoticalloycn.com`
- Vercel production binding: external launch task; not asserted by this release
- GitHub target: `wuxi304-collab/tongjun-overseas`

## V22 editorial note

The site now separates a technically defensible route from a commercially quotable basis. An offer may contain open conditions, but they must remain visible. Price, lead time, stock and route availability are treated as time-bound confirmations rather than permanent capability claims.
