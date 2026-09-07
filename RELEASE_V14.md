# Release V14 — Technical Data Architecture

Date: 2026-09-07

## Scope
V14 deepens the ATI-inspired enterprise architecture from visual/portfolio structure into a disciplined technical-data layer.

## Added
- `/technical-data` Technical Data Center.
- Six flagship reference sheets: Alloy 625, Alloy 718, Alloy C-276, Alloy 825, 36Ni-Fe low-expansion alloy, Super Duplex 2507.
- Composition, standards-by-form, physical-property context, application signals, qualification boundaries and print-reference behavior.
- Technical Data links across mega navigation, mobile navigation, footer, resources, homepage and Alloy Finder.
- Alloy Finder now exposes a Technical Data column for covered grades.
- Internal `TECHNICAL_DATA_SOURCES.md` provenance register (not deployed publicly).

## Standards hygiene
- Removed ASTM F1684 as a current default route for Invar/36Ni-Fe. ASTM lists F1684 as withdrawn in 2024.
- Public low-expansion guidance now defaults to buyer/project/producer requirements plus explicit CTE criteria. ASTM B753 is referenced only where its thermostat-component scope is applicable; identity is confirmed by governing spec.

## Design
- Added dense, corporate technical-sheet styling with hard-edge tables, data identity cards, document hierarchy and print mode.
- No competitor logos, protected photos or manufacturer-specific trade claims are used.

## Boundary
All website data are sourcing/engineering references. Final acceptance is governed by PO, current standards, approved-source rules and certified material documentation.
