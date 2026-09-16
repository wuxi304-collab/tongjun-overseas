const fs=require('fs');
const path=require('path');
const root=path.resolve(__dirname,'..');
const htmls=fs.readdirSync(root).filter(f=>f.endsWith('.html')).sort();
const failures=[];
const warnings=[];

function size(rel){return fs.statSync(path.join(root,rel)).size;}
function kb(n){return Math.round(n/1024);}

const budgets={
  'assets/site.js':120*1024,
  'assets/brand-v34.152-r14.css':300*1024,
  'assets/site.css':180*1024,
};
for(const [rel,max] of Object.entries(budgets)){
  const fp=path.join(root,rel);
  if(!fs.existsSync(fp)){failures.push(`missing critical asset ${rel}`);continue;}
  const bytes=size(rel);
  if(bytes>max) failures.push(`${rel}: ${kb(bytes)} KB exceeds ${kb(max)} KB budget`);
}

const referencedImages=new Set();
for(const file of htmls){
  const text=fs.readFileSync(path.join(root,file),'utf8');
  if(/<(?:img|script)\b[^>]*(?:src)=["']https?:\/\//i.test(text)) failures.push(`${file}: external runtime image/script dependency detected`);
  if(/<link\b[^>]*rel=["']stylesheet["'][^>]*href=["']https?:\/\//i.test(text) || /<link\b[^>]*href=["']https?:\/\/[^"']+["'][^>]*rel=["']stylesheet["']/i.test(text)) failures.push(`${file}: external stylesheet dependency detected`);
  for(const m of text.matchAll(/<img\b[^>]*src=["']([^"']+)["']/gi)){
    const src=m[1].split(/[?#]/)[0];
    if(src.startsWith('/assets/images/')) referencedImages.add(src.slice(1));
  }
  const head=(text.match(/<head[\s\S]*?<\/head>/i)||[])[0]||'';
  for(const m of head.matchAll(/<script\b([^>]*)src=["']([^"']+)["']([^>]*)>/gi)){
    const attrs=(m[1]||'')+(m[3]||'');
    if(!/\b(?:defer|async)(?:\s|=|>|$)/i.test(attrs)) failures.push(`${file}: blocking head script ${m[2]}`);
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

if(failures.length){console.error('FAIL: performance budget audit');failures.forEach(x=>console.error(' - '+x));process.exit(1);}
for(const w of warnings) console.warn('WARN: '+w);
console.log(`PASS: performance budget audit (${htmls.length} HTML; critical JS/CSS budgets, ${referencedImages.size} referenced images / ${kb(imageTotal)} KB, no external runtime dependencies).`);
