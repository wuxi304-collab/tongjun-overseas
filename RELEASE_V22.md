# RELEASE V22 — Qualified Offer System

Date: 2026-09-07

## Why this release exists

V21 made buyer decision gates visible. V22 carries those gates into the commercial handoff so a quotation can state exactly what is fixed, what is evidence-controlled, what is logistics-dependent and what still requires confirmation.

## Public changes

- Added a homepage **Qualified Offer System** covering material identity, supply route, evidence scope, logistics basis and commercial assumptions.
- Added an **Evidence-to-Offer Boundary** to Quality + Traceability.
- Added optional Technical RFQ fields for Incoterm, named destination / port, required delivery date and packing / handling.
- Added a live **Qualified Offer Readiness** state alongside the V21 Buyer Review State.
- Added a stable offer-screen reference (`OF-YYYYMMDD-XXXXXX`) to the RFQ.
- Extended the structured RFQ / server payload with the V22 logistics and offer-reference fields.
- Extended the RFQ regression test to prove those fields survive server-side routing.

## Commercial rule

Never hide an open technical, evidence or logistics assumption inside a single price.

## Boundary

Offer readiness is a quotation-structure aid, not a price, capacity, stock, lead-time, origin or certification promise. Availability and commercial terms remain time-bound confirmations against the final requirement and purchase order.

## Validation

`npm run check` → PASS (50 HTML files + RFQ regression test).
