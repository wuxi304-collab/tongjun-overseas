from pathlib import Path

ROOT = Path('.')


def replace_once(path, old, new, label):
    text = path.read_text(encoding='utf-8')
    if new in text:
        return
    if old not in text:
        raise SystemExit(f'V34.152 anchor missing: {label} in {path}')
    path.write_text(text.replace(old, new, 1), encoding='utf-8')


def append_once(path, marker, block):
    text = path.read_text(encoding='utf-8')
    if marker not in text:
        path.write_text(text + block, encoding='utf-8')


rfq = ROOT / 'rfq.html'
site_js = ROOT / 'assets/site.js'
polish_css = ROOT / 'assets/polish.css'
polish_js = ROOT / 'assets/polish.js'
api = ROOT / 'api/rfq.js'
test = ROOT / 'scripts/test-rfq.js'

# 1) Insert the controlled review inputs before the existing readiness / review widgets.
anchor = '<div class="field full"><div class="rfq-readiness" id="rfqReadiness">'
workflow_markup = r'''<div class="field full"><section class="v34-152-review" id="technicalReviewControl" aria-labelledby="technicalReviewTitle">
<div class="v34-152-review-head"><div><span>RFQ → TECHNICAL REVIEW → QUALIFIED OFFER</span><h3 id="technicalReviewTitle">Make every commercial promise traceable to a review gate.</h3></div><p>Assumptions, deviations, alternative-route authority and evidence responsibility stay visible until release. A price is not permission to silently change the technical basis.</p></div>
<div class="v34-152-review-flow" aria-label="Technical review plan"><div data-review-step="verify"><small>01 · VERIFY</small><b>Requirement identity</b><p>Grade · standard · form · size · condition · service.</p><span>Owner · Tongjun technical desk</span></div><div data-review-step="qualify"><small>02 · QUALIFY</small><b>Source route</b><p>Manufacturability · origin · approved source · evidence route.</p><span>Owner · Tongjun + source</span></div><div data-review-step="align"><small>03 · ALIGN</small><b>Authority + deviations</b><p>Deviation register · alternates · certificate / inspection ownership.</p><span>Owner · buyer + Tongjun</span></div><div data-review-step="offer"><small>04 · OFFER</small><b>Qualified basis</b><p>Only released assumptions become the commercial offer basis.</p><span>Owner · commercial release</span></div></div>
<div class="v34-152-control-grid">
<div class="v34-152-control"><span>QUOTE ASSUMPTIONS</span><label for="quoteAssumptions">Commercial / technical assumptions carried into the quotation</label><textarea id="quoteAssumptions" name="quote_assumptions" placeholder="e.g. ASTM B443 latest agreed edition; solution annealed; CIF Hamburg; quoted lead time starts after technical release; final mill route subject to qualification."></textarea><p>No assumption is silently converted into a guarantee.</p></div>
<div class="v34-152-control"><span>ALTERNATE ROUTE AUTHORITY</span><label for="alternateRoutePermission">May Tongjun present an alternative route?</label><select id="alternateRoutePermission" name="alternate_route_permission"><option value="">Select authority</option><option value="no-alternates">No alternates — quote only the stated basis</option><option value="ask-before-quoting">Ask before any alternate is quoted</option><option value="separate-alternate">Alternate may be shown separately, never substituted</option></select><p>Any alternate remains a separate line item / route until the buyer accepts it.</p></div>
<div class="v34-152-control"><span>CERTIFICATE RESPONSIBILITY</span><label for="certificateResponsibility">Who owns certificate definition / provision?</label><select id="certificateResponsibility" name="certificate_responsibility"><option value="">Assign responsibility</option><option value="buyer-specifies-source-provides">Buyer specifies · source provides</option><option value="tongjun-coordinates-source-provides">Tongjun coordinates · source provides</option><option value="buyer-project-approval">Buyer / project authority controls acceptance</option><option value="to-be-agreed">To be agreed before offer release</option></select></div>
<div class="v34-152-control"><span>INSPECTION RESPONSIBILITY</span><label for="inspectionResponsibility">Who defines / witnesses inspection?</label><select id="inspectionResponsibility" name="inspection_responsibility"><option value="">Assign responsibility</option><option value="source-standard-inspection">Source performs standard inspection</option><option value="buyer-defined-inspection">Buyer defines additional inspection</option><option value="third-party-witness">Named third party witnesses / verifies</option><option value="tongjun-coordinates">Tongjun coordinates the agreed inspection plan</option><option value="to-be-agreed">To be agreed before offer release</option></select></div>
</div>
<div class="v34-152-deviation"><div class="v34-152-deviation-head"><div><span>DEVIATION REGISTER</span><b>Nothing disappears into quotation fine print.</b></div><select id="deviationStatus" name="deviation_status" aria-label="Deviation register status"><option value="">Select deviation state</option><option value="none">No known deviation at this review</option><option value="open">Open deviation(s)</option><option value="buyer-decision">Buyer decision required</option><option value="accepted">Deviation(s) accepted for quotation basis</option><option value="rejected">Deviation(s) rejected — stated basis retained</option></select></div><label for="deviationRegister">Requirement → proposed deviation → technical / commercial impact → evidence → disposition</label><textarea id="deviationRegister" name="deviation_register" placeholder="DEV-01 | Requirement: ... | Proposed: ... | Impact: ... | Evidence: ... | Disposition / owner: ..."></textarea></div>
<div class="v34-152-release" id="releaseChecklist"><div class="v34-152-release-head"><div><span>RELEASE CHECKLIST</span><b id="qualifiedOfferState">NOT RELEASED</b></div><p id="qualifiedOfferReason">Technical review controls are still open.</p></div><div class="v34-152-release-grid"><div data-release-gate="technical"><small>01</small><b>Technical basis</b><span>OPEN</span></div><div data-release-gate="assumptions"><small>02</small><b>Assumptions visible</b><span>OPEN</span></div><div data-release-gate="deviations"><small>03</small><b>Deviation state</b><span>OPEN</span></div><div data-release-gate="alternate"><small>04</small><b>Alternate authority</b><span>OPEN</span></div><div data-release-gate="evidence"><small>05</small><b>Evidence ownership</b><span>OPEN</span></div><div data-release-gate="logistics"><small>06</small><b>Logistics basis</b><span>OPEN</span></div></div><div class="v34-152-release-rule"><b>Release rule</b><span>Qualified Offer means the offer basis is explicit and reviewable. It does not claim final mill capability, project approval or inspection acceptance before evidence exists.</span></div></div>
<input type="hidden" name="release_status" value="NOT RELEASED"/><input type="hidden" name="release_checklist"/><input type="hidden" name="technical_review_plan" value="VERIFY requirement identity → QUALIFY source/evidence route → ALIGN deviations/alternate authority/responsibility → OFFER on explicit release basis"/>
</section></div>'''
replace_once(rfq, anchor, workflow_markup + anchor, 'RFQ technical review control insertion')

# 2) Include the V34.152 fields in URL prefill where it is useful / safe.
old_prefill = "'incoterm','destination','delivery_target','packing','notes'];"
new_prefill = "'incoterm','destination','delivery_target','packing','quote_assumptions','alternate_route_permission','certificate_responsibility','inspection_responsibility','deviation_status','deviation_register','notes'];"
replace_once(site_js, old_prefill, new_prefill, 'site.js RFQ prefill fields')

# 3) Keep the structured email / copied RFQ aligned with the server payload.
old_body = "        `Qualified Offer Reference: ${f.get('offer_ref')||''}`,\n        `Incoterm: ${f.get('incoterm')||''}`,"
new_body = "        `Qualified Offer Reference: ${f.get('offer_ref')||''}`,\n        `Quote Assumptions: ${f.get('quote_assumptions')||''}`,\n        `Deviation Status: ${f.get('deviation_status')||''}`,\n        `Deviation Register: ${f.get('deviation_register')||''}`,\n        `Alternate Route Permission: ${f.get('alternate_route_permission')||''}`,\n        `Certificate Responsibility: ${f.get('certificate_responsibility')||''}`,\n        `Inspection Responsibility: ${f.get('inspection_responsibility')||''}`,\n        `Release Status: ${f.get('release_status')||''}`,\n        `Release Checklist: ${f.get('release_checklist')||''}`,\n        `Technical Review Plan: ${f.get('technical_review_plan')||''}`,\n        `Incoterm: ${f.get('incoterm')||''}`,"
replace_once(site_js, old_body, new_body, 'site.js structured RFQ workflow fields')

# 4) API allow-list: persist only bounded, explicit workflow fields.
old_limits = "  notes:3500, source:300, product:180, utm_source:180, utm_medium:180,"
new_limits = "  quote_assumptions:2500, deviation_status:80, deviation_register:3500, alternate_route_permission:120,\n  certificate_responsibility:180, inspection_responsibility:180, release_status:120, release_checklist:2500, technical_review_plan:2500,\n  notes:3500, source:300, product:180, utm_source:180, utm_medium:180,"
replace_once(api, old_limits, new_limits, 'api/rfq.js V34.152 allow-list')

# 5) Extend the existing RFQ transport test so new controls cannot silently disappear.
old_fixture = "      approval:'Project AVL',incoterm:'CIF',destination:'Hamburg, Germany',delivery_target:'2026-11-15',packing:'Export seaworthy',offer_ref:'OF-20260907-ABC123'"
new_fixture = "      approval:'Project AVL',incoterm:'CIF',destination:'Hamburg, Germany',delivery_target:'2026-11-15',packing:'Export seaworthy',offer_ref:'OF-20260907-ABC123',\n      quote_assumptions:'Lead time starts after technical release',deviation_status:'buyer-decision',deviation_register:'DEV-01 | width tolerance | buyer decision',\n      alternate_route_permission:'separate-alternate',certificate_responsibility:'buyer-specifies-source-provides',inspection_responsibility:'third-party-witness',\n      release_status:'QUALIFIED WITH CONDITIONS',release_checklist:'technical=READY | deviations=CONDITIONAL',technical_review_plan:'VERIFY > QUALIFY > ALIGN > OFFER'"
replace_once(test, old_fixture, new_fixture, 'scripts/test-rfq.js workflow fixture')
old_assert = "  assert.equal(sent.offer_ref,'OF-20260907-ABC123');"
new_assert = "  assert.equal(sent.offer_ref,'OF-20260907-ABC123');\n  assert.equal(sent.quote_assumptions,'Lead time starts after technical release');\n  assert.equal(sent.deviation_status,'buyer-decision');\n  assert.match(sent.deviation_register,/DEV-01/);\n  assert.equal(sent.alternate_route_permission,'separate-alternate');\n  assert.equal(sent.certificate_responsibility,'buyer-specifies-source-provides');\n  assert.equal(sent.inspection_responsibility,'third-party-witness');\n  assert.equal(sent.release_status,'QUALIFIED WITH CONDITIONS');\n  assert.match(sent.release_checklist,/technical=READY/);\n  assert.equal(sent.technical_review_plan,'VERIFY > QUALIFY > ALIGN > OFFER');"
replace_once(test, old_assert, new_assert, 'scripts/test-rfq.js workflow assertions')

CSS = r'''

/* V34.152 STAGING — RFQ → Technical Review → Qualified Offer controls */
body.brand-v34 .v34-152-review{margin:8px 0 22px;border:1px solid #b9c7cf;background:#f8fafb;color:#142936}
body.brand-v34 .v34-152-review-head{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(280px,.95fr);gap:28px;padding:24px 24px 20px;border-bottom:1px solid #ccd6dc;background:#eef3f6}
body.brand-v34 .v34-152-review-head span,body.brand-v34 .v34-152-control>span,body.brand-v34 .v34-152-deviation-head span,body.brand-v34 .v34-152-release-head span{font-family:var(--tj-font-mono);font-size:10px;letter-spacing:.095em;color:#8d4c1e}
body.brand-v34 .v34-152-review-head h3{margin:7px 0 0;font-family:var(--tj-font-display);font-size:26px;line-height:1.08;letter-spacing:-.02em;color:#102838}
body.brand-v34 .v34-152-review-head p{margin:0;color:#5a6d79;line-height:1.55}
body.brand-v34 .v34-152-review-flow{display:grid;grid-template-columns:repeat(4,1fr);border-bottom:1px solid #ccd6dc;background:#102836;color:#e9f1f5}
body.brand-v34 .v34-152-review-flow>div{min-height:164px;padding:20px 18px;border-right:1px solid rgba(255,255,255,.13);display:flex;flex-direction:column}
body.brand-v34 .v34-152-review-flow>div:last-child{border-right:0}
body.brand-v34 .v34-152-review-flow small{font-family:var(--tj-font-mono);font-size:10px;letter-spacing:.08em;color:#83aac1}
body.brand-v34 .v34-152-review-flow b{margin:10px 0 7px;color:#fff;font-family:var(--tj-font-display);font-size:17px}
body.brand-v34 .v34-152-review-flow p{margin:0;color:#bdcbd3;font-size:12px;line-height:1.5}
body.brand-v34 .v34-152-review-flow span{margin-top:auto;padding-top:16px;color:#eea15d;font-size:10px;letter-spacing:.035em}
body.brand-v34 .v34-152-control-grid{display:grid;grid-template-columns:1fr 1fr}
body.brand-v34 .v34-152-control{padding:20px 22px;border-right:1px solid #d5dde2;border-bottom:1px solid #d5dde2}
body.brand-v34 .v34-152-control:nth-child(2n){border-right:0}
body.brand-v34 .v34-152-control label,body.brand-v34 .v34-152-deviation>label{display:block;margin:9px 0 7px;font-weight:700;color:#273e4c}
body.brand-v34 .v34-152-control p{margin:8px 0 0;color:#73818a;font-size:11px}
body.brand-v34 .v34-152-control textarea,body.brand-v34 .v34-152-control select,body.brand-v34 .v34-152-deviation textarea,body.brand-v34 .v34-152-deviation select{width:100%;box-sizing:border-box;border:1px solid #b8c5cd;background:#fff;color:#172b37;padding:11px 12px;border-radius:2px;font:inherit}
body.brand-v34 .v34-152-control textarea,body.brand-v34 .v34-152-deviation textarea{min-height:92px;resize:vertical}
body.brand-v34 .v34-152-deviation{padding:22px;border-bottom:1px solid #cbd5db;background:#fff}
body.brand-v34 .v34-152-deviation-head{display:grid;grid-template-columns:1fr minmax(240px,.72fr);gap:20px;align-items:end}
body.brand-v34 .v34-152-deviation-head b{display:block;margin-top:7px;font-size:16px;color:#17313f}
body.brand-v34 .v34-152-release{background:#0d2230;color:#eef5f8}
body.brand-v34 .v34-152-release-head{display:grid;grid-template-columns:auto 1fr;gap:20px;align-items:end;padding:22px}
body.brand-v34 .v34-152-release-head b{display:block;margin-top:7px;font-family:var(--tj-font-display);font-size:22px;color:#fff}
body.brand-v34 .v34-152-release-head p{margin:0;text-align:right;color:#b8c8d1}
body.brand-v34 .v34-152-release-grid{display:grid;grid-template-columns:repeat(6,1fr);border-top:1px solid rgba(255,255,255,.12);border-bottom:1px solid rgba(255,255,255,.12)}
body.brand-v34 .v34-152-release-grid>div{padding:16px 12px;border-right:1px solid rgba(255,255,255,.12);min-height:92px}
body.brand-v34 .v34-152-release-grid>div:last-child{border-right:0}
body.brand-v34 .v34-152-release-grid small{font-family:var(--tj-font-mono);color:#7096ad}
body.brand-v34 .v34-152-release-grid b{display:block;margin:7px 0 13px;font-size:12px;color:#e9f1f5}
body.brand-v34 .v34-152-release-grid span{font-family:var(--tj-font-mono);font-size:9px;letter-spacing:.06em;color:#e4a064}
body.brand-v34 .v34-152-release-grid>div.is-ready span{color:#9bc9ad}
body.brand-v34 .v34-152-release-grid>div.is-conditional span{color:#efbc77}
body.brand-v34 .v34-152-release-rule{display:grid;grid-template-columns:120px 1fr;gap:18px;padding:18px 22px;color:#bccbd3;font-size:12px;line-height:1.55}
body.brand-v34 .v34-152-release-rule b{color:#eea15d;font-size:10px;letter-spacing:.08em;text-transform:uppercase}
@media(max-width:900px){body.brand-v34 .v34-152-review-head,body.brand-v34 .v34-152-deviation-head{grid-template-columns:1fr}body.brand-v34 .v34-152-review-flow{grid-template-columns:1fr 1fr}body.brand-v34 .v34-152-review-flow>div:nth-child(2){border-right:0}body.brand-v34 .v34-152-review-flow>div:nth-child(-n+2){border-bottom:1px solid rgba(255,255,255,.13)}body.brand-v34 .v34-152-release-grid{grid-template-columns:repeat(3,1fr)}body.brand-v34 .v34-152-release-grid>div:nth-child(3){border-right:0}body.brand-v34 .v34-152-release-grid>div:nth-child(-n+3){border-bottom:1px solid rgba(255,255,255,.12)}body.brand-v34 .v34-152-release-head{grid-template-columns:1fr}body.brand-v34 .v34-152-release-head p{text-align:left}}
@media(max-width:620px){body.brand-v34 .v34-152-review-head{padding:19px 16px}body.brand-v34 .v34-152-review-head h3{font-size:22px}body.brand-v34 .v34-152-review-flow,body.brand-v34 .v34-152-control-grid{grid-template-columns:1fr}body.brand-v34 .v34-152-review-flow>div{min-height:132px;border-right:0;border-bottom:1px solid rgba(255,255,255,.13)}body.brand-v34 .v34-152-control{border-right:0;padding:18px 16px}body.brand-v34 .v34-152-deviation{padding:18px 16px}body.brand-v34 .v34-152-release-grid{grid-template-columns:1fr 1fr}body.brand-v34 .v34-152-release-grid>div{border-bottom:1px solid rgba(255,255,255,.12)}body.brand-v34 .v34-152-release-grid>div:nth-child(odd){border-right:1px solid rgba(255,255,255,.12)}body.brand-v34 .v34-152-release-grid>div:nth-child(even){border-right:0}body.brand-v34 .v34-152-release-rule{grid-template-columns:1fr;gap:7px;padding:16px}}
'''
append_once(polish_css, 'V34.152 STAGING — RFQ → Technical Review → Qualified Offer controls', CSS)

JS = r'''

/* V34.152 STAGING — explicit offer-basis release logic */
(() => {
  'use strict';
  const d=document,b=d.body;if(!b||b.dataset.page!=='rfq')return;
  const form=d.getElementById('rfqForm'),box=d.getElementById('releaseChecklist');if(!form||!box)return;
  const val=name=>String(form.elements.namedItem(name)?.value||'').trim();
  const gate=(name,state)=>{const el=box.querySelector(`[data-release-gate="${name}"]`);if(!el)return;el.classList.remove('is-ready','is-open','is-conditional');el.classList.add(state==='READY'?'is-ready':state==='CONDITIONAL'?'is-conditional':'is-open');const s=el.querySelector('span');if(s)s.textContent=state};
  const update=()=>{
    const technical=Boolean(val('grade')&&val('size')&&val('qty')&&val('application')&&(val('standard')||val('form')));
    const assumptions=Boolean(val('quote_assumptions'));
    const devState=val('deviation_status'),devText=val('deviation_register');
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
    const checklist=[`technical=${technical?'READY':'OPEN'}`,`assumptions=${assumptions?'READY':'OPEN'}`,`deviations=${deviations?(devConditional?'CONDITIONAL':'READY'):'OPEN'}`,`alternate=${alternate?'READY':'OPEN'}`,`evidence_ownership=${evidence?'READY':'OPEN'}`,`logistics=${logistics?'READY':'OPEN'}`].join(' | ');
    const checklistEl=form.elements.namedItem('release_checklist');if(checklistEl)checklistEl.value=checklist;
  };
  ['input','change'].forEach(evt=>form.addEventListener(evt,update));update();
})();
'''
append_once(polish_js, 'V34.152 STAGING — explicit offer-basis release logic', JS)

print('V34.152 staging delta applied: RFQ review controls + release semantics + API persistence + tests.')
