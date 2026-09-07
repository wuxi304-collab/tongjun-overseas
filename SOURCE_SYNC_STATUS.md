# Source Sync Status — V21

Date: 2026-09-07  
Target: `wuxi304-collab/tongjun-overseas` (private)

## Remote objective

GitHub `main` is being converted from a governance-only repository into the canonical text/source mirror of the validated site.

## V21 priority sync set

The release prioritizes the files that define buyer behavior and production logic:

- `index.html`
- `quality.html`
- `rfq.html`
- `technical-alloy-625.html`
- `technical-alloy-718.html`
- `technical-alloy-c276.html`
- `technical-invar-36.html`
- `document-center.html`
- `assets/site.css`
- `assets/site.js`
- `api/rfq.js`
- `scripts/validate-site.js`
- `package.json`
- V21 release / health / source-sync governance

## Completion boundary

Even after the V21 priority set is mirrored, the repository must **not** be called production-complete until every remaining public HTML page, required WebP image, favicon, manifest, sitemap, robots file and deployment asset is present and `npm run check` passes from a fresh GitHub checkout.

## Full-sync completion gate

1. Mirror all public HTML.
2. Mirror `assets/site.css`, `assets/site.js`, favicon and required images.
3. Mirror validation scripts and deployment manifests.
4. Run `npm run check` from the GitHub checkout.
5. Compare the resulting tree against the validated V21 source release.
6. Only then mark GitHub `main` as production-deployable.
