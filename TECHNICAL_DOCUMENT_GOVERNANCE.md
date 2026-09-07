# Technical Document Governance — V15

Last reviewed: 2026-09-07

## Public document classes

- `TJ-TDS-*`: controlled web technical reference sheets.
- `TJ-TOOL-*`: interactive screening tools.
- `TJ-MTX-*`: standards/product-form routing matrices.
- `TJ-INDEX-*`: portfolio indexes.
- `TJ-GUIDE-*`: buyer-facing editorial references.
- `TJ-CTRL-*`: governance / qualification references.

## Authority hierarchy

1. Buyer purchase order / project specification.
2. Current applicable product-form standard or buyer-named contractual revision.
3. Approved source and certified mill / producer documentation.
4. Tongjun controlled web reference.

A Tongjun document revision is **not** the revision of an ASTM, AMS, EN, ASME or customer specification.

## Revision rules

- Change exact technical values or standard routes -> increment document revision.
- Editorial / layout-only changes -> release version increments, document revision may remain unchanged.
- Every exact value must have a traceable source in `TECHNICAL_DATA_SOURCES.md`.
- Withdrawn or superseded standards may only appear with explicit status context.
- Web reference is never an MTC, CoC, approved-source certificate or design allowables document.
