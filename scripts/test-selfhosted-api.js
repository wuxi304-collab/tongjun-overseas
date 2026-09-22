'use strict';

const assert=require('assert');

async function run(){
  process.env.TONGJUN_API_HOST='127.0.0.1';
  process.env.TONGJUN_API_PORT='0';
  process.env.TONGJUN_RELEASE_COMMIT='1234567890abcdef1234567890abcdef12345678';
  process.env.TONGJUN_DEPLOYMENT_ENVIRONMENT='production';
  delete process.env.RFQ_WEBHOOK_URL;
  delete process.env.RFQ_SHARED_SECRET;

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
  console.log('PASS: Tencent Lighthouse Node adapter — localhost server, health/RFQ routing, JSON parsing and method gates validated.');
}

run().catch(err=>{console.error(err);process.exit(1);});
