# Release V25 — Launch Gate

Date: 2026-09-07

V25 is a launch-control release. It does not add a new sourcing workflow. It converts launch readiness into executable checks and closes SEO, legal, RFQ-fallback and public-navigation gaps identified in the V24 source.

## Changes

- Added `scripts/audit-launch.js` and wired it into `npm run check`.
- Launch audit now verifies title / meta-description ranges for indexable pages, canonical URLs, one-H1 structure, Open Graph essentials, sitemap/noindex consistency, JSON-LD parseability, internal CTA targets, legal footer links and RFQ email fallback presence.
- SEO metadata tightened across corporate, application, material and resource pages; indexable pages now sit inside the launch title/description envelope.
- Homepage organization schema now includes the technical-enquiry contact point and a separate WebSite schema.
- Privacy Notice expanded around RFQ/contact data, technical requirement data, service providers, retention, security and buyer choices.
- Terms of Use expanded around reference values, capability/availability, quotation boundaries and transaction-document precedence.
- RFQ acknowledgement now links the Privacy Notice while retaining the technical-qualification boundary.
- Privacy and Terms links are exposed in the public footer.

## Technical-data boundary

No chemistry, mechanical-property, density, CTE value or product-standard route changed in V25. Controlled technical document revisions therefore remain unchanged.

## Validation

`npm run check` → PASS

- 50 HTML files: route / canonical / image / deployment validation PASS
- RFQ V22 regression: buyer-decision + qualified-offer payload + origin gate PASS
- V25 launch audit: SEO + sitemap + JSON-LD + CTA routes + legal links + RFQ fallback PASS

## Remaining external launch gates

- Production Vercel project/domain binding is not asserted by this release.
- `RFQ_WEBHOOK_URL` must be configured for server-side production routing; structured email fallback remains available.
- Screenshot-level browser/device QA has not been completed in the current environment.
- GitHub `main` must be proven against the complete V25 tree from a fresh checkout before it is called production-deployable.
