# 同钧出海 / Tongjun Overseas

Private source repository for **TONGJUN SPECIAL METALS** and the `exoticalloycn.com` international high-performance-materials platform.

## Current release

**V27 — Remote Text Canonicalization** (2026-09-08)

V27 freezes validated public behavior and closes the GitHub text-source gap. All HTML, CSS, JavaScript, API, validation, deployment, governance and operating text files are treated as a single canonical set. The remaining remote difference is deliberately isolated to the referenced WebP image assets; that binary gate must close before GitHub `main` is production-deployable.

## Positioning

**Special Metals. Precisely Sourced.**

Tongjun Special Metals is an **engineering-led sourcing and qualification desk**. Manufacturer, stockholder, processor and Tongjun supply-desk responsibilities remain explicit and separate.

Legal entity: **Tongjun Metal Technology (Wuxi) Co., Ltd.**

## Validation

```bash
npm run check
npm run verify:source
npm run verify:text-source
```

The complete local artifact contains 50 HTML files and all referenced image assets. `SOURCE_MANIFEST_V27.gitsha1` is the full byte-level reference; `SOURCE_MANIFEST_V27_TEXT.gitsha1` is the remote text-canonicalization reference.

## Production boundary

The repository is private and contains internal operating / governance material. Public deployment is controlled by `.vercelignore`. Source synchronization and production deployment are separate gates.
