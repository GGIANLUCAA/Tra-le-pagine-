/* Real Chromium smoke: simulate Android viewport against locally served V9 files.
 * The GitHub API is safely mocked to test UI behavior, not live data claims.
 */
import {chromium} from "playwright";
import assert from "node:assert/strict";
import {mkdirSync} from "node:fs";

const ROOT=process.env.TEST_URL || "http://127.0.0.1:8765/";
const SCREEN=process.env.SCREEN_DIR || "test-screenshots";
mkdirSync(SCREEN,{recursive:true});

async function run() {
  const browser=await chromium.launch({headless:true});
  const context=await browser.newContext({viewport:{width:390,height:844},
    deviceScaleFactor:2,isMobile:true,hasTouch:true,locale:"it-IT"});
  const page=await context.newPage();
  const issues=[];
  page.on("pageerror",error=>issues.push(String(error)));
  // Intercept API for reproducible test; the public live test runs separately.
  await page.route(/^https:\/\/api\.github\.com\/repos\/GGIANLUCAA\/Tra-le-pagine-\/.*/,async route=>{
    const path=new URL(route.request().url()).pathname;
    const data=path.endsWith("/contents/episodes")
      ? [{type:"dir",name:"01_scacchi"},{type:"dir",name:"03_siddharta"}]
      : path.endsWith("/releases")
        ? [{tag_name:"tlp-video-01_scacchi-39171898138",name:"Tra le Pagine · La novella degli scacchi",
          draft:false,prerelease:false,published_at:"2026-10-20T00:00:00Z",
          assets:[{name:"TRA_LE_PAGINE_VIDEO.mp4",size:2_000_000,state:"uploaded",
          browser_download_url:"https://github.com/GGIANLUCAA/Tra-le-pagine-/releases/download/tlp-video-01_scacchi-39171898138/TRA_LE_PAGINE_VIDEO.mp4"}]}]
      : path.endsWith("/actions/runs")
        ? {workflow_runs:[{id:12345678,display_title:"Siddharta",name:"Render con voce Google",
            created_at:"2026-10-20T00:00:00Z",status:"completed",conclusion:"success"}]}
        : {};
    await route.fulfill({status:200,contentType:"application/json",body:JSON.stringify(data)});
  });
  await page.goto(ROOT,{waitUntil:"domcontentloaded",timeout:30000});
  await page.locator("#stat-episodes").getByText("2").waitFor({timeout:15000});
  await page.locator("#stat-runs").getByText("1").waitFor();
  await page.locator("#backend-status").getByText("Modalità GitHub guidata").waitFor();
  assert.match(await page.title(),/Tra le Pagine/);
  await page.screenshot({path:SCREEN+"/home-mobile.png",fullPage:true});
  console.log("PASS: Home mobile, live-shaped GitHub data, no OAuth secrets");

  await page.locator("button[data-go='nuovo']").first().click();
  await page.locator("#video-title").fill("Siddharta — Una ricerca");
  await page.locator("#video-idea").fill(
    "Racconta la storia di Siddharta con immagini cinematografiche coerenti e narrazione naturale in italiano.");
  await page.locator("#save-brief").click();
  await page.locator("#saved-projects .saved-card").getByText("Siddharta — Una ricerca").waitFor();
  await page.reload({waitUntil:"domcontentloaded"});
  await page.locator("#saved-projects .saved-card").getByText("Siddharta — Una ricerca").waitFor();
  console.log("PASS: local draft persistence on mobile");

  await page.locator("#menu-open").click();
  await page.locator(".sidebar .nav-item[data-tab='videoteca']").click();
  await page.locator("#videos-grid .video-tile").first().waitFor();
  await page.locator("#videos-grid [data-watch='01_scacchi']").click();
  await page.locator("#public-video-dialog").waitFor({state:"visible"});
  assert.match(await page.locator("#public-video-download").getAttribute("href"),/TRA_LE_PAGINE_VIDEO\.mp4$/);
  await page.screenshot({path:SCREEN+"/videoteca-v11-android.png",fullPage:true});
  await page.locator("#public-video-close").click();
  console.log("PASS: V11 direct MP4 library, video player and download link (mock Release)");
  await page.locator("#menu-open").click();
  await page.locator(".sidebar .nav-item[data-tab='episodi']").click();
  await page.locator("#episode-grid .episode-card").first().waitFor();
  await page.locator("#episode-grid .episode-card").last().click();
  await page.locator("#selected-panel").waitFor({state:"visible"});
  await page.locator("#episode-grid .episode-preview-btn").last().click();
  await page.locator("#episode-preview").waitFor({state:"visible"});
  await page.locator("#preview-heading").getByText(/siddharta/i).waitFor();
  await page.locator("#preview-no-scenes").waitFor({state:"visible"});
  await page.locator("#preview-file").waitFor({state:"attached"});
  await page.screenshot({path:SCREEN+"/preview-mobile.png",fullPage:true});
  await page.locator("#preview-close").click();
  console.log("PASS: V10 preview shows honest missing-media state and private MP4 picker");
  const renderLabel=await page.locator("#action-render").textContent();
  assert.match(renderLabel,/Google/);
  await page.screenshot({path:SCREEN+"/episodes-mobile.png",fullPage:true});
  console.log("PASS: mobile sidebar and episode selection (Google still default)");

  await page.locator("#menu-open").click();
  await page.locator(".sidebar .nav-item[data-tab='archivio']").click();
  await page.locator("#media-query").fill("ancient river India");
  await page.locator("#media-import").waitFor({state:"visible"});
  await page.screenshot({path:SCREEN+"/archive-mobile.png",fullPage:true});
  console.log("PASS: V7 archive, search and selective import controls");

  await page.locator("#menu-open").click();
  await page.locator(".sidebar .nav-item[data-tab='produzioni']").click();
  await page.locator("#all-runs .run-item").first().waitFor();
  const href=await page.locator("#all-runs .run-item").first().getAttribute("href");
  assert.equal(href,"https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/12345678");
  await page.screenshot({path:SCREEN+"/runs-mobile.png",fullPage:true});
  console.log("PASS: productions list opens official GitHub run");

  assert.deepEqual(issues,[], "Unexpected browser JS runtime errors");
  console.log("PASS: no browser JavaScript runtime errors");

  await context.close();
  await browser.close();
}
run().catch(e=>{console.error("E2E FAILED:",e);process.exitCode=1;});
