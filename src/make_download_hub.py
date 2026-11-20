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
PREVIEW_SUFFIX = "_preview.mp4"   # light 540p proxy used by the in-page player

FRIENDLY = {
    "REEL_VANGOGH_V5.mp4": "Social Reel V5 — Van Gogh · DIRECTED cut, timing-polished (tagli centrati sul beat, 1080p)",
    "REEL_VANGOGH_V4.mp4": "Social Reel V4 — Van Gogh · DIRECTED cut (dettagli + campo intero + carrellate, 1080p)",
    "REEL_VANGOGH_V3.mp4": "Social Reel V3 — Van Gogh · Gallery cut (quadri interi, fluido)",
    "REEL_VANGOGH_V2.mp4": "Social Reel V2 — Van Gogh · Starry Skies (cinema / beat-locked)",
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


def ensure_preview(v):
    """Build a light 540p proxy (fast to stream) for a local master video."""
    pv = v.with_name(v.stem + PREVIEW_SUFFIX)
    if pv.exists() and pv.stat().st_mtime >= v.stat().st_mtime:
        return pv
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(v),
           "-vf", "scale=540:-2", "-c:v", "libx264", "-crf", "26",
           "-maxrate", "2M", "-bufsize", "4M", "-preset", "veryfast",
           "-profile:v", "high", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
           "-c:a", "aac", "-b:a", "96k", str(pv)]
    try:
        subprocess.run(cmd, check=True)
        return pv
    except Exception as e:                                   # noqa: BLE001
        print(f"  preview failed for {v.name}: {e}")
        return None


def local_cards(vids):
    out = []
    for v in vids:
        rel = v.relative_to(ROOT).as_posix()
        pv = ensure_preview(v)
        src = pv.relative_to(ROOT).as_posix() if pv else rel
        poster = v.parent / "COPERTINA.jpg"
        poster_rel = poster.relative_to(ROOT).as_posix() if poster.exists() else ""
        title = html.escape(title_of(v))
        img = (f'<img loading="lazy" src="{poster_rel}" alt="">' if poster_rel
               else '<div style="aspect-ratio:9/16;background:#111"></div>')
        out.append(f"""    <div class="card" data-t="{title.lower()}">
      <h3>{title}</h3>
      <div class="sub">{human(v.stat().st_size)} · player 540p · streaming</div>
      <div class="frame" data-src="{src}" data-poster="{poster_rel}">{img}</div>
      <div class="meta"><a class="dl" href="{rel}" download>Scarica {human(v.stat().st_size)} (1080p)</a></div>
    </div>""")
    return out


def library_cards(items):
    out = []
    for it in items:
        key = it.get("key", "")
        media = f"{LIB}/media/{key}"
        # catalog gives the cover path without extension; fall back to stripped key
        cpath = it.get("cover") or f"/cover/{Path(key).stem}"
        cover = cpath if cpath.startswith("http") else f"{LIB}{cpath}"
        ttl = html.escape(it.get("title") or pretty_name(it))
        cat = html.escape(it.get("category") or "")
        meta = f"{human(it.get('size'))}"
        if it.get("duration"):
            meta += f" · {mmss(it['duration'])}"
        if it.get("width") and it.get("height"):
            meta += f" · {it['width']}×{it['height']}"
        data_t = html.escape(f"{ttl} {cat}".lower(), quote=True)
        out.append(f"""    <div class="card" data-t="{data_t}">
      <h3>{ttl}</h3>
      <div class="sub">{cat} · {meta}</div>
      <div class="frame" data-src="{media}" data-poster="{cover}">
        <img loading="lazy" src="{cover}" alt=""></div>
      <div class="meta"><a class="dl" href="{media}" download>Scarica MP4</a></div>
    </div>""")
    return out


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    vids = sorted((p for p in ROOT.rglob("*.mp4")
                   if p.parent != ROOT and not p.name.endswith(PREVIEW_SUFFIX)),
                  key=lambda p: p.stat().st_mtime, reverse=True)

    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_STORED) as z:
        for v in vids:
            z.write(v, v.name)

    catalog = load_catalog()
    local_total = human(sum(v.stat().st_size for v in vids))
    lib_total = human(sum(i.get("size") or 0 for i in catalog))

    if vids:
        hero = (f'<a class="all" href="{ZIP.name}" download>'
                f'Scarica TUTTI i video locali (ZIP · {local_total})</a>')
        local_block = (f'  <h3 class="sec">I tuoi video — pronti sul server</h3>\n'
                       f'  <div class="grid">\n{chr(10).join(local_cards(vids))}\n  </div>\n\n')
        hint = f"{len(vids)} video sul server (subito pronti) + {len(catalog)} in libreria ({lib_total})"
    else:
        hero = ""
        local_block = ""
        hint = f"Nessun video locale al momento — {len(catalog)} video disponibili in libreria ({lib_total})"

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
         box-shadow:0 30px 80px rgba(0,0,0,.65);background:#000;position:relative}}
  video,.frame img{{display:block;width:100%;height:auto}}
  .frame[data-src]{{cursor:pointer}}
  .frame[data-src]::after{{content:"▶";position:absolute;inset:0;display:flex;align-items:center;
    justify-content:center;font-size:42px;color:#fff;text-shadow:0 2px 20px rgba(0,0,0,.85);
    background:radial-gradient(55% 38% at 50% 50%,rgba(0,0,0,.30),transparent 72%)}}
  .frame[data-src]:hover::after{{background:radial-gradient(55% 38% at 50% 50%,rgba(0,0,0,.48),transparent 72%)}}
  .search{{font-family:system-ui,sans-serif;font-size:14px;padding:11px 16px;border-radius:999px;
    border:1px solid rgba(218,198,168,.5);background:rgba(0,0,0,.35);color:var(--ivory);
    width:min(90vw,420px);margin-top:14px;outline:none}}
  .search:focus{{border-color:var(--gold)}}
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
    <input id="q" class="search" placeholder="Cerca per artista o titolo…" autocomplete="off">
    <div class="hint" style="margin-top:12px"><b id="count" style="color:var(--gold)">{len(vids) + len(catalog)}</b> video — tocca un poster per guardarlo in streaming</div>
    <div style="margin-top:14px">{hero}</div>
    <div class="hint" style="margin-top:8px">{hint}</div>
  </header>

{local_block}  <h3 class="sec">Libreria completa — {len(catalog)} video</h3>
  <div class="grid">
{chr(10).join(library_cards(catalog))}
  </div>
<script>
  var q = document.getElementById('q');
  var count = document.getElementById('count');
  if (q) q.addEventListener('input', function () {{
    var s = this.value.trim().toLowerCase(), n = 0;
    document.querySelectorAll('.card[data-t]').forEach(function (c) {{
      var hit = !s || c.dataset.t.indexOf(s) >= 0;
      c.style.display = hit ? '' : 'none';
      if (hit) n++;
    }});
    count.textContent = n;
  }});
  document.addEventListener('click', function (e) {{
    var f = e.target.closest('.frame[data-src]');
    if (!f) return;
    var v = document.createElement('video');
    v.controls = true; v.autoplay = true; v.playsInline = true;
    v.setAttribute('playsinline', '');
    if (f.dataset.poster) v.poster = f.dataset.poster;
    v.src = f.dataset.src;                  // streams on demand (HTTP Range)
    f.innerHTML = ''; f.appendChild(v); f.removeAttribute('data-src');
  }});
</script>
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
