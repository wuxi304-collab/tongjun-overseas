'use strict';

const assert=require('assert');
const path=require('path');
const { spawn }=require('child_process');

async function run(){
  process.env.TONGJUN_API_HOST='127.0.0.1';
  process.env.TONGJUN_API_PORT='0';
  process.env.TONGJUN_RELEASE_COMMIT='1234567890abcdef1234567890abcdef12345678';
  process.env.TONGJUN_DEPLOYMENT_ENVIRONMENT='production';
  delete process.env.RFQ_MAIL_TRANSPORT;
  delete process.env.RFQ_MAIL_TO;
  delete process.env.RFQ_MAIL_FROM;
  delete process.env.RESEND_API_KEY;
  delete process.env.MS_GRAPH_CLIENT_ID;
  delete process.env.MS_GRAPH_CLIENT_SECRET;
  delete process.env.MS_GRAPH_REFRESH_TOKEN;
  delete process.env.RFQ_SMTP_HOST;

  const {createServer}=require('../server/tongjun-api.js');
  const server=createServer();
  await new Promise((resolve,reject)=>{
    server.once('error',reject);
    server.listen(0,'127.0.0.1',resolve);
  });
  const port=server.address().port;
  const base=`http://127.0.0.1:${port}`;

  let r=await fetch(base+'/api/health');
  assert.equal(r.status,503);
  let body=await r.json();
  assert.equal(body.service,'tongjun-overseas');
  assert.equal(body.site_release,'V34.152 R15.26');
  assert.equal(body.hero_release,'V34.152 R15.24');
  assert.equal(body.release,process.env.TONGJUN_RELEASE_COMMIT);
  assert.equal(body.deployment_environment,'production');

  r=await fetch(base+'/api/health',{method:'HEAD'});
  assert.equal(r.status,503);
  assert.equal(r.headers.get('x-tongjun-release'),'V34.152 R15.26');

  r=await fetch(base+'/api/rfq',{method:'GET'});
  assert.equal(r.status,405);

  r=await fetch(base+'/api/rfq',{
    method:'POST',
    headers:{'content-type':'application/json'},
    body:'{bad json'
  });
  assert.equal(r.status,400);
  body=await r.json();
  assert.equal(body.error,'invalid_json');

  r=await fetch(base+'/not-a-route');
  assert.equal(r.status,404);

  await new Promise(resolve=>server.close(resolve));

  // Release identity must resolve even when the service user does not own the checkout:
  // systemd runs the unit as www-data against a root-owned repository, and git's ownership
  // guard used to silently degrade the reported release to "local".
  delete process.env.TONGJUN_RELEASE_COMMIT;
  const child=spawn(process.execPath,['server/tongjun-api.js'],{
    cwd:path.join(__dirname,'..'),
    env:{...process.env,TONGJUN_API_PORT:'0',TONGJUN_API_HOST:'127.0.0.1'}
  });
  let output='';
  child.stdout.on('data',chunk=>{output+=String(chunk);});
  child.stderr.on('data',chunk=>{output+=String(chunk);});
  await new Promise(resolve=>setTimeout(resolve,2500));
  child.kill('SIGTERM');
  await new Promise(resolve=>child.once('exit',resolve));
  assert.match(output,/release [0-9a-f]{40}/i,`release identity did not resolve to a commit SHA: ${output.trim()}`);

  console.log('PASS: Tencent Lighthouse Node adapter — localhost server, health/RFQ routing, JSON parsing, method gates and release-identity resolution validated.');
}

run().catch(err=>{console.error(err);process.exit(1);});
