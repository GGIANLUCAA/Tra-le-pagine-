# Aggiornamento esecutivo V77 · 30 ottobre 2026

La ricerca non è più soltanto ipotetica: GitHub Actions [run 41024818174](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41024818174) ha prodotto **un vero JPEG di 6800×3871, 12.130.063 byte, SHA256 `830978840378c93991b16ed9219e1a78343c633aa8b62035fa65bf9f9ff26cd9`**, in artifact **12963745760**. È la derivata *BoschFXD* da Wikimedia Commons (PD-Art/PDM), con colori rimasterizzati: **non** una scansione cromatica ufficiale Prado. È stata estratta e ispezionata come immagine, non un MP4. La licenza e il nome esatto della derivata vanno conservati nel pacchetto.

La registrazione musicale **Water Lily**, Kevin MacLeod, ISRC USUAN1400035, è già disponibile in forma originale con SHA256 `b8c4f3b03a50af34c01a3f3b986a3d411f56a6c0c9a5b00807ccb5d83c74e8c6` e licenza **CC BY 4.0** secondo [scheda ufficiale Incompetech](https://remote.incompetech.com/music/royalty-free/index.html?Search=Search&isrc=USUAN1400035). Credito obbligatorio in tutti e quattro i post, salvo variante con altra registrazione.

La modifica al blocco V58 in questa PR autorizza **solo Bosch P002823 come quarto quadro**; non attiva una serie indiscriminata. Con fonte e musica verificati è ammesso un solo rendering **Cinema Standard** dopo merge/test; i due Critico richiedono ancora nuova traccia Gacrux con verifica costo e ASR, i Museum restano in review/bloccati da V80 e dimensioni Prado non riconciliate. Nessun quinto quadro, V25 automatico o upload privato.

---

# Bosch · The Garden of Earthly Delights — V77 scoped preflight (30 October 2026)

**Operational outcome:** research and recipe prepared; **0 new 4×1 MP4**, **0 renders started**, **0 V25 approvals**, **no queue/lock modifications**. Bosch V22 is a *historical Critico reference*, not one of the four new slots.

## Important primary-source discrepancy

The [Prado collection record](https://www.museodelprado.es/en/the-collection/art-work/triptych-garden-earthly-delights/02388242-6d6a-4e9e-a992-e1311eab3609) gives **185.8 cm panel height, 172.5 cm central panel width, 76.5 cm per wing** (open panels add to 325.5 cm). A [different Prado encyclopedia entry](https://www.museodelprado.es/aprende/enciclopedia/voz/jardin-de-las-delicias-el-el-bosco/578702d4-4420-4e97-8518-8363a1fc2c9e) gives **205.5 × 384.9 cm**. Both are institutionally attributed. **Do not silently select one** for V46 museum scale; clarify panel/overall/frame conventions and document the decision. These are *documented source values*, not measured physical dimensions in this run.

## Authentic art, not a fake museum

The [Commons Bosch Research source](https://commons.wikimedia.org/wiki/File:The_Garden_of_earthly_delights.jpg) advertises 39,137 × 22,279 px and PD-Art; an [alternate high-resolution scan](https://commons.wikimedia.org/wiki/File:The_Garden_of_Earthly_Delights_by_Bosch_High_Resolution.jpg) advertises 30,000 × 17,078 px. These are **candidate pages only**: no source bytes downloaded in this run, so **no SHA256** is claimed. The historical Bosch V21 `BoschFXD` file is described as colour-adjusted: do **not** treat it as unmodified original. Confirm file-level reuse rights, exact image, colour fidelity and Italian jurisdiction before render.

The frame and hinged triptych installation require work-specific V80 evidence. A generic gold border is forbidden; no current Prado room photo or historic frame has been verified or licensed. Current status: `frame_status=unverified`; **both Museum slots blocked**. The painting includes classical nude figures: preserve the original faithfully, select editorial crops appropriate to audience and platform without fabricating costumes or erasing figures.

## Four distinct storyboards (NOT rendered)

1. **Critico Standard:** new professional script and one new verified Gacrux WAV; tree-man in first seconds, then Eden, garden, fruit/riders, glass, Hell, final triptych. Use the **Bosch V22** low-motion 23-shot reference and word-to-subject QA, not its historical MP4 or WAV.
2. **Critico Museum:** **same exact new WAV/script**; single camera path with V76 semantic chapters and V57 continuity, physical panels and work-specific frame. Blocked until V80.
3. **Cinema Standard:** licensed music, no voice; original art details and dramatic Eden→Garden→Hell arc. No asset/license preflight pass yet.
4. **Cinema Museum:** licensed music, no voice; continuous entry/exit, correct scale and unchanged frame/room, no invented opening of wings. Blocked until V80.

**Production gates:** source SHA/rights, dimension reconciliation, V80 frame, exact recording license, voice-cost scope, and **Bosch-only V58 lock extension plus tests**. Do not trigger a paid API or render while blocked. Preserve Socrate/Klimt/Hokusai masters, queue states and other formats.

Machine-readable blockers and shot structure: `ARTVISION_BOSCH_PREFLIGHT_V77.json`.
