from pathlib import Path

path = Path('assets/polish.js')
text = path.read_text(encoding='utf-8')
marker = 'V34.152 R2 — release authority alignment'
if marker in text:
    print('V34.152 R2 already applied.')
    raise SystemExit(0)

old = r'''    const devState=val('deviation_status'),devText=val('deviation_register');
    const deviations=devState==='none'||devState==='rejected'||((devState==='accepted'||devState==='buyer-decision'||devState==='open')&&Boolean(devText));
    const devConditional=devState==='open'||devState==='buyer-decision';
    const alternate=Boolean(val('alternate_route_permission'));
    const evidence=Boolean(val('certificate_responsibility')&&val('inspection_responsibility'));
    const logistics=Boolean((val('incoterm')&&val('destination'))||val('delivery_target')||val('packing'));
    gate('technical',technical?'READY':'OPEN');gate('assumptions',assumptions?'READY':'OPEN');gate('deviations',deviations?(devConditional?'CONDITIONAL':'READY'):'OPEN');gate('alternate',alternate?'READY':'OPEN');gate('evidence',evidence?'READY':'OPEN');gate('logistics',logistics?'READY':'OPEN');
    const hardReady=technical&&alternate&&evidence&&deviations;
    const cleanReady=hardReady&&assumptions&&logistics&&!devConditional;
    const status=cleanReady?'QUALIFIED BASIS':hardReady?'QUALIFIED WITH CONDITIONS':'NOT RELEASED';
    const statusEl=form.elements.namedItem('release_status');if(statusEl)statusEl.value=status;
    const stateEl=d.getElementById('qualifiedOfferState');if(stateEl)stateEl.textContent=status;
    const open=[];if(!technical)open.push('technical basis');if(!assumptions)open.push('quotation assumptions');if(!deviations)open.push('deviation disposition');if(!alternate)open.push('alternate authority');if(!evidence)open.push('certificate / inspection ownership');if(!logistics)open.push('logistics basis');if(devConditional)open.push('buyer-controlled deviation');
    const reason=d.getElementById('qualifiedOfferReason');if(reason)reason.textContent=cleanReady?'All release controls are explicit. Final capability and approval remain evidence-bound.':hardReady?`Offer may be prepared only with visible conditions: ${open.join(' · ')||'conditional deviation'}.`:`Open release controls: ${open.join(' · ')}.`;
    const checklist=[`technical=${technical?'READY':'OPEN'}`,`assumptions=${assumptions?'READY':'OPEN'}`,`deviations=${deviations?(devConditional?'CONDITIONAL':'READY'):'OPEN'}`,`alternate=${alternate?'READY':'OPEN'}`,`evidence_ownership=${evidence?'READY':'OPEN'}`,`logistics=${logistics?'READY':'OPEN'}`].join(' | ');'''

new = r'''    /* V34.152 R2 — release authority alignment */
    const devState=val('deviation_status'),devText=val('deviation_register');
    const deviations=devState==='none'||((devState==='accepted'||devState==='rejected'||devState==='buyer-decision'||devState==='open')&&Boolean(devText));
    const devConditional=devState==='open'||devState==='buyer-decision';
    const alternate=Boolean(val('alternate_route_permission'));
    const certOwner=val('certificate_responsibility'),inspectionOwner=val('inspection_responsibility');
    const evidenceDeclared=Boolean(certOwner&&inspectionOwner);
    const evidenceConditional=evidenceDeclared&&(certOwner==='to-be-agreed'||inspectionOwner==='to-be-agreed');
    const evidenceAssigned=evidenceDeclared&&!evidenceConditional;
    const logistics=Boolean((val('incoterm')&&val('destination'))||val('delivery_target')||val('packing'));
    gate('technical',technical?'READY':'OPEN');
    gate('assumptions',assumptions?'READY':'OPEN');
    gate('deviations',deviations?(devConditional?'CONDITIONAL':'READY'):'OPEN');
    gate('alternate',alternate?'READY':'OPEN');
    gate('evidence',evidenceDeclared?(evidenceConditional?'CONDITIONAL':'READY'):'OPEN');
    gate('logistics',logistics?'READY':'OPEN');
    const hardReady=technical&&assumptions&&alternate&&evidenceAssigned&&deviations;
    const cleanReady=hardReady&&logistics&&!devConditional;
    const status=cleanReady?'QUALIFIED BASIS':hardReady?'QUALIFIED WITH CONDITIONS':'NOT RELEASED';
    const statusEl=form.elements.namedItem('release_status');if(statusEl)statusEl.value=status;
    const stateEl=d.getElementById('qualifiedOfferState');if(stateEl)stateEl.textContent=status;
    const open=[];
    if(!technical)open.push('technical basis');
    if(!assumptions)open.push('quotation assumptions');
    if(!deviations)open.push('deviation disposition');
    if(!alternate)open.push('alternate authority');
    if(!evidenceDeclared)open.push('certificate / inspection ownership');
    else if(evidenceConditional)open.push('certificate / inspection owner assignment');
    if(!logistics)open.push('logistics basis');
    if(devConditional)open.push('buyer-controlled deviation');
    const reason=d.getElementById('qualifiedOfferReason');
    if(reason)reason.textContent=cleanReady?'All release controls are explicit. Final capability and approval remain evidence-bound.':hardReady?`Offer may be prepared only with visible conditions: ${open.join(' · ')||'conditional deviation'}.`:`Open release controls: ${open.join(' · ')}.`;
    const checklist=[`technical=${technical?'READY':'OPEN'}`,`assumptions=${assumptions?'READY':'OPEN'}`,`deviations=${deviations?(devConditional?'CONDITIONAL':'READY'):'OPEN'}`,`alternate=${alternate?'READY':'OPEN'}`,`evidence_ownership=${evidenceDeclared?(evidenceConditional?'CONDITIONAL':'READY'):'OPEN'}`,`logistics=${logistics?'READY':'OPEN'}`].join(' | ');
    const legacyOffer=d.querySelector('[data-offer-gate="commercial"]'),legacyState=d.getElementById('offerCommercialState');
    if(legacyOffer){legacyOffer.classList.remove('is-ready','is-open');legacyOffer.classList.add(status==='QUALIFIED BASIS'?'is-ready':'is-open')}
    if(legacyState)legacyState.textContent=status==='QUALIFIED BASIS'?'Qualified basis':status==='QUALIFIED WITH CONDITIONS'?'Conditional':'Not released';'''

if old not in text:
    raise SystemExit('V34.152 R2 anchor not found; refusing non-deterministic edit.')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
print('V34.152 R2 applied: assumptions hard gate, evidence ownership assigned, legacy offer synchronized.')
