// Exercise the actual generated client and service worker without pretending to
// validate browser rendering, OS dialogs, or radio transfers.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const {execFileSync} = require('node:child_process');
const os = require('node:os');

let folder;
test.before(() => {
  folder=fs.mkdtempSync(path.join(os.tmpdir(),'card-runtime-'));
  const root=path.resolve(__dirname,'..');
  execFileSync('python',['-c',`import sys;from pathlib import Path;sys.path.insert(0,${JSON.stringify(path.join(root,'scripts'))});import build_offline;from PIL import Image;d=Path(${JSON.stringify(folder)});(d/'assets').mkdir();Image.new('RGB',(32,32)).save(d/'assets/photo.jpg');(d/'contacto.vcf').write_text('BEGIN:VCARD\\nVERSION:3.0\\nFN:Ana\\nN:;Ana;;;\\nEND:VCARD\\n');(d/'styles.css').write_text('');(d/'script.js').write_text('');(d/'index.html').write_text('<html lang="es"><head></head><body><main></main></body></html>');build_offline.build(d,'contacto.vcf',d/'assets/photo.jpg','https://example.org/','Ana')`]);
});
test.after(()=>fs.rmSync(folder,{recursive:true,force:true}));
const tick=()=>new Promise(r=>setImmediate(r));
function client(navigator={}) {
 const handlers={},status={textContent:''};
 const context={navigator,window:{CARD_CACHE:'test',CARD_OFFLINE_FILES:['/']},File:class {constructor(parts,name,options){this.name=name;this.type=options.type}},fetch:async()=>({ok:true,blob:async()=>({})}),document:{documentElement:{lang:'es'},querySelector:s=>s==='[data-offline-status]'?status:{addEventListener:(type,fn)=>handlers[s]=fn}},setTimeout,clearTimeout,caches:{open:async()=>({match:async()=>({ok:true})})}};
 vm.runInNewContext(fs.readFileSync(path.join(folder,'offline.js'),'utf8'),context);
 return {handlers,status};
}
test('Unsupported file sharing offers a local download fallback',async()=>{
 const c=client();await tick();await c.handlers['[data-share-contact]']();assert.match(c.status.textContent,/Archivos o Contactos/);
});
test('Compatible sharing passes a photo VCF file to the native share sheet',async()=>{
 let sent;const c=client({canShare:()=>true,share:async data=>sent=data});await tick();await c.handlers['[data-share-contact]']();assert.equal(sent.files[0].name,'contacto-con-foto.vcf');assert.equal(sent.files[0].type,'text/vcard');
});
test('Cancellation is quiet and an OS error offers the fallback',async()=>{
 const c=client({canShare:()=>true,share:async()=>{throw {name:'AbortError'}}});await tick();await c.handlers['[data-share-contact]']();assert.equal(c.status.textContent,'');
 const d=client({canShare:()=>true,share:async()=>{throw {name:'NotAllowedError'}}});await tick();await d.handlers['[data-share-contact]']();assert.match(d.status.textContent,/Descargá/);
});
test('Offline preparation confirms the cache and rejects incomplete cache',async()=>{
 const nav={serviceWorker:{register:async()=>({active:{state:'activated'}})}};
 const c=client(nav);await c.handlers['[data-prepare-offline]']();assert.match(c.status.textContent,/lista para usar offline/);
 const code=fs.readFileSync(path.join(folder,'offline.js'),'utf8');const handlers={},status={textContent:''};
 const ctx={navigator:nav,window:{CARD_CACHE:'missing',CARD_OFFLINE_FILES:['/']},document:{documentElement:{lang:'es'},querySelector:s=>s==='[data-offline-status]'?status:{addEventListener:(t,f)=>handlers[s]=f}},fetch:async()=>{throw Error()},File:class{},caches:{open:async()=>({match:async()=>undefined})},setTimeout,clearTimeout};vm.runInNewContext(code,ctx);await handlers['[data-prepare-offline]']();assert.match(status.textContent,/No se completó/);
});
test('Service worker serves a cached card when the network is unavailable',async()=>{
 const events={};let delivered;const cached={ok:true,offline:true};
 const ctx={self:{addEventListener:(type,fn)=>events[type]=fn},location:{origin:'https://example.org'},URL,fetch:async()=>{throw Error('offline')},caches:{open:async()=>({match:async p=>p==='/'?cached:undefined})}};
 vm.runInNewContext(fs.readFileSync(path.join(folder,'sw.js'),'utf8'),ctx);
 events.fetch({request:{url:'https://example.org/',method:'GET'},respondWith:p=>delivered=p,waitUntil:()=>{}});
 assert.equal(await delivered,cached);
 delivered=undefined;events.fetch({request:{url:'https://external.example.org/',method:'GET'},respondWith:p=>delivered=p});assert.equal(delivered,undefined);
});
