# RELEASE V19 — Evidence Architecture & Buyer Acceptance System

Date: 2026-09-07

## Objective

V19 turns traceability from a quality-page topic into a site-wide decision architecture. The core sequence is now **Claim → Evidence → Acceptance** and it is connected directly to material selection, manufacturability and the technical RFQ.

## Homepage

- Added a three-question Evidence Architecture: **Perform / Make / Accept**.
- Reframed price as the commercial output of a closed technical decision, not the starting point.
- Kept the V17 requirement→route→evidence→scale protocol and V18 source-role system intact.

## Quality + Traceability

- Added a six-layer Evidence Package Matrix covering material identity, manufacturing route, processing handoff, verification, delivery identity and buyer-controlled approvals.
- Added a Claim → Evidence → Acceptance strip to make responsibility and approval explicit.

## Flagship technical references

Alloy 625, Alloy 718, Alloy C-276 and 36Ni-Fe / Invar 36 now include a Procurement Evidence Map between engineering properties and sourcing qualification.

## RFQ

- Added an optional **Customer / Project Approval** field.
- Evidence preview now distinguishes **CORE / CONDITIONAL / PO-DRIVEN / BUYER-CONTROLLED** evidence.
- API payload accepts the approval field and preserves it in structured RFQ routing.

## Boundary

The evidence map is a procurement-planning framework. It does not replace the purchase order, current material/product standard, certified mill documentation, OEM/project approval or third-party acceptance where required.
