import { readFileSync } from 'node:fs';
import { strict as assert } from 'node:assert';
const page = readFileSync(new URL('../docs/prelaunch-v18.html', import.meta.url), 'utf8');
const studio = readFileSync(new URL('../docs/index.html', import.meta.url), 'utf8');
const growth = readFileSync(new URL('../docs/creator-growth.html', import.meta.url), 'utf8');
assert.match(page, /<meta name="viewport"/);
assert.match(page, /Esporta selezione/);
assert.match(page, /PRELAUNCH_ADDITIONS_V18.json/);
assert.match(page, /CREATOR_IDEAS_V14.json/);
assert.match(page, /textContent/);
assert.match(page, /localStorage/);
assert.match(page, /status:'editorial_ideas_only'/);
assert.doesNotMatch(page, /GEMINI_API_KEY|github_pat_|Bearer [A-Za-z0-9]/);
assert.match(studio, /href="\.\/prelaunch-v18.html"/);
assert.match(growth, /href="\.\/prelaunch-v18.html"/);
const script = page.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(script, 'Mobile page script missing');
new Function(script[1]); // Parse only, do not require DOM or external browser APIs in Node.
console.log('Prelaunch V18: mobile page links, local selection and JavaScript syntax OK.');
