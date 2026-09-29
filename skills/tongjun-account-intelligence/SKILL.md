---
name: tongjun-account-intelligence
description: Enrich Tongjun Overseas target accounts with public, business-relevant evidence; verify company identity, official contact routes, named business contacts, supplier-onboarding paths, material/application fit, and evidence confidence. Keep all personal-contact enrichment reviewable and never publish account intelligence to the public website.
---

# Tongjun Account Intelligence

Use this skill when a Tongjun Overseas target company, customer pool, prospect list, or supplier-registration target needs enrichment or re-verification.

## Goal

Turn a company name/domain into a reviewable account-intelligence record that can be written back to the private customer pool without confusing:
- official company facts,
- inferred commercial fit,
- public business contact data,
- third-party discovery,
- security-oriented OSINT output.

The source of truth for live account data is the Google Sheet `同钧出海｜海外特材客户池`. The GitHub repository contains workflow logic only; do not store newly discovered personal contact data in the public repository.

## Required inputs

Use the fields already available whenever possible:
- company name
- country
- official website/domain
- target material family
- expected product form
- target role
- current evidence/notes

Do not require a personal contact before starting.

## Default workflow

1. Resolve the legal/operating company and canonical domain.
2. Read the official website first: contact, team, supplier/vendor, quality/certification, products/capabilities, locations and current project/news pages.
3. Record only business-relevant public contact channels.
4. Identify named contacts only when role + company assignment are supported by evidence.
5. Separate fact from inference:
   - Fact: source says X.
   - Inference: X suggests a likely purchasing path.
6. Write confidence and remaining gaps explicitly.
7. Prepare field-level writeback for the customer pool. Do not send outreach from this skill.

## Evidence levels

- L1 — current official company webpage, official document, official supplier portal, official company filing.
- L2 — official group/subsidiary source or current first-party press release/brochure.
- L3 — reputable professional network, trade directory, conference/exhibitor record, recognized industry database.
- L4 — search-index discovery or uncorroborated third-party mention; use only as a lead for verification.

Never promote L3/L4 data to “verified” without corroboration.

## Tool adapters

### Public-business research — DEFAULT

Use official company sources and bounded public-web research. Prefer:
- company contact/team pages
- vendor/supplier registration pages
- quality/certification pages
- official brochures/PDFs
- current first-party press releases
- reputable professional-network evidence for role corroboration

### theHarvester — AUTHORIZED SECURITY SCOPE ONLY

theHarvester’s current documentation frames use around authorized security assessments. Do not run it against a prospect merely because the company is in the sales list.

Only accept its output when the input record contains:
`authorized_security_scope: true`

When enabled:
- prefer P0/passive sources,
- do not use DNS brute force, port scans, screenshots, takeover checks, direct endpoint probing or breach selectors,
- retain source outcome/status because zero-result and partial runs are different.

### SpiderFoot — PASSIVE MODULES ONLY FOR COMMERCIAL RESEARCH

If used for a prospect:
- allow public passive modules relevant to company/domain identity and business contact discovery,
- disable port scanning, banner grabbing, vulnerability, breach, dark-web, credential, bucket-enumeration and intrusive modules,
- do not treat a graph edge as verified identity by itself.

### Maigret — OFF BY DEFAULT

Do not enumerate a person’s general social footprint for ordinary B2B prospecting.

It may be used only when:
- a business-relevant username was already supplied or publicly linked by the company/contact,
- the purpose is narrow identity corroboration,
- `allow_person_account_checks: true` is explicitly set.

Do not write personal lifestyle/social findings to the customer pool.

## Contact rules

Accept an email as usable only when:
- it is published by the company/authorized business source; or
- it is independently corroborated and belongs to a business domain associated with the account.

Never synthesize email addresses from naming patterns.

Do not write consumer-domain addresses (for example gmail.com, outlook.com, yahoo.com) as procurement contacts unless the company itself publishes that address as its business channel.

## Account-fit rules

Keep these dimensions separate:
- material fit,
- product-form / thickness fit,
- procurement ownership,
- country-of-origin / approved-source constraints,
- supplier onboarding requirements,
- evidence confidence.

“Uses Alloy 625” does not imply “buys 10–70 mm plate”.
“Has a procurement department” does not imply the named person buys specialty-alloy plate.

## Google Sheet writeback

Target spreadsheet: `同钧出海｜海外特材客户池`
Primary tab: `客户池`

Map reviewed evidence to existing fields:
- 官网/来源
- 公开联系渠道
- 实际联系人
- 实际职务
- 联系人来源/LinkedIn
- 联系人邮箱
- 认证/规范
- 采购可能性
- 情报完整度
- 最近核验
- 最近活动 / 下一动作 when the enrichment changes the next commercial step

Preserve existing status/priority unless new evidence directly invalidates the current fit.

## Output contract

Return one normalized record per account:

```json
{
  "account": {
    "name": "",
    "domain": "",
    "country": ""
  },
  "company_facts": [],
  "official_channels": [],
  "contacts": [],
  "supplier_onboarding": [],
  "fit": {
    "material": "",
    "product_form": "",
    "procurement_path": "",
    "origin_constraints": ""
  },
  "evidence": [],
  "confidence": "high|medium|low",
  "gaps": [],
  "writeback": {}
}
```

Every factual field should have a source or be marked unresolved.
