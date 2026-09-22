'use strict';

const http = require('http');
const { execFileSync } = require('child_process');
const rfqHandler = require('../api/rfq.js');
const healthHandler = require('../api/health.js');

const HOST = String(process.env.TONGJUN_API_HOST || '127.0.0.1').trim();
const PORT = Number(process.env.TONGJUN_API_PORT || 8787);
const MAX_ADAPTER_BODY_BYTES = 32 * 1024;

function resolveGitCommit(){
  if(process.env.TONGJUN_RELEASE_COMMIT) return process.env.TONGJUN_RELEASE_COMMIT;
  try{
    return execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim();
  }catch{
    return 'local';
  }
}

if(!process.env.TONGJUN_RELEASE_COMMIT){
  process.env.TONGJUN_RELEASE_COMMIT = resolveGitCommit();
}
if(!process.env.TONGJUN_DEPLOYMENT_ENVIRONMENT){
  process.env.TONGJUN_DEPLOYMENT_ENVIRONMENT = 'production';
}

function adaptResponse(res){
  return {
    setHeader(name,value){ res.setHeader(name,value); },
    status(code){ res.statusCode=code; return this; },
    json(payload){
      if(!res.getHeader('Content-Type')) res.setHeader('Content-Type','application/json; charset=utf-8');
      res.end(JSON.stringify(payload));
      return payload;
    },
    end(){ res.end(); return this; }
  };
}

function sendJson(res,status,payload){
  res.statusCode=status;
  res.setHeader('Cache-Control','no-store');
  res.setHeader('Content-Type','application/json; charset=utf-8');
  res.end(JSON.stringify(payload));
}

function readJsonBody(req){
  return new Promise((resolve,reject)=>{
    const chunks=[];
    let bytes=0;
    req.on('data',chunk=>{
      bytes+=chunk.length;
      if(bytes>MAX_ADAPTER_BODY_BYTES){
        const err=new Error('payload_too_large');
        err.code='PAYLOAD_TOO_LARGE';
        reject(err);
        req.destroy();
        return;
      }
      chunks.push(chunk);
    });
    req.on('end',()=>{
      if(!chunks.length){ resolve({}); return; }
      try{
        const parsed=JSON.parse(Buffer.concat(chunks).toString('utf8'));
        if(!parsed || typeof parsed!=='object' || Array.isArray(parsed)){
          const err=new Error('invalid_json_object');
          err.code='INVALID_JSON';
          reject(err);
          return;
        }
        resolve(parsed);
      }catch(err){
        if(!err.code) err.code='INVALID_JSON';
        reject(err);
      }
    });
    req.on('error',reject);
  });
}

async function dispatch(req,res){
  const pathname=new URL(req.url || '/', 'http://127.0.0.1').pathname;
  const reply=adaptResponse(res);

  if(pathname==='/api/health'){
    return healthHandler(req,reply);
  }

  if(pathname==='/api/rfq'){
    if(req.method==='POST'){
      try{
        req.body=await readJsonBody(req);
      }catch(err){
        if(err && err.code==='PAYLOAD_TOO_LARGE') return sendJson(res,413,{ok:false,error:'payload_too_large'});
        return sendJson(res,400,{ok:false,error:'invalid_json'});
      }
    }
    return rfqHandler(req,reply);
  }

  return sendJson(res,404,{ok:false,error:'not_found'});
}

function createServer(){
  return http.createServer((req,res)=>{
    dispatch(req,res).catch(err=>{
      console.error('TONGJUN_API_UNHANDLED', err && err.stack ? err.stack : err);
      if(!res.headersSent) sendJson(res,500,{ok:false,error:'internal_error'});
      else res.end();
    });
  });
}

if(require.main===module){
  const server=createServer();
  server.listen(PORT,HOST,()=>{
    console.log(
      `Tongjun API listening on http://${HOST}:${PORT} · release ${process.env.TONGJUN_RELEASE_COMMIT}`
    );
  });

  const shutdown=signal=>{
    console.log(`Received ${signal}; closing Tongjun API.`);
    server.close(()=>process.exit(0));
    setTimeout(()=>process.exit(1),5000).unref();
  };
  process.on('SIGTERM',()=>shutdown('SIGTERM'));
  process.on('SIGINT',()=>shutdown('SIGINT'));
}

module.exports={createServer,dispatch};
