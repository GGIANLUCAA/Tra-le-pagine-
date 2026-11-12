import {test} from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {runInNewContext,Script} from "node:vm";

const html=readFileSync("site/control-center-preview.html","utf8");
const helper=readFileSync("site/control-center-action-hub.fragment.js","utf8");
const sections=html.match(/<script>([\s\S]*?)<\/script>/);
test("V10 source stays inline, JavaScript syntax parses, backend has no writes",()=>{
 assert.ok(sections,"single inline UI script exists");
 new Script(sections[1]);new Script(helper);
 assert.ok(sections[1].includes(helper.trim()),"helper actually included in the UI");
 assert.match(html,/id="repairCopyOpen"/);
 assert.match(html,/id="repairOwnerNote"/);
 assert.match(html,/data-action-work/);
 assert.match(html,/data-action-project/);
 assert.match(html,/Copia e apri la chat/);
});
const state={data:{works:[],health:[],asof:"2026-11-10T17:00:00Z"},actionFilter:"needs",chatLinks:{},chatScope:"project"};
const PROJECT_LABELS={artvision:"ArtVision 4×1",storia:"La Storia Rivive",wow:"WOW LAB"};
const safe=str=>String(str??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const sourceName=name=>true;
const env={state,PROJECT_LABELS,source:sourceName,escapeText:safe};
const functions=runInNewContext(helper+"\n({actionSlotState,actionSlotMode,contextForActionSlot,projectStartContext,actionWorksPanel,actionProjectCards});",env);
const work={id:"the_garden_of_death",title:"The Garden of Death",artist:"Hugo Simberg",delivered:2,
 variants:[
  {id:"critico_standard",label:"Critico",preview_ready:true,site_catalog:true,site_available:true,recorded:true,filename:"A.mp4"},
  {id:"critico_museum",label:"Critico Museum",preview_ready:false,site_catalog:true,site_available:false,recorded:true,filename:"B.mp4"},
  {id:"cinema_standard",label:"Cinema",preview_ready:false,site_catalog:false,recorded:true,filename:"C.mp4"},
  {id:"cinema_museum",label:"Cinema Museum",preview_ready:false,site_catalog:false,recorded:false,filename:null}
 ]};
state.data.works=[work];
test("V10 separates watchable, offline, recorded and not evidenced variants",()=>{
 const statuses=work.variants.map(function(v){return functions.actionSlotState(v).kind});
 assert.deepEqual(Array.from(statuses),["ready","offline","registered","missing"]);
 assert.deepEqual(Array.from(work.variants.map(function(v){return functions.actionSlotMode(v)})),["improve","recover","recover","complete"]);
});
test("V10 shows each slot and targeted buttons; no invented Gold or automatic render",()=>{
 const h=functions.actionWorksPanel();
 assert.match(h,/The Garden of Death/);
 assert.match(h,/1\/4 guardabili sul sito/);
 assert.match(h,/data-action-slot="cinema_museum"/);
 assert.match(h,/data-action-mode="complete"/);
 assert.match(h,/data-action-mode="recover"/);
 assert.match(h,/data-action-mode="improve"/);
 assert.doesNotMatch(h,/Gold approvato/);
 const c=functions.contextForActionSlot(work,work.variants[2],"recover");
 assert.equal(c.slot.filename,"C.mp4");
 assert.equal(c.work.id,"the_garden_of_death");
 assert.equal(c.project,"artvision");
});
test("V10 project start button requests permissioned ChatGPT workflow, never dispatches",()=>{
 const h=functions.actionProjectCards();
 assert.match(h,/Richiedi produzione ora/);
 assert.match(h,/non avvia da solo/i);
 assert.equal((h.match(/data-action-project=/g)||[]).length,3);
 assert.equal(functions.projectStartContext("artvision").action,"produce");
});
test("V10 per-video chat link wins over work/workflow/project mapping",()=>{
 const start=html.indexOf("function workChatKey(ctx){"),end=html.indexOf("function contextForIssue(issue){",start);
 assert.ok(start>0&&end>start);
 const finder=runInNewContext(html.slice(start,end)+"\n({slotChatKey,workChatKey,chatScopeKey,linkedChat});",{
  state,workflowChatKey:()=>null
 });
 const ctx={type:"slot",project:"artvision",work:work,slot:work.variants[3],run:null};
 assert.equal(finder.slotChatKey(ctx),"slot:the_garden_of_death:cinema_museum");
 state.chatScope="slot";assert.equal(finder.chatScopeKey(ctx),"slot:the_garden_of_death:cinema_museum");
 state.chatLinks.artvision="https://chatgpt.com/c/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee";
 state.chatLinks["work:the_garden_of_death"]="https://chatgpt.com/c/11111111-2222-3333-4444-555555555555";
 state.chatLinks["slot:the_garden_of_death:cinema_museum"]="https://chatgpt.com/c/99999999-8888-7777-6666-555555555555";
 assert.match(finder.linkedChat(ctx),/99999999/);
 delete state.chatLinks["slot:the_garden_of_death:cinema_museum"];
 assert.match(finder.linkedChat(ctx),/11111111/);
 delete state.chatLinks["work:the_garden_of_death"];
 assert.match(finder.linkedChat(ctx),/aaaaaaaa/);
});
test("V10 prompt tells GPT to distinguish recovery versus one slot production; never claims work done",()=>{
 const a=html.indexOf("function prepareRepairPrompt(ctx,details){"),b=html.indexOf("function renderRepairDialog(){",a);
 assert.ok(a>0&&b>a);
 const prompt=runInNewContext(html.slice(a,b)+"\nprepareRepairPrompt;",{
  PROJECT_LABELS,site:"https://video-library-studio.600led.workers.dev",state
 });
 state.repairNote="Il movimento di camera non è naturale.";
 const request=prompt({type:"slot",project:"artvision",title:"Garden · Critico",
  action:"improve",work,slot:work.variants[0]},null);
 assert.match(request,/A\.mp4/);assert.match(request,/Il movimento di camera/);
 assert.match(request,/versione N\+1/);assert.match(request,/NON avviare produzioni doppie/);
 const produce=prompt(functions.projectStartContext("artvision"),null);
 assert.match(produce,/nuova produzione REALE/);
 assert.match(produce,/NON crearne una seconda/);
 assert.doesNotMatch(produce,/produzione avviata con successo/i);
 state.repairNote="";
});
test("V10 handles missing data without claiming a movie is absent",()=>{
 const other=runInNewContext(helper+"\n({actionSlotState,actionWorksPanel});",{
  state:{data:{works:[work]},actionFilter:"needs"},PROJECT_LABELS,escapeText:safe,source:()=>false
 });
 assert.equal(other.actionSlotState(work.variants[0]).kind,"unknown");
 assert.match(other.actionWorksPanel(),/non è verificabile/i);
});
