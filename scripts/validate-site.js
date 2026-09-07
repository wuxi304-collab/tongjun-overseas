const fs=require('fs'); const path=require('path');
const root=path.resolve(__dirname,'..');
const htmls=fs.readdirSync(root).filter(f=>f.endsWith('.html'));
let errors=[]; const canon=new Map();
function localTarget(href){
  if(!href || /^(https?:|mailto:|tel:|javascript:|#)/.test(href)) return null;
  const clean=href.split(/[?#]/)[0];
  if(!clean) return null;
  if(clean==='/') return 'index.html';
  if(clean.startsWith('/')) return clean.slice(1)+'.html';
  if(clean.endsWith('.html')) return clean;
  return null;
}
for(const f of htmls){
  const s=fs.readFileSync(path.join(root,f),'utf8');
  if(!/<title>[^<]+<\/title>/i.test(s)) errors.push(`${f}: missing title`);
  if(f!=='404.html' && !/<meta[^>]+name=["']description["'][^>]+content=["'][^"']+/i.test(s) && !/<meta[^>]+content=["'][^"']+[^>]+name=["']description["']/i.test(s)) errors.push(`${f}: missing meta description`);
  const h1Count=(s.match(/<h1\b/gi)||[]).length; if(f!=='404.html' && h1Count!==1) errors.push(`${f}: expected 1 h1, found ${h1Count}`);
  if(/<\/input>/i.test(s)) errors.push(`${f}: invalid closing input tag`);
  if(f!=='404.html' && !/rel=["']canonical["']/i.test(s)) errors.push(`${f}: missing canonical`);
  const cm=s.match(/rel=["']canonical["'][^>]*href=["']([^"']+)/i)||s.match(/href=["']([^"']+)["'][^>]*rel=["']canonical["']/i);
  if(cm){ if(cm[1].endsWith('.html')) errors.push(`${f}: canonical contains .html with cleanUrls`); if(canon.has(cm[1])) errors.push(`${f}: duplicate canonical with ${canon.get(cm[1])}`); canon.set(cm[1],f); }
  for(const m of s.matchAll(/<img\b[^>]*src=["']([^"']+)["'][^>]*>/gi)){
    const src=m[1]; if(!/^https?:|^data:/.test(src)){const fp=path.join(root,src.replace(/^\//,'')); if(!fs.existsSync(fp)) errors.push(`${f}: missing image ${src}`)}
    if(!/\balt=["'][^"']*["']/i.test(m[0])) errors.push(`${f}: img missing alt`);
  }
  for(const m of s.matchAll(/<a\b[^>]*href=["']([^"']+)["'][^>]*>/gi)){
    const target=localTarget(m[1]); if(target && !fs.existsSync(path.join(root,target))) errors.push(`${f}: broken local route ${m[1]} -> ${target}`)
  }
  if(/href=["'][^"']+\.html(?:[?#][^"']*)?["']/i.test(s)) errors.push(`${f}: internal href still contains .html`);
}
for(const f of ['assets/favicon.svg','manifest.webmanifest','.well-known/security.txt','assets/images/og-cover.webp','sitemap.xml','robots.txt','vercel.json','api/rfq.js','.vercelignore']) if(!fs.existsSync(path.join(root,f))) errors.push(`missing core asset ${f}`);
const sm=fs.readFileSync(path.join(root,'sitemap.xml'),'utf8'); if(/\.html<\/loc>/.test(sm)) errors.push('sitemap contains .html with cleanUrls');
for(const f of htmls){const h=fs.readFileSync(path.join(root,f),'utf8'); const robotsTags=h.match(/<meta\b[^>]*>/gi)||[]; const noindex=robotsTags.some(tag=>/name=[\"']robots[\"']/i.test(tag)&&/content=[\"'][^\"']*noindex/i.test(tag)); if(noindex){const cm=h.match(/rel=[\"']canonical[\"'][^>]*href=[\"']([^\"']+)/i)||h.match(/href=[\"']([^\"']+)[\"'][^>]*rel=[\"']canonical[\"']/i); if(cm && sm.includes(`<loc>${cm[1]}</loc>`)) errors.push(`${f}: noindex canonical appears in sitemap`);}}

const vi=fs.readFileSync(path.join(root,'.vercelignore'),'utf8');
for(const token of ['/*','!api/**','!assets/**','!*.html']) if(!vi.includes(token)) errors.push(`.vercelignore missing allowlist token ${token}`);
if(/!ops(?:\/|\b)/.test(vi)) errors.push('.vercelignore must not allow public deployment of ops');
const privateNames=['Knight Group','Hempel Special Metals','BIBUS Metals','Quest 4 Alloys','NeoNickel','Impact Special Metals','Avocet Precision Metals','Hart B.V.','Witzenmann','Godrej Process Equipment','TEMA India'];
for(const f of htmls){const h=fs.readFileSync(path.join(root,f),'utf8'); for(const n of privateNames) if(h.includes(n)) errors.push(`${f}: private account name leaked into public HTML: ${n}`);}
const api=fs.readFileSync(path.join(root,'api/rfq.js'),'utf8'); if(!api.includes('route_ref:80')) errors.push('api/rfq.js missing route_ref allowlist');
const js=fs.readFileSync(path.join(root,'assets/site.js'),'utf8'); if(!js.includes("ensureHidden(form,'route_ref'")) errors.push('site.js missing RFQ route_ref handoff');


const index=fs.readFileSync(path.join(root,'index.html'),'utf8');
if(!index.includes('class="navlinks mega-nav"')) errors.push('index.html missing V13 mega navigation');
if(!index.includes('id="quickAlloyForm"')) errors.push('index.html missing quick alloy finder');
for(const f of ['alloys.html','product-forms.html']) if(!fs.existsSync(path.join(root,f))) errors.push(`missing V13 route ${f}`);
if(!sm.includes('<loc>https://exoticalloycn.com/alloys</loc>')) errors.push('sitemap missing /alloys');
if(!sm.includes('<loc>https://exoticalloycn.com/product-forms</loc>')) errors.push('sitemap missing /product-forms');
const alloys=fs.readFileSync(path.join(root,'alloys.html'),'utf8');
const alloyRows=(alloys.match(/<tr data-family=/g)||[]).length; if(alloyRows<28) errors.push(`alloys.html expected at least 28 alloy rows, found ${alloyRows}`);
if(!alloys.includes('id="alloySearch"') || !alloys.includes('id="familyFilter"')) errors.push('alloys.html missing finder controls');
const forms=fs.readFileSync(path.join(root,'product-forms.html'),'utf8');
const formCards=(forms.match(/class="form-card/g)||[]).length; if(formCards<6) errors.push(`product-forms.html expected 6 form cards, found ${formCards}`);
for(const f of htmls){const h=fs.readFileSync(path.join(root,f),'utf8'); const footerCount=(h.match(/<footer class="footer">/g)||[]).length; if(footerCount!==1) errors.push(`${f}: expected one global footer, found ${footerCount}`);}


const technicalPages=['technical-data.html','technical-alloy-625.html','technical-alloy-718.html','technical-alloy-c276.html','technical-alloy-825.html','technical-invar-36.html','technical-super-duplex-2507.html'];
for(const f of technicalPages) if(!fs.existsSync(path.join(root,f))) errors.push(`missing V14 technical route ${f}`);
for(const f of technicalPages.slice(1)){const h=fs.readFileSync(path.join(root,f),'utf8'); if(!h.includes('data-tech-sheet="true"')) errors.push(`${f}: missing technical sheet marker`); if(!h.includes('data-print-sheet')) errors.push(`${f}: missing print action`);}
if(!sm.includes('<loc>https://exoticalloycn.com/technical-data</loc>')) errors.push('sitemap missing /technical-data');
for(const r of ['technical-alloy-625','technical-alloy-718','technical-alloy-c276','technical-alloy-825','technical-invar-36','technical-super-duplex-2507']) if(!sm.includes(`<loc>https://exoticalloycn.com/${r}</loc>`)) errors.push(`sitemap missing /${r}`);
const standardsHtml=fs.readFileSync(path.join(root,'standards.html'),'utf8'); if(/ASTM F1684(?![^<]{0,80}withdrawn)/i.test(standardsHtml)) errors.push('standards.html still uses ASTM F1684 as a current default');
const tInvar=fs.readFileSync(path.join(root,'technical-invar-36.html'),'utf8'); if(!/F1684 was withdrawn in 2024/i.test(tInvar)) errors.push('technical-invar-36.html missing withdrawn-standard warning'); if(!/B753 is scoped to thermostat component alloys/i.test(tInvar)) errors.push('technical-invar-36.html missing B753 scope warning');
if(!fs.existsSync(path.join(root,'TECHNICAL_DATA_SOURCES.md'))) errors.push('missing internal technical data source register');
const indexV14=fs.readFileSync(path.join(root,'index.html'),'utf8'); if(!indexV14.includes('/technical-data')) errors.push('index.html missing Technical Data Center link');
const resourcesV14=fs.readFileSync(path.join(root,'resources.html'),'utf8'); if(!resourcesV14.includes('Technical Data Center')) errors.push('resources.html missing Technical Data Center feature');
const alloyFinderV14=fs.readFileSync(path.join(root,'alloys.html'),'utf8'); if(!alloyFinderV14.includes('Data sheet →')) errors.push('alloys.html missing technical data links');
if(!js.includes('bindPrintSheets')) errors.push('site.js missing technical-sheet print binding');

// V15 controlled document system
for(const f of ['material-compare.html','standards-matrix.html','document-center.html']) if(!fs.existsSync(path.join(root,f))) errors.push(`missing V15 route ${f}`);
for(const r of ['material-compare','standards-matrix','document-center']) if(!sm.includes(`<loc>https://exoticalloycn.com/${r}</loc>`)) errors.push(`sitemap missing /${r}`);
const cmp=fs.readFileSync(path.join(root,'material-compare.html'),'utf8'); const cmpItems=(cmp.match(/\"id\":/g)||[]).length; if(cmpItems<8) errors.push(`material-compare.html expected at least 8 materials, found ${cmpItems}`);
if(!js.includes('bindMaterialCompare')||!js.includes('bindStandardsMatrix')||!js.includes('bindDocumentCenter')) errors.push('site.js missing V15 tool bindings');
const mx=fs.readFileSync(path.join(root,'standards-matrix.html'),'utf8'); const mxRows=(mx.match(/data-standard-row/g)||[]).length; if(mxRows<10) errors.push(`standards-matrix.html expected at least 10 routes, found ${mxRows}`);
const dc=fs.readFileSync(path.join(root,'document-center.html'),'utf8'); const dcRows=(dc.match(/data-doc-row/g)||[]).length; if(dcRows<15) errors.push(`document-center.html expected at least 15 document rows, found ${dcRows}`);
for(const f of technicalPages.slice(1)){const h=fs.readFileSync(path.join(root,f),'utf8'); if(!/data-doc-id=/.test(h)||!/data-doc-rev=/.test(h)) errors.push(`${f}: missing V15 document metadata`); if(!h.includes('doc-control-strip')) errors.push(`${f}: missing document control strip`); if(!h.includes('TechArticle')) errors.push(`${f}: missing TechArticle schema`);}
if(!fs.existsSync(path.join(root,'TECHNICAL_DOCUMENT_GOVERNANCE.md'))) errors.push('missing V15 technical document governance');


// V21 buyer decision interface
if(!index.includes('buyer-decision-board') && !index.includes('decision-spine-home')) errors.push('index.html missing buyer decision architecture');
const qualityV21=fs.readFileSync(path.join(root,'quality.html'),'utf8');
if(!qualityV21.includes('buyer-acceptance-table')) errors.push('quality.html missing V21 buyer acceptance matrix');
const rfqV21=fs.readFileSync(path.join(root,'rfq.html'),'utf8');
for(const token of ['name="procurement_stage"','name="buyer_gate"','id="buyerReview"']) if(!rfqV21.includes(token)) errors.push(`rfq.html missing V21 token ${token}`);
if(!js.includes("ensureHidden(form,'decision_ref'")) errors.push('site.js missing V21 decision_ref handoff');
if(!api.includes('decision_ref:80')||!api.includes('procurement_stage:120')||!api.includes('buyer_gate:120')) errors.push('api/rfq.js missing V21 buyer-decision allowlist');
for(const f of ['technical-alloy-625.html','technical-alloy-718.html','technical-alloy-c276.html','technical-invar-36.html']){
  const h=fs.readFileSync(path.join(root,f),'utf8');
  if(!h.includes('tech-decision-snapshot')) errors.push(`${f}: missing V21 buyer decision snapshot`);
  if(!h.includes('href="#decision"')) errors.push(`${f}: missing V21 decision nav`);
}

const dcV21=fs.readFileSync(path.join(root,'document-center.html'),'utf8');
for(const id of ['TJ-TDS-625-001','TJ-TDS-718-001','TJ-TDS-C276-001','TJ-TDS-36NI-001']) if(!dcV21.includes(`<span>${id}</span><b>REV 03</b>`)) errors.push(`document-center.html missing V21 revision 03 for ${id}`);

// V22 qualified offer system
if(!index.includes('qualified-offer-system') && !index.includes('decision-spine-offer')) errors.push('index.html missing qualified-offer architecture');
const qualityV22=fs.readFileSync(path.join(root,'quality.html'),'utf8');
if(!qualityV22.includes('offer-boundary-section')) errors.push('quality.html missing V22 evidence-to-offer boundary');
const rfqV22=fs.readFileSync(path.join(root,'rfq.html'),'utf8');
for(const token of ['name="incoterm"','name="destination"','name="delivery_target"','name="packing"','id="offerReadiness"']) if(!rfqV22.includes(token)) errors.push(`rfq.html missing V22 token ${token}`);
if(!js.includes("ensureHidden(form,'offer_ref'")||!js.includes('updateOfferReadiness')) errors.push('site.js missing V22 qualified-offer state');
if(!api.includes('incoterm:80')||!api.includes('destination:240')||!api.includes('delivery_target:80')||!api.includes('packing:500')||!api.includes('offer_ref:80')) errors.push('api/rfq.js missing V22 qualified-offer allowlist');


// V24 launch-readiness consolidation
if(!index.includes('decision-spine-home')||!index.includes('decision-spine-offer')) errors.push('index.html missing V24 consolidated Buyer Decision Spine');
if(!index.includes('home-rfq-direct')) errors.push('index.html missing V24 direct RFQ handoff');
if(!index.includes('mobile-menu-quick')) errors.push('index.html missing V24 mobile quick navigation');
for(const f of ['precision-strip.html','nickel-alloys.html','invar-36.html','heavy-plate.html','titanium-zirconium.html']){
  const h=fs.readFileSync(path.join(root,f),'utf8');
  if(!h.includes('v24-specpanel')||!h.includes('v24-landing-scope')) errors.push(`${f}: missing V24 differentiated landing hierarchy`);
}
for(const f of ['technical-alloy-625.html','technical-alloy-718.html','technical-alloy-c276.html','technical-invar-36.html']){
  const h=fs.readFileSync(path.join(root,f),'utf8');
  if(!h.includes('tech-focus-strip')) errors.push(`${f}: missing V24 purchase-focus strip`);
}
if(!js.includes('nav-open')||!js.includes("details[open]")) errors.push('site.js missing V24 mobile navigation behavior');

if(errors.length){console.error(errors.join('\n')); process.exit(1)}
console.log(`PASS: ${htmls.length} HTML files; clean routes, canonical, images and deployment assets validated.`);


