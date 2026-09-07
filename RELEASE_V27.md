# RELEASE V27 — Remote Text Canonicalization

Date: 2026-09-08

## Why this release exists

V26 hardened the launch baseline, but GitHub `main` still contained only a partial source mirror. V27 freezes public behavior and closes the remote text-source gap while isolating the remaining binary-image gap as a separate, auditable gate.

## Canonicalization scope

- Preserve the validated V26 public information architecture, buyer workflow, technical values and RFQ schema.
- Mirror the complete UTF-8 / text source set to `wuxi304-collab/tongjun-overseas`: all 50 public HTML pages, CSS, JS, API, deployment manifests, validation scripts, sitemap/discovery assets, legal pages, governance and internal operating text files.
- Preserve `assets/images/*.webp` as a separate binary gate; do not call the remote production-complete until all 15 WebP files are present and byte-matched.
- Replace presence-based sync claims with Git blob verification through full and text-only source manifests.
- Keep public deployment boundaries governed by `.vercelignore`.

## Public behavior boundary

No public feature, sourcing promise, technical value, standard route, RFQ field, buyer decision state or controlled technical-document value changes in V27. Controlled document revisions remain unchanged.

## Validation

- `npm run check` → PASS on the complete local V27 source artifact.
- `npm run verify:source` → PASS for the complete local artifact.
- `npm run verify:text-source` → PASS for the text canonicalization set.

## Remaining remote gate

The connected GitHub repository must not be called production-deployable until the 15 referenced WebP image assets are mirrored, the complete remote tree matches the full V27 manifest, and a fresh checkout passes `npm run check`.

## External launch gates

Vercel project/domain binding, `RFQ_WEBHOOK_URL` delivery, branded mail and screenshot-level browser/device QA remain separate launch gates.
