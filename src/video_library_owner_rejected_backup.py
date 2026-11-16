#!/usr/bin/env python3
"""Back up owner-rejected public R2 media to a private-to-repo GitHub Actions artifact.

READ ONLY: downloads existing PUBLIC website objects, checks original size,
R2 ETag, and complete SHA256; emits a zip + manifest. Never uploads or deletes
anything in Cloudflare R2. Keep the exact backup artifact if a delete is done.
"""
import argparse
import hashlib
import json
import pathlib
import sys
import time
import urllib.parse
import zipfile
import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "reports/video_library_owner_discard_20261116.json"
ORIGIN = "https://video-library-studio.600led.workers.dev"
MAX_FILE = 64 * 1024 * 1024
MAX_SUM = 130 * 1024 * 1024


def validate(doc):
    assert doc["schema"] == "video-library-owner-discard-v1"
    assert doc["status"] == "PENDING_BACKUP_AND_LIVE_VALIDATION"
    rows = doc["files"]
    assert len(rows) == 17
    names = [x["key"] for x in rows]
    assert len(set(names)) == len(names)
    assert sum(x["bytes"] for x in rows) == doc["counts"]["mp4Bytes"]
    assert sum(x["cover"]["bytes"] for x in rows) == doc["counts"]["coverBytes"]
    for item in rows:
        assert item["genre"] in ("musical_note_visualizer", "technical_visual_effect_demo")
        assert not item["deleted"] and not item["hidden"]
        assert 0.5 < item["duration"] < 60
        assert 1000 <= item["bytes"] <= MAX_FILE
        assert item["cover"]["key"] == item["key"].removesuffix(".mp4") + ".jpg"
        assert "/" not in item["key"] and ".." not in item["key"]
    assert doc["actualDeletedBytes"] == 0
    return rows


def download(session, uri, destination, expected_bytes, etag=None):
    # No user cookies/tokens; the files are already public. Streaming prevents
    # accidental large downloads if the remote object unexpectedly changes.
    for attempt in range(3):
        try:
            with session.get(uri, stream=True, timeout=(20, 100),
                             headers={"Accept-Encoding": "identity"}) as response:
                response.raise_for_status()
                if response.status_code != 200:
                    raise ValueError(f"Non-200 source: {response.status_code} {uri}")
                h=response.headers
                if etag and h.get("etag", "").strip('"') != etag:
                    raise ValueError("ETag no longer matches storage inventory: " + uri)
                if h.get("content-length") and int(h["content-length"]) != expected_bytes:
                    raise ValueError("Content-Length changed: " + uri)
                sha=hashlib.sha256()
                count=0
                with destination.open("wb") as out:
                    for block in response.iter_content(1024 * 1024):
                        if not block:
                            continue
                        count+=len(block)
                        if count>expected_bytes or count>MAX_FILE:
                            raise ValueError("Unexpected download size: " + uri)
                        sha.update(block)
                        out.write(block)
                if count != expected_bytes:
                    raise ValueError(f"Truncated download: {uri} ({count}/{expected_bytes})")
                return sha.hexdigest()
        except (requests.RequestException, OSError) as err:
            if attempt==2:
                raise
            time.sleep(2*(attempt+1))
    raise RuntimeError("Unreachable")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",type=pathlib.Path,default=SOURCE)
    ap.add_argument("--output-dir",type=pathlib.Path,default=pathlib.Path("private_backup"))
    args=ap.parse_args()
    doc=json.loads(args.manifest.read_text(encoding="utf-8"))
    rows=validate(doc)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    cache=args.output_dir / "payload"
    cache.mkdir(exist_ok=True)
    artifacts=[]
    total=0
    with requests.Session() as session:
        for item in rows:
            for rec,resource in [(item,"media"),(item["cover"],"cover")]:
                filename=rec["key"]
                expected=int(rec["bytes"])
                total+=expected
                if total>MAX_SUM:
                    raise ValueError("Backup exceeded total cap")
                raw=filename if resource=="media" else filename.removesuffix(".jpg")
                url=ORIGIN+"/"+resource+"/"+urllib.parse.quote(raw,safe="")
                dst=cache/filename
                sha=download(session,url,dst,expected,rec.get("etag"))
                artifacts.append({"key":filename,"origin":resource,"bytes":expected,
                                  "etag":rec["etag"],"sha256":sha})
                print(f"Verified {resource}: {filename} ({expected} bytes)",flush=True)
    checked={
        "sourceManifest":args.manifest.name,"schema":"vls-owner-rejected-backup-v1",
        "sourceBucket":"video-library-studio","countMP4":len(rows),
        "totalMediaAndCoverBytes":total,
        "sha256Verified":True,
        "uploadTarget":"GitHub Actions artifact for rollback ONLY",
        "objects":artifacts
    }
    (args.output_dir/"verified_manifest.json").write_text(
       json.dumps(checked,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    archive=args.output_dir/"VIDEO_LIBRARY_REJECTED_RECOVERY_20261116.zip"
    with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_STORED) as z:
        z.write(args.manifest,arcname="source_cleanup_manifest.json")
        z.write(args.output_dir/"verified_manifest.json",arcname="verified_manifest.json")
        for row in artifacts:
            z.write(cache/row["key"],arcname="objects/"+row["key"])
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None, "Backup CRC self-test failed"
        assert len(z.namelist())==len(artifacts)+2
    sha=hashlib.sha256(archive.read_bytes()).hexdigest()
    print(json.dumps({"backupReady":True,"backupArchive":str(archive),
                      "backupArchiveSHA256":sha,"mp4":len(rows),
                      "objects":len(artifacts),"bytes":total},indent=2),flush=True)


if __name__ == "__main__":
    main()
