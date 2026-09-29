# AGENTS.md — Tongjun Overseas / exoticalloycn.com

## Product
Tongjun Special Metals is an engineering-led special-metals sourcing and qualification desk operated by Tongjun Metal Technology (Wuxi) Co., Ltd.

## Non-negotiables
- Do not present Tongjun as the manufacturer unless a page explicitly identifies a verified manufacturing role.
- Keep manufacturing, stockholding, processing and trading responsibilities distinct.
- Technical claims must be tied to material, product form, condition, standard and qualification boundary.
- Do not publish unverified mill capability, stock, origin, dimensional range or approval claims.
- RFQ email fallback is ask2205@outlook.com.
- Canonical production domain is https://exoticalloycn.com.
- Public visual language: industrial enterprise, full-bleed real materials photography, square geometry, deep blue/graphite, restrained orange accent.
- Public copy must not mention the competitor used as an internal design reference.

## Account intelligence
- Use `skills/tongjun-account-intelligence/SKILL.md` for target-account enrichment and re-verification.
- The live source of truth for prospect/account intelligence is the Google Sheet `同钧出海｜海外特材客户池`.
- Until repository visibility is verified private, do not add newly discovered personal contact data, buyer lists, or raw OSINT exports to this repository.
- Prefer current official company evidence; never synthesize personal email addresses.
- theHarvester requires an explicitly authorized security scope and is disabled for ordinary prospecting.
- SpiderFoot, when used for commercial research, is passive-only; no scanning, breach, dark-web, credential, vulnerability or bucket-enumeration modules.
- Maigret is off by default and may only support narrow business-identity corroboration when explicitly allowed.
- Keep material fit, product-form fit, purchasing ownership, origin/approved-source constraints and evidence confidence as separate judgments.

## Change protocol
1. Inspect current release and SITE_HEALTH.md.
2. Preserve URL stability and canonical metadata.
3. Run `npm run check`.
4. Run `npm run check:account-intel` when the account-intelligence skill or adapter changes.
5. Update SITE_HEALTH.md and add a release note for material public-site changes.
6. Prefer evidence and qualification clarity over catalogue breadth.
