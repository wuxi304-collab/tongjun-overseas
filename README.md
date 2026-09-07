# 同钧出海 / Tongjun Overseas

Private source repository for **TONGJUN SPECIAL METALS** and the `exoticalloycn.com` international high-performance-materials platform.

## Current release

**V26 — Canonical Source Mirror Convergence** (2026-09-07)

V26 keeps the validated V25 public behavior frozen and moves repository governance toward a canonical source mirror. The public site logic is unchanged; the release focuses on synchronizing the buyer-critical source tree, validation assets and deployment metadata without weakening the production-completion gate.

### Public architecture

- Materials + Product Forms + Markets + Capabilities + Resources
- Alloy Finder and Technical Data Center
- Material Compare
- Standards-by-Product-Form Matrix
- Controlled Document Center with stable technical document IDs / revisions
- Supply Route Builder + Problem Order Desk
- Structured Technical RFQ + evidence-package and qualified-offer planning
- Buyer Review State: Perform → Make → Accept → Release
- Qualified Offer Readiness: technical basis + evidence boundary + logistics basis + commercial assumptions
- Quality + Traceability with source roles, chain of custody, evidence matrix and buyer acceptance controls
- Buyer Decision Snapshots on flagship Alloy 625 / 718 / C-276 / 36Ni-Fe references

## Positioning

**Special Metals. Precisely Sourced.**

Tongjun Special Metals is an **engineering-led sourcing and qualification desk**. Manufacturer, stockholder, processor and Tongjun supply-desk responsibilities remain explicit and separate.

Legal entity: **Tongjun Metal Technology (Wuxi) Co., Ltd.**

## Validation

```bash
npm run check
```

V26 retains the V25 launch validation baseline:

- 50 HTML files
- exact sitemap ↔ indexable canonical parity
- title / meta-description launch ranges
- Open Graph / Twitter metadata
- valid JSON-LD on every indexable page
- Privacy / Terms links in every global footer
- controlled technical-directory revision parity
- RFQ payload, origin, fail-closed fallback path and lightweight rate gate
- deployment cache and security-header rules

A local clean-route crawl also checks all **46 indexable canonical routes**.

## Production boundary

The source release contains internal operating material and governance documents that must stay private. Public deployment is controlled by `.vercelignore`; only the explicit public allowlist is deployable.

## Release governance

Read `AGENTS.md`, `CRAFT.md`, `SITE_HEALTH.md`, `SOURCE_SYNC_STATUS.md` and `RELEASE_V26.md` before material changes.
