(()=>{
  const BRAND_MAIN='TONGJUN';
  const BRAND_SUB='METAL TECH · EST. 2026';
  const LEGACY_BRAND='TONGJUN METAL TECH';
  const LOCAL={
    'og-social.webp':'/assets/images/og-cover.webp',
    'precision-strip.webp':'/assets/images/precision-strip.webp',
    'nickel-alloys.webp':'/assets/images/nickel-alloys.webp',
    'heavy-plate.webp':'/assets/images/heavy-plate.webp',
    'invar-lng.webp':'/assets/images/invar-lng.webp',
    'invar-tooling.webp':'/assets/images/invar-tooling.webp',
    'titanium-zirconium.webp':'/assets/images/titanium-zirconium.webp',
    'about-engineering.webp':'/assets/images/engineering-discussion-v2.webp',
    'quality-inspection.webp':'/assets/images/quality-lab-v2.webp',
    'traceability-pmi.webp':'/assets/images/quality-lab-v2.webp',
    'resources-metal.webp':'/assets/images/materials-warehouse-v2.webp',
    'standards-rfq.webp':'/assets/images/engineering-review-v2.webp'
  };

  function normalizeBrandLockup(root){
    if(!root) return;
    const composite=root.querySelector(':scope > .tj-brand-composite');
    if(composite){
      const strong=composite.querySelector('.tj-brand-copy strong');
      const small=composite.querySelector('.tj-brand-copy small');
      if(strong) strong.textContent=BRAND_MAIN;
      if(small) small.textContent=BRAND_SUB;
      return;
    }
    // Legacy markup only: never target the vector composite container itself.
    const label=root.querySelector(':scope > span:last-child:not(.tj-brand-composite)');
    if(label) label.textContent=LEGACY_BRAND;
  }

  function normalizeHeader(){
    const brand=document.querySelector('.site-header .brand');
    if(brand){
      brand.setAttribute('aria-label','Tongjun Metal Tech home');
      normalizeBrandLockup(brand);
    }
    const cta=document.querySelector('.site-header .nav-cta');
    if(cta){cta.href='/rfq';cta.innerHTML='Request a Quote <span>→</span>';}
    const nav=document.querySelector('.site-header .navlinks');
    if(nav){
      const direct=[...nav.children];
      const cap=direct.find(x=>x.matches('a')&&/Capabilities/i.test(x.textContent));
      if(cap){cap.textContent='Quality';cap.href='/quality';}
      const res=direct.find(x=>x.matches('a')&&/Resources/i.test(x.textContent));
      if(res){res.textContent='Technical Data';res.href='/technical-data';}
    }
  }

  function normalizeFooter(){
    document.querySelectorAll('.site-footer .brand,footer .brand').forEach(normalizeBrandLockup);
  }

  function basename(src){
    try{return new URL(src,location.href).pathname.split('/').pop()||''}
    catch{return String(src||'').split('/').pop()||''}
  }

  function applyFallback(img){
    if(!img||img.dataset.tjFallbackApplied==='1') return;
    const key=basename(img.getAttribute('src')||img.currentSrc||'');
    const fallback=LOCAL[key];
    if(!fallback) return;
    img.dataset.tjFallbackApplied='1';
    img.classList.add('tj-image-fallback');
    img.dataset.originalAsset=key;
    img.src=fallback;
  }

  function recoverImages(){
    document.querySelectorAll('img').forEach(img=>{
      const raw=img.getAttribute('src')||'';
      if(!/assets\/images\//.test(raw)) return;
      img.addEventListener('error',()=>applyFallback(img),{once:true});
      if(img.complete&&img.naturalWidth===0) applyFallback(img);
    });
  }

  function removeFloatingBots(){
    const selectors=['#dify-chatbot-bubble-button','#dify-chatbot-bubble-window','iframe[src*="dify"]','iframe[src*="chatbot"]','iframe[src*="coze"]','.chatbot-bubble','.floating-chatbot','.floating-assistant'];
    document.querySelectorAll(selectors.join(',')).forEach(el=>el.remove());
    const observer=new MutationObserver(()=>document.querySelectorAll(selectors.join(',')).forEach(el=>el.remove()));
    observer.observe(document.documentElement,{childList:true,subtree:true});
    setTimeout(()=>observer.disconnect(),12000);
  }

  document.addEventListener('DOMContentLoaded',()=>{
    normalizeHeader();
    normalizeFooter();
    recoverImages();
    removeFloatingBots();
  });
})();
