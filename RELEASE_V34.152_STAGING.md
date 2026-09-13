# V34.152 — RFQ → Technical Review → Qualified Offer (STAGING)

> Status: **NOT RELEASED**. This branch is an isolated implementation delta built on the latest GitHub-recoverable V34.144 overlay. It must not be represented as the authoritative V34.152 release until the delta is applied to the verified V34.151 source package and the full release gates pass there.

## Objective

Turn the RFQ from a data-capture form into an auditable offer-control chain:

`RFQ → VERIFY → QUALIFY → ALIGN → QUALIFIED OFFER`

## Controls added

- **Quotation Assumptions** — assumptions remain explicit instead of silently becoming promises.
- **Deviation Register** — requirement, proposed deviation, impact, evidence and disposition remain visible.
- **Alternate Route Authority** — no silent substitution; buyer authority is recorded before an alternative route is shown or used.
- **Certificate Responsibility** — certificate definition / provision ownership is explicit.
- **Inspection Responsibility** — standard, buyer-defined, third-party or Tongjun-coordinated inspection ownership is explicit.
- **Release Checklist** — technical basis, assumptions, deviation state, alternate authority, evidence ownership and logistics are evaluated independently.

## Release semantics

- `NOT RELEASED` — one or more hard controls remain open. Quotation assumptions are a hard gate. Certificate and inspection responsibility must be assigned to an actual owner; `to be agreed` remains conditional and cannot release the offer.
- `QUALIFIED WITH CONDITIONS` — technical basis, quotation assumptions, alternate authority, evidence ownership and deviation record are explicit, but logistics and/or a buyer-controlled open deviation still remain conditional.
- `QUALIFIED BASIS` — all six release controls are explicit, evidence ownership is assigned and no open / buyer-decision deviation remains.

The legacy four-gate **Qualified offer readiness** indicator is synchronized to the new Release Checklist. It cannot show `Qualified basis` while the stricter V34.152 release state is still `NOT RELEASED` or `QUALIFIED WITH CONDITIONS`.

`QUALIFIED BASIS` is **not** a claim that mill capability, project approval, certificate acceptance or inspection acceptance already exists. Those remain evidence-bound.

## Transport / audit scope

The new fields are persisted through `/api/rfq` with bounded lengths and are added to the structured copy/email fallback. `scripts/test-rfq.js` verifies the workflow fields survive the API transport.

## Staging validation completed

The isolated V34.152 delta passes:

- JavaScript syntax checks for `assets/site.js`, `assets/polish.js` and `api/rfq.js`;
- RFQ API transport regression, including all new workflow fields;
- unique RFQ control-name and DOM-id checks;
- release-authority semantic assertions for hard assumptions, assigned evidence ownership and legacy offer synchronization.

The GitHub-recoverable V34.144 overlay is intentionally **not** used for full-site release validation because it lacks the complete image asset set that existed in the later packaged working source.

## Promotion gate to real V34.152

Do not rename or seal this staging branch as V34.152 until all of the following are true:

1. Recover / mount the exact verified V34.151 source package.
2. Apply `scripts/apply-v34-152.py` and `scripts/refine-v34-152-release.py` to that package, resolving anchors against the real V34.151 files.
3. Run the full V34.151 test suite plus RFQ workflow regression.
4. Re-run the 390 px indexed-page overflow scan and RFQ mobile interaction check.
5. Package, hash and clean-room verify the resulting source.
6. Only then sync the sealed V34.152 source and, separately, deploy production.
