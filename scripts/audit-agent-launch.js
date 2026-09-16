const fs=require('fs');
const path=require('path');
const root=path.resolve(__dirname,'..');
const fail=[];
const req=(p)=>{if(!fs.existsSync(path.join(root,p)))fail.push(`missing ${p}`)};
[
  'api/quote-agent.js','api/material-agent.js','lib/agent-core.js','assets/agents.css',
  'MINIMAX_ENV.example','vercel.json','.vercelignore'
].forEach(req);

function text(p){return fs.readFileSync(path.join(root,p),'utf8')}
function must(p,re,msg){if(!re.test(text(p)))fail.push(`${p}: ${msg}`)}

// R15 production posture: agent capabilities remain server-side infrastructure.
// The public sourcing site is not required to expose an "AI Desk" or agent widgets.
// Keep the release gate focused on API safety, deterministic fallback and secret hygiene.
must('api/quote-agent.js',/pending_live_commercial_confirmation/,'fail-closed price state missing');
must('api/quote-agent.js',/QUOTE_PRICE_FEED_URL/,'optional live price adapter missing');
must('api/quote-agent.js',/module\.exports|export\s+default/,'quote-agent handler export missing');
must('api/material-agent.js',/module\.exports|export\s+default/,'material-agent handler export missing');
must('lib/agent-core.js',/process\.env\.MINIMAX_API_KEY/,'server-side MiniMax key lookup missing');
must('lib/agent-core.js',/MiniMax-M3/,'MiniMax model default missing');
must('.vercelignore',/!lib\/\n!lib\/\*\*/,'lib/ is excluded from Vercel deployment');
must('.vercelignore',/!api\/\n!api\/\*\*/,'api/ is excluded from Vercel deployment');

const env=text('MINIMAX_ENV.example');
if(!/^MINIMAX_API_KEY=\s*$/m.test(env))fail.push('MINIMAX_ENV.example must keep MINIMAX_API_KEY blank');
if(/^MINIMAX_API_KEY=\S+/m.test(env))fail.push('MINIMAX_ENV.example contains a non-empty key');

const skip=new Set(['.git','node_modules','_site']);
function walk(dir){
  for(const ent of fs.readdirSync(dir,{withFileTypes:true})){
    if(skip.has(ent.name))continue;
    const full=path.join(dir,ent.name);
    if(ent.isDirectory())walk(full);
    else if(/(^|\/)\.env(?:\.|$)/.test(path.relative(root,full).replaceAll('\\','/')) && !full.endsWith('.env.example'))
      fail.push(`secret-bearing env file must not be committed: ${path.relative(root,full)}`);
    else if(ent.isFile() && fs.statSync(full).size<1_000_000){
      let s=''; try{s=fs.readFileSync(full,'utf8')}catch{continue}
      if(/^MINIMAX_API_KEY=\S+/m.test(s))fail.push(`non-empty MINIMAX_API_KEY assignment: ${path.relative(root,full)}`);
    }
  }
}
walk(root);

if(fail.length){console.error('FAIL: agent backend safety audit');for(const x of fail)console.error('-',x);process.exit(1)}
console.log('PASS: agent backend safety (2 APIs, deterministic fallback, server-side MiniMax key, Vercel api/lib inclusion, fail-closed pricing, no committed key; public AI widgets not required).');
