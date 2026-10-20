import test from "node:test";
import assert from "node:assert/strict";
import {normalizeRelease} from "../docs/videoteca_v11.js";

const base="https://github.com/GGIANLUCAA/Tra-le-pagine-/releases/download/";
const example={
  tag_name:"tlp-video-01_scacchi-39171898138",
  name:"Tra le Pagine · La novella degli scacchi",
  draft:false,prerelease:false,
  published_at:"2026-10-20T04:09:00Z",
  assets:[{name:"TRA_LE_PAGINE_VIDEO.mp4",size:4_000_000,state:"uploaded",
    browser_download_url:base+"tlp-video-01_scacchi-39171898138/TRA_LE_PAGINE_VIDEO.mp4"}]
};

test("recognizes only approved tag + actual uploaded MP4",()=>{
  const video=normalizeRelease(example);
  assert.equal(video.slug,"01_scacchi");
  assert.equal(video.run,"39171898138");
  assert.match(video.url,/TRA_LE_PAGINE_VIDEO\.mp4$/);
  assert.equal(video.public,true);
});
test("never treats random GitHub release or source code as episode video",()=>{
  for(const tag of ["v10.0","tlp-video-../secret-39171898138","tlp-video-01_scacchi-noid"]){
    assert.equal(normalizeRelease({...example,tag_name:tag}),null);
  }
});
test("drafts and prereleases not shown in studio",()=>{
  assert.equal(normalizeRelease({...example,draft:true}),null);
  assert.equal(normalizeRelease({...example,prerelease:true}),null);
});
test("invalid asset host, extension, size or upload state rejected",()=>{
  for(const asset of [
    {...example.assets[0],name:"raw.zip"},
    {...example.assets[0],browser_download_url:"https://evil.invalid/file.mp4"},
    {...example.assets[0],size:150_000_000},
    {...example.assets[0],state:"new"},
  ])assert.equal(normalizeRelease({...example,assets:[asset]}),null);
});
test("no MP4 means no fake playable video",()=>{
  assert.equal(normalizeRelease({...example,assets:[]}),null);
});
