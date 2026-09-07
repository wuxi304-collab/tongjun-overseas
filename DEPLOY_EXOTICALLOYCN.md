# Deploy exoticalloycn.com — V17

## Recommended topology
GitHub private repo `wuxi304-collab/tongjun-overseas` → Vercel → `exoticalloycn.com`

## Domain
- Production apex: `https://exoticalloycn.com`
- `www.exoticalloycn.com` redirects permanently to apex.
- `cleanUrls` is enabled, so `.html` routes redirect to clean URLs. Canonicals and sitemap use clean URLs.

## RFQ environment variables
- `RFQ_WEBHOOK_URL`: required for server-side RFQ delivery.
- `RFQ_SHARED_SECRET`: recommended secret sent to the receiving webhook in `X-Tongjun-Webhook-Secret`.
- `RFQ_ALLOWED_ORIGINS`: optional comma-separated origin allowlist. Defaults to apex + www; Vercel preview hostname is accepted automatically.

If the webhook is not configured or delivery fails, the browser falls back to a structured email addressed to `ask2205@outlook.com`.

## V17 RFQ payload
The server payload includes the structured technical RFQ plus an `evidence_package` planning string derived from the RFQ fields. This is a planning aid only and must not be treated as a certification, stock, origin or capability promise.

## DNS
After the domain is registered, add the records exactly as shown by Vercel's Domains screen. Do not copy generic DNS values from old screenshots or tutorials.

## Release gate
Run `npm run check`, test `/api/rfq` with the production webhook configured, and verify the apex/www redirect before outbound campaigns are switched to the new domain.
