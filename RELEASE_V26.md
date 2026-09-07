# RELEASE V26 — Canonical Source Mirror Convergence

Date: 2026-09-07

## Why this release exists

V25 closed the launch gate. V26 freezes public buyer behavior and focuses on reproducibility, deployment hygiene and convergence between the validated source artifact and the connected GitHub repository.

## Source-convergence scope

- Preserve the V25 information architecture, qualification logic and RFQ field schema.
- Keep the V25 launch audit in the release check chain.
- Harden RFQ routing with a lightweight per-instance rate gate while preserving origin allowlisting, payload limits, honeypot handling and fail-closed webhook behavior.
- Change mutable shared-asset caching from one-year immutable caching to short revalidation.
- Add CSP and Cross-Origin-Opener-Policy to the Vercel header set.
- Keep buyer-critical source, legal surfaces, technical references, sitemap/discovery assets and deployment manifests aligned with the canonical release.
- Record the remaining remote-tree / binary-image / live-deployment gap explicitly; priority-file presence is not equivalent to production completeness.

## Public behavior boundary

No new sourcing promise, technical value, standard route, RFQ field or buyer decision workflow is introduced in V26. Controlled technical document revisions therefore remain unchanged.

## Validation

`npm run check` → PASS

- 50 HTML route / canonical / image validation PASS
- RFQ payload + origin gate + fail-closed route + rate gate PASS
- V25/V26 launch audit: SEO + sitemap + JSON-LD + CTA routes + legal links + fallback + deployment-header checks PASS

## Remaining external gates

- GitHub `main` must be proven equivalent to the complete V26 source, including referenced images, from a fresh checkout.
- Vercel project ownership, domain binding and production deployment are not asserted.
- `RFQ_WEBHOOK_URL` must be configured and an end-to-end production delivery test must pass.
- Screenshot-level browser / device QA remains pending in an environment that permits local or deployed navigation.
