# SITE HEALTH — V19

Date: 2026-09-07

- Release: V19 — Evidence Architecture & Buyer Acceptance System
- Validation: `npm run check` PASS (50 HTML files)
- Public technical sheets: 6 controlled references
- Flagship references with Procurement Evidence Map: 4
- Technical tools: Material Compare, Standards Matrix, Document Center, Supply Route, Technical RFQ
- Procurement workflow: Requirement → Route → Evidence → Trial / Scale
- Decision workflow: Perform → Make → Accept
- Evidence workflow: Claim → Evidence → Acceptance
- Traceability workflow: Source → Heat/Lot → Standard → Processing → Inspection → Delivery
- Evidence taxonomy: CORE / CONDITIONAL / PO-DRIVEN / BUYER-CONTROLLED
- Document governance: `TJ-TDS / TJ-TOOL / TJ-MTX / TJ-INDEX / TJ-GUIDE / TJ-CTRL`
- Public/private deployment boundary: enforced by `.vercelignore` allowlist
- RFQ API: accepts `approval`; production webhook still requires `RFQ_WEBHOOK_URL`
- Canonical domain: `https://exoticalloycn.com`
- Vercel production binding: external launch task; not asserted by this release
- GitHub target: `wuxi304-collab/tongjun-overseas`

## Performance note
Editorial image payload remains WebP-based with intrinsic dimensions normalized. Above-fold hero keeps explicit eager/high-priority behavior; non-critical images remain lazy/async.

## V19 editorial note
V19 connects material selection, manufacturability and buyer acceptance into one evidence architecture. The Quality page now carries a six-layer evidence-package matrix, flagship technical references include procurement evidence maps, and the RFQ distinguishes core evidence from conditional, PO-driven and buyer-controlled requirements.
