# V34.144 — Conversion-focused visual finish

## Scope

V34.144 continues the V34.143 buyer-path convergence without changing information architecture or RFQ transport logic.

### Visual system
- Flatter, more editorial industrial imagery treatment on the home page.
- Reduced card/template styling in product entry points.
- Stronger specification-ledger treatment across flagship material-family pages.
- More auditable supplier-qualification rows and evidence hierarchy.
- Clearer technical-table typography and row scanning.

### RFQ
- Live five-stage progress state based on existing form fields.
- Required-field completion feedback in the existing mobile RFQ progress bar.
- Focus/value/error states are visual only; form payload and submission behavior are unchanged.
- Privacy acceptance remains a separate final gate.

### Mobile
- Home/product imagery ratios tuned independently from desktop.
- Technical Data rows collapse to a single readable column.
- RFQ stage/progress behavior is touch-first and reduced-motion safe.

## Release boundary
- No third-party font dependency.
- No animation framework.
- No change to RFQ endpoint, validation contract, evidence language, or buyer-claim boundaries.
- `main` and production deployment remain untouched until branch validation is complete.
