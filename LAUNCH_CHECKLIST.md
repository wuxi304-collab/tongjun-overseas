# Launch Checklist — exoticalloycn.com

## Ready in V7
- [x] Production domain embedded in canonical / OG / sitemap
- [x] Responsive core pages
- [x] Original industrial WebP image system
- [x] 6 application landing pages
- [x] 7 specification-led alloy / product SEO pages
- [x] Quality / traceability page
- [x] Supply-route builder
- [x] Standards / RFQ logic
- [x] Structured RFQ API endpoint with email fallback
- [x] Privacy / terms baseline
- [x] robots.txt / sitemap.xml / llms.txt
- [x] Vercel static deployment config

## Required before public sales launch
- [ ] Confirm domain registration is complete
- [ ] Connect exoticalloycn.com DNS to Vercel
- [ ] Configure RFQ mail delivery (`RFQ_MAIL_TRANSPORT` + `RFQ_MAIL_TO` + `RFQ_MAIL_FROM` + transport credentials) and confirm `/api/health` returns `ok: true`
- [ ] Set up branded email: rfq@ / sales@ / named mailbox
- [ ] Configure SPF / DKIM / DMARC
- [ ] Create GitHub private repo `tongjun-overseas` and push current branch
- [ ] Add analytics / Search Console only after privacy disclosure is updated
- [ ] Run live-domain crawl after DNS is active

## V8 deployment gate
- [x] Canonical and sitemap use Vercel clean URLs
- [x] Internal navigation uses extensionless production routes
- [x] Favicon exists
- [x] Web manifest exists
- [x] 1200×630 social share image exists
- [x] security.txt exists
- [x] RFQ confirmation page exists and is noindex
- [x] RFQ API has input limits, origin allowlist and delivery request ID
- [x] Local preview resolves clean routes
- [ ] GitHub private repo exists and is connected
- [ ] Vercel project is connected
- [ ] exoticalloycn.com DNS attached to Vercel
- [ ] RFQ mail delivery configured and end-to-end tested (buyer receives the `[Tongjun RFQ] …` email at the configured recipient, Reply-To points at the buyer)
- [ ] branded mailbox configured; replace temporary Outlook contact when ready
