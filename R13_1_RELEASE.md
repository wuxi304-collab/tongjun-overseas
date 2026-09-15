# V34.152 R13.1 release candidate

Purpose: move the V34.152 visual system beyond the R12.2 fallback without publishing incomplete R13 references.

Release rules:
- Brand date remains `EST. 2026`; no unsupported `SINCE 2010` claim.
- Header/footer use the validated R13 AVIF logo only after materialization succeeds.
- Homepage uses the R13 AVIF international-port hero only after materialization succeeds.
- Existing R12 page-specific industrial imagery remains in place for Quality, Technical Data, About, RFQ and other inner pages until dedicated replacement assets are actually present and validated.
- No HTML may reference `quality-lab-r13`, `engineering-team-r13` or `technical-lab-r13` in this release.
- R12.2 remains the rollback point.

Materialized assets:
- `assets/images/logo-r13.avif`
- `assets/images/hero-port-r13.avif`

Source chunks live under `.sync/r13-release/` and are reconstructed deterministically by `scripts/materialize-r13-release.py`.
