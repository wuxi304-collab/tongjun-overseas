const fs=require('fs');
const path=require('path');
const root=path.resolve(__dirname,'..');
const htmls=fs.readdirSync(root).filter(f=>f.endsWith('.html')).sort();
const failures=[];

function attrs(tag){
  const out={};
  for(const m of tag.matchAll(/([:\w-]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g)){
    const key=m[1].toLowerCase();
    if(key.startsWith('<')) continue;
    out[key]=m[2]??m[3]??m[4]??'';
  }
  return out;
}

for(const file of htmls){
  const text=fs.readFileSync(path.join(root,file),'utf8');
  if(!/<html\b[^>]*\blang=["']en["']/i.test(text)) failures.push(`${file}: html lang=en missing`);
  if(!/class=["'][^"']*skip-link[^"']*["'][^>]*href=["']#main-content["']/i.test(text)) failures.push(`${file}: skip link to #main-content missing`);
  if(!/<main\b[^>]*\bid=["']main-content["']/i.test(text)) failures.push(`${file}: main landmark #main-content missing`);
  if(!/<nav\b[^>]*(?:aria-label|aria-labelledby)=/i.test(text)) failures.push(`${file}: navigation landmark lacks accessible name`);
  if(/tabindex=["']?[1-9]\d*/i.test(text)) failures.push(`${file}: positive tabindex is not allowed`);
  const ids=[...text.matchAll(/\bid=["']([^"']+)["']/gi)].map(m=>m[1]);
  const seen=new Set();
  for(const id of ids){if(seen.has(id)) failures.push(`${file}: duplicate id ${id}`); seen.add(id);}
  for(const m of text.matchAll(/<img\b[^>]*>/gi)){
    const a=attrs(m[0]);
    if(!Object.prototype.hasOwnProperty.call(a,'alt')) failures.push(`${file}: img missing alt attribute`);
  }
  for(const m of text.matchAll(/<button\b[^>]*>/gi)){
    const a=attrs(m[0]);
    if(!a.type) failures.push(`${file}: button missing explicit type`);
    const hasName=Boolean(a['aria-label']||a['aria-labelledby']);
    const start=m.index+m[0].length;
    const close=text.indexOf('</button>',start);
    const visible=close>=0?text.slice(start,close).replace(/<[^>]+>/g,'').trim():'';
    if(!hasName&&!visible) failures.push(`${file}: button lacks accessible name`);
  }
}

// Buyer-form control/label coverage is enforced separately by validate-form-semantics.py;
// keep a guard here so the dedicated validator cannot silently disappear from the release branch.
if(!fs.existsSync(path.join(root,'scripts','validate-form-semantics.py'))) failures.push('missing dedicated buyer-form semantics validator');

if(failures.length){console.error('FAIL: accessibility audit');failures.slice(0,80).forEach(x=>console.error(' - '+x));if(failures.length>80)console.error(` - ... ${failures.length-80} more`);process.exit(1);}
console.log(`PASS: accessibility audit (${htmls.length} HTML; language, landmarks, skip links, IDs, images, buttons and semantics gate presence).`);
