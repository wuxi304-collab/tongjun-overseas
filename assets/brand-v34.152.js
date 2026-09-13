(()=>{
  const BRAND='TONGJUN METAL TECH';
  const FALLBACK_PORT='https://images.unsplash.com/photo-1774929108070-b60d3879e071?auto=format&fit=crop&fm=jpg&q=82&w=2200';
  const FALLBACK_COIL='https://images.unsplash.com/photo-1576473318185-48d76fc03314?auto=format&fit=crop&fm=jpg&q=82&w=1600';
  const FALLBACK_METAL='https://images.unsplash.com/photo-1728392051874-dadee8a8a7c9?auto=format&fit=crop&fm=jpg&q=82&w=1600';
  const IMAGE_MAP={
    'hero-special-metals.webp':FALLBACK_PORT,'logistics-stock.webp':FALLBACK_PORT,'og-cover.webp':FALLBACK_PORT,'og-social.webp':FALLBACK_PORT,
    'precision-strip.webp':FALLBACK_COIL,'nickel-alloys.webp':FALLBACK_METAL,'heavy-plate.webp':FALLBACK_METAL,
    'invar-lng.webp':FALLBACK_PORT,'invar-tooling.webp':FALLBACK_METAL,'titanium-zirconium.webp':FALLBACK_METAL,'about-engineering.webp':FALLBACK_METAL
  };
  function normalizeHeader(){
    const brand=document.querySelector('.site-header .brand');
    if(brand){brand.setAttribute('aria-label','Tongjun Metal Tech home');const label=brand.querySelector(':scope > span:last-child');if(label)label.textContent=BRAND;}
    const cta=document.querySelector('.site-header .nav-cta');if(cta)cta.innerHTML='Request a Quote <span>→</span>';
    const nav=document.querySelector('.site-header .navlinks');if(nav){const direct=[...nav.children];const cap=direct.find(x=>x.matches('a')&&/Capabilities/i.test(x.textContent));if(cap)cap.textContent='Quality';const res=direct.find(x=>x.matches('a')&&/Resources/i.test(x.textContent));if(res)res.textContent='Technical Data';}
  }
  function normalizeFooter(){document.querySelectorAll('.site-footer .brand,footer .brand').forEach(b=>{const label=b.querySelector(':scope > span:last-child');if(label)label.textContent=BRAND;});}
  function basename(src){try{return new URL(src,location.href).pathname.split('/').pop()||''}catch{return String(src||'').split('/').pop()||''}}
  function applyFallback(img){
    if(!img||img.dataset.tjFallbackApplied==='1')return;
    const key=basename(img.getAttribute('src')||img.currentSrc||'');
    const fallback=IMAGE_MAP[key];if(!fallback)return;
    img.dataset.tjFallbackApplied='1';img.classList.add('tj-image-fallback');img.dataset.originalAsset=key;img.referrerPolicy='no-referrer';img.src=fallback;
  }
  function recoverImages(){
    document.querySelectorAll('img').forEach(img=>{
      const raw=img.getAttribute('src')||'';
      if(!/assets\/images\//.test(raw))return;
      img.addEventListener('error',()=>applyFallback(img),{once:true});
      if(img.complete&&img.naturalWidth===0)applyFallback(img);
    });
  }
  function removeFloatingBots(){
    const selectors=['#dify-chatbot-bubble-button','#dify-chatbot-bubble-window','iframe[src*="dify"]','iframe[src*="chatbot"]','iframe[src*="coze"]','.chatbot-bubble','.floating-chatbot','.floating-assistant'];
    document.querySelectorAll(selectors.join(',')).forEach(el=>el.remove());
    const observer=new MutationObserver(()=>document.querySelectorAll(selectors.join(',')).forEach(el=>el.remove()));
    observer.observe(document.documentElement,{childList:true,subtree:true});
    setTimeout(()=>observer.disconnect(),12000);
  }
  document.addEventListener('DOMContentLoaded',()=>{normalizeHeader();normalizeFooter();recoverImages();removeFloatingBots();});
})();
