# RELEASE V15 — Controlled Technical Document System

Date: 2026-09-07

## Scope

V15 turns the V14 technical data layer into a controlled technical-document and engineering-tool system while preserving the ATI-inspired industrial enterprise visual language.

## New public routes

- `/material-compare` — three-material reference screening tool.
- `/standards-matrix` — product-form specification routing matrix.
- `/document-center` — document register with Tongjun document IDs, revisions and review dates.

## Document control

The six flagship technical sheets now carry stable `TJ-TDS-*` document IDs, revision 02, last-review date and explicit authority hierarchy. TechArticle structured data is added to each controlled technical sheet.

## Site integration

- Desktop mega navigation, mobile navigation, utility bar and footer now surface the technical document system.
- Homepage and Resources add Tools + Resources pathways.
- Technical Data Center adds Material Compare, Standards Matrix and Document Center as first-class tools.

## Safety / qualification boundary

Comparison and standards tools are screening aids only. Purchase acceptance remains governed by buyer requirements, applicable current standards, approved source requirements and certified producer documentation.

## Performance hardening
- Re-encoded editorial WebP assets for materially smaller transfer size while preserving the ATI-style industrial visual system.
- Hero remains 1280×720; card/application imagery is normalized to 800×450; OG remains 1200×630.
- Image tags now carry intrinsic width/height, async decoding, and lazy loading by default where not already explicitly eager, reducing layout shift and unnecessary below-fold work.
