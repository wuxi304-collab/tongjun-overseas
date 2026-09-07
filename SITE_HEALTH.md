# SITE HEALTH — V21

Date: 2026-09-07

- Release: V21 — Buyer Decision Interface
- Validation: `npm run check` PASS (50 HTML files)
- Public technical sheets: 6 controlled references
- Flagship references with Buyer Decision Snapshot: 4
- Flagship revision state: 625 / 718 / C-276 / 36Ni-Fe → REV 03
- Technical tools: Material Compare, Standards Matrix, Document Center, Supply Route, Technical RFQ
- Procurement workflow: Requirement → Route → Evidence → Trial / Scale
- Decision workflow: Perform → Make → Accept → Release
- Buyer gates: Service Fit → Manufacturability → Evidence Readiness → Buyer Acceptance
- Evidence workflow: Claim → Evidence → Acceptance
- Traceability workflow: Source → Heat/Lot → Standard → Processing → Inspection → Delivery
- Evidence taxonomy: CORE / CONDITIONAL / PO-DRIVEN / BUYER-CONTROLLED
- RFQ buyer context: Procurement Stage + Buyer Release Gate + stable decision reference
- Document governance: `TJ-TDS / TJ-TOOL / TJ-MTX / TJ-INDEX / TJ-GUIDE / TJ-CTRL`
- Public/private deployment boundary: enforced by `.vercelignore` allowlist
- RFQ API: accepts `procurement_stage`, `buyer_gate`, `decision_ref`; production webhook still requires `RFQ_WEBHOOK_URL`
- Canonical domain: `https://exoticalloycn.com`
- Vercel production binding: external launch task; not asserted by this release
- GitHub target: `wuxi304-collab/tongjun-overseas`

## Performance note

Editorial image payload remains WebP-based with intrinsic dimensions normalized. Above-fold hero keeps explicit eager/high-priority behavior; non-critical images remain lazy/async.

## V21 editorial note

The site now exposes the procurement release logic instead of merely describing sourcing competence. A nominal grade match can no longer visually masquerade as an approved supply route: service fit, manufacturability, evidence and buyer authority remain separate gates.
