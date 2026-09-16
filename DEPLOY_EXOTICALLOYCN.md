# Deploy exoticalloycn.com — V34.152 R14.2

## Recommended topology
GitHub repo `wuxi304-collab/tongjun-overseas` → Vercel → `exoticalloycn.com`

GitHub Pages is a static release mirror only. It can validate the customer-facing HTML/CSS/JS artifact, but it does **not** host the Vercel serverless `/api/rfq` function. RFQ submissions on the Pages mirror therefore exercise the structured email fallback rather than secure webhook delivery.

## Domain
- Production apex: `https://exoticalloycn.com`
- `www.exoticalloycn.com` redirects permanently to apex.
- `cleanUrls` is enabled, so `.html` routes redirect to clean URLs. Canonicals and sitemap use clean URLs.

## RFQ environment variables
Production secure RFQ delivery requires:

- `RFQ_WEBHOOK_URL` — **required** for server-side RFQ delivery. The endpoint must accept JSON POSTs and return a 2xx status after it has accepted the record.
- `RFQ_SHARED_SECRET` — recommended. Sent to the receiving webhook in `X-Tongjun-Webhook-Secret`.
- `RFQ_ALLOWED_ORIGINS` — optional comma-separated origin allowlist. Defaults to `https://exoticalloycn.com,https://www.exoticalloycn.com`; the active Vercel preview hostname is accepted automatically through `VERCEL_URL`.

If `RFQ_WEBHOOK_URL` is missing, the API returns `503 rfq_route_not_configured`. If the downstream webhook fails or times out, the API returns `502 rfq_delivery_failed`. The browser then opens the structured email fallback addressed to `ask2205@outlook.com`.

## R14.2 delivery trace contract
Every POST attempt receives a trace ID in the form:

`TJ-YYYYMMDD-XXXXXXXX`

For accepted and rejected POSTs, the same ID is returned in:

- JSON field `request_id`
- response header `X-Tongjun-Request-Id`

The same ID is forwarded to the downstream webhook in `X-Tongjun-Request-Id` and stored in the webhook JSON record as `request_id`.

If secure routing fails in the browser and the API returned a trace ID, the email fallback appends:

`Secure Route Attempt: TJ-...`

This lets the customer-facing fallback, Vercel logs and downstream webhook logs be correlated to the same attempt.

## RFQ payload and safety boundaries
The server payload includes the structured technical RFQ, attribution context, buyer release controls and the `evidence_package` planning string derived from RFQ fields. This is a planning aid only and must not be treated as a certification, stock, origin, mill approval or manufacturing-capability promise.

The API also enforces:

- POST only
- origin allowlist
- honeypot handling
- request-body size limit
- server-side field length limits
- required field validation
- email format validation
- best-effort per-instance request throttling
- 8-second downstream webhook timeout

The in-memory request throttle is **not a global distributed rate limiter**. If production abuse becomes material, use Vercel Firewall/rate limiting or a durable shared store rather than relying on the function instance map.

## Production smoke test
A production smoke test is intentionally opt-in. It will not run unless `RFQ_SMOKE_URL` is explicitly supplied.

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
3. Deploy the release to production.
4. Run `npm run smoke:rfq:production` against `https://exoticalloycn.com/api/rfq`.
5. Confirm the same trace ID exists in the downstream receiver.
6. Verify apex/www redirect, `/rfq`, `/thank-you`, and the current `site.js?v=20260916-r14-2` asset.
7. Only then enable outbound campaigns or buyer traffic.

## DNS
Use the DNS records shown by the active Vercel Domains screen for the production project. Do not copy generic DNS values from old screenshots or tutorials.
