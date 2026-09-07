# SITE HEALTH — V20

Date: 2026-09-07

- Release: V20 — Corporate Role & Credibility Layer
- Validation: `npm run check` PASS (50 HTML files)
- Public technical sheets: 6 controlled references
- Flagship references with Procurement Evidence Map: 4
- Technical tools: Material Compare, Standards Matrix, Document Center, Supply Route, Technical RFQ
- Procurement workflow: Requirement → Route → Evidence → Trial / Scale
- Decision workflow: Perform → Make → Accept
- Evidence workflow: Claim → Evidence → Acceptance
- Traceability workflow: Source → Heat/Lot → Standard → Processing → Inspection → Delivery
- Responsibility architecture: Tongjun route coordination / manufacturing-source evidence / buyer acceptance authority
- Evidence taxonomy: CORE / CONDITIONAL / PO-DRIVEN / BUYER-CONTROLLED
- Document governance: `TJ-TDS / TJ-TOOL / TJ-MTX / TJ-INDEX / TJ-GUIDE / TJ-CTRL`
- Public/private deployment boundary: enforced by `.vercelignore` allowlist
- RFQ API: accepts `approval`; production webhook still requires `RFQ_WEBHOOK_URL`
- Canonical domain: `https://exoticalloycn.com`
- GitHub target: `wuxi304-collab/tongjun-overseas`

## Performance note
Editorial image payload remains WebP-based with intrinsic dimensions normalized. Above-fold hero keeps explicit eager/high-priority behavior; non-critical images remain lazy/async.

## V20 editorial note
The public About layer no longer uses defensive “not a mill” language or internal launch TODOs. It states the operating role positively, separates Tongjun/source/buyer responsibilities, and exposes a compact corporate identity ledger without inventing owned mills, certifications, approvals, offices or manufacturing history.

## Next gate
Before production launch: complete GitHub full-source synchronization, configure the Vercel project and RFQ webhook, bind apex/www domain, test structured RFQ delivery, and verify the public/private deployment boundary.
