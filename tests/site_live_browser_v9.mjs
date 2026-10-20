/* Chromium against the real published GitHub Pages site.
 * No API mocks, no authentication, no render launches, no paid AI.
 */
import {chromium} from "playwright";
import assert from "node:assert/strict";
import {mkdirSync} from "node:fs";
const URL="https://ggianlucaa.github.io/Tra-le-pagine-/";
const DEST="test-screenshots";
mkdirSync(DEST,{recursive:true});

async function main() {
  const browser=await chromium.launch({headless:true});
  try {
    const ctx=await browser.newContext({viewport:{width:390,height:844},
      deviceScaleFactor:2,isMobile:true,hasTouch:true,locale:"it-IT"});
    const page=await ctx.newPage(),errors=[];
    page.on("pageerror",e=>errors.push(e.message));
    const response=await page.goto(URL,{waitUntil:"domcontentloaded",timeout:30000});
    assert.equal(response?.status(),200,"Published site must return HTTP 200");
    await page.locator("#stat-episodes").waitFor({state:"visible",timeout:10000});
    await page.waitForFunction(()=>{
      const n=document.querySelector("#stat-episodes")?.textContent?.trim();
      return n && /^\d+$/.test(n);
    },null,{timeout:20000});
    const episodeCount=Number(await page.locator("#stat-episodes").textContent());
    assert.ok(episodeCount>=1,"Episodes are visible from real GitHub API");
    await page.screenshot({path:DEST+"/real-site-android.png",fullPage:true});
    console.log("REAL PASS: Pages HTTPS 200, actual GitHub episodes =",episodeCount);
    await page.locator("#menu-open").click();
    await page.locator(".sidebar [data-tab='episodi']").click();
    const shown=await page.locator("#episode-grid .episode-card").count();
    assert.equal(shown,episodeCount);
    console.log("REAL PASS: actual episodes loaded and navigable =",shown);
    assert.deepEqual(errors,[],"No JavaScript runtime exceptions on live site");
    console.log("REAL PASS: no browser JavaScript runtime exceptions");
    await ctx.close();
  } finally {
    await browser.close();
  }
}
main().catch(e=>{console.error("REAL BROWSER FAILURE",e);process.exitCode=1;});
