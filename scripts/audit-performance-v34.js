const fs=require('fs');
const path=require('path');
const root=path.resolve(__dirname,'..');
const htmls=fs.readdirSync(root).filter(f=>f.endsWith('.html')).sort();
const failures=[];
const warnings=[];

function size(rel){return fs.statSync(path.join(root,rel)).size;}
function kb(n){return Math.round(n/1024);}
function attr(tag,name){
  const m=tag.match(new RegExp('\\b'+name+'\\s*=\\s*["\\\']([^"\\\']*)["\\\']','i'));
  return m?m[1]:'';
}
function cleanUrl(value){return String(value||'').split('#')[0];}

const budgets={
  'assets/site.js':120*1024,
  'assets/tongjun-site-r15-19.css':360*1024,
};
for(const [rel,max] of Object.entries(budgets)){
  const fp=path.join(root,rel);
  if(!fs.existsSync(fp)){failures.push(`missing critical asset ${rel}`);continue;}
  const bytes=size(rel);
  if(bytes>max) failures.push(`${rel}: ${kb(bytes)} KB exceeds ${kb(max)} KB budget`);
}

const referencedImages=new Set();
let preloadPages=0;
let lcpCandidates=0;
for(const file of htmls){
  const text=fs.readFileSync(path.join(root,file),'utf8');
  if(/<(?:img|script)\b[^>]*(?:src)=["']https?:\/\//i.test(text)) failures.push(`${file}: external runtime image/script dependency detected`);
  if(/<link\b[^>]*rel=["']stylesheet["'][^>]*href=["']https?:\/\//i.test(text) || /<link\b[^>]*href=["']https?:\/\/[^"']+["'][^>]*rel=["']stylesheet["']/i.test(text)) failures.push(`${file}: external stylesheet dependency detected`);
  const stylesheetTags=[...text.matchAll(/<link\b[^>]*>/gi)].map(m=>m[0]).filter(tag=>attr(tag,'rel').toLowerCase().split(/\s+/).includes('stylesheet'));
  if(stylesheetTags.length!==1) failures.push(`${file}: expected one release stylesheet request, found ${stylesheetTags.length}`);
  else if(!/tongjun-site-r15-19\.css\?v=20260921-r15-19/.test(attr(stylesheetTags[0],'href'))) failures.push(`${file}: R15.19 release stylesheet href missing or stale`);

  const imageTags=[...text.matchAll(/<img\b[^>]*>/gi)].map(m=>m[0]);
  const contentImages=[];
  for(const tag of imageTags){
    const src=attr(tag,'src');
    const base=src.split(/[?#]/)[0];
    if(base.startsWith('/assets/images/')){
      referencedImages.add(base.slice(1));
      contentImages.push({tag,src});
      if(!attr(tag,'width') || !attr(tag,'height')) failures.push(`${file}: content image lacks intrinsic width/height: ${src}`);
      const loading=attr(tag,'loading').toLowerCase();
      if(!['eager','lazy'].includes(loading)) failures.push(`${file}: content image lacks explicit eager/lazy loading policy: ${src}`);
    }
  }

  const preloadTags=[...text.matchAll(/<link\b[^>]*>/gi)].map(m=>m[0]).filter(tag=>{
    const rel=attr(tag,'rel').toLowerCase().split(/\s+/).filter(Boolean);
    return rel.includes('preload') && attr(tag,'as').toLowerCase()==='image';
  });
  if(preloadTags.length>1) failures.push(`${file}: more than one image preload (${preloadTags.length}) creates competing LCP candidates`);
  if(preloadTags.length===1){
    preloadPages+=1;
    const href=attr(preloadTags[0],'href');
    const matches=contentImages.filter(x=>cleanUrl(x.src)===cleanUrl(href));
    const high=matches.filter(x=>attr(x.tag,'fetchpriority').toLowerCase()==='high' && attr(x.tag,'loading').toLowerCase()==='eager');
    if(matches.length<1) failures.push(`${file}: image preload does not match a rendered local image: ${href}`);
    if(high.length!==1) failures.push(`${file}: preload must map to exactly one eager/high image; href=${href}, matches=${matches.length}, eagerHigh=${high.length}`);
    lcpCandidates+=high.length;
  }

  const head=(text.match(/<head[\s\S]*?<\/head>/i)||[])[0]||'';
  for(const m of head.matchAll(/<script\b([^>]*)src=["']([^"']+)["']([^>]*)>/gi)){
    const attrs=(m[1]||'')+(m[3]||'');
    if(!/\b(?:defer|async)(?:\s|=|>|$)/i.test(attrs)) failures.push(`${file}: blocking head script ${m[2]}`);
  }

  if(file==='index.html'){
    const hero=(text.match(/<section class=["']hero["']>[\s\S]*?<\/section>/i)||[])[0]||'';
    const heroLogistics=(hero.match(/logistics-stock\.webp/g)||[]).length;
    if(heroLogistics!==1) failures.push(`index.html: homepage hero must render one frozen logistics image, found ${heroLogistics}`);
    if(/class=["'][^"']*\bhero-photo\b/i.test(hero)) failures.push('index.html: hidden legacy hero-photo figure returned');
    const bg=(hero.match(/<img\b[^>]*class=["'][^"']*\bhero-bg-r6\b[^"']*["'][^>]*>/i)||[])[0]||'';
    if(!bg) failures.push('index.html: hero-bg-r6 LCP image missing');
    else {
      if(attr(bg,'loading').toLowerCase()!=='eager') failures.push('index.html: hero background must load eagerly');
      if(attr(bg,'fetchpriority').toLowerCase()!=='high') failures.push('index.html: hero background must have fetchpriority=high');
      if(attr(bg,'width')!=='2048' || attr(bg,'height')!=='1154') failures.push('index.html: hero intrinsic dimensions must remain 2048x1154');
    }
  }
}

let imageTotal=0;
for(const rel of referencedImages){
  const fp=path.join(root,rel);
  if(!fs.existsSync(fp)){failures.push(`referenced image missing ${rel}`);continue;}
  const bytes=fs.statSync(fp).size;
  imageTotal+=bytes;
  if(bytes>900*1024) failures.push(`${rel}: ${kb(bytes)} KB exceeds 900 KB per-image budget`);
  else if(bytes>600*1024) warnings.push(`${rel}: ${kb(bytes)} KB is above 600 KB review threshold`);
}
if(imageTotal>8*1024*1024) failures.push(`referenced image set: ${kb(imageTotal)} KB exceeds 8192 KB aggregate budget`);

const criticalJs=fs.readFileSync(path.join(root,'assets','site.js'),'utf8');
if(criticalJs.includes('images.unsplash.com')) failures.push('site.js contains external Unsplash dependency');
const brandJs=fs.readFileSync(path.join(root,'assets','brand-v34.152.js'),'utf8');
if(brandJs.includes('images.unsplash.com')) failures.push('brand runtime contains external Unsplash dependency');

if(failures.length){console.error('FAIL: performance + LCP contract audit');failures.forEach(x=>console.error(' - '+x));process.exit(1);}
for(const w of warnings) console.warn('WARN: '+w);
console.log(`PASS: performance + LCP audit (${htmls.length} HTML; one release stylesheet request/page; ${preloadPages} image-preload pages / ${lcpCandidates} unique eager-high LCP candidates; all content images dimensioned + loading-explicit; ${referencedImages.size} referenced images / ${kb(imageTotal)} KB; no external runtime dependencies).`);
