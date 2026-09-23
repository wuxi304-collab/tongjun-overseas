(() => {
  'use strict';

  const PARAM_KEYS=['source','utm_source','utm_medium','utm_campaign','utm_content','ac','persona','wedge'];
  const SAFE_MAX=240;
  const safe=(v,max=SAFE_MAX)=>String(v||'').replace(/[\u0000-\u001f\u007f]/g,'').trim().slice(0,max);
  const getStore=(k)=>{ try{return sessionStorage.getItem(k)||''}catch{return ''} };
  const setStore=(k,v)=>{ try{sessionStorage.setItem(k,v)}catch{} };

  function captureAttribution(){
    const params=new URLSearchParams(location.search);
    PARAM_KEYS.forEach(k=>{
      const v=safe(params.get(k),240);
      if(v) setStore(`tj_${k}`,v);
    });
    if(!getStore('tj_first_landing')) setStore('tj_first_landing',safe(location.pathname,300));
    if(!getStore('tj_first_seen')) setStore('tj_first_seen',new Date().toISOString());
    if(!getStore('tj_first_referrer')){
      let ref='direct';
      try{ if(document.referrer){ const u=new URL(document.referrer); ref=safe(u.hostname,180)||'direct'; } }catch{}
      setStore('tj_first_referrer',ref);
    }
    return params;
  }

  function inferWedge(path){
    if(/precision-strip|precision-stainless/.test(path)) return 'precision-strip';
    if(/invar-aerospace|invar-36/.test(path)) return 'invar-tooling';
    if(/invar-lng/.test(path)) return 'invar-lng';
    if(/nickel-process|alloy-625|alloy-c276|alloy-825|nickel-alloys/.test(path)) return 'nickel-process';
    if(/heavy-plate|extra-wide|super-duplex/.test(path)) return 'heavy-plate';
    if(/titanium/.test(path)) return 'titanium';
    return '';
  }

  function applyCampaignContext(params){
    const persona=safe(params.get('persona')||getStore('tj_persona'),120).toLowerCase();
    const wedge=safe(params.get('wedge')||getStore('tj_wedge')||inferWedge(location.pathname),180).toLowerCase();
    const ac=safe(params.get('ac')||getStore('tj_ac'),80);
    if(!persona && !ac) return;

    const personaMap={
      procurement:['Procurement view','MOQ, lead time, origin, price basis and backup route are separated before commercial commitment.'],
      engineering:['Engineering view','Material identity, manufacturable size, condition and application evidence are checked as separate questions.'],
      quality:['Quality view','Heat traceability, MTC, inspection scope and approval boundary are defined before scale-up.'],
      management:['Management view','The route is framed around supply risk, qualification friction, lead time and continuity rather than a single quoted source.']
    };
    const wedgeMap={
      'precision-strip':'Precision strip: thickness tolerance, temper, edge, surface, coil build and repeatability drive the sourcing route.',
      'invar-tooling':'Invar tooling: CTE, stress relief, plate condition, flatness and machining stability must be qualified together.',
      'invar-lng':'LNG Invar: product form, dimensional control, continuous length and project qualification are treated as a dedicated route.',
      'nickel-process':'Nickel process alloys: grade, product form, corrosion service, code basis and inspection requirements must align.',
      'heavy-plate':'Heavy plate: grade capability is not enough; width, thickness, heat treatment, UT and fabrication route define feasibility.',
      'titanium':'Titanium / zirconium: corrosion service, product form, cleanliness, code basis and traceability determine the source path.'
    };
    const p=personaMap[persona]||['Buyer view','We separate what is confirmed from what still requires mill, stock or qualification evidence.'];
    const w=wedgeMap[wedge]||'Special metals: application, product form, dimensions and qualification determine the commercial route.';

    const target=document.querySelector('.pagehero, .hero');
    if(!target || document.querySelector('.campaign-context')) return;
    const section=document.createElement('section');
    section.className='campaign-context';
    section.setAttribute('aria-label','Campaign context');
    section.innerHTML=`<div class="wrap campaign-in"><span class="campaign-label">${escapeHtml(p[0])}</span><span class="campaign-copy"><b>${escapeHtml(w)}</b> ${escapeHtml(p[1])}</span><a class="campaign-action" href="/rfq">Turn this into an RFQ →</a></div>`;
    target.insertAdjacentElement('afterend',section);
  }


  function makeRouteRef(prefix){
    const day=new Date().toISOString().slice(0,10).replace(/-/g,'');
    let token='';
    try{
      const bytes=new Uint8Array(3); crypto.getRandomValues(bytes); token=[...bytes].map(b=>b.toString(16).padStart(2,'0')).join('').toUpperCase();
    }catch{ token=Math.random().toString(16).slice(2,8).toUpperCase().padEnd(6,'0'); }
    return `${prefix}-${day}-${token}`;
  }

  function ensureHidden(form,name,value){
    let el=form.elements[name];
    if(!el){ el=document.createElement('input'); el.type='hidden'; el.name=name; form.appendChild(el); }
    if(value && !el.value) el.value=value;
    return el;
  }

  function bindRouteBuilder(params){
    const routeForm=document.querySelector('#routeForm');
    const routeResult=document.querySelector('#routeResult');
    if(!routeForm||!routeResult) return;
    routeForm.addEventListener('submit',e=>{
      e.preventDefault();
      const f=new FormData(routeForm);
      const family=f.get('family');
      const qualification=f.get('qualification');
      const quantity=f.get('quantity');
      const delivery=f.get('delivery');
      let primary='Chinese manufacturing route';
      let backup='International-origin qualification route';
      let evidence='Current mill capability, MTC sample, dimensions, condition and inspection plan.';
      if(qualification==='named' || qualification==='critical'){
        primary='International-origin / approved-mill route';
        backup='Chinese alternative route for later qualification';
        evidence='Approved mill/origin requirement, applicable standard, MTC, inspection and customer approval path.';
      }
      if(quantity==='sample' || delivery==='urgent'){
        primary='Stock & processing route';
        backup=qualification==='named'?'International-origin stock route':'Chinese production route for scale-up';
        evidence='Heat-number traceability, stock status, processing route, MTC and actual dispatch lead time.';
      }
      if(delivery==='development' && qualification==='open'){
        primary='Chinese non-standard development route';
        backup='Stock route for trial material';
        evidence='Feasibility review, trial lot, dimensional/quality validation and commercial scale-up plan.';
      }
      const familyName={precision:'Precision strip / foil',nickel:'Nickel / corrosion alloy',invar:'Invar / low expansion',heavy:'Heavy / extra-wide plate',titanium:'Titanium / zirconium'}[family]||family;
      const q=new URLSearchParams();
      q.set('source','supply-route'); if(family) q.set('product',family);
      ['utm_source','utm_medium','utm_campaign','utm_content','ac','persona','wedge'].forEach(k=>{const v=params.get(k)||getStore(`tj_${k}`);if(v)q.set(k,v)});
      const routeRef=makeRouteRef('SR');
      const routeBrief=`Supply-route screen ${routeRef}: ${primary}. Product family: ${familyName}. Backup: ${backup}. Evidence first: ${evidence}`;
      setStore('tj_route_ref',routeRef);
      setStore('tj_route_brief',safe(routeBrief,1800));
      routeResult.innerHTML=`<div class="eyebrow">Recommended starting route</div><div class="screen-ref">Screen reference · ${escapeHtml(routeRef)}</div><h2>${escapeHtml(primary)}</h2><div class="route-output"><b>Product family</b><span>${escapeHtml(familyName)}</span></div><div class="route-output"><b>Qualification backup</b><span>${escapeHtml(backup)}</span></div><div class="route-output"><b>Evidence to request first</b><span>${escapeHtml(evidence)}</span></div><a class="cta" href="/rfq?${q.toString()}">Turn this into an RFQ ↗</a>`;
    });
  }

  function bindProblemOrder(params){
    const form=document.querySelector('#problemOrderForm');
    const result=document.querySelector('#problemOrderResult');
    if(!form||!result) return;
    const familyNames={precision:'Precision strip / foil',nickel:'Nickel / corrosion alloy',invar:'Invar / low expansion',heavy:'Heavy / extra-wide plate',titanium:'Titanium / zirconium',other:'Other special metal'};
    form.addEventListener('submit',e=>{
      e.preventDefault(); if(!form.reportValidity()) return;
      const f=new FormData(form);
      const family=safe(f.get('family'),80), constraint=safe(f.get('constraint'),80), qualification=safe(f.get('qualification'),80), quantity=safe(f.get('quantity'),80), delivery=safe(f.get('delivery'),80), origin=safe(f.get('origin'),80), details=safe(f.get('details'),1600);
      let primary='Dual-source feasibility screen';
      let feasibility='Confirm grade + form + actual dimension against current manufacturing and processing capability.';
      let qualificationGate='Confirm buyer approval boundary before naming a commercial source.';
      let evidence='Current MTC sample, heat traceability and dimension/condition capability evidence.';
      let commercial='Compare a scalable route with a backup route before price commitment.';
      let risk='Do not convert a grade match into a supply claim until dimensional capability and qualification are both evidenced.';

      if(constraint==='dimension'){
        primary=(delivery==='development' && qualification==='open')?'Non-standard development route':'Dimension-first feasibility route';
        feasibility='Verify actual thickness/width/length or section envelope, condition, tolerance and process route — not just grade capability.';
        commercial=delivery==='development'?'Define a trial lot and scale-up path before commercial volume.':'Check stock/process bridge versus new mill production and state the lead-time tradeoff.';
      } else if(constraint==='moq'){
        primary='Small-lot stock & processing route';
        commercial='Use heat-traceable stock or service-center processing for the trial; define the production route separately for scale-up.';
        evidence='Heat number, original MTC, stock identity, processing record and actual dispatch quantity.';
      } else if(constraint==='urgent' || delivery==='urgent'){
        primary='Urgent stock / bridge-supply route';
        commercial='Separate immediate bridge supply from the longer-term production source so urgency does not silently change origin or qualification.';
        evidence='Actual stock status, heat identity, MTC, processing route and dispatch lead time.';
      } else if(constraint==='origin' || origin==='named' || qualification==='named'){
        primary='Approved-origin / named-mill route';
        qualificationGate='Lock the named mill, country-of-origin or approved-list rule before screening stock or alternative production.';
        evidence='Approved-source requirement, original MTC, origin evidence, processing traceability and any required customer approval.';
        risk='A China-side stockholder or processor does not change the original mill/origin. Keep origin and processing responsibility explicit.';
      } else if(constraint==='qualification' || qualification==='critical'){
        primary='Qualification-first route';
        qualificationGate='Define the project/customer approval path, test evidence and trial acceptance criteria before commercial scale-up.';
        evidence='Applicable standard, customer specification, MTC, inspection/test plan, trial-lot evidence and approval record where required.';
        risk='Technical manufacturability does not equal end-use approval. Treat qualification as a separate gate.';
      } else if(constraint==='docs'){
        primary='Evidence-first source validation';
        evidence='Start with original MTC, heat traceability, source identity, inspection scope and any PMI/UT/third-party requirement before price comparison.';
        risk='Reject any route that cannot preserve traceability from original material through secondary processing.';
      } else if(constraint==='processing'){
        primary='Stock + controlled processing route';
        feasibility='Confirm incoming material identity first, then processing envelope, tolerance, edge/surface requirement and yield risk.';
        evidence='Original MTC + processor work record + final dimensional/inspection result tied to the same heat/lot.';
      }
      if(quantity==='sample' && !['qualification','origin'].includes(constraint)) commercial='Prefer a traceable small-lot or stock route for the trial, with a separate production route defined before scale-up.';
      if(origin==='china' && qualification==='open' && delivery==='development') commercial='A Chinese non-standard development route can be screened in parallel with a stock route for trial material.';

      const familyName=familyNames[family]||family;
      const problemRef=makeRouteRef('PS');
      const brief=[`Problem-order screen ${problemRef}: ${primary}.`,`Family: ${familyName}.`,`Main constraint: ${constraint}.`,`Feasibility gate: ${feasibility}`,`Qualification gate: ${qualificationGate}`,`Evidence first: ${evidence}`,`Commercial route: ${commercial}`,`Risk boundary: ${risk}`,details?`Buyer context: ${details}`:''].filter(Boolean).join(' ');
      setStore('tj_problem_ref',problemRef);
      setStore('tj_problem_brief',safe(brief,3400));
      setStore('tj_problem_family',family);
      const q=new URLSearchParams(); q.set('source','problem-order'); if(family) q.set('product',family);
      ['utm_source','utm_medium','utm_campaign','utm_content','ac','persona','wedge'].forEach(k=>{const v=params.get(k)||getStore(`tj_${k}`);if(v)q.set(k,v)});
      result.innerHTML=`<div class="eyebrow">Recommended starting route</div><div class="screen-ref">Screen reference · ${escapeHtml(problemRef)}</div><h2>${escapeHtml(primary)}</h2><div class="problem-gates"><div class="problem-gate"><small>Feasibility gate</small><span>${escapeHtml(feasibility)}</span></div><div class="problem-gate"><small>Qualification gate</small><span>${escapeHtml(qualificationGate)}</span></div><div class="problem-gate"><small>Evidence first</small><span>${escapeHtml(evidence)}</span></div><div class="problem-gate"><small>Commercial action</small><span>${escapeHtml(commercial)}</span></div></div><div class="risk-line"><b>Boundary:</b> ${escapeHtml(risk)}</div><div class="problem-actions"><a class="cta" href="/rfq?${q.toString()}">Convert to technical RFQ ↗</a><button class="btn-secondary" id="copyProblemBrief" type="button">Copy route brief</button></div>`;
      const copy=result.querySelector('#copyProblemBrief');
      if(copy) copy.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(brief);showToast('Route brief copied.')}catch{showToast('Copy is unavailable in this browser.')}});
    });
  }

  function bindRfq(form,params){
    PARAM_KEYS.forEach(k=>{
      const v=safe(params.get(k)||getStore(`tj_${k}`),240);
      ensureHidden(form,k,v);
    });
    ensureHidden(form,'first_landing',getStore('tj_first_landing'));
    ensureHidden(form,'first_referrer',getStore('tj_first_referrer'));
    ensureHidden(form,'first_seen',getStore('tj_first_seen'));
    const routeRef=(sourceHint=>sourceHint==='problem-order'?getStore('tj_problem_ref'):sourceHint==='supply-route'?getStore('tj_route_ref'):(getStore('tj_problem_ref')||getStore('tj_route_ref')))(safe(params.get('source')||getStore('tj_source'),120));
    ensureHidden(form,'route_ref',routeRef);
    if(form.elements.product && params.get('product')) form.elements.product.value=safe(params.get('product'),180);
    const prefillKeys=['country','grade','standard','form','size','condition','qty','application','certificate','origin','approval','procurement_stage','buyer_gate','incoterm','destination','delivery_target','packing','quote_assumptions','alternate_route_permission','certificate_responsibility','inspection_responsibility','deviation_status','deviation_register','notes'];
    prefillKeys.forEach(k=>{ const v=safe(params.get(k),k==='application'||k==='notes'?2500:300); if(v && form.elements[k] && !form.elements[k].value) form.elements[k].value=v; });
    const source=safe(params.get('source')||getStore('tj_source'),120);
    if(form.elements.notes && !form.elements.notes.value){
      if(source==='problem-order' && getStore('tj_problem_brief')) form.elements.notes.value=getStore('tj_problem_brief');
      else if(source==='supply-route' && getStore('tj_route_brief')) form.elements.notes.value=getStore('tj_route_brief');
    }

    const readiness=document.querySelector('#rfqReadiness');
    const readinessScore=document.querySelector('#readinessScore');
    const readinessBar=document.querySelector('#readinessBar');
    const readinessMissing=document.querySelector('#readinessMissing');
    const readinessFields=[['grade','Grade / UNS'],['standard','Standard'],['form','Product form'],['size','Size'],['condition','Condition'],['qty','Quantity'],['application','Application'],['certificate','Certificate / inspection']];
    const updateReadiness=()=>{
      if(!readiness) return;
      const missing=readinessFields.filter(([k])=>!safe(form.elements[k]?.value,400)).map(([,label])=>label);
      const done=readinessFields.length-missing.length; const pct=Math.round(done/readinessFields.length*100);
      if(readinessScore) readinessScore.textContent=`${done}/8 · ${pct}%`;
      if(readinessBar) readinessBar.style.width=`${pct}%`;
      if(readinessMissing) readinessMissing.textContent=missing.length?`Still useful to add: ${missing.join(' · ')}.`:'Eight-field technical core is complete. Origin / approved-mill restrictions can still be added where applicable.';
      readiness.classList.toggle('ready',missing.length===0);
    };

    const evidenceBox=document.querySelector('#evidencePreview');
    const evidenceList=document.querySelector('#evidenceList');
    const buildEvidencePackage=()=>{
      const formName=safe(form.elements.form?.value,180).toLowerCase();
      const certificate=safe(form.elements.certificate?.value,300);
      const origin=safe(form.elements.origin?.value,300);
      const approval=safe(form.elements.approval?.value,300);
      const procurementStage=safe(form.elements.procurement_stage?.value,120);
      const buyerGate=safe(form.elements.buyer_gate?.value,120);
      const incoterm=safe(form.elements.incoterm?.value,80);
      const destination=safe(form.elements.destination?.value,240);
      const deliveryTarget=safe(form.elements.delivery_target?.value,80);
      const packing=safe(form.elements.packing?.value,500);
      const standard=safe(form.elements.standard?.value,180);
      const condition=safe(form.elements.condition?.value,240);
      const items=[];
      items.push(`CORE · Material identity${standard?` + governing standard (${standard})`:' + governing product standard'}`);
      items.push('CORE · Heat / lot traceability + certified source documentation');
      items.push('CORE · Delivery identity: labels / piece or coil marking linked to the source record');
      if(condition) items.push(`CONDITIONAL · Condition / heat-treatment verification (${condition})`);
      if(formName.includes('strip')||formName.includes('foil')) items.push('CONDITIONAL · Mother material → slitting / edge → finished coil processing traceability');
      else if(formName.includes('plate')) items.push('CONDITIONAL · Plate identity + dimensional verification; UT / PMI only where specified');
      else if(formName.includes('bar')||formName.includes('forging')) items.push('CONDITIONAL · Long-product / forging route + heat-treatment and NDT records where specified');
      else if(formName.includes('tube')) items.push('CONDITIONAL · Tube / pipe route + dimensional, weld and NDE requirements where applicable');
      else if(formName.includes('titanium')||formName.includes('zirconium')) items.push('CONDITIONAL · Reactive-metal identity + source / processing contamination-control boundary as applicable');
      else items.push('CONDITIONAL · Processing traceability for any secondary operation');
      if(certificate) items.push(`PO-DRIVEN · Requested certificate / inspection scope: ${certificate}`);
      else items.push('PO-DRIVEN · Inspection scope to be defined by PO / project requirement');
      if(origin) items.push(`BUYER-CONTROLLED · Origin / approved-mill control: ${origin}`);
      if(approval) items.push(`BUYER-CONTROLLED · Customer / project approval: ${approval}`);
      if(procurementStage==='trial') items.push('PO-DRIVEN · Trial-lot acceptance criteria + scale-up release condition');
      if(procurementStage==='repeat') items.push('BUYER-CONTROLLED · Change-control check against the previously accepted source / process route');
      if(procurementStage==='urgent') items.push('CONDITIONAL · Urgent bridge route: stock custody + processing + actual dispatch evidence');
      if(procurementStage==='tender') items.push('BUYER-CONTROLLED · Tender / project qualification status and named-source restrictions');
      if(buyerGate==='approval') items.push('BUYER-CONTROLLED · Explicit AVL / OEM / project approval gate before commercial release');
      if(incoterm||destination||deliveryTarget) items.push(`COMMERCIAL-BASIS · Logistics basis: ${[incoterm,destination,deliveryTarget].filter(Boolean).join(' · ')}`);
      if(packing) items.push(`COMMERCIAL-BASIS · Packing / handling: ${packing}`);
      const unique=[...new Set(items)];
      return unique;
    };
    const updateEvidence=()=>{
      if(!evidenceBox||!evidenceList) return;
      const items=buildEvidencePackage();
      evidenceList.innerHTML=items.map(x=>{
        const [rawTag,...rest]=x.split(' · '); const text=rest.join(' · ')||x;
        const cls=rawTag.toLowerCase().replace(/[^a-z]+/g,'-').replace(/^-|-$/g,'');
        return `<li><span class="evidence-tag ${escapeHtml(cls)}">${escapeHtml(rawTag)}</span>${escapeHtml(text)}</li>`;
      }).join('');
      evidenceBox.classList.toggle('specific',Boolean(safe(form.elements.standard?.value,180)||safe(form.elements.certificate?.value,300)||safe(form.elements.origin?.value,300)||safe(form.elements.approval?.value,300)||safe(form.elements.condition?.value,240)));
    };

    const buyerReview=document.querySelector('#buyerReview');
    const buyerReviewRef=document.querySelector('#buyerReviewRef');
    const performState=document.querySelector('#performState');
    const makeState=document.querySelector('#makeState');
    const acceptState=document.querySelector('#acceptState');
    const releaseState=document.querySelector('#releaseState');
    const buyerReviewFoot=document.querySelector('#buyerReviewFoot');
    const decisionRef=ensureHidden(form,'decision_ref',getStore('tj_decision_ref')||makeRouteRef('BR')).value;
    setStore('tj_decision_ref',decisionRef);
    const offerRef=ensureHidden(form,'offer_ref',getStore('tj_offer_ref')||makeRouteRef('OF')).value;
    setStore('tj_offer_ref',offerRef);
    if(buyerReviewRef) buyerReviewRef.textContent=`Review reference · ${decisionRef}`;

    const setGate=(name,state,text)=>{
      const gate=buyerReview?.querySelector(`[data-review-gate="${name}"]`);
      if(gate){gate.classList.remove('is-open','is-ready','is-controlled');gate.classList.add(state);}
      const target={perform:performState,make:makeState,accept:acceptState,release:releaseState}[name];
      if(target) target.textContent=text;
    };
    const updateBuyerReview=()=>{
      if(!buyerReview) return;
      const application=safe(form.elements.application?.value,2500);
      const grade=safe(form.elements.grade?.value,180);
      const standard=safe(form.elements.standard?.value,180);
      const productForm=safe(form.elements.form?.value,120);
      const size=safe(form.elements.size?.value,240);
      const condition=safe(form.elements.condition?.value,240);
      const certificate=safe(form.elements.certificate?.value,300);
      const origin=safe(form.elements.origin?.value,300);
      const approval=safe(form.elements.approval?.value,300);
      const buyerGate=safe(form.elements.buyer_gate?.value,120);
      const performReady=Boolean(grade&&application);
      const makeReady=Boolean(productForm&&size&&(standard||condition));
      const acceptSpecific=Boolean(certificate||origin||approval||buyerGate);
      setGate('perform',performReady?'is-ready':'is-open',performReady?'Service basis defined':'Needs application basis');
      setGate('make',makeReady?'is-ready':'is-open',makeReady?'Route inputs defined':'Needs form / standard');
      setGate('accept',acceptSpecific?'is-controlled':'is-open',acceptSpecific?'Acceptance boundary declared':'Needs evidence boundary');
      const releaseReady=performReady&&makeReady&&acceptSpecific;
      setGate('release',releaseReady?'is-ready':'is-open',releaseReady?'Ready for route review':'Not released');
      buyerReview.classList.toggle('ready',releaseReady);
      if(buyerReviewFoot){
        if(releaseReady) buyerReviewFoot.textContent='The RFQ is specific enough to screen a technical route. Final capability, source approval and commercial release still require evidence.';
        else {
          const open=[];
          if(!performReady) open.push('service / application basis');
          if(!makeReady) open.push('form + size + standard or condition');
          if(!acceptSpecific) open.push('evidence / origin / approval boundary');
          buyerReviewFoot.textContent=`Open before commercial release: ${open.join(' · ')}.`;
        }
      }
    };

    const offerReadiness=document.querySelector('#offerReadiness');
    const offerReadinessRef=document.querySelector('#offerReadinessRef');
    const offerReadinessFoot=document.querySelector('#offerReadinessFoot');
    const updateOfferReadiness=()=>{
      if(!offerReadiness) return;
      const grade=safe(form.elements.grade?.value,180);
      const standard=safe(form.elements.standard?.value,180);
      const formValue=safe(form.elements.form?.value,120);
      const size=safe(form.elements.size?.value,240);
      const qty=safe(form.elements.qty?.value,180);
      const application=safe(form.elements.application?.value,2500);
      const certificate=safe(form.elements.certificate?.value,300);
      const origin=safe(form.elements.origin?.value,300);
      const approval=safe(form.elements.approval?.value,300);
      const buyerGate=safe(form.elements.buyer_gate?.value,120);
      const incoterm=safe(form.elements.incoterm?.value,80);
      const destination=safe(form.elements.destination?.value,240);
      const deliveryTarget=safe(form.elements.delivery_target?.value,80);
      const packing=safe(form.elements.packing?.value,500);
      const technical=Boolean(grade&&size&&qty&&application&&(standard||formValue));
      const evidence=Boolean(certificate||origin||approval||buyerGate);
      const logistics=Boolean((incoterm&&destination)||deliveryTarget||packing);
      const offer=technical&&evidence&&logistics;
      const setOfferGate=(gate,cls,text,id)=>{
        const el=offerReadiness.querySelector(`[data-offer-gate="${gate}"]`);
        if(el){el.classList.remove('is-ready','is-open');el.classList.add(cls)}
        const state=document.querySelector(id); if(state) state.textContent=text;
      };
      setOfferGate('technical',technical?'is-ready':'is-open',technical?'Basis defined':'Open','#offerTechnicalState');
      setOfferGate('evidence',evidence?'is-ready':'is-open',evidence?'Boundary declared':'Open','#offerEvidenceState');
      setOfferGate('logistics',logistics?'is-ready':'is-open',logistics?'Basis declared':'Open','#offerLogisticsState');
      setOfferGate('commercial',offer?'is-ready':'is-open',offer?'Qualified basis':'Conditional','#offerCommercialState');
      if(offerReadinessRef) offerReadinessRef.textContent=`Offer ref · ${offerRef}`;
      if(offerReadinessFoot){
        const open=[];
        if(!technical) open.push('technical basis');
        if(!evidence) open.push('evidence / approval boundary');
        if(!logistics) open.push('logistics basis');
        offerReadinessFoot.textContent=offer? 'The request is specific enough to prepare a qualified commercial basis. Price, route availability and lead time remain time-bound confirmations.' : `Open before a clean offer: ${open.join(' · ')}. Any quotation should show these as conditions.`;
      }
    };

    const buildPayload=()=>{
      const f=new FormData(form);
      const subject=`RFQ | ${f.get('grade')||'Special Metal'} | ${f.get('size')||''}`;
      const body=[
        `Name: ${f.get('name')||''}`,
        `Company: ${f.get('company')||''}`,
        `Business Email: ${f.get('email')||''}`,
        `Country / Region: ${f.get('country')||''}`,
        `Material / Grade: ${f.get('grade')||''}`,
        `Standard: ${f.get('standard')||''}`,
        `Product Form: ${f.get('form')||''}`,
        `Size: ${f.get('size')||''}`,
        `Condition / Heat Treatment: ${f.get('condition')||''}`,
        `Quantity: ${f.get('qty')||''}`,
        `Application: ${f.get('application')||''}`,
        `Certificate / Inspection: ${f.get('certificate')||''}`,
        `Origin Preference / Mill Restriction: ${f.get('origin')||''}`,
        `Customer / Project Approval: ${f.get('approval')||''}`,
        `Procurement Stage: ${f.get('procurement_stage')||''}`,
        `Buyer Release Gate: ${f.get('buyer_gate')||''}`,
        `Decision Review Reference: ${f.get('decision_ref')||''}`,
        `Qualified Offer Reference: ${f.get('offer_ref')||''}`,
        `Quote Assumptions: ${f.get('quote_assumptions')||''}`,
        `Deviation Status: ${f.get('deviation_status')||''}`,
        `Deviation Register: ${f.get('deviation_register')||''}`,
        `Alternate Route Permission: ${f.get('alternate_route_permission')||''}`,
        `Certificate Responsibility: ${f.get('certificate_responsibility')||''}`,
        `Inspection Responsibility: ${f.get('inspection_responsibility')||''}`,
        `Release Status: ${f.get('release_status')||''}`,
        `Release Checklist: ${f.get('release_checklist')||''}`,
        `Technical Review Plan: ${f.get('technical_review_plan')||''}`,
        `Incoterm: ${f.get('incoterm')||''}`,
        `Named Destination / Port: ${f.get('destination')||''}`,
        `Required Delivery Date: ${f.get('delivery_target')||''}`,
        `Packing / Handling: ${f.get('packing')||''}`,
        `Notes / Delivery: ${f.get('notes')||''}`,
        `Route Screen Reference: ${f.get('route_ref')||''}`,
        `Evidence Package Planning: ${buildEvidencePackage().join(' | ')}`,
        '',
        `Attribution Code: ${f.get('ac')||''}`,
        `Persona: ${f.get('persona')||''}`,
        `Wedge: ${f.get('wedge')||''}`,
        `Landing Source: ${f.get('source')||''}`,
        `First Landing: ${f.get('first_landing')||''}`,
        `First Referrer: ${f.get('first_referrer')||''}`,
        `UTM Source: ${f.get('utm_source')||''}`,
        `UTM Medium: ${f.get('utm_medium')||''}`,
        `UTM Campaign: ${f.get('utm_campaign')||''}`,
        `UTM Content: ${f.get('utm_content')||''}`
      ].join('\n');
      return {subject,body};
    };

    const preview=document.querySelector('#rfqPreview');
    const updatePreview=()=>{
      if(!preview) return;
      const {subject,body}=buildPayload();
      preview.innerHTML=`<div class="eyebrow">Structured RFQ preview</div><strong>${escapeHtml(subject)}</strong><pre>${escapeHtml(body)}</pre>`;
    };
    form.addEventListener('input',()=>{updatePreview();updateReadiness();updateEvidence();updateBuyerReview();updateOfferReadiness();}); updatePreview(); updateReadiness(); updateEvidence(); updateBuyerReview(); updateOfferReadiness();

    form.addEventListener('submit',async e=>{
      e.preventDefault(); if(!form.reportValidity()) return;
      const fd=new FormData(form); const payload=Object.fromEntries(fd.entries());
      const {subject,body}=buildPayload(); payload.subject=subject; payload.structured_body=body; payload.evidence_package=buildEvidencePackage().join(' | ');
      const btn=form.querySelector('button[type="submit"]'); const original=btn?btn.textContent:'';
      if(btn){btn.disabled=true;btn.textContent='Submitting…'}
      try{
        const r=await fetch('/api/rfq',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
        let result={}; try{result=await r.json()}catch{}
        if(!r.ok) throw new Error(result.error||'rfq_route_unavailable');
        if(result.request_id) setStore('tj_rfq_id',safe(result.request_id,80));
        setStore('tj_last_rfq','accepted');
        showToast(result.request_id?`RFQ received · ${result.request_id}`:'RFQ received. Opening confirmation.');
        if(btn) btn.textContent='RFQ Submitted ✓';
        setTimeout(()=>{location.href='/thank-you';},650);
      }catch(err){
        if(btn){btn.disabled=false;btn.textContent=original}
        showToast('Secure routing is not active yet. Opening email fallback.');
        setTimeout(()=>{location.href=`mailto:wuxi304@outlook.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;},350);
      }
    });

    const copy=document.querySelector('#copyRfq');
    if(copy) copy.addEventListener('click',async()=>{
      if(!form.reportValidity()) return;
      const {subject,body}=buildPayload();
      try{await navigator.clipboard.writeText(`${subject}\n\n${body}`);showToast('Structured RFQ copied.')}catch{showToast('Copy is unavailable in this browser.')}
    });
  }


  function bindMegaNavigation(){
    const toggles=[...document.querySelectorAll('.navtoggle')];
    const items=[...document.querySelectorAll('.navitem.has-mega')];
    const closeAll=(except=null)=>items.forEach(item=>{if(item!==except){item.classList.remove('open');const b=item.querySelector('.navtoggle');if(b)b.setAttribute('aria-expanded','false')}});
    toggles.forEach(btn=>btn.addEventListener('click',e=>{
      e.stopPropagation(); const item=btn.closest('.navitem'); const next=!item.classList.contains('open'); closeAll(item); item.classList.toggle('open',next); btn.setAttribute('aria-expanded',String(next));
    }));
    document.addEventListener('click',()=>closeAll());
    document.addEventListener('keydown',e=>{if(e.key==='Escape')closeAll()});
    const ham=document.querySelector('.hamb'), mm=document.querySelector('.mobile-menu');
    if(ham&&mm){
      const setMobile=(open)=>{mm.classList.toggle('open',open);document.body.classList.toggle('nav-open',open);ham.setAttribute('aria-expanded',String(open));ham.setAttribute('aria-label',open?'Close menu':'Open menu')};
      ham.addEventListener('click',()=>setMobile(!mm.classList.contains('open')));
      mm.querySelectorAll('details').forEach(detail=>detail.addEventListener('toggle',()=>{if(!detail.open)return;mm.querySelectorAll('details[open]').forEach(other=>{if(other!==detail)other.open=false})}));
      mm.querySelectorAll('a').forEach(link=>link.addEventListener('click',()=>setMobile(false)));
      document.addEventListener('keydown',e=>{if(e.key==='Escape'&&mm.classList.contains('open')){setMobile(false);ham.focus()}});
      window.addEventListener('resize',()=>{if(window.innerWidth>860&&mm.classList.contains('open'))setMobile(false)});
    }
  }

  function bindAlloyFinder(){
    const input=document.querySelector('#alloySearch');
    const family=document.querySelector('#familyFilter');
    const tbody=document.querySelector('#alloyRows');
    if(!input||!family||!tbody)return;
    const rows=[...tbody.querySelectorAll('tr')];
    const count=document.querySelector('#alloyCount'), empty=document.querySelector('#alloyEmpty');
    const params=new URLSearchParams(location.search);
    if(params.get('q')) input.value=safe(params.get('q'),120);
    if([...family.options].some(o=>o.value===params.get('family'))) family.value=params.get('family');
    const run=()=>{
      const q=safe(input.value,120).toLowerCase(); const f=family.value; let n=0;
      rows.forEach(row=>{const show=(!q||row.dataset.search.includes(q))&&(f==='all'||row.dataset.family===f);row.hidden=!show;if(show)n++});
      if(count)count.textContent=String(n);if(empty)empty.hidden=n!==0;
    };
    input.addEventListener('input',run); family.addEventListener('change',run); run();
  }

  function bindQuickAlloy(){
    const form=document.querySelector('#quickAlloyForm'), input=document.querySelector('#quickAlloy');
    if(!form||!input)return;
    form.addEventListener('submit',e=>{e.preventDefault();const q=safe(input.value,120);location.href=q?`/alloys?q=${encodeURIComponent(q)}`:'/alloys'});
  }



  function bindMaterialCompare(){
    const shell=document.querySelector('[data-material-compare]'), dataNode=document.querySelector('#materialCompareData');
    if(!shell||!dataNode)return;
    let materials=[];try{materials=JSON.parse(dataNode.textContent||'[]')}catch{return}
    const selects=['compareA','compareB','compareC'].map(id=>document.getElementById(id));
    if(selects.some(x=>!x))return;
    selects.forEach((sel,i)=>{materials.forEach(m=>{const o=document.createElement('option');o.value=m.id;o.textContent=`${m.name} · ${m.uns}`;sel.appendChild(o)});sel.value=(materials[[0,2,5][i]]||materials[i]||materials[0]).id});
    const fields=[['family','Material family'],['density','Reference density'],['strength','Strength signal'],['corrosion','Corrosion signal'],['temperature','Temperature signal'],['expansion','Expansion signal'],['forms','Common forms'],['standard','Specification anchor'],['signal','Where it starts to fit'],['caution','Qualification caution']];
    const render=()=>{const chosen=selects.map(s=>materials.find(m=>m.id===s.value)||materials[0]);const host=document.getElementById('compareTable');if(!host)return;let h='<table class="compare-table"><thead><tr><th>Decision variable</th>'+chosen.map(m=>`<th><span>${escapeHtml(m.uns)}</span><b>${escapeHtml(m.name)}</b><a href="${escapeHtml(m.href)}">Open reference →</a></th>`).join('')+'</tr></thead><tbody>';fields.forEach(([key,label])=>{h+=`<tr><td>${escapeHtml(label)}</td>`+chosen.map(m=>`<td>${escapeHtml(m[key]||'—')}</td>`).join('')+'</tr>'});h+='</tbody></table>';host.innerHTML=h};
    selects.forEach(s=>s.addEventListener('change',render));
    const rotate=document.getElementById('swapCompare');if(rotate)rotate.addEventListener('click',()=>{const a=selects[0].value;selects[0].value=selects[1].value;selects[1].value=selects[2].value;selects[2].value=a;render()});
    render();
  }

  function bindStandardsMatrix(){
    const input=document.getElementById('standardSearch'), body=document.getElementById('standardRows');if(!input||!body)return;
    const rows=[...body.querySelectorAll('[data-standard-row]')],count=document.getElementById('standardCount'),empty=document.getElementById('standardEmpty');
    const run=()=>{const q=safe(input.value,160).toLowerCase();let n=0;rows.forEach(r=>{const show=!q||(r.dataset.search||'').includes(q);r.hidden=!show;if(show)n++});if(count)count.textContent=String(n);if(empty)empty.hidden=n!==0};
    input.addEventListener('input',run);run();
  }

  function bindDocumentCenter(){
    const input=document.getElementById('docSearch'),type=document.getElementById('docType'),reg=document.getElementById('docRegister');if(!input||!type||!reg)return;
    const rows=[...reg.querySelectorAll('[data-doc-row]')],count=document.getElementById('docCount'),empty=document.getElementById('docEmpty');
    const run=()=>{const q=safe(input.value,160).toLowerCase(),t=type.value;let n=0;rows.forEach(r=>{const show=(!q||(r.dataset.search||'').includes(q))&&(t==='all'||r.dataset.type===t);r.hidden=!show;if(show)n++});if(count)count.textContent=String(n);if(empty)empty.hidden=n!==0};
    input.addEventListener('input',run);type.addEventListener('change',run);run();
  }

  function bindPrintSheets(){
    document.querySelectorAll('[data-print-sheet]').forEach(btn=>btn.addEventListener('click',()=>window.print()));
  }

  function bindThankYou(){
    const box=document.querySelector('#rfqReference'); if(!box) return;
    const id=getStore('tj_rfq_id');
    if(id){box.innerHTML=`Reference: <b>${escapeHtml(id)}</b> · keep this ID for follow-up`;box.classList.add('show')}
  }

  function showToast(text){const toast=document.querySelector('.toast');if(!toast)return;toast.textContent=text;toast.classList.add('show');setTimeout(()=>toast.classList.remove('show'),4500)}
  function escapeHtml(value){return String(value).replace(/[&<>'"]/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[ch]))}

  document.addEventListener('DOMContentLoaded',()=>{
    const params=captureAttribution();
    bindMegaNavigation();
    bindAlloyFinder();
    bindQuickAlloy();
    bindMaterialCompare();
    bindStandardsMatrix();
    bindDocumentCenter();
    bindPrintSheets();
    applyCampaignContext(params);
    bindRouteBuilder(params);
    bindProblemOrder(params);
    document.querySelectorAll('#rfqForm').forEach(form=>bindRfq(form,params));
    bindThankYou();
  });
})();
