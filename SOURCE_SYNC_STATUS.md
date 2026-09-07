# Source Sync Status — V26

Date: 2026-09-07  
Target: `wuxi304-collab/tongjun-overseas` (private)

## Current truth

The complete validated V26 artifact remains the release authority. The connected GitHub repository now carries V26 governance, buyer-critical source, deployment controls and the executable launch audit, but production completeness still requires a fresh-checkout proof against the full artifact.

## Canonical mirror gate

1. Mirror all 50 public HTML pages.
2. Mirror `assets/site.css`, `assets/site.js`, favicon and every referenced public image.
3. Mirror `api/rfq.js`, `scripts/validate-site.js`, `scripts/test-rfq.js` and `scripts/audit-launch.js`.
4. Mirror sitemap, robots, manifest, `llms.txt`, security.txt and deployment manifests.
5. Keep internal operating and source-provenance material excluded from the public deployment package.
6. Run `npm run check` from a fresh GitHub checkout.
7. Run a clean-route crawl across all indexable canonical routes.
8. Compare remote file inventory / hashes against the validated V26 artifact.
9. Only then mark GitHub `main` production-deployable.

## Deployment boundary

V26 does not assert a Vercel production binding or successful live-domain deployment. `RFQ_WEBHOOK_URL` remains required for server-side RFQ delivery; browser-level production QA remains an external gate.
