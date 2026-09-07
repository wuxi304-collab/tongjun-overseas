# RELEASE V21 — Buyer Decision Interface

Date: 2026-09-07

## Why this release exists

V18 made source roles and chain-of-custody explicit. V19 connected claims to evidence and buyer acceptance. V20 clarified corporate responsibility. V21 turns those ideas into a buyer-facing decision interface: the site now shows which gates are open, who owns the evidence, and what releases a route toward commercial commitment.

## Public changes

- Added a homepage **Buyer Decision Board** with four release gates:
  1. Service fit
  2. Manufacturability
  3. Evidence readiness
  4. Buyer acceptance
- Added a **Buyer Acceptance Matrix** to Quality + Traceability that separates owner, evidence and release condition.
- Added **Procurement Stage** and **Buyer Release Gate** to the Technical RFQ.
- Added a live RFQ **Buyer Review State** using Perform → Make → Accept → Release.
- Added a stable buyer review reference (`BR-YYYYMMDD-XXXXXX`) to the structured RFQ payload.
- Added procurement-stage logic to the Evidence Package Preview for trial, repeat, urgent and tender routes.
- Added **Buyer Decision Snapshot** sections to the four flagship controlled technical references:
  - Alloy 625
  - Alloy 718
  - Alloy C-276
  - 36Ni-Fe / Invar 36
- Bumped those four controlled technical references from REV 02 to **REV 03** and updated the Document Center register.

## Decision rule

A lower price cannot close an open technical, evidence or buyer-approval gate.

## Boundary

The Buyer Review State is a sourcing-screening aid. It does not certify manufacturability, source approval, inventory, origin, inspection results or final acceptance. The purchase order, governing standard, certified source documents and authorized buyer approval remain controlling.

## Validation

`npm run check` → PASS (50 HTML files).
