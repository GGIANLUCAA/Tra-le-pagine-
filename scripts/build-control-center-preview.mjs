#!/usr/bin/env node
// Build a single Cloudflare Worker bundle from the two reviewed V2 source files.
// Intentionally does NOT deploy, mutate main, trigger videos, or use secrets.
import assert from "node:assert/strict";
import {readFileSync,mkdirSync,writeFileSync} from "node:fs";
import {join,dirname,resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {Script} from "node:vm";
const root=resolve(dirname(fileURLToPath(import.meta.url)),"..");
const html=readFileSync(join(root,"site/control-center-preview.html"),"utf8");
const worker=readFileSync(join(root,"site/control-center-preview.worker.js"),"utf8");
assert.ok(html.includes('<main id="content"')&&html.includes('data-page="works"'));
assert.ok(worker.includes('if(request.method!=="GET")'));
assert.ok(worker.includes('if(path==="/api/status")'));
assert.ok(worker.includes('if(path==="/api/check")'));
assert.ok(worker.includes("await getPage()"));
const match=html.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(match,"Inline UI script missing");
new Script(match[1],{filename:"control-center-preview-inline.js"});
const bundled="const PAGE = "+JSON.stringify(html)+";\n"+worker.replace("await getPage()","PAGE");
new Script(bundled.replace("export default","const DEPLOYED = "),{filename:"control-center-preview-bundled.js"});
const file=join(root,"output/control-center-preview/worker.js");
mkdirSync(dirname(file),{recursive:true});
writeFileSync(file,bundled,"utf8");
console.log("Built read-only Cloudflare preview bundle:",file,bundled.length,"bytes");
