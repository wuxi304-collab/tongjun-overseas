# GitHub Sync Policy

Target repository: **wuxi304-collab/tongjun-overseas** (private)

## Rule
Every material website/content change must be committed to the target private repository after local validation. The repository is now available to the connected GitHub account and is the canonical source target.

## Commit convention
- `site:` page / UX / conversion changes
- `content:` technical or editorial updates
- `seo:` metadata / structured data / indexing
- `ops:` deployment / analytics / email / infrastructure
- `supply:` supplier/channel intelligence changes

## Sync gate
1. Run `npm run check`.
2. Confirm public/private deployment boundaries in `.vercelignore`.
3. Commit the validated source snapshot to `main` or a review branch.
4. Preserve release notes and `SITE_HEALTH.md` with every material release.

Do not mirror internal supplier, account or operating intelligence into a public repository.
