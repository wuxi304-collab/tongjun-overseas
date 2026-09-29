# Account Intelligence Data Policy

This repository is public as of the current GitHub connection state. Treat all account research as potentially sensitive operating data.

## Storage boundary

- GitHub: workflow code, schemas, templates, tests, documentation only.
- Google Sheet `同钧出海｜海外特材客户池`: live account intelligence and reviewed business contacts.
- Public website: no buyer lists, personal contact records, raw OSINT exports or supplier-intelligence notes.

## Allowed enrichment

- official company websites and documents
- official supplier/vendor portals
- public business contact channels
- named business contacts whose role/company relationship is publicly evidenced
- public certifications, capabilities, locations and current project/company news
- bounded reputable third-party corroboration

## Disallowed by default

- credential/breach data
- dark-web collection
- active port/service scanning
- vulnerability probing
- takeover testing
- private/personal social profiling
- guessed email addresses
- bulk personal-contact harvesting without review

## Tool-specific controls

theHarvester:
- require `authorized_security_scope=true`
- P0/passive only unless separate written authorization exists

SpiderFoot:
- commercial prospect mode is passive-only
- disable intrusive/security/breach/dark-web modules

Maigret:
- disabled unless `allow_person_account_checks=true`
- business-relevance and narrow identity corroboration only

## Evidence discipline

L1 official current source > L2 first-party group/document > L3 professional/industry source > L4 search lead.

Do not convert an inference into a fact. Do not overwrite stronger evidence with weaker evidence.
