#!/usr/bin/env python3
"""Build a download hub for EVERY produced video.

Two sources are merged:
  1. Local MP4s found under /workspace/output  (direct download + ZIP)
  2. The full public video library (Cloudflare worker) /api/catalog
     -> every item is linked to /media/<key> (mp4) and /cover/<key> (jpeg)

Writes:
  - index.html                  preview + single download link per video
  - SCARICA_TUTTI_I_VIDEO.zip   every LOCAL video in one file

Re-run after each production to refresh the page.
"""
import html, json, subprocess, urllib.request, zipfile
from pathlib import Path

ROOT = Path("/workspace/output")
HUB = ROOT / "index.html"
ZIP = ROOT / "SCARICA_TUTTI_I_VIDEO.zip"
CATALOG_JSON = ROOT / "_catalog.json"

LIB = "https://video-library-studio.600led.workers.dev"

FRIENDLY = {
    "REEL_VANGOGH_STARRY_SKIES.mp4": "Social Reel — Van Gogh · Starry Skies",
    "ARTVISION_BOTTICELLI_PRIMAVERA.mp4": "ArtVision Critico — Botticelli · La primavera",
    "ARTVISION_CARAVAGGIO_VOCAZIONE_MATTEO.mp4": "ArtVision Critico — Caravaggio · La vocazione di San Matteo",
}


def title_of(p):
    return FRIENDLY.get(p.name, p.stem.replace("_", " ").title())


def human(n):
    n = float(n or 0)
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {u}" if u == "B" else f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} TB"


def mmss(sec):
    sec = int(round(sec or 0))
    return f"{sec // 60}:{sec % 60:02d}"


def _fetch_catalog():
    # some egress paths block the default python UA -> use curl, then urllib.
    try:
        out = subprocess.run(["curl", "-s", "--max-time", "40", f"{LIB}/api/catalog"],
                             capture_output=True, text=True, check=True).stdout
        if out.strip():
            return json.loads(out)
    except Exception:
        pass
    req = urllib.request.Request(f"{LIB}/api/catalog", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def load_catalog():
    try:
        data = _fetch_catalog()
    except Exception:
        if CATALOG_JSON.exists():
            data = json.loads(CATALOG_JSON.read_text())
        else:
            return []
    items = data if isinstance(data, list) else data.get("items", [])
    items = [i for i in items if i.get("available", True)]
    CATALOG_JSON.write_text(json.dumps(items, ensure_ascii=False))
    return items


def pretty_name(it):
    name = it.get("name") or it.get("key", "")
    stem = Path(name).stem
    # "01_Klimt_Critico_Standard_Gacrux" -> "Klimt Critico Standard Gacrux"
    return stem.replace("_", " ").strip().title()


def local_cards(vids):
    out = []
    for v in vids:
        rel = v.relative_to(ROOT).as_posix()
        poster = v.parent / "COPERTINA.jpg"
        poster_attr = f' poster="{poster.relative_to(ROOT).as_posix()}"' if poster.exists() else ""
        out.append(f"""    <div class="card">
      <h3>{html.escape(title_of(v))}</h3>
      <div class="sub">{human(v.stat().st_size)} · MP4</div>
      <div class="frame"><video controls playsinline preload="metadata"{poster_attr}>
        <source src="{rel}" type="video/mp4"></video></div>
      <div class="meta"><a class="dl" href="{rel}" download>Scarica MP4</a></div>
    </div>""")
    return out


def library_cards(items):
    out = []
    for it in items:
        key = it.get("key", "")
        media = f"{LIB}/media/{key}"
        cover = f"{LIB}/cover/{key}"
        ttl = html.escape(it.get("title") or pretty_name(it))
        cat = html.escape(it.get("category") or "")
        meta = f"{human(it.get('size'))}"
        if it.get("duration"):
            meta += f" · {mmss(it['duration'])}"
        if it.get("width") and it.get("height"):
            meta += f" · {it['width']}×{it['height']}"
        out.append(f"""    <div class="card">
      <h3>{ttl}</h3>
      <div class="sub">{cat} · {meta}</div>
      <a class="frame" href="{media}" download><img loading="lazy" src="{cover}" alt=""></a>
      <div class="meta"><a class="dl" href="{media}" download>Scarica MP4</a></div>
    </div>""")
    return out


def main():
    vids = sorted((p for p in ROOT.rglob("*.mp4") if p.parent != ROOT),
                  key=lambda p: p.stat().st_mtime, reverse=True)

    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_STORED) as z:
        for v in vids:
            z.write(v, v.name)

    catalog = load_catalog()
    local_total = human(sum(v.stat().st_size for v in vids))
    lib_total = human(sum(i.get("size") or 0 for i in catalog))

    HUB.write_text(f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Video prodotti — download</title>
<style>
  :root{{--ink:#0d0f15;--ivory:#f8f4ec;--gold:#dac6a8}}
  *{{box-sizing:border-box}}
  body{{margin:0;background:radial-gradient(120% 80% at 50% 0%,#1a1c24 0%,#0d0f15 60%);color:var(--ivory);
       font-family:Georgia,'Times New Roman',serif;min-height:100vh;padding:32px 16px}}
  header{{text-align:center;margin-bottom:24px}}
  h1{{font-size:20px;letter-spacing:.14em;text-transform:uppercase;font-weight:400;margin:0 0 6px;color:var(--gold)}}
  h2{{font-size:26px;margin:0 0 16px;font-weight:500}}
  .all{{display:inline-block;background:var(--gold);color:#0d0f15;font-family:system-ui,sans-serif;
        font-size:15px;font-weight:600;padding:12px 24px;border-radius:999px;text-decoration:none;margin-bottom:6px}}
  .all:hover{{filter:brightness(1.08)}}
  .hint{{font-family:system-ui,sans-serif;font-size:12px;color:#9a9386}}
  h3.sec{{max-width:1180px;margin:40px auto 0;font-size:15px;letter-spacing:.1em;text-transform:uppercase;
          color:var(--gold);font-weight:400;border-bottom:1px solid rgba(218,198,168,.3);padding-bottom:8px}}
  .grid{{display:flex;gap:28px;flex-wrap:wrap;justify-content:center;max-width:1180px;margin:22px auto 0}}
  .card{{width:min(92vw,330px)}}
  .card h3{{font-size:15px;margin:0 0 4px;color:var(--gold);letter-spacing:.02em}}
  .card .sub{{font-family:system-ui,sans-serif;font-size:12px;color:#9a9386;margin-bottom:10px}}
  .frame{{display:block;border:1px solid rgba(218,198,168,.5);border-radius:14px;overflow:hidden;
         box-shadow:0 30px 80px rgba(0,0,0,.65);background:#000}}
  video,.frame img{{display:block;width:100%;height:auto}}
  .meta{{margin-top:10px;text-align:center}}
  .dl{{display:inline-block;border:1px solid rgba(218,198,168,.6);border-radius:999px;padding:8px 18px;
       font-family:system-ui,sans-serif;font-size:13px;color:var(--gold);text-decoration:none}}
  .dl:hover{{background:rgba(218,198,168,.12)}}
</style>
</head>
<body>
  <header>
    <h1>Video prodotti</h1>
    <h2>{len(vids) + len(catalog)} video in totale</h2>
    <a class="all" href="{ZIP.name}" download>Scarica TUTTI i video locali (ZIP · {local_total})</a>
    <div class="hint">{len(vids)} video sul server (subito pronti) + {len(catalog)} in libreria ({lib_total})</div>
  </header>

  <h3 class="sec">I tuoi video — pronti sul server</h3>
  <div class="grid">
{chr(10).join(local_cards(vids))}
  </div>

  <h3 class="sec">Libreria completa — {len(catalog)} video</h3>
  <div class="grid">
{chr(10).join(library_cards(catalog))}
  </div>
</body>
</html>
""", encoding="utf-8")

    print(f"local videos: {len(vids)} (total {local_total})")
    for v in vids:
        print("  -", v.relative_to(ROOT))
    print(f"library videos: {len(catalog)} (total {lib_total})")
    print(f"ZIP:  {ZIP.name} ({human(ZIP.stat().st_size)})")
    print(f"HUB:  {HUB}")


if __name__ == "__main__":
    main()
