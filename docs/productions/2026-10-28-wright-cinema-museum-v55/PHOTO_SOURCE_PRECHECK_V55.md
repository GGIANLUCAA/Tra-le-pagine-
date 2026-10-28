# Wright V55 — Actual source photo preflight and blockers

The first generated Wright Museum MP4 was **rejected** (SHA256 `21a8112cd95d2326221654cb49a2d22518f72aa69dd3abbb3677403518050800`): the claimed framed gallery source was visually a cropped detail, so the result showed a rectangle floating in black matte. It is not a valid Museum variant.

**Independent photo probe:** [GitHub run 40779722427](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/40779722427), followed by [retry run 40779884173](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/40779884173), both with downloadable JPEG contact sheets and real source hashes.

| Source | Actual visual inspection | Licence on Wikimedia Commons | Result |
|---|---|---|---|
| [Ad Meskens 2019 photo](https://commons.wikimedia.org/wiki/File:London_National_Gallery_Wright_of_Derby_Experiment_on_a_Bird_in_an_Air_Pump.jpg) | Tight crop of lecturer, bird and faces, **no frame or room** | CC BY-SA 4.0, author credit required | REJECTED as museum photo, SHA256 `b82ea9c5ca81ab220a4d34f908293e920293b15a2b7eaa0215ac14a92c0dd523` |
| [Steve Knight April 2025 photo](https://commons.wikimedia.org/wiki/File:Joseph_Wright_of_Derby_-_An_experiment_on_a_bird_with_an_air_pump_-_1768.jpg) | Nearly whole painting but **no gilded frame or wall** | CC BY 2.0 | REJECTED as museum frame source; SHA256 `3710d350ef4dea2eda51ecc5d00ef2a9fc3e53bd36d45634202a96af9b5d2166` |
| [Steve Knight December 2025 photo](https://commons.wikimedia.org/wiki/File:An_Experiment_on_a_bird_in_an_air_pump_1768_Joseph_Wright_of_Derby_-_54977535687.jpg) | Nearly whole painting but **no gilded frame or wall** | CC BY 4.0 | REJECTED as museum frame source; SHA256 `0ae471d28eba0a1ea6e48bb6e470000bcafee18f84f39f80d2be62430bdc80a2` |
| [Tristan Surtel framed photo](https://commons.wikimedia.org/wiki/File:An_Experiment_on_a_Bird_in_the_Air_Pump.jpg) | Wikimedia thumbnail visually shows a **genuine gilded border around the whole painting**, but full source bytes NOT acquired | Commons labels Public Domain Mark; 3D frame photo rights require independent review | **POTENTIAL SOURCE**, blocked download HTTP 429 from upload.wikimedia on both direct and redirect routes |

**Museum data:** National Gallery NG725; actual oil painting 183 × 244 cm, frame described by the museum as nineteenth-century English, oil-gilded; outer frame measurements not verified. The picture is on loan to Derby Museums until 1 November 2026; 2018/2019/2025 London photos are historical, not current location.

**Next safe action:** obtain a genuinely framed, correctly licensed photo (or a clearly declared tasteful reconstruction that matches the real frame and physical scale); visually inspect the source pixels BEFORE render; correct artist/photographer/rights/hashtags in four posts and manifest; run the 4x1 structural gate, then one distinct Museum render. No retry on paid AI video services. Keep V52B Cinema Standard untouched. Do not mark this Museum variant rendered, approved or online.

**Prevention implemented:** `scripts/artvision_wright_cinema_museum_v55.py` rejects the known cropped-source SHA before render. The source-selection and rights metadata still need updating when a valid full-frame asset is acquired. No automatic social publication or site import.
