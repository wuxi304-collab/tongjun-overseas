# TONGJUN SPECIAL METALS — V11

Release date: 2026-09-06

## Theme

**Sales execution layer + public/private deployment boundary.**

V11 does not add another broad product category. It makes the existing acquisition path auditable and creates an internal account-based sales desk that can live in the same private Git repository without being deployed to the public website.

## Public-site changes

- Added route-screen references:
  - `PS-YYYYMMDD-XXXXXX` for Problem Order Desk screens.
  - `SR-YYYYMMDD-XXXXXX` for Supply Route Builder screens.
- Route references are stored in session state and handed into the Technical RFQ as `route_ref`.
- RFQ webhook payload allowlist now accepts `route_ref`.
- Public screen results show the route reference for human handoff.
- Added `.vercelignore` as an explicit public deployment allowlist.

## Deployment privacy boundary

The private repository can now contain `/ops` material while Vercel receives only the public website surface:
- `/api/**`
- `/assets/**`
- `/.well-known/**`
- root HTML pages
- `vercel.json`, `package.json`, manifest, robots, sitemap, llms.txt

Internal Markdown, release notes, preview scripts, sales workbench, account names and contact data are excluded from public deployment.

## Internal sales operations

Created `/ops` with:
- `week1-workbench.html` — interactive account desk, local status/contact/touch tracking and JSON export.
- `week1-execution-v2.md` — revised Week 1 send batch.
- `week1-accounts-v2.json` — structured account intelligence.
- `account-research/*.md` — one internal dossier per reviewed account.
- `OUTBOUND_RULES.md` — send gate and 4-touch discipline.

## Account-fit correction

The earlier first-ten-by-rank list mixed channel customers, mills/processors, agents and piping specialists. V11 applies an account-fit gate before outreach.

Active Week 1 combines:
- 5 channel-customer targets.
- 5 true end-user/fabricator targets.

Five original accounts are reclassified to VERIFY / PARTNER / HOLD instead of being emailed mechanically.

## Mailbox gate

The target outbound mailbox remains `ask2205@outlook.com`.
The connected Outlook profile checked on 2026-09-06 is still `wuxi304@outlook.com`; V11 therefore treats outbound sending as blocked until the sender is switched/verified.

## Validation

`npm run check` validates:
- JS syntax.
- API syntax.
- clean local routes.
- canonical URLs.
- images and alt text.
- noindex/sitemap boundaries.
- `.vercelignore` public allowlist.
- no `/ops` deployment allow.
- no reviewed account names leaked into public HTML.
- RFQ route reference handoff.
