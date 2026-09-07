# SITE HEALTH — V18

Date: 2026-09-07

- Release: V18 — Source-Role & Chain-of-Custody System
- Validation: `npm run check` PASS (50 HTML files)
- Public technical sheets: 6 controlled references
- Technical tools: Material Compare, Standards Matrix, Document Center
- Procurement workflow: Requirement → Route → Evidence → Trial / Scale
- Quality workflow: Source → Heat/Lot → Standard → Processing → Inspection → Delivery
- Document governance: `TJ-TDS / TJ-TOOL / TJ-MTX / TJ-INDEX / TJ-GUIDE / TJ-CTRL`
- Public/private deployment boundary: enforced by `.vercelignore` allowlist
- RFQ API: route exists; production webhook still requires `RFQ_WEBHOOK_URL`
- Canonical domain: `https://exoticalloycn.com`
- Vercel production binding: external launch task; not asserted by this release
- GitHub target: `wuxi304-collab/tongjun-overseas`

## Performance note
Editorial image payload remains WebP-based with intrinsic dimensions normalized. Above-fold hero keeps explicit eager/high-priority behavior; non-critical images remain lazy/async.

## V18 editorial note
V18 adds the Source-Role Ledger and six-stage chain-of-custody model to Quality + Traceability, while preserving the V17 challenge-to-evidence workflow. Manufacturing origin, custody, secondary processing, inspection and buyer approval remain separate responsibility layers.
