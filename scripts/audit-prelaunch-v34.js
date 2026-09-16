const fs=require('fs');
const path=require('path');
const root=path.resolve(__dirname,'..');
const htmls=fs.readdirSync(root).filter(f=>f.endsWith('.html')).sort();
const failures=[];

if(htmls.length!==50) failures.push(`expected 50 root HTML files, found ${htmls.length}`);
const forbidden=['SINCE 2010','hero-special-metals.webp','quality-lab-r13','engineering-team-r13','technical-lab-r13','logo-r13.avif','hero-port-r13.avif'];
for(const file of htmls){
  const text=fs.readFileSync(path.join(root,file),'utf8');
  if(!text.includes('assets/site.js?v=20260916-r14-2')) failures.push(`${file}: current site.js release marker missing`);
  for(const marker of forbidden) if(text.includes(marker)) failures.push(`${file}: forbidden release marker ${marker}`);
  if(/<meta\b[^>]*name=["']robots["'][^>]*content=["'][^"']*noindex/i.test(text) && file!=='404.html' && file!=='thank-you.html'){
    failures.push(`${file}: unexpected production noindex`);
  }
}

for(const required of ['api/rfq.js','api/health.js','vercel.json','.vercelignore','robots.txt','sitemap.xml','scripts/check-production-readiness.js','scripts/smoke-rfq-production.js']){
  if(!fs.existsSync(path.join(root,required))) failures.push(`missing production release file ${required}`);
}

const vi=fs.readFileSync(path.join(root,'.vercelignore'),'utf8');
if(/!ops(?:\/|\b)/.test(vi)) failures.push('.vercelignore exposes ops');
if(!vi.includes('!api/**')) failures.push('.vercelignore must deploy serverless API');

const robots=fs.readFileSync(path.join(root,'robots.txt'),'utf8');
if(/Disallow:\s*\/$/m.test(robots)) failures.push('production robots.txt blocks the entire site');

const health=fs.readFileSync(path.join(root,'api','health.js'),'utf8');
for(const marker of ['rfq_route_configured','Cache-Control','RFQ_WEBHOOK_URL']) if(!health.includes(marker)) failures.push(`api/health.js missing ${marker}`);
if(/RFQ_SHARED_SECRET/.test(health)) failures.push('api/health.js must not expose or depend on RFQ_SHARED_SECRET');

const smoke=fs.readFileSync(path.join(root,'scripts','smoke-rfq-production.js'),'utf8');
if(!smoke.includes('RFQ_SMOKE_URL')) failures.push('production RFQ smoke is not explicitly opt-in');
if(!smoke.includes('NO COMMERCIAL ORDER')) failures.push('production RFQ smoke is not clearly marked synthetic');

if(failures.length){console.error('FAIL: R15 prelaunch audit');failures.forEach(x=>console.error(' - '+x));process.exit(1);}
console.log('PASS: R15 prelaunch audit — production source, deploy boundary, runtime version, health and smoke contracts validated.');
