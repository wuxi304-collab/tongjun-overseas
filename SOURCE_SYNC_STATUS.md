# Source Sync Status — V27

Date: 2026-09-08  
Target: `wuxi304-collab/tongjun-overseas` (private)

## V27 rule

The complete local V27 artifact remains the release authority. Remote synchronization is judged by path + Git blob SHA, not by file-name presence.

## Text canonicalization

`SOURCE_MANIFEST_V27_TEXT.gitsha1` covers every V27 source file except WebP binaries. The V27 remote operation is intended to make that entire text set byte-identical on GitHub `main`.

## Remaining binary gate

The only permitted remote source gap after V27 text canonicalization is the 15 referenced `assets/images/*.webp` files. GitHub `main` remains **non-production** until those binaries are mirrored and the full tree matches `SOURCE_MANIFEST_V27.gitsha1`.

## Production-completion gate

1. Text manifest parity: materialization in progress; remote verification pending.
2. Mirror and byte-match all 15 WebP assets.
3. Verify full remote inventory against the full V27 manifest.
4. Run `npm run check` and `npm run verify:source` from a fresh GitHub checkout.
5. Only then mark GitHub `main` production-deployable.

Vercel binding, RFQ webhook delivery, branded mail and browser/device visual QA remain separate gates.
