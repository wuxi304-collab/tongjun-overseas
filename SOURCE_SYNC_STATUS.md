# Source Sync Status — V23

Date: 2026-09-07
Target: `wuxi304-collab/tongjun-overseas` (private)

## Remote objective

GitHub `main` is being converted from a partial source mirror into the canonical production source. V23 keeps the same completion rule: the branch is not production-deployable until every required public page, shared asset and validation file is mirrored and passes from a fresh checkout.

## V23 priority sync set

- `index.html` — compact buyer-release hero and decision dock
- `quality.html` — Claim → Record → Link → Release evidence console
- `rfq.html` — five-block buyer input hierarchy and mobile RFQ refinement
- `technical-alloy-625.html` / `718` / `c276` / `technical-invar-36.html` — four-gate decision snapshot
- `assets/site.css` — V23 visual hierarchy and mobile rules
- `assets/site.js` — existing buyer / offer-state logic unchanged in V23
- `api/rfq.js` — V22 schema retained
- `scripts/validate-site.js` + `scripts/test-rfq.js`
- release / health / governance documents

## Completion boundary

Priority-file presence is not equivalent to a complete production tree. Required WebP images, favicon, sitemap, robots, manifest, remaining public HTML and deployment assets must also be mirrored.

## Full-sync completion gate

1. Mirror all public HTML.
2. Mirror shared CSS / JS, favicon and every referenced public image.
3. Mirror validation scripts and deployment manifests.
4. Run `npm run check` from the GitHub checkout.
5. Compare the resulting tree against the validated V23 source release.
6. Only then mark GitHub `main` as production-deployable.
