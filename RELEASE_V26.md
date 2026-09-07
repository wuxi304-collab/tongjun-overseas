# RELEASE V26 — Canonical Source Mirror Convergence

Date: 2026-09-07

## Why this release exists

V25 closed the local launch gate, but the connected GitHub `main` branch remained a partial source mirror. V26 freezes public behavior and focuses on making the repository progressively reproducible instead of adding another public feature layer.

## Source-convergence scope

- Preserve the validated V25 public information architecture and buyer workflows.
- Mirror buyer-critical public pages first: homepage, Quality, Technical RFQ and Technical Data Center.
- Mirror shared runtime assets: `assets/site.css`, `assets/site.js`.
- Mirror validation and discovery assets: `scripts/validate-site.js`, sitemap, robots, manifest, `llms.txt` and security.txt.
- Mirror legal / failure surfaces: Privacy, Terms and 404.
- Mirror controlled technical entry points and Document Center before treating GitHub as canonical.
- Record the remaining binary-image and long-tail page gap explicitly; priority-file presence is not equivalent to a production-complete tree.

## Public behavior boundary

No new sourcing promise, technical value, standard route, RFQ field or buyer workflow is introduced in V26. Controlled technical document revisions therefore remain unchanged.

## Validation

`npm run check` must remain PASS against the complete local V26 source tree.

GitHub `main` remains non-production until a fresh checkout contains every public HTML page, shared asset and referenced image, and passes the same validation and clean-route crawl.
