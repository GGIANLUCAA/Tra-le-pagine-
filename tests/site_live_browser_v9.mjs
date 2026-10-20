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
    const genuineCard=page.locator('#episode-grid [data-episode="01_scacchi"]');
    await genuineCard.waitFor({state:"visible"});
    const cover=genuineCard.locator("img");
    await cover.waitFor({state:"visible"});
    await page.waitForFunction(()=>{
      const img=document.querySelector('[data-episode="01_scacchi"] img');
      return img && img.complete && img.naturalWidth>100;
    },null,{timeout:15000});
    console.log("REAL PASS: genuine Scacchi cover JPG visible on Android");
    await page.locator('#episode-grid [data-preview="01_scacchi"]').click();
    await page.locator("#episode-preview").waitFor({state:"visible"});
    await page.locator("#preview-frame").waitFor({state:"visible"});
    await page.waitForFunction(()=>{
      const img=document.querySelector("#preview-frame");
      return img && img.complete && img.naturalWidth>100;
    },null,{timeout:15000});
    const slideCount=await page.locator("#preview-slide-count").textContent();
    assert.match(slideCount,/1 \/ 5/);
    await page.screenshot({path:DEST+"/real-gallery-scacchi-v10.png",fullPage:true});
    await page.locator("#preview-next").click();
    await page.locator("#preview-slide-count").getByText("2 / 5").waitFor();
    await page.locator("#preview-close").click();
    console.log("REAL PASS: gallery slides load real photos and controls work");
    await page.locator("#menu-open").click();
    await page.locator(".sidebar [data-tab='videoteca']").click();
    await page.locator("#view-videoteca").waitFor({state:"visible"});
    await page.locator("#videos-grid").waitFor({state:"visible"});
    await page.screenshot({path:DEST+"/real-videoteca-v11.png",fullPage:true});
    console.log("REAL PASS: video library V11 visible on actual public site");
    await page.locator("#menu-open").click();
    await page.locator(".sidebar [data-tab='nuovo']").click();
    await page.locator("#autopilot-create").waitFor({state:"visible"});
    await page.screenshot({path:DEST+"/real-creator-v11.png",fullPage:true});
    console.log("REAL PASS: story-to-video beta control available on mobile");
    assert.deepEqual(errors,[],"No JavaScript runtime exceptions on live site");
    console.log("REAL PASS: no browser JavaScript runtime exceptions");
    await ctx.close();
  } finally {
    await browser.close();
  }
}
main().catch(e=>{console.error("REAL BROWSER FAILURE",e);process.exitCode=1;});
