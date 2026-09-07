# Source Sync Status — V20

Date: 2026-09-07
Target: `wuxi304-collab/tongjun-overseas` (private)

## Remote coverage now

The repository is no longer governance-only. V20 now includes real source-level artifacts in `main`:

- `about.html` — V20 corporate responsibility / credibility layer
- `api/rfq.js` — structured Technical RFQ API route
- `package.json` — V20 validation command manifest
- `vercel.json` — clean URL, www→apex redirect and security/cache headers
- release governance, technical provenance and site-health documents through V20

## Not yet fully mirrored

The validated V20 release still contains additional public HTML pages, shared CSS/JS, WebP image assets, validation scripts, sitemap/robots/manifest and other deployment files that are not yet all present in GitHub `main`.

Therefore the current remote branch must **not** be treated as a complete production deployment source yet.

## Complete validated V20 release artifacts

- `exoticalloycn-site-v20.zip` — SHA-256 `3ded165e2475ef7fd81c987cd8538f2dcdaf3ce2c576da42553eae9c9fed4a76`
- `exoticalloycn-public-v20.zip` — SHA-256 `7fa4e3fb235b9d75673e835b765d41f71425cec52dc8fc474504aa536f54a396`
- `exoticalloycn-site-v20-2026-09-07.bundle` — SHA-256 `b25638d66f8bf93e6557fa6417ec49add90aaa7f5de65a93d367aa035105b272`

## Full-sync completion gate

1. Mirror all public HTML.
2. Mirror `assets/site.css`, `assets/site.js`, favicon and required images.
3. Mirror validation scripts and deployment manifests.
4. Run `npm run check` from the GitHub checkout.
5. Compare the resulting tree against the validated V20 source release.
6. Only then mark GitHub `main` as production-deployable.
