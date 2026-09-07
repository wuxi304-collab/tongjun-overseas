# Release V6 — Conversion & Application Routes

Date: 2026-09-06

## Added
- 6 application-specific landing pages for account-based outreach
- Homepage application-route section
- Industry page links to dedicated landing pages
- Server-side RFQ endpoint skeleton (`/api/rfq.js`) with webhook delivery and email fallback
- RFQ honeypot and validation
- Updated sitemap and site architecture

## Deployment dependency
Set `RFQ_WEBHOOK_URL` in Vercel/hosting environment. Until configured, the browser falls back to `ask2205@outlook.com`.

## Domain
Production canonical domain remains `https://exoticalloycn.com`.
