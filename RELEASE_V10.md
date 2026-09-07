# Release V10 — Problem Order Conversion

Date: 2026-09-06

## Purpose
Move the site from generic inquiry capture to constraint-first technical conversion.

## Added
- `/problem-order` noindex buyer tool for difficult specifications.
- Constraint screen for dimension, MOQ, lead time, origin, qualification, documentation and processing.
- Route brief persisted only in session and transferred into the RFQ without putting technical detail in tracking URLs.
- RFQ query-prefill support plus an 8-field readiness indicator.
- Supply Route Builder now persists its route brief into the RFQ journey.
- Homepage Buyer Tools expanded to four steps: Constraint → Route → Specification → RFQ.
- Distribution landing page now sends ambiguous orders through Problem Order Desk before direct RFQ.
- Removed duplicated footer route/standards links and fixed malformed RFQ input markup.

## Boundary
The tool returns a sourcing hypothesis and evidence gate. It does not claim stock, mill approval, manufacturability or end-use qualification.
