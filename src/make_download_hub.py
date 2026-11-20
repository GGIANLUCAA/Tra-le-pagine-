#!/usr/bin/env python3
"""Build a download hub for every produced video.

Scans the output root for MP4s and writes:
  - index.html          preview + "scarica" link per video + ZIP unico
  - SCARICA_TUTTI_I_VIDEO.zip   tutti i video in un solo file

Rilanciare dopo ogni produzione per aggiornare la pagina.
"""
import html, zipfile
from pathlib import Path

ROOT = Path("/workspace/output")
HUB = ROOT / "index.html"
ZIP = ROOT / "SCARICA_TUTTI_I_VIDEO.zip"

FRIENDLY = {
    "REEL_VANGOGH_STARRY_SKIES.mp4": "Social Reel — Van Gogh · Starry Skies",
    "ARTVISION_BOTTICELLI_PRIMAVERA.mp4": "ArtVision Critico — Botticelli · La primavera",
    "ARTVISION_CARAVAGGIO_VOCAZIONE_MATTEO.mp4": "ArtVision Critico — Caravaggio · La vocazione di San Matteo",
}


def title_of(p):
    return FRIENDLY.get(p.name, p.stem.replace("_", " ").title())


def human(n):
    n = float(n)
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {u}" if u == "B" else f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} TB"


def main():
    vids = sorted((p for p in ROOT.rglob("*.mp4") if p.parent != ROOT),
                  key=lambda p: p.stat().st_mtime, reverse=True)

    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_STORED) as z:
        for v in vids:
            z.write(v, v.name)

    cards = []
    for v in vids:
        rel = v.relative_to(ROOT).as_posix()
        poster = v.parent / "COPERTINA.jpg"
        poster_attr = f' poster="{poster.relative_to(ROOT).as_posix()}"' if poster.exists() else ""
        cards.append(f"""    <div class="card">
      <h3>{html.escape(title_of(v))}</h3>
      <div class="sub">{human(v.stat().st_size)} · MP4</div>
      <div class="frame"><video controls playsinline preload="metadata"{poster_attr}>
        <source src="{rel}" type="video/mp4"></video></div>
      <div class="meta"><a class="dl" href="{rel}" download>Scarica MP4</a></div>
    </div>""")

    total = human(sum(v.stat().st_size for v in vids))
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
  .grid{{display:flex;gap:28px;flex-wrap:wrap;justify-content:center;max-width:1180px;margin:26px auto 0}}
  .card{{width:min(92vw,430px)}}
  .card h3{{font-size:17px;margin:0 0 4px;color:var(--gold);letter-spacing:.03em}}
  .card .sub{{font-family:system-ui,sans-serif;font-size:12px;color:#9a9386;margin-bottom:12px}}
  .frame{{border:1px solid rgba(218,198,168,.5);border-radius:14px;overflow:hidden;
         box-shadow:0 30px 80px rgba(0,0,0,.65);background:#000}}
  video{{display:block;width:100%;height:auto}}
  .meta{{margin-top:12px;text-align:center}}
  .dl{{display:inline-block;border:1px solid rgba(218,198,168,.6);border-radius:999px;padding:9px 20px;
       font-family:system-ui,sans-serif;font-size:13px;color:var(--gold);text-decoration:none}}
  .dl:hover{{background:rgba(218,198,168,.12)}}
</style>
</head>
<body>
  <header>
    <h1>Video prodotti</h1>
    <h2>{len(vids)} video · {total}</h2>
    <a class="all" href="{ZIP.name}" download>Scarica TUTTI i video (ZIP)</a>
    <div class="hint">oppure scarica i singoli video qui sotto</div>
  </header>
  <div class="grid">
{chr(10).join(cards)}
  </div>
</body>
</html>
""", encoding="utf-8")

    print(f"videos: {len(vids)} (total {total})")
    for v in vids:
        print("  -", v.relative_to(ROOT))
    print(f"ZIP:  {ZIP.name} ({human(ZIP.stat().st_size)})")
    print(f"HUB:  {HUB}")


if __name__ == "__main__":
    main()
