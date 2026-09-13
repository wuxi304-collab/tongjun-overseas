(() => {
  'use strict';
  const d=document;
  const b=d.body;
  if(!b || !b.classList.contains('brand-v34')) return;

  const reduced=window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(!reduced) b.classList.add('tj-motion-enabled');

  /* Reliable header elevation across browsers. */
  const header=d.querySelector('.site-header.nav');
  if(header){
    let queued=false;
    const paint=()=>{
      queued=false;
      header.classList.toggle('is-scrolled',window.scrollY>24);
    };
    const onScroll=()=>{if(!queued){queued=true;requestAnimationFrame(paint)}};
    paint();
    addEventListener('scroll',onScroll,{passive:true});
  }

  /* Below-fold reveal rhythm. Hero choreography remains CSS-only. */
  if(!reduced && 'IntersectionObserver' in window){
    const selectors=[
      '.section > .wrap > .sec-head',
      '.product-editorial-grid > .product-tile',
      '.industries > .industry',
      '.capgrid > .cap',
      '.flagship-grid > a',
      '.decision-spine-grid > div',
      '.decision-spine-offer',
      '.v34-qualification-rail-grid > div',
      '.resource-directory > a',
      '.resource-list > a',
      '.method-grid > .method-card',
      '.twocol > *',
      '.rfqbox > *',
      '.prefooter-grid > *',
      '.tds-row',
      '.v29-tool-band a',
      '.source-role-grid > div',
      '.quality-console-grid > div'
    ];
    const nodes=[...new Set(selectors.flatMap(s=>[...d.querySelectorAll(s)]))]
      .filter(el=>!el.closest('.hero,.pagehero,.tech-hero,.landinghero,.articlehero,.v29-core-hero'));

    nodes.forEach((el,i)=>{
      el.classList.add('tj-reveal');
      const parent=el.parentElement;
      const siblings=parent ? [...parent.children].filter(x=>nodes.includes(x)) : [];
      const pos=Math.max(0,siblings.indexOf(el));
      el.style.setProperty('--tj-reveal-delay',`${Math.min(pos,4)*55}ms`);
    });

    const io=new IntersectionObserver(entries=>{
      entries.forEach(entry=>{
        if(entry.isIntersecting){
          entry.target.classList.add('tj-visible');
          io.unobserve(entry.target);
        }
      });
    },{threshold:.12,rootMargin:'0px 0px -7% 0px'});
    nodes.forEach(el=>io.observe(el));
  }

  /* Same-page section spy for technical reference navigation. */
  const sectionLinks=[...d.querySelectorAll('.section-nav a[href^="#"]')];
  if(sectionLinks.length && 'IntersectionObserver' in window){
    const pairs=sectionLinks.map(a=>{
      const id=decodeURIComponent(a.getAttribute('href').slice(1));
      return {a,target:d.getElementById(id)};
    }).filter(x=>x.target);
    const setCurrent=a=>{
      sectionLinks.forEach(link=>link.removeAttribute('aria-current'));
      if(a) a.setAttribute('aria-current','location');
    };
    const spy=new IntersectionObserver(entries=>{
      const visible=entries.filter(e=>e.isIntersecting).sort((a,b)=>Math.abs(a.boundingClientRect.top)-Math.abs(b.boundingClientRect.top));
      if(!visible.length) return;
      const hit=pairs.find(x=>x.target===visible[0].target);
      if(hit) setCurrent(hit.a);
    },{rootMargin:'-24% 0px -62% 0px',threshold:[0,.1,.5]});
    pairs.forEach(x=>spy.observe(x.target));
    sectionLinks.forEach(a=>a.addEventListener('click',()=>setCurrent(a)));
  }

  /* Pointer-intent prefetch makes same-origin page transitions feel continuous. */
  const connection=navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  const canPrefetch=!connection?.saveData && !/2g/.test(connection?.effectiveType||'');
  if(canPrefetch){
    const seen=new Set();
    let count=0;
    const prefetch=a=>{
      if(count>=6) return;
      try{
        const u=new URL(a.href,location.href);
        if(u.origin!==location.origin || u.pathname===location.pathname || seen.has(u.pathname)) return;
        if(/\/rfq\/?$/.test(u.pathname) || /mailto:|tel:/.test(a.href)) return;
        seen.add(u.pathname);count++;
        const link=d.createElement('link');
        link.rel='prefetch';link.href=u.pathname+u.search;link.as='document';
        d.head.appendChild(link);
      }catch{}
    };
    d.addEventListener('pointerover',e=>{
      const a=e.target.closest && e.target.closest('a[href]');
      if(a) prefetch(a);
    },{passive:true});
    d.addEventListener('focusin',e=>{
      const a=e.target.closest && e.target.closest('a[href]');
      if(a) prefetch(a);
    });
  }

  /* Keep keyboard and pointer states consistent on compact menus. */
  d.querySelectorAll('.mobile-menu details').forEach(detail=>{
    const summary=detail.querySelector('summary');
    if(!summary) return;
    detail.addEventListener('toggle',()=>summary.setAttribute('aria-expanded',String(detail.open)));
    summary.setAttribute('aria-expanded',String(detail.open));
  });
})();

/* V34.143 — compact navigation continuity */
(() => {
  'use strict';
  const d=document;
  const b=d.body;
  if(!b || !b.classList.contains('brand-v34')) return;
  const nav=d.querySelector('.section-nav-inner');
  if(nav && 'MutationObserver' in window){
    const compact=()=>window.matchMedia('(max-width: 860px)').matches;
    const centerCurrent=()=>{
      if(!compact()) return;
      const current=nav.querySelector('a[aria-current="location"],a[aria-current="page"]');
      if(!current) return;
      const left=current.offsetLeft-(nav.clientWidth-current.offsetWidth)/2;
      nav.scrollTo({left:Math.max(0,left),behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});
    };
    const mo=new MutationObserver(mutations=>{
      if(mutations.some(m=>m.type==='attributes' && m.attributeName==='aria-current')) centerCurrent();
    });
    nav.querySelectorAll('a').forEach(a=>mo.observe(a,{attributes:true,attributeFilter:['aria-current']}));
    addEventListener('resize',centerCurrent,{passive:true});
    setTimeout(centerCurrent,0);
  }
})();


/* V34.144 — RFQ progress semantics */
(() => {
  'use strict';
  const d=document,b=d.body;if(!b||b.dataset.page!=='rfq')return;
  const form=d.getElementById('rfqForm');if(!form)return;
  const stages=[['name','company','email','country'],['grade','standard','form','size','condition','qty','application'],['certificate','origin','approval','procurement_stage','buyer_gate'],['incoterm','destination','delivery_target','packing'],['notes']];
  const required=['name','company','email','grade','size','qty','application'];
  const stageEls=[...form.querySelectorAll('.rfq-form-stagebar span')],groupEls=[...form.querySelectorAll('.rfq-group-label')];
  const mobile=d.getElementById('mobileRfqProgress'),mobileState=d.getElementById('mobileRequiredState'),mobileHint=d.getElementById('mobileRequiredHint'),privacy=form.querySelector('.checkline input[type="checkbox"]');
  const field=name=>form.elements.namedItem(name),valued=el=>el&&(el.type==='checkbox'||el.type==='radio'?el.checked:String(el.value||'').trim().length>0);
  const setFieldState=el=>{if(!el||!el.closest)return;const wrap=el.closest('.field');if(!wrap)return;wrap.classList.toggle('has-value',!!valued(el));if(el.required)wrap.classList.toggle('has-error',!el.checkValidity()&&el.dataset.touched==='1')};
  const update=activeName=>{form.querySelectorAll('input,select,textarea').forEach(setFieldState);stages.forEach((names,i)=>{const members=names.map(field).filter(Boolean),requiredMembers=members.filter(x=>x.required),done=requiredMembers.length?requiredMembers.every(valued):members.some(valued),active=activeName&&names.includes(activeName);stageEls[i]?.classList.toggle('is-complete',done);stageEls[i]?.classList.toggle('is-active',!!active);groupEls[i]?.classList.toggle('is-active',!!active)});const complete=required.reduce((n,name)=>n+(valued(field(name))?1:0),0);if(mobileState)mobileState.textContent=`${complete}/${required.length} complete`;const missing=required.filter(name=>!valued(field(name)));if(mobileHint)mobileHint.textContent=missing.length?`Next: ${missing[0].replace(/_/g,' ')}`:(privacy&&!privacy.checked?'Accept privacy to send':'Ready for final review');if(mobile)mobile.classList.toggle('ready',complete===required.length&&(!privacy||privacy.checked))};
  form.addEventListener('focusin',e=>{if(e.target?.name)update(e.target.name)});form.addEventListener('focusout',e=>{if(e.target&&'dataset'in e.target){e.target.dataset.touched='1';setFieldState(e.target)}});form.addEventListener('input',e=>{if(e.target?.name)update(e.target.name)});form.addEventListener('change',e=>{if(e.target?.name)update(e.target.name);else update('')});form.addEventListener('submit',()=>{form.querySelectorAll('[required]').forEach(el=>{el.dataset.touched='1';setFieldState(el)});update('')});update('');
})();


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
    /* V34.152 R2 — release authority alignment */
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
    if(legacyState)legacyState.textContent=status==='QUALIFIED BASIS'?'Qualified basis':status==='QUALIFIED WITH CONDITIONS'?'Conditional':'Not released';
    const checklistEl=form.elements.namedItem('release_checklist');if(checklistEl)checklistEl.value=checklist;
  };
  ['input','change'].forEach(evt=>form.addEventListener(evt,update));update();
})();
