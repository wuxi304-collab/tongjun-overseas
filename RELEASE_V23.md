# RELEASE V23 — Visual Decision Hierarchy

Date: 2026-09-07

## Why this release exists

V18–V22 established source-role, evidence, buyer-acceptance and qualified-offer logic. V23 does not add a new workflow. It makes the existing logic easier to scan and use, especially above the fold and on mobile.

## Public changes

- Rebuilt the homepage hero into a compact buyer-release interface: Service Fit → Manufacturability → Evidence Readiness → Buyer Release.
- Removed the verbose hero trust ribbon and replaced it with a lower-density decision dock plus concise proof line.
- Added a Quality evidence-control console: Claim → Record → Link → Release.
- Restyled the initial Quality qualification modules as an industrial control grid rather than generic cards.
- Reorganized Technical RFQ visually into five buyer input blocks: Contact, Material, Approval, Logistics, Application.
- Reduced mobile RFQ pre-form scrolling and improved field / submit ergonomics.
- Expanded the four flagship Buyer Decision Snapshots to Perform → Make → Accept → Release without changing controlled technical values.
- Strengthened document-control visual hierarchy on flagship technical references.

## Controlled-document boundary

No exact technical values or standards routes were changed in the four flagship references. Their controlled technical document revision remains REV 03 under the existing governance rule for editorial / layout-only changes.

## Validation

`npm run check` → PASS (50 HTML files + RFQ V22 regression test; no API schema change in V23).
