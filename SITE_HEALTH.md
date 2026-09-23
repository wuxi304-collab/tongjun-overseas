# SITE HEALTH — V27

Date: 2026-09-08

- Release: V27 — Remote Text Canonicalization
- Package version: 27.0.0
- Complete local `npm run check`: PASS
- Complete local `npm run verify:source`: PASS
- Text-set `npm run verify:text-source`: PASS
- HTML pages: 50
- Indexable canonical routes: 46
- Local clean-route crawl: 46 / 46 PASS
- Sitemap parity: exact match to indexable canonical set
- Structured data: valid JSON-LD on every indexable page
- Legal navigation: Privacy + Terms in every global footer
- Controlled technical sheets: 6 references
- Flagship revision state: 625 / 718 / C-276 / 36Ni-Fe → REV 03; 825 / 2507 → REV 02
- RFQ safeguards: origin allowlist + payload limits + honeypot + fail-closed mail configuration + 502 on delivery failure + email fallback + lightweight per-instance rate gate + body-free delivery ledger
- Canonical domain: `https://exoticalloycn.com`
- GitHub target: `wuxi304-collab/tongjun-overseas`
- Remote text canonicalization: V27 target
- Remaining binary gate: 15 referenced `assets/images/*.webp` files
- Production RFQ delivery: server-side mail (`RFQ_MAIL_TRANSPORT` / `RFQ_MAIL_TO` / `RFQ_MAIL_FROM`); the former webhook hop was retired
- Vercel production binding: not established / not asserted
- Screenshot-level browser QA: NOT completed
