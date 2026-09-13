from pathlib import Path

css=Path('assets/polish.css')
js=Path('assets/polish.js')

CSS=r'''

/* V34.144 — conversion-focused visual finish */
body.brand-v34[data-page="home"] .hero-photo{border-radius:6px;border-color:#bdc9d0;box-shadow:0 18px 46px rgba(9,28,42,.12)}
body.brand-v34[data-page="home"] .hero-photo img{filter:saturate(.78) contrast(1.035);transform:scale(1.005)}
body.brand-v34[data-page="home"] .hero-photo:after{background:linear-gradient(180deg,rgba(255,255,255,0) 58%,rgba(8,22,38,.12) 100%)}
body.brand-v34[data-page="home"] .product-tile{border-radius:4px;box-shadow:none;border-color:#cbd5db}
body.brand-v34[data-page="home"] .product-media{aspect-ratio:16/9;background:#e7ecef}
body.brand-v34[data-page="home"] .product-media img{filter:saturate(.74) contrast(1.03);transition:transform 700ms cubic-bezier(.2,.7,.2,1),filter 320ms ease}
@media(hover:hover) and (pointer:fine){body.brand-v34[data-page="home"] .product-tile:hover .product-media img{transform:scale(1.018);filter:saturate(.82) contrast(1.04)}}
body.brand-v34[data-page="home"] .product-copy{padding-top:20px}
body.brand-v34[data-page="home"] .product-kicker{font-family:var(--tj-font-mono);font-size:9px;letter-spacing:.09em}
body.brand-v34[data-page="home"] .product-meta{border-top:1px solid #d7dfe4;padding-top:12px;margin-top:18px}
body.brand-v34 :where(.v30-gate-grid,.v30-mode-grid)>div{position:relative;overflow:hidden}
body.brand-v34 .v30-gate-grid>div:before{content:"";position:absolute;left:0;top:0;bottom:0;width:2px;background:#1b587e;opacity:.22}
body.brand-v34 .v30-gate-grid>div:first-child:before{background:#df772a;opacity:.72}
body.brand-v34 .v30-gate-grid b{font-family:var(--tj-font-display);font-weight:650;letter-spacing:-.015em}
body.brand-v34 .v30-gate-grid p{max-width:34ch;color:#657580}
body.brand-v34 .v30-ledger-table>a{min-height:62px;align-items:center}
body.brand-v34 .v30-ledger-table>a>span:last-child{font-family:var(--tj-font-mono);font-size:10px;letter-spacing:.04em;color:#51636f}
body.brand-v34[data-page="supplier-qualification"] :where(.v34-role-matrix,.v34-evidence-grid,.v34-onboarding-grid)>div{padding-top:24px;padding-bottom:24px}
body.brand-v34[data-page="supplier-qualification"] :where(.v34-role-matrix,.v34-evidence-grid,.v34-onboarding-grid) small{font-family:var(--tj-font-mono);letter-spacing:.08em}
body.brand-v34[data-page="supplier-qualification"] .v34-checklist-rows>div{min-height:58px;align-items:center}
body.brand-v34[data-page="supplier-qualification"] .v34-checklist-rows span{color:#6a7984}
body.brand-v34[data-page="technical-data"] .tds-row{grid-template-columns:minmax(170px,.72fr) minmax(0,1.35fr) minmax(145px,.62fr)}
body.brand-v34[data-page="technical-data"] .tds-row>strong{font-family:var(--tj-font-display);font-weight:650;letter-spacing:-.012em}
body.brand-v34[data-page="technical-data"] .tds-row:hover{background:#f6f9fb}
body.brand-v34 :where(.tech-table,.data-table) thead th{font-family:var(--tj-font-mono);font-size:10px;letter-spacing:.055em;text-transform:uppercase}
body.brand-v34 :where(.tech-table,.data-table) tbody td{line-height:1.46}
body.brand-v34[data-page="rfq"] .rfq-form-stagebar span{position:relative;transition:background-color 180ms ease,color 180ms ease,border-color 180ms ease}
body.brand-v34[data-page="rfq"] .rfq-form-stagebar span:after{content:"";position:absolute;left:10px;right:10px;bottom:5px;height:2px;background:#6f7e87;transform:scaleX(0);transform-origin:left;transition:transform 220ms ease,background-color 180ms ease}
body.brand-v34[data-page="rfq"] .rfq-form-stagebar span.is-active{color:#fff;background:#243741}
body.brand-v34[data-page="rfq"] .rfq-form-stagebar span.is-active:after{transform:scaleX(.45);background:#e67a2c}
body.brand-v34[data-page="rfq"] .rfq-form-stagebar span.is-complete{color:#dce8ee;background:#1d303a}
body.brand-v34[data-page="rfq"] .rfq-form-stagebar span.is-complete:after{transform:scaleX(1);background:#74a4c4}
body.brand-v34[data-page="rfq"] .rfq-group-label.is-active{background:linear-gradient(90deg,#eaf3f8,transparent 82%);border-top-color:#95afbf}
body.brand-v34[data-page="rfq"] .field.has-value>label{color:#243b4a}
body.brand-v34[data-page="rfq"] .field.has-value :where(input,select,textarea){border-color:#afbec7}
body.brand-v34[data-page="rfq"] .field.has-error :where(input,select,textarea){border-color:#b94f3a;box-shadow:0 0 0 2px rgba(185,79,58,.08)}
body.brand-v34[data-page="rfq"] .field.has-error>label{color:#9b3d2d}
body.brand-v34[data-page="rfq"] .v34-mobile-rfq-progress{transition:border-color 180ms ease,background-color 180ms ease}
body.brand-v34[data-page="rfq"] .v34-mobile-rfq-progress.ready{border-top-color:#da7b35;background:rgba(18,30,39,.985)}
@media(max-width:860px){body.brand-v34[data-page="home"] .hero-grid{gap:26px}body.brand-v34[data-page="home"] .hero-photo{border-radius:4px;aspect-ratio:16/10;box-shadow:none}body.brand-v34[data-page="home"] .product-editorial-grid{gap:10px}body.brand-v34[data-page="technical-data"] .tds-row{grid-template-columns:1fr}body.brand-v34[data-page="technical-data"] .tds-row>*{min-width:0}body.brand-v34[data-page="rfq"] .rfq-form-stagebar span:after{left:8px;right:8px}}
@media(max-width:620px){body.brand-v34[data-page="home"] .product-media{aspect-ratio:16/10}body.brand-v34[data-page="home"] .product-copy{padding:17px 16px 18px}body.brand-v34[data-page="rfq"] .v34-mobile-rfq-progress b{font-family:var(--tj-font-ui);font-weight:680}}
@media(prefers-reduced-motion:reduce){body.brand-v34[data-page="rfq"] .rfq-form-stagebar span:after,body.brand-v34[data-page="home"] .product-media img{transition:none!important}}
'''

JS=r'''

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
'''

for path,block,marker in [(css,CSS,'V34.144 — conversion-focused visual finish'),(js,JS,'V34.144 — RFQ progress semantics')]:
    text=path.read_text()
    if marker not in text:
        path.write_text(text+block)
