const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const root = path.resolve(__dirname, '..');
const manifestPath = path.join(root, 'SOURCE_MANIFEST_V27_TEXT.gitsha1');
function gitBlobSha(buf){ const h=Buffer.from(`blob ${buf.length}\0`); return crypto.createHash('sha1').update(h).update(buf).digest('hex'); }
const failures=[];
for(const line of fs.readFileSync(manifestPath,'utf8').split(/\r?\n/).filter(Boolean)){
  const m=line.match(/^([0-9a-f]{40})\t(.+)$/); if(!m){failures.push(`malformed: ${line}`);continue;}
  const abs=path.join(root,m[2]); if(!fs.existsSync(abs)){failures.push(`missing: ${m[2]}`);continue;}
  if(gitBlobSha(fs.readFileSync(abs))!==m[1]) failures.push(`blob mismatch: ${m[2]}`);
}
if(failures.length){ console.error('FAIL: text source manifest'); failures.forEach(x=>console.error(`- ${x}`)); process.exit(1); }
console.log('PASS: V27 text source manifest');
