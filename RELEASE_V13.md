# Tongjun Special Metals — V13 Release

Date: 2026-09-06
Theme: ATI-style information architecture, not a clone.

## What changed

### 1. Enterprise navigation
- Replaced the flat six-link header with a two-tier corporate navigation system.
- Added utility bar, Materials + Products mega menu, Markets mega menu, richer mobile navigation and a dedicated RFQ CTA.
- Added ATI-like secondary section navigation on core category pages.

### 2. Alloy Finder
- Added `/alloys` with 28 technical alloy entries across stainless/duplex, nickel/superalloys, Invar/low-expansion, titanium and zirconium.
- Search supports grade, UNS, product form and application terms.
- Family filtering is query-string aware (`?family=nickel`, `?q=625`).
- Every row explicitly separates alloy identity from actual dimensional / qualification capability.

### 3. Product Forms
- Added `/product-forms` to separate geometry from alloy chemistry.
- Covers precision strip/foil, sheet/coil, plate, bar/forging, tube/components and powder/master alloy.
- Each form describes route question and buyer evidence instead of claiming blanket manufacturing capability.

### 4. Homepage simplification
- Reduced homepage from a long conversion funnel to a corporate material-company hierarchy.
- Current order: Hero → portfolio → Material/Form/Market navigator → Markets → technical spotlight → Capabilities → Resources → RFQ.
- Removed redundant SEO/FAQ/tool sections from the homepage while keeping the underlying pages live.

### 5. Technical Resources
- Rebuilt `/resources` as a real resource center.
- Primary entry points: Alloy Finder, Standards Map, Quality + Traceability, Product Forms, Buyer Guides, Problem Order Desk, Supply Route Builder and Technical RFQ.

### 6. Public/private boundary
- Existing `.vercelignore` public allowlist remains intact.
- `/ops` and internal account data remain outside public deployment.

## Design reference logic
Borrowed only at the design-system level from mature specialty-material companies such as ATI:
- industrial photography hierarchy
- blue structural system + warm orange action accent
- hard-edge enterprise modules
- Materials / Products / Markets / Capabilities / Resources hierarchy
- section-level navigation
- technical resource and product-finder logic

No ATI logo, starburst, proprietary imagery, source code, registered slogans or customer marks are used.

## Validation
- 40 HTML pages
- 36 public sitemap URLs
- 4 noindex utility/internal-conversion pages
- 28 Alloy Finder entries
- 6 Product Form modules
- `npm run check`: PASS
- clean URL/canonical/image/alt/deployment validation: PASS
- public footer uniqueness check: PASS
- V13 finder and mega-navigation validation: PASS
