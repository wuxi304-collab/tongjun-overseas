const assert=require('assert');
function resMock(){return {code:200,headers:{},payload:null,setHeader(k,v){this.headers[k]=v},status(n){this.code=n;return this},json(v){this.payload=v;return this}}}
async function run(handler,body){const req={method:'POST',headers:{},body};const res=resMock();await handler(req,res);return res}
(async()=>{
  delete process.env.MINIMAX_API_KEY;
  const quote=require('../api/quote-agent'); const material=require('../api/material-agent');
  let r=await run(quote,{query:'UNS N06625 ASTM B443 plate 12 x 2000 x 6000 mm, 8 tonnes, seawater process equipment'});
  assert.equal(r.code,200);assert.equal(r.payload.ok,true);assert.equal(r.payload.agent,'quote');assert.ok(r.payload.data.extracted.grade);assert.equal(r.payload.data.price_status,'pending_live_commercial_confirmation');
  r=await run(material,{service:'seawater heat exchanger',media:'seawater',temperature:'55 C',product_form:'tube / plate'});
  assert.equal(r.code,200);assert.equal(r.payload.ok,true);assert.equal(r.payload.agent,'material');assert.ok(r.payload.data.candidates.length>=2);
  console.log('Agent fallback tests: PASS');
})().catch(e=>{console.error(e);process.exit(1)});
