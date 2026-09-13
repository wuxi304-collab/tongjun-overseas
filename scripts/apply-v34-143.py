from pathlib import Path

CSS_MARK = '/* V34.143 — buyer-path visual convergence'
JS_MARK = '/* V34.143 — compact navigation continuity */'

CSS = r'''
/* V34.143 — buyer-path visual convergence
   Home → family → qualification → RFQ now shares one information hierarchy. */
:root{
  --tj-rail:#cfd8de;
  --tj-ink-soft:#53636f;
  --tj-blue-soft:#eef4f8;
  --tj-warm-soft:#fbf4ed;
}
body.brand-v34[data-page="home"] .hero-grid>div:first-child{max-width:820px}
body.brand-v34[data-page="home"] .hero h1{max-width:11.5ch;text-wrap:balance}
body.brand-v34[data-page="home"] .hero .lead{max-width:58ch;line-height:1.58}
body.brand-v34[data-page="home"] .v34-hero-identity{margin-top:30px;border-color:rgba(255,255,255,.22)}
body.brand-v34[data-page="home"] .v34-hero-identity b{font-family:var(--tj-font-mono);font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:#9fb2bf}
body.brand-v34[data-page="home"] .hero-proofbar{margin-top:22px!important}
body.brand-v34[data-page="home"] .hero-proofbar>div{min-height:86px!important}
body.brand-v34[data-page="home"] .v34-trust-head{margin-bottom:38px}
body.brand-v34[data-page="home"] .v34-trust-grid>div{min-height:218px;padding-top:22px}
body.brand-v34[data-page="home"] .v34-trust-grid b{margin-top:34px;font-size:20px}
body.brand-v34[data-page="home"] .quick-finder{border-radius:4px;box-shadow:none}
body.brand-v34[data-page="home"] .product-editorial-grid{gap:14px}
body.brand-v34[data-page="home"] .product-copy p{max-width:47ch}
body.brand-v34[data-page="materials"] .v29-core-copy>p{max-width:58ch}
body.brand-v34[data-page="materials"] .v29-hero-rail{margin-top:34px}
body.brand-v34[data-page="materials"] .v29-material-family{border-top:1px solid var(--tj-rail)}
body.brand-v34[data-page="materials"] .v29-material-family .twocol{align-items:start}
body.brand-v34[data-page="materials"] .v29-material-family .eyebrow{font-family:var(--tj-font-mono);font-size:10px;letter-spacing:.08em}
body.brand-v34[data-page="materials"] .v29-material-family h2{max-width:18ch;text-wrap:balance}
body.brand-v34[data-page="materials"] .v29-material-family .data-table{border-top:2px solid #183b53;background:#fff}
body.brand-v34[data-page="materials"] .v29-material-family .data-table th{background:#f5f8fa;color:#5a6a76}
body.brand-v34[data-page="materials"] .seo-grid{gap:1px;background:var(--tj-rail);border:1px solid var(--tj-rail)}
body.brand-v34[data-page="materials"] .seo-link{border:0!important;border-radius:0!important;background:#fff}
body.brand-v34 :where(.v30-entry-copy>p){max-width:58ch;line-height:1.58}
body.brand-v34 .v30-entry-rail{border-top:1px solid var(--tj-rail);border-bottom:1px solid var(--tj-rail)}
body.brand-v34 .v30-entry-rail>div{min-height:86px}
body.brand-v34 .v30-gate-grid{gap:1px;background:var(--tj-rail);border:1px solid var(--tj-rail)}
body.brand-v34 .v30-gate-grid>div{border:0!important;border-radius:0!important;background:#fff;min-height:214px}
body.brand-v34 .v30-gate-grid small{font-family:var(--tj-font-mono);letter-spacing:.08em}
body.brand-v34 .v30-ledger-table{border-top:2px solid #183b53}
body.brand-v34 .v30-ledger-head{background:#edf2f5}
body.brand-v34 .v30-ledger-table>a{transition:background-color var(--tj-fast) ease}
body.brand-v34 .v30-ledger-table>a:hover{transform:none!important;background:#f6f9fb}
body.brand-v34 .v30-mode-grid{gap:1px;background:#344553;border:1px solid #344553}
body.brand-v34 .v30-mode-grid>div{border:0!important;border-radius:0!important}
body.brand-v34[data-page="supplier-qualification"] .v34-sq-hero p{max-width:61ch}
body.brand-v34[data-page="supplier-qualification"] .v34-identity-ledger{border-top:2px solid #183b53}
body.brand-v34[data-page="supplier-qualification"] .v34-identity-ledger>div{border-bottom:1px solid var(--tj-rail)}
body.brand-v34[data-page="supplier-qualification"] .v34-role-matrix,
body.brand-v34[data-page="supplier-qualification"] .v34-evidence-grid,
body.brand-v34[data-page="supplier-qualification"] .v34-onboarding-grid{gap:1px;background:var(--tj-rail);border:1px solid var(--tj-rail)}
body.brand-v34[data-page="supplier-qualification"] :where(.v34-role-matrix,.v34-evidence-grid,.v34-onboarding-grid)>div{border:0!important;border-radius:0!important;background:#fff}
body.brand-v34[data-page="supplier-qualification"] .v34-checklist-rows>div{border-bottom-color:var(--tj-rail)}
body.brand-v34[data-page="supplier-qualification"] .v34-checklist-rows b{font-weight:680}
body.brand-v34[data-page="supplier-qualification"] .v34-onboarding-actions{border-top:1px solid var(--tj-rail);padding-top:22px;margin-top:24px}
body.brand-v34[data-page="rfq"] .v29-rfq-form{border-radius:6px}
body.brand-v34[data-page="rfq"] .rfq-form-header{padding-bottom:18px;margin-bottom:4px}
body.brand-v34[data-page="rfq"] .rfq-group-label{background:linear-gradient(90deg,var(--tj-blue-soft),transparent 72%);padding-left:14px}
body.brand-v34[data-page="rfq"] .field>small{color:#74838d;line-height:1.45}
body.brand-v34[data-page="rfq"] :where(.rfq-readiness,.buyer-review,.evidence-preview,.offer-readiness){border:1px solid #d1d9de;background:#f8fafb}
body.brand-v34[data-page="rfq"] :where(.buyer-review-grid,.offer-readiness-grid){gap:1px;background:#d7dee3}
body.brand-v34[data-page="rfq"] :where(.buyer-review-grid,.offer-readiness-grid)>div{background:#fff;border:0!important;border-radius:0!important}
body.brand-v34[data-page="rfq"] .rfq-actions{padding-top:4px}
body.brand-v34[data-page="rfq"] #rfq-submit{padding-top:4px}
body.brand-v34 :where(.tech-hero,.pagehero) .eyebrow{font-family:var(--tj-font-mono);letter-spacing:.08em}
body.brand-v34 .tech-hero h1{text-wrap:balance}
body.brand-v34 :where(.tech-table,.data-table) th{white-space:nowrap}
body.brand-v34 :where(.tech-table,.data-table) td:first-child{font-weight:630;color:#233541}
body.brand-v34 .callout{border-left-width:2px;border-radius:0}
@media(min-width:981px){
  body.brand-v34 .footer .footgrid{grid-template-columns:1.35fr repeat(3,.72fr);gap:56px}
  body.brand-v34 .footer h4{margin-bottom:14px}
}
@media(max-width:860px){
  body.brand-v34[data-page="home"] .hero h1{max-width:9.8ch}
  body.brand-v34[data-page="home"] .v34-hero-identity{grid-template-columns:1fr;margin-top:24px}
  body.brand-v34[data-page="home"] .v34-hero-identity span{min-height:auto;border-right:0;border-bottom:1px solid rgba(255,255,255,.16)}
  body.brand-v34[data-page="home"] .v34-hero-identity span:last-child{border-bottom:0}
  body.brand-v34[data-page="materials"] .v29-material-family{padding-block:72px}
  body.brand-v34 :where(.v30-gate-grid,.v30-mode-grid){grid-template-columns:1fr 1fr}
  body.brand-v34[data-page="rfq"] .rfq-group-label{padding-left:10px}
}
@media(max-width:620px){
  body.brand-v34[data-page="home"] .hero h1{font-size:clamp(42px,13vw,58px);max-width:8.8ch}
  body.brand-v34[data-page="home"] .hero-proofbar{grid-template-columns:1fr!important}
  body.brand-v34[data-page="home"] .hero-proofbar>div{min-height:auto!important}
  body.brand-v34 :where(.v30-gate-grid,.v30-mode-grid){grid-template-columns:1fr}
  body.brand-v34 .v30-entry-rail{grid-template-columns:1fr 1fr}
  body.brand-v34[data-page="supplier-qualification"] .v34-onboarding-actions{display:grid;gap:10px}
}
'''

JS = r'''
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
'''

for name, marker, block in [
    ('assets/polish.css', CSS_MARK, CSS),
    ('assets/polish.js', JS_MARK, JS),
]:
    p=Path(name)
    text=p.read_text()
    if marker not in text:
        p.write_text(text.rstrip()+'\n\n'+block.strip()+'\n')
