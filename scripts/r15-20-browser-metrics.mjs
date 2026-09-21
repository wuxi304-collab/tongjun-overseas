import { spawn } from 'node:child_process';
import { writeFile } from 'node:fs/promises';

const chrome = process.env.CHROME;
const base = process.env.BASE;
if (!chrome || !base) throw new Error('CHROME and BASE are required');

const cases = [
  ['home', '/'],
  ['technical-data', '/technical-data.html'],
  ['standards', '/standards.html'],
  ['titanium', '/titanium-heat-exchangers.html'],
  ['invar', '/resource-invar-lng-vs-tooling.html'],
];
const viewports = [[1440,1000],[390,844]];

const proc = spawn(chrome, [
  '--headless=new','--no-sandbox','--disable-gpu',
  '--remote-debugging-port=9222',
  '--user-data-dir=/tmp/r15-20-cdp',
  'about:blank'
], { stdio:'ignore' });

const sleep = ms => new Promise(r => setTimeout(r, ms));
async function json(url, opts) {
  const res = await fetch(url, opts);
  if (!res.ok) throw new Error(`${res.status} ${url}`);
  return res.json();
}
let version;
for (let i=0;i<60;i++) {
  try { version = await json('http://127.0.0.1:9222/json/version'); break; }
  catch { await sleep(100); }
}
if (!version) throw new Error('Chrome DevTools endpoint did not start');

const ws = new WebSocket(version.webSocketDebuggerUrl);
await new Promise((resolve,reject)=>{ ws.onopen=resolve; ws.onerror=reject; });

let id = 0;
const pending = new Map();
const eventWaiters = [];
ws.onmessage = ev => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) {
    const {resolve,reject} = pending.get(msg.id);
    pending.delete(msg.id);
    if (msg.error) reject(new Error(JSON.stringify(msg.error))); else resolve(msg.result);
    return;
  }
  for (let i=eventWaiters.length-1;i>=0;i--) {
    const w=eventWaiters[i];
    if (msg.method===w.method && (!w.sessionId || msg.sessionId===w.sessionId)) {
      eventWaiters.splice(i,1); w.resolve(msg.params);
    }
  }
};
function send(method, params={}, sessionId) {
  return new Promise((resolve,reject)=>{
    const msg={id:++id,method,params};
    if (sessionId) msg.sessionId=sessionId;
    pending.set(msg.id,{resolve,reject});
    ws.send(JSON.stringify(msg));
  });
}
function waitEvent(method, sessionId, timeout=10000) {
  return new Promise((resolve,reject)=>{
    const item={method,sessionId,resolve,reject};
    eventWaiters.push(item);
    setTimeout(()=>{
      const i=eventWaiters.indexOf(item);
      if(i>=0){eventWaiters.splice(i,1);reject(new Error('timeout '+method));}
    },timeout);
  });
}

const expression = `(() => {
  const one = s => document.querySelector(s);
  const absRect = el => {
    if (!el) return null;
    const r=el.getBoundingClientRect();
    return {top:Math.round(r.top+scrollY),height:Math.round(r.height),width:Math.round(r.width),bottom:Math.round(r.bottom+scrollY)};
  };
  const hero=one('.hero,.pagehero,.tech-hero');
  const h1=one('h1');
  const footer=one('footer.footer');
  const prefooter=one('.prefooter');
  const main=one('main');
  const cs=h1?getComputedStyle(h1):null;
  const fs=cs?parseFloat(cs.fontSize):0;
  const lh=cs?(parseFloat(cs.lineHeight)||fs*1.2):0;
  const h1r=h1?h1.getBoundingClientRect():null;
  const sections=[...document.querySelectorAll('main > section')].map((s,i)=>({i,className:s.className,...absRect(s)}));
  const all=[...document.querySelectorAll('body *')];
  const viewportRight=innerWidth;
  const offenders=all.filter(el=>{
    const r=el.getBoundingClientRect();
    return r.right>viewportRight+2 || r.left<-2;
  }).slice(0,12).map(el=>({tag:el.tagName.toLowerCase(),className:el.className||'',left:Math.round(el.getBoundingClientRect().left),right:Math.round(el.getBoundingClientRect().right),scrollWidth:el.scrollWidth,clientWidth:el.clientWidth}));
  return {
    url:location.href,
    viewport:{width:innerWidth,height:innerHeight},
    document:{scrollWidth:document.documentElement.scrollWidth,scrollHeight:document.documentElement.scrollHeight},
    hero:absRect(hero),
    h1:{text:h1?.innerText||'',...absRect(h1),fontSize:fs,lineHeight:lh,lines:h1r&&lh?Math.round(h1r.height/lh):null},
    main:absRect(main),
    firstMainSection:sections[0]||null,
    secondMainSection:sections[1]||null,
    prefooter:absRect(prefooter),
    footer:absRect(footer),
    footerViewportRatio:footer?+(footer.getBoundingClientRect().height/innerHeight).toFixed(2):null,
    sectionCount:sections.length,
    ctaCount:document.querySelectorAll('a.cta').length,
    stickyActionCount:document.querySelectorAll('.mobile-actionbar a').length,
    rfqBoxCount:document.querySelectorAll('.rfqbox').length,
    horizontalOverflow:document.documentElement.scrollWidth>innerWidth+1,
    offenders
  };
})()`;

const output = [];
for (const [slug,path] of cases) {
  const t = await send('Target.createTarget',{url:'about:blank'});
  const a = await send('Target.attachToTarget',{targetId:t.targetId,flatten:true});
  const sessionId=a.sessionId;
  await send('Page.enable',{},sessionId);
  await send('Runtime.enable',{},sessionId);
  for (const [width,height] of viewports) {
    await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false},sessionId);
    const loaded=waitEvent('Page.loadEventFired',sessionId,15000);
    await send('Page.navigate',{url:base+path},sessionId);
    await loaded;
    await sleep(500);
    const result=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true},sessionId);
    output.push({slug,width,height,...result.result.value});
  }
  await send('Target.closeTarget',{targetId:t.targetId});
}
await writeFile('visual-qa/r15-20/browser-metrics.json', JSON.stringify(output,null,2));
console.log(JSON.stringify(output,null,2));
ws.close();
proc.kill('SIGTERM');
