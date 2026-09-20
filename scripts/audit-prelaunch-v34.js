const fs=require('fs');
const path=require('path');
const root=path.resolve(__dirname,'..');
const htmls=fs.readdirSync(root).filter(f=>f.endsWith('.html')).sort();
const failures=[];
const sitemap=fs.readFileSync(path.join(root,'sitemap.xml'),'utf8');

function attr(tag,name){
  const m=tag.match(new RegExp(`\\b${name}\\s*=\\s*["']([^"']*)["']`,'i'));
  return m?m[1]:'';
}
function robotsContent(html){
  const tags=html.match(/<meta\b[^>]*>/gi)||[];
  for(const tag of tags) if(attr(tag,'name').toLowerCase()==='robots') return attr(tag,'content');
  return '';
}
function routeFor(file){return file==='index.html'?'/':'/'+file.replace(/\.html$/,'');}

if(htmls.length!==50) failures.push(`expected 50 root HTML files, found ${htmls.length}`);
const forbidden=['SINCE 2010','hero-special-metals.webp','quality-lab-r13','engineering-team-r13','technical-lab-r13','logo-r13.avif','hero-port-r13.avif'];
for(const file of htmls){
  const text=fs.readFileSync(path.join(root,file),'utf8');
  if(!text.includes('assets/site.js?v=20260916-r14-2')) failures.push(`${file}: current site.js release marker missing`);
  for(const marker of forbidden) if(text.includes(marker)) failures.push(`${file}: forbidden release marker ${marker}`);
  const robots=robotsContent(text);
  if(/noindex/i.test(robots)){
    const route=routeFor(file);
    const loc=`<loc>https://exoticalloycn.com${route}</loc>`;
    if(sitemap.includes(loc)) failures.push(`${file}: noindex page appears in sitemap`);
  }
}

for(const required of ['api/rfq.js','api/health.js','vercel.json','.vercelignore','robots.txt','sitemap.xml','RELEASE_R15_14.json','VISUAL_MANIFEST_R15_7.json','scripts/write-release-metadata.py','scripts/check-production-readiness.js','scripts/smoke-rfq-production.js']){
  if(!fs.existsSync(path.join(root,required))) failures.push(`missing production release file ${required}`);
}

const vi=fs.readFileSync(path.join(root,'.vercelignore'),'utf8');
if(/!ops(?:\/|\b)/.test(vi)) failures.push('.vercelignore exposes ops');
if(!vi.includes('!api/**')) failures.push('.vercelignore must deploy serverless API');
if(!vi.includes('!RELEASE_R15_14.json')) failures.push('.vercelignore must include R15.14 release descriptor for build identity');
if(!vi.includes('!VISUAL_MANIFEST_R15_7.json')) failures.push('.vercelignore must include frozen visual manifest for build identity');

const robotsTxt=fs.readFileSync(path.join(root,'robots.txt'),'utf8');
if(/Disallow:\s*\/$/m.test(robotsTxt)) failures.push('production robots.txt blocks the entire site');

const health=fs.readFileSync(path.join(root,'api','health.js'),'utf8');
for(const marker of ['rfq_route_configured','rfq_route_https_valid','rfq_signature_configured','Cache-Control','RFQ_WEBHOOK_URL','RFQ_SHARED_SECRET','V34.152 R15.14','X-Tongjun-Release','visual_release']) if(!health.includes(marker)) failures.push(`api/health.js missing ${marker}`);
if(/X-Tongjun-Webhook-Secret/.test(health)) failures.push('api/health.js must never expose the raw webhook secret header');
if(/RFQ_SHARED_SECRET\s*[:=]\s*process\.env\.RFQ_SHARED_SECRET/.test(health)) failures.push('api/health.js must not serialize RFQ_SHARED_SECRET into the response payload');

const smoke=fs.readFileSync(path.join(root,'scripts','smoke-rfq-production.js'),'utf8');
if(!smoke.includes('RFQ_SMOKE_URL')) failures.push('production RFQ smoke is not explicitly opt-in');
if(!smoke.includes('NO COMMERCIAL ORDER')) failures.push('production RFQ smoke is not clearly marked synthetic');

if(failures.length){console.error('FAIL: R15 prelaunch audit');failures.forEach(x=>console.error(' - '+x));process.exit(1);}
console.log('PASS: R15 prelaunch audit — production source, index/noindex sitemap consistency, deploy boundary, runtime version, health and smoke contracts validated.');
