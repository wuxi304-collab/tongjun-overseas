# Deploy exoticalloycn.com — V34.152 R15.9

## Current launch status — 2026-09-20
**BLOCKED for production traffic until DNS and Vercel project binding are verified.**

From the current engineering environment, the production apex still could not be verified as externally reachable. The connected Vercel accounts currently expose no visible team/project through the connector. GitHub Pages is healthy as a temporary mirror, but that does **not** prove the production apex, Vercel domain binding, environment variables or serverless RFQ route are live.

Do not switch outbound campaigns, SEO promotion or buyer traffic to the apex until `npm run check:production` and the production RFQ smoke both pass.

## Recommended topology
GitHub repo `wuxi304-collab/tongjun-overseas` → Vercel → `exoticalloycn.com`

GitHub Pages is a temporary static release mirror only. R15.1 deliberately hardens it:

- every HTML page is `noindex,nofollow,noarchive`;
- `robots.txt` disallows the entire mirror;
- `ops/`, `api/`, `scripts/`, `tests/`, `lib/` and build-only root files are excluded;
- no `CNAME` is shipped in the Pages artifact;
- Pages does **not** host the Vercel serverless `/api/rfq` or `/api/health` functions.

The source repository still contains a historical `CNAME` file. Neither the Vercel public allowlist nor the R15 Pages builder deploys it. Treat Vercel Domains + authoritative DNS as the source of truth, not the repository `CNAME`.

## Domain
- Production apex: `https://exoticalloycn.com`
- `www.exoticalloycn.com` must redirect permanently to apex.
- `cleanUrls` is enabled, so `.html` routes redirect to clean URLs.
- Production canonicals and sitemap use clean apex URLs.
- Production pages must remain indexable; the Pages mirror must remain noindex.

## RFQ environment variables
Production secure RFQ delivery requires:

- `RFQ_WEBHOOK_URL` — **required** for server-side RFQ delivery. The endpoint must accept JSON POSTs and return a 2xx status after it has accepted the record.
- `RFQ_SHARED_SECRET` — recommended. Sent to the receiving webhook in `X-Tongjun-Webhook-Secret`.
- `RFQ_ALLOWED_ORIGINS` — optional comma-separated origin allowlist. Defaults to `https://exoticalloycn.com,https://www.exoticalloycn.com`; the active Vercel preview hostname is accepted automatically through `VERCEL_URL`.

If `RFQ_WEBHOOK_URL` is missing, the API returns `503 rfq_route_not_configured`. If the downstream webhook fails or times out, the API returns `502 rfq_delivery_failed`. The browser then opens the structured email fallback addressed to `ask2205@outlook.com`.

## R14.2 delivery trace contract
Every RFQ POST attempt receives a trace ID in the form:

`TJ-YYYYMMDD-XXXXXXXX`

For accepted and rejected POSTs, the same ID is returned in:

- JSON field `request_id`;
- response header `X-Tongjun-Request-Id`.

The same ID is forwarded to the downstream webhook in `X-Tongjun-Request-Id` and stored in the webhook JSON record as `request_id`.

If secure routing fails in the browser and the API returned a trace ID, the email fallback appends:

`Secure Route Attempt: TJ-...`

This lets the customer-facing fallback, Vercel logs and downstream webhook logs be correlated to the same attempt.

## R15.9 release identity contract
Every built artifact now exposes a non-secret machine-readable identity at:

`/.well-known/release.json`

It contains:

- `site_release: V34.152 R15.9`;
- source branch and exact 40-character source commit;
- `visual_release: V34.152 R15.7`;
- SHA256 of the frozen visual manifest;
- deployment environment (`production` or `github-pages-mirror`);
- canonical production origin.

The production `/api/health` response exposes the same site/visual release plus the Vercel git commit and sends `X-Tongjun-Release: V34.152 R15.9`.

`npm run check:production` now requires the static `release.json` commit to exactly match `/api/health.release`. A mixed CDN/function deployment, stale static artifact or wrong production commit therefore fails the production gate even if the homepage itself returns HTTP 200.

## R15 production readiness endpoint
Vercel deploys `GET /api/health` from `api/health.js`.

It returns only non-secret readiness data:

- `service: tongjun-overseas`;
- `rfq_route_configured: true|false`;
- a non-secret release identifier;
- `checked_at` timestamp.

Expected behavior:

- `200` + `ok: true` only when `RFQ_WEBHOOK_URL` is configured;
- `503` + `ok: false` when the secure RFQ route is not configured;
- `405` for unsupported methods;
- `Cache-Control: no-store`.

The endpoint never returns the webhook URL or shared secret.

## RFQ payload and safety boundaries
The server payload includes the structured technical RFQ, attribution context, buyer release controls and the `evidence_package` planning string derived from RFQ fields. This is a planning aid only and must not be treated as a certification, stock, origin, mill approval or manufacturing-capability promise.

The API also enforces:

- POST only;
- origin allowlist;
- honeypot handling;
- request-body size limit;
- server-side field length limits;
- required field validation;
- email format validation;
- best-effort per-instance request throttling;
- 8-second downstream webhook timeout.

The in-memory request throttle is **not a global distributed rate limiter**. If production abuse becomes material, use Vercel Firewall/rate limiting or a durable shared store rather than relying on the function instance map.

## Stage 1 — read-only production preflight
Run this before sending any synthetic RFQ:

```bash
npm run check:production
```

Optional alternate target:

```bash
PRODUCTION_BASE_URL=https://exoticalloycn.com npm run check:production
```

The preflight does **not** submit an RFQ. It verifies:

1. DNS resolves for the apex hostname.
2. HTTPS homepage returns `200`.
3. `www` redirects to the apex.
4. Production homepage canonical points to `https://exoticalloycn.com/`.
5. Production homepage is **not** `noindex`.
6. Security headers include HSTS, CSP, `nosniff`, frame denial and Referrer Policy.
7. Current runtime `site.js?v=20260916-r14-2` is active.
8. `/rfq` returns `200` and contains `#rfqForm`.
9. `/thank-you` returns `200`.
10. `/api/health` returns `200`, `ok: true` and `rfq_route_configured: true`.
11. `/.well-known/release.json` returns R15.9 production identity.
12. Static release identity and `/api/health` report the exact same 40-character source commit.

Any failure means production remains blocked.

## Stage 2 — production RFQ smoke
The production smoke is intentionally opt-in. It will not run unless `RFQ_SMOKE_URL` is explicitly supplied.

Example:

```bash
RFQ_SMOKE_URL=https://exoticalloycn.com/api/rfq npm run smoke:rfq:production
```

Optional overrides:

```bash
RFQ_SMOKE_ORIGIN=https://exoticalloycn.com \
RFQ_SMOKE_EMAIL=ask2205@outlook.com \
RFQ_SMOKE_URL=https://exoticalloycn.com/api/rfq \
npm run smoke:rfq:production
```

The smoke payload is clearly marked `PRODUCTION SMOKE TEST` and `NO COMMERCIAL ORDER`. Success requires all of the following:

1. HTTP `202`.
2. JSON `ok: true`.
3. A valid `TJ-...` request ID.
4. `X-Tongjun-Request-Id` exactly matches the JSON `request_id`.
5. The receiving webhook/mailbox can locate the same request ID.

A `503` means the production secure route is not configured. A `502` means Vercel reached the RFQ function but the downstream webhook did not accept the record.

## Release gate
Before switching outbound campaigns to the production domain:

1. Run `npm run check` on the release source.
2. Confirm Vercel production environment has `RFQ_WEBHOOK_URL` and, preferably, `RFQ_SHARED_SECRET`.
3. Confirm Vercel Domains shows both apex and `www` with valid DNS/SSL state.
4. Deploy the release to production.
5. Run `npm run check:production` and require a full pass.
6. Run `npm run smoke:rfq:production` against `https://exoticalloycn.com/api/rfq`.
7. Confirm the same `TJ-...` trace ID exists in the downstream receiver.
8. Verify `/.well-known/release.json` and `/api/health` expose the same R15.9 source commit.
9. Verify `/rfq`, `/thank-you`, sitemap/canonical and current runtime one final time.
10. Only then enable outbound campaigns, buyer traffic or SEO promotion.

## DNS
Use the DNS records shown by the **active Vercel Domains screen for the production project**. Do not copy generic DNS values from screenshots, tutorials or an old GitHub Pages setup.

The production readiness script is the final practical test: if the apex does not resolve, it fails before any RFQ smoke is attempted.
