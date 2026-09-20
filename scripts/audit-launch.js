const fs=require('fs');
const path=require('path');
const root=path.resolve(__dirname,'..');
const htmlFiles=fs.readdirSync(root).filter(f=>f.endsWith('.html')).sort();
const sitemap=fs.readFileSync(path.join(root,'sitemap.xml'),'utf8');
const sitemapRoutes=new Set([...sitemap.matchAll(/<loc>https:\/\/exoticalloycn\.com([^<]*)<\/loc>/g)].map(m=>m[1]||'/'));
const failures=[];
const warn=[];
const routeFor=f=>f==='index.html'?'/':'/'+f.replace(/\.html$/,'');
const targetExists=href=>{
  if(!href.startsWith('/')||href.startsWith('//')) return true;
  const clean=href.split(/[?#]/)[0];
  if(clean==='/') return fs.existsSync(path.join(root,'index.html'));
  return fs.existsSync(path.join(root,clean.slice(1)+'.html')) || fs.existsSync(path.join(root,clean.slice(1))) || fs.existsSync(path.join(root,clean.slice(1),'index.html'));
};
for(const file of htmlFiles){
  const text=fs.readFileSync(path.join(root,file),'utf8');
  const route=routeFor(file);
  const title=(text.match(/<title>([\s\S]*?)<\/title>/i)||[])[1]?.replace(/<[^>]+>/g,'').replace(/&amp;/g,'&').trim()||'';
  const desc=(text.match(/<meta\s+content="([^"]*)"\s+name="description"\s*\/>/i)||[])[1]||'';
  const robots=(text.match(/<meta\s+content="([^"]*)"\s+name="robots"\s*\/>/i)||[])[1]||'';
  const noindex=/noindex/i.test(robots);
  const canon=(text.match(/<link\s+href="([^"]*)"\s+rel="canonical"\s*\/>/i)||[])[1]||'';
  const expectedCanon='https://exoticalloycn.com'+route;
  const h1=(text.match(/<h1\b/gi)||[]).length;
  if(h1!==1) failures.push(`${file}: expected 1 h1, found ${h1}`);
  if(!canon || canon!==expectedCanon) failures.push(`${file}: canonical mismatch (${canon||'missing'})`);
  if(!noindex){
    if(title.length<30||title.length>65) failures.push(`${file}: title length ${title.length}`);
    if(desc.length<80||desc.length>170) failures.push(`${file}: description length ${desc.length}`);
    for(const key of ['og:title','og:description','og:url','og:image']) if(!text.includes(`property="${key}"`)) failures.push(`${file}: missing ${key}`);
    if(!sitemapRoutes.has(route)) failures.push(`${file}: indexable route missing from sitemap`);
  } else if(sitemapRoutes.has(route)) failures.push(`${file}: noindex route present in sitemap`);
  for(const m of text.matchAll(/<script[^>]+type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/gi)){
    try{JSON.parse(m[1]);}catch(e){failures.push(`${file}: invalid JSON-LD (${e.message})`);}
  }
  for(const m of text.matchAll(/href="([^"]+)"/gi)){
    const href=m[1];
    if(href.startsWith('/api/')) continue;
    if(!targetExists(href)) failures.push(`${file}: broken internal href ${href}`);
  }
  if(text.includes('<footer') && !text.includes('href="/privacy"')) failures.push(`${file}: footer missing privacy link`);
  if(text.includes('<footer') && !text.includes('href="/terms"')) failures.push(`${file}: footer missing terms link`);
}
if(!fs.existsSync(path.join(root,'robots.txt'))) failures.push('robots.txt missing');
if(!fs.existsSync(path.join(root,'sitemap.xml'))) failures.push('sitemap.xml missing');
if(!fs.existsSync(path.join(root,'.well-known','security.txt'))) failures.push('security.txt missing');
if(!fs.existsSync(path.join(root,'404.html'))) failures.push('404.html missing');
const rfq=fs.readFileSync(path.join(root,'rfq.html'),'utf8');
if(!rfq.includes('href="/privacy"')) failures.push('rfq.html: privacy acknowledgement missing');
if(!fs.readFileSync(path.join(root,'assets','site.js'),'utf8').includes('mailto:ask2205@outlook.com')) failures.push('site.js: email fallback missing');
const vercel=JSON.parse(fs.readFileSync(path.join(root,'vercel.json'),'utf8'));
const headerPairs=vercel.headers?.flatMap(x=>x.headers||[])||[];
const headerMap=Object.fromEntries(headerPairs.map(x=>[x.key,x.value]));
if(!headerMap['Content-Security-Policy']) failures.push('vercel.json: CSP missing');
if(headerMap['Cross-Origin-Opener-Policy']!=='same-origin') failures.push('vercel.json: COOP missing');
const assetHeaderRule=(vercel.headers||[]).find(x=>x.source==='/assets/(.*)');
const assetCache=(assetHeaderRule?.headers||[]).find(x=>x.key==='Cache-Control')?.value||'';
if(!String(assetCache).includes('max-age=3600') || !String(assetCache).includes('stale-while-revalidate=86400')) failures.push('vercel.json: shared asset cache policy mismatch');
const releaseHeaderRule=(vercel.headers||[]).find(x=>x.source==='/.well-known/release.json');
const releaseCache=(releaseHeaderRule?.headers||[]).find(x=>x.key==='Cache-Control')?.value||'';
if(!/no-store/i.test(String(releaseCache))) failures.push('vercel.json: release identity must be no-store');
const api=fs.readFileSync(path.join(root,'api','rfq.js'),'utf8');
if(!api.includes('RATE_MAX')) failures.push('api/rfq.js: rate gate missing');
if(!api.includes("rfq_route_not_configured")) failures.push('api/rfq.js: fail-closed route guard missing');

if(failures.length){ console.error('FAIL: launch audit'); failures.forEach(x=>console.error(' - '+x)); process.exit(1); }
console.log(`PASS: launch audit (${htmlFiles.length} HTML; SEO, sitemap, JSON-LD, CTA routes, legal links, RFQ fallback).`);
