# Domain, Email & Deployment Decision — V2

## Brand
- Market brand: **Tongjun Special Metals**
- Legal entity: **Tongjun Metal Technology (Wuxi) Co., Ltd.**
- Preferred domain pattern: `tongjunspecialmetals.com`
- Shorter alternatives to check at a registrar: `tongjunmetals.com`, `tongjunalloys.com`, `tongjunmaterials.com`.
- **Do not claim availability until registrar/RDAP confirmation at purchase time.** Search-engine absence is not proof of domain availability.

## Email
Production launch should migrate outbound and RFQ traffic from the temporary Outlook address to branded-domain email.
Recommended addresses:
- `tm@<domain>` — named outbound account
- `sales@<domain>` — general sales
- `rfq@<domain>` — RFQ routing

Configure before scaled outreach:
- SPF
- DKIM
- DMARC (start p=none; review reports before enforcement)
- Microsoft 365 or equivalent mailbox
- Separate transactional/form sender if needed

## Deployment
Recommended V1 production path:
1. Next.js or static-export deployment on Vercel / Cloudflare Pages.
2. Server-side RFQ endpoint with anti-spam and rate limiting.
3. Store no sensitive technical drawings by default; use secure agreed channels for confidential data.
4. GA4 or privacy-conscious analytics, plus Bing/Google Search Console.
5. Sitemap, robots, canonical URLs, structured data, 404, redirect policy.
6. UTM parameters on every outbound campaign link.

## Email landing strategy
Examples:
- Knight → `/precision-strip?utm_source=outlook&utm_campaign=week1_knight`
- Dongsung → `/invar-36?utm_source=outlook&utm_campaign=lng_dongsung`
- L&T → `/heavy-plate?utm_source=outlook&utm_campaign=heavyplate_lt`

The email should not send the prospect to the generic homepage unless the account thesis is still broad.
