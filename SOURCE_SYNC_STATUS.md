# Source Sync Status — V25

Date: 2026-09-07
Target: `wuxi304-collab/tongjun-overseas` (private)

## Current truth

The validated **local V25 source artifact** is the complete release.

The connected GitHub `main` branch is still a partial source mirror. It contains governance, API / RFQ regression assets and selected source files, but the remote tree has not yet been proven equivalent to the validated V25 public tree.

Therefore GitHub `main` must **not** be treated as production-deployable yet.

## V25 priority mirror

The highest-value source set is:

- `index.html`, `quality.html`, `rfq.html`
- `assets/site.css`, `assets/site.js`
- `api/rfq.js`
- `scripts/validate-site.js`, `scripts/test-rfq.js`
- `technical-data.html`, Document Center and flagship controlled references
- `privacy.html`, `terms.html`, `404.html`
- `manifest.webmanifest`, `robots.txt`, `sitemap.xml`, `llms.txt`, `.well-known/security.txt`
- `vercel.json`, `.vercelignore`, `package.json`
- V25 release / health / governance documents

## Production-completion gate

1. Mirror every public HTML page.
2. Mirror shared CSS / JS, favicon and every referenced public image.
3. Mirror sitemap, robots, manifest, security.txt and deployment assets.
4. Run `npm run check` from a fresh GitHub checkout.
5. Run the clean-route crawl from that checkout.
6. Compare the remote tree / hashes with the validated V25 source artifact.
7. Only then mark GitHub `main` as production-deployable.
