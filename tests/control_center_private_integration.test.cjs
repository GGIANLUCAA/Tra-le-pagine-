// Regression checks for the authenticated Control Center entry point.
// Read-only and designed to run without API keys, downloads or video production.
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const {test}=require('node:test');
const html=fs.readFileSync(path.join(__dirname,'../site/video-library-v2.html'),'utf8');
const scripts=[...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
test('Single inline site application script still parses',()=>{
 assert.equal(scripts.length,1,'Do not add multiple frontend scripts');
 new vm.Script(scripts[0]);
});
test('Existing video site controls remain present',()=>{
 for(const id of ['adminBanner','adminLogout','adminDialog','ready','readyRail','studioMetrics','collectionGrid','library','adminOpen','exportCSV']){
   assert.ok(html.includes('id="'+id+'"'),'Missing original control '+id);
 }
 assert.ok(html.includes('function swPostUpdate'));
 assert.ok(html.includes('function openEditorial'));
});
test('Control Center is launched only from private Studio UI',()=>{
 assert.ok(html.includes('id="openControlCenterStudio"'));
 assert.ok(html.includes('id="openControlCenterBanner"'));
 assert.ok(html.includes('id="controlCenterDialog"'));
 assert.ok(html.includes("if(!g.admin){$('#adminDialog').showModal();return}"));
 assert.ok(html.includes("if(!g.admin&&$('#controlCenterDialog').open)closeControlCenter()"));
 assert.ok(html.includes("$('#adminLogout').onclick=()=>{closeControlCenter();"));
 assert.ok(!html.includes('id="controlCenterFrame" src='));
});
test('Embedded frame is isolated, never receives admin token or credentials',()=>{
 const match=html.match(/<iframe[^>]*id="controlCenterFrame"[^>]*>/);
 assert.ok(match,'Expected iframe');
 assert.match(match[0],/sandbox="allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox allow-downloads"/);
 assert.match(match[0],/referrerpolicy="no-referrer"/);
 assert.match(match[0],/allow="fullscreen; clipboard-write"/);
 assert.doesNotMatch(match[0],/\bsrc=/);
 assert.match(html,/\$\('#controlCenterFrame'\)\.src='https:\/\/artvision-control-preview\.600led\.workers\.dev\/'/);
 assert.doesNotMatch(html,/controlCenterFrame'\)\.src=.*g\.token/);
});
test('Only the authenticated private area contains the primary Studio launch card',()=>{
 const studio=html.indexOf('<section class="showcase-section ready-section" id="ready"');
 const launcher=html.indexOf('id="openControlCenterStudio"');
 const nextPublic=html.indexOf('<section class="library-section"',studio);
 assert.ok(studio>=0&&launcher>studio&&launcher<nextPublic);
 assert.match(html,/const active=!!\(g\.admin&&g\.studio\)/);
 assert.match(html,/\$\('#ready'\)\.hidden=!active/);
});
