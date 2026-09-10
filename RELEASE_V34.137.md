# RELEASE V34.137 — Mobile Resilience & Release-Candidate Hardening

Date: 2026-09-10  
Status: **Release candidate / packaging not yet closed**  
Project: **Tongjun Special Metals / exoticalloycn.com**

## Release intent

V34.137 continues the V34 pre-launch hardening line. This increment is not a visual redesign release. It closes verified small-screen defects and removes mobile first-fold outliers while preserving the validated desktop experience and the sourcing / qualification information architecture.

The release authority remains the complete V34.137 working tree. A prior archive, GitHub mirror, browser preview, or deployed copy must not be promoted as the V34.137 source of truth unless byte parity is demonstrated.

## V34.136–V34.137 changes

### 1. 390 px indexed-page regression sweep

A real Chromium scan was run across **47 indexable pages at 390 px viewport width**.

A genuine horizontal-overflow defect was found on `standards.html`:

- viewport width: **390 px**
- previous effective page width: **568 px**
- root cause: standards table exceeded the mobile layout boundary

The standards table is now contained in a **focusable, horizontally scrollable standards region**, preserving access to the full technical table without forcing document-level horizontal overflow.

Current result:

- **47 / 47 indexable pages: document-level horizontal overflow = 0**

### 2. Technical Data mobile first-fold

`technical-data.html` was changed to an action-first mobile hierarchy.

H1:

- Previous: `Controlled technical data for sourcing decisions.`
- Current: `Technical data for sourcing decisions.`

On small screens, the large Technical Data hero image is suppressed so the technical directory enters the viewport earlier. The desktop hero treatment is retained.

### 3. Long-H1 normalization

The 390 px scan identified and removed four-line H1 outliers.

`resource-invar-lng-vs-tooling.html`:

- Current H1: **`Invar 36: LNG strip vs tooling plate`**

`titanium-heat-exchangers.html`:

- Current H1: **`Titanium + zirconium for corrosive service.`**

Current result:

- **390 px scan: no four-line H1 outlier remains**

### 4. Regression-gate discipline

V34.136 / V34.137 regression checks were added around the mobile fixes.

During implementation, the gate correctly rejected two CSS scopes targeting nonexistent `data-page` values. Those selectors were removed rather than introducing artificial page IDs merely to satisfy the checker.

This preserves the rule that validation gates must expose real source defects; source semantics must not be distorted to make a test pass.

## Current validated envelope

Latest reported working-tree state:

- CSS: **~238.9 KB**
- JavaScript: **44.7 KB**
- Public images: **652.7 KB**
- 390 px indexed pages with document-level horizontal overflow: **0 / 47**
- Working-tree regression suite: **PASS**

## Verified predecessor

V34.135 was independently sealed and clean-room verified before the V34.136–V34.137 changes:

- file parity: **166 / 166 SHA-256 matches**
- full `npm run check` after fresh extraction: **PASS**
- V34.135 ZIP SHA-256:  
  `84d907b8b0312da3aa9838674dd0c57a6b0edcf8d4aac664d47cac2415c4a016`

V34.135 is therefore a verified predecessor, **not the current release artifact**.

## V34.137 closure gates

V34.137 must not be called sealed, latest packaged release, or production-complete until all of the following are completed against the same working tree:

1. Synchronize release / source-authority documentation to V34.137.
2. Rebuild the current homepage browser preview from the V34.137 source.
3. Run the full validation suite from the V34.137 worktree.
4. Produce a new V34.137 source ZIP.
5. Produce the ZIP SHA-256 digest.
6. Extract the ZIP into a new empty directory.
7. Verify the extracted inventory and per-file SHA-256 parity against the packaged source tree.
8. Run the complete `npm run check` from the freshly extracted directory.
9. Only after clean-room PASS, designate that exact ZIP digest as the V34.137 sealed artifact.
10. Synchronize the verified tree to GitHub and verify remote parity before treating GitHub as a release authority.
11. Production deployment / Vercel verification remains a separate gate from source packaging.

## Non-regression rule

Do not fall back to the V34.135 archive, the current GitHub `main`, or an older browser preview and label it V34.137. If the V34.137 working tree is unavailable, release closure must stop at documentation / recovery rather than manufacture a false parity claim.
