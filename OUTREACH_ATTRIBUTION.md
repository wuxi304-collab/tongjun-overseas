# Outreach Attribution — V11

Public outreach URLs may carry only anonymous campaign context:

- `utm_source`
- `utm_medium`
- `utm_campaign`
- `utm_content`
- `ac` — anonymous account code
- `persona`
- `wedge`

Never put buyer legal names, contact names, personal emails, RFQ details, project names or drawing references in query parameters.

## Technical handoff

Interactive source screens generate a session-scoped route reference:

- `PS-*` = Problem Order screen
- `SR-*` = Supply Route screen

The reference and screen brief are kept in browser session storage and passed into the RFQ payload. They are not used as public account identifiers.

## Private account mapping

The real mapping from `ac` codes to buyer names is stored only under `/ops` in the private repository. Root `.vercelignore` excludes `/ops` from Vercel deployment.
