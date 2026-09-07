# GitHub Sync Policy

Target repository: **wuxi304-collab/tongjun-overseas** (private)

## Status — V20
The repository is the canonical **source target**, but the connected GitHub API has not yet mirrored the complete validated V20 site tree and binary image assets. Governance, release notes and technical provenance are current; a complete V20 source ZIP and Git bundle are maintained separately until full tree synchronization is completed.

Do not treat the current `main` branch as production-deployable solely because release governance is current.

## Rule
Every material website/content change must be validated locally and recorded in the target private repository. A release is considered **fully synchronized** only when the complete public source tree, required assets, API routes, validation scripts and deployment manifests are present at the target commit.

## Commit convention
- `site:` page / UX / conversion changes
- `content:` technical or editorial updates
- `seo:` metadata / structured data / indexing
- `ops:` deployment / analytics / email / infrastructure
- `supply:` supplier/channel intelligence changes

## Sync gate
1. Run `npm run check`.
2. Confirm public/private deployment boundaries in `.vercelignore`.
3. Confirm the remote commit contains all public HTML, CSS/JS, images, API routes and manifests required by `vercel.json`.
4. Preserve release notes, `SITE_HEALTH.md` and the technical source register with every material release.
5. Only after step 3 may GitHub `main` be treated as the production deployment source.

Do not mirror internal supplier, account or operating intelligence into a public repository.
