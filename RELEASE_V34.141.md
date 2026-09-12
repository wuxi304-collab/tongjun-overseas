# V34.141 — UI polish and typography consolidation

V34.141 refines the verified V34.140 source tree without changing information architecture or RFQ business logic.

- System-first English typography: Aptos / Inter / Segoe UI fallbacks.
- Removed forced `font-stretch: 92%` from display roles.
- Standardized tabular numerals for technical IDs, tables and specification values.
- Restricted hover elevation to fine-pointer devices.
- Improved touch behavior and horizontal technical scrollers.
- Controlled compact-screen heading measure instead of aggressive type reduction.
- Print/PDF mode disables motion and transforms.
- Existing reduced-motion and same-origin page-transition behavior retained.

Local verification: `npm run check` PASS across 51 HTML pages.

This commit is release documentation only; production `main` is not changed by this file.
