# Source Sync Status — V22

Date: 2026-09-07
Target: `wuxi304-collab/tongjun-overseas` (private)

## Remote objective

GitHub `main` is being converted from a governance-only repository into the canonical source mirror of the validated site. V22 adds a commercial-hand-off layer, but the same production-completion rule remains: the remote branch is not production-deployable until every required public page and asset is mirrored and validated from a fresh checkout.

## V22 priority sync set

- `index.html` — buyer decision + qualified offer system
- `quality.html` — evidence / acceptance + evidence-to-offer boundary
- `rfq.html` — buyer review + qualified offer readiness
- `assets/site.js` — decision, evidence and offer-state logic
- `assets/site.css` — V21/V22 interface styles
- `api/rfq.js` — V22 logistics / offer-reference payload
- `scripts/validate-site.js` + `scripts/test-rfq.js`
- `document-center.html` + four flagship technical references
- release / health / governance documents

## Completion boundary

Priority-file presence is not equivalent to a complete production tree. Required WebP images, favicon, sitemap, robots, manifest, remaining public HTML and deployment assets must also be mirrored.

## Full-sync completion gate

1. Mirror all public HTML.
2. Mirror shared CSS / JS, favicon and every referenced public image.
3. Mirror validation scripts and deployment manifests.
4. Run `npm run check` from the GitHub checkout.
5. Compare the resulting tree against the validated V22 source release.
6. Only then mark GitHub `main` as production-deployable.
