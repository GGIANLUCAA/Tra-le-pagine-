// Video Library Studio category navigation regression checks. No API calls or uploads.
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const {test}=require('node:test');
const html=fs.readFileSync(path.resolve(__dirname,'../site/video-library-v2.html'),'utf8');
const scripts=[...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].map(x=>x[1]);
const app=scripts[0]||"";
const expected=[
  "Libri narrati","Racconti e fiabe","Artisti e pittura","Critica d’arte",
  "La Storia Rivive","Restauri storici","Musica e visual","WOW LAB",
  "Cinema e cortometraggi","Documentari e curiosità","Cronaca e attualità",
  "Provini e backstage","Altri progetti"
];
test('Original site JavaScript parses with the new category navigation',()=>{
  assert.equal(scripts.length,1);
  new vm.Script(app);
  assert.match(html,/id="collectionGrid"/);
  assert.match(html,/id="filters"/);
  assert.match(html,/id="controlCenterFrame"/);
  assert.match(app,/function renderMuseum/);
});
test('All 13 categories are in taxonomy and admin menu, without a home eight-card cap',()=>{
  const taxonomy=app.slice(app.indexOf('const CATEGORY_WORLDS='),app.indexOf('let initialCategoryApplied='));
  for(const name of expected){
    assert.ok(taxonomy.includes('"'+name+'"'),'Missing catalogue world '+name);
    assert.ok(html.includes('<option>'+name+'</option>'),'Missing admin option '+name);
  }
  assert.doesNotMatch(app,/for\s*\(const category of categories\.slice\(0,8\)\)/);
  assert.match(app,/for\(const category of allCategories\)/);
  assert.match(app,/b\.disabled=records\.length===0/);
  assert.match(app,/In preparazione/);
  assert.match(app,/records\.length\+' produzioni'/);
});
test('Book categories normalize legacy values without modifying server metadata',()=>{
  const b=app.indexOf('function categoryLabel(input){');
  const e=app.indexOf('let initialCategoryApplied=',b);
  const fn=vm.runInNewContext(app.slice(b,e)+'\ncategoryLabel;');
  assert.equal(fn("Libri raccontati"),"Libri narrati");
  assert.equal(fn("Libri narrati"),"Libri narrati");
  assert.equal(fn("Racconti e fiabe"),"Racconti e fiabe");
  assert.equal(fn("Critica d’arte"),"Critica d’arte");
  assert.equal(fn(null),"Altri progetti");
  assert.match(app,/x\.viewCategory=categoryLabel\(x\.category\|\|x\.guess\.category\)/);
});
test('Inference recognizes narrated books, fairy tales, historical films and tests',()=>{
  const b=app.indexOf('function inferred(x){');
  const e=app.indexOf('const base=k=>',b);
  assert.ok(b>=0&&e>b);
  const inferred=vm.runInNewContext(app.slice(b,e)+'\ninferred;',{
    norm:s=>String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase(),
    topic:()=>''
  });
  function category(filename){return inferred({key:filename,available:true}).category}
  assert.equal(category('TRA_LE_PAGINE_EP03_SIDDHARTA.mp4'),'Libri raccontati');
  assert.equal(category('TRA_LE_PAGINE_NILS_HOLGERSSON_NARRATO.mp4'),'Racconti e fiabe');
  assert.equal(category('LA_STORIA_RIVIVE_BEIRUT_1919.mp4'),'La Storia Rivive');
  assert.equal(category('ARROSEUR_1895_CINEMA_RESTORED.mp4'),'Restauri storici');
  assert.equal(category('WOW_LAB_CROW_V2.mp4'),'WOW LAB');
  assert.equal(category('ARTVISION_BOSCH_CINEMA_V6.mp4'),'Artisti e pittura');
  assert.equal(category('SOURCE_SHOT_05__8973.mp4'),'Provini e backstage');
});
test('Category link selects the same category from Center and does not change other operations',()=>{
  assert.match(app,/new URLSearchParams\(location\.search\)\.get\('category'\)/);
  assert.match(app,/initialCategoryNavigate=true/);
  assert.match(app,/requestAnimationFrame\(\(\)=>gotoSection\('library'\)\)/);
  assert.match(app,/if\(CATEGORY_WORLDS\.includes\(label\)\|\|g\.items\.some/);
  assert.match(app,/const cats=\['Tutti',\.\.\.CATEGORY_WORLDS/);
  assert.match(app,/g\.category===c/);
  assert.match(app,/function filtered\(\)/);
  assert.match(app,/function edit\(x\)/);
  assert.match(app,/async function manage\(/);
});
