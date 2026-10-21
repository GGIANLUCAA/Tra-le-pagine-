# Regia e controllo qualità V17 — componente aggiuntivo gratuito

Questa versione NON modifica Cinema V6 Gold Master, Critico V2, libri V12, i vecchi preset, la voce Google Gemini Gacrux, le copertine, gli asset o i workflow dei video già consegnati. Non aggiunge API, modelli GPU, server a pagamento o pubblicazione automatica.

## Cosa è realmente operativo

- `src/quality_director_v17.py`: una revisione *offline* che legge la scheda PROJECT_V13.json e, se disponibile, un MP4 già renderizzato.
- `config/quality_director_v17.json`: checklist specializzate per **libri**, **ArtVision Cinema V6**, **Critico V2**, **Controluce**, **Visual Music** e **HyperLumen**.
- Prima del render: descrizioni di scena, motivazione delle focali, ancore del parlato, presenza e dimensione immagini, autorizzazioni dichiarate, immagini consecutive percettivamente simili.
- Dopo il render: presenza tracce video/audio, sottotitoli indesiderati, risoluzione, formato verticale, pause audio prolungate e fotogrammi quasi neri tra gli **otto campioni già estratti da V16**. Nessun secondo render e nessuna chiamata a modelli.
- Report `QUALITY_REPORT_V17.json` e pagina mobile `QUALITY_REVIEW_V17.html` consultabile offline su Android.
- L'esecutore V16 prova a generare il report dopo il suo **review_kit**. Se il nuovo controllo fallisce, salva `QUALITY_V17_ERROR.txt`, senza scartare l'MP4 e senza modificare la qualificazione V16.

## Cosa NON sa fare

Questo modulo non vede e comprende automaticamente tutta la narrazione visiva. Il confronto semantico fra frase, quadro, personaggio e immagine **deve essere completato dall'agente** consultando la pagina e i media reali. L'hash percettivo segnala somiglianza, non bruttezza; due dettagli dello stesso quadro possono essere voluti. Una scena quasi nera può essere una scelta artistica. Le checklist per Visual Music/HyperLumen NON indicano che i loro generatori siano installati.

Non assegna un inesistente "voto estetico 100/100" e non dichiara pronto un filmato solo perché ffprobe ha successo. Le verifiche dei diritti richiedono riscontro con le fonti originali.

## Procedura corretta da smartphone

1. In ChatGPT descrivere titolo, categoria e riferimento di regia. GPT usa V13, V16 e le regole approvate, **non inventa un nuovo renderer**.
2. Preparare `PROJECT_V13.json` con asset/cues e lanciare `python src/quality_director_v17.py --project output/progetto/PROJECT_V13.json --out output/qa-preflight` in un ambiente che ha il repository. Sul telefono è disponibile anche **Actions > Regia qualità V17 > Run workflow**, indicando il file PROJECT già presente nel repo.
3. Esaminare e correggere i punti segnalati prima di consumare eventuali crediti di generazione. Le anomalie non sono necessariamente difetti: vanno valutate rispetto alla categoria.
4. Far renderizzare con il renderer esistente. Nel V16 i file del kit e della revisione V17 si trovano nello stesso output all'interno del checkpoint.
5. Aprire `QUALITY_REVIEW_V17.html` sul telefono, ascoltare l'audio e **rivedere il filmato completo**, verificando soprattutto inizio/fine, ogni transizione, immagini/voce, fonti e atmosfera.
6. Correggere **solo** problemi reali. Non riscrivere voce, stile, musica e Gold Master se sono già riusciti. Salvare una nuova revisione senza sovrascrivere il master approvato.
7. La pubblicazione è separata dalla produzione e richiede autorizzazione.

## Comandi locali, nessun servizio aggiuntivo

```bash
python src/quality_director_v17.py --format artvision_cinema --out output/qa-cinema
python src/quality_director_v17.py --project output/progetto/PROJECT_V13.json --out output/qa-preflight
python src/quality_director_v17.py --project output/progetto/PROJECT_V13.json --video output/video.mp4 --out output/qa-finale
python -m unittest discover -s tests -p 'test_quality_director_v17.py' -v
```

Il terzo comando è pensato per un ambiente con video effettivamente disponibile; non è garantito che l'MP4 storico sia in GitHub anziché in un Artifact o archivio privato.

## Approccio economico

Python + Pillow + FFmpeg/ffprobe; analisi su CPU, nessun account esterno, nessuna chiave segreta, nessun invio di media a servizi AI. GitHub Actions può consumare minuti inclusi nel piano: non trattarli come risorsa infinita. Prima si riusano contatti, dati, audio e immagini già verificati. Il rendering rimane sotto il controllo delle pipeline e del budget già esistenti.

## Integrità e rollback

La modifica all'esecutore è limitata a un hook **dopo** il render V16: i controlli sono soltanto informativi, non riscrivono MP4 o preset. Si può disattivare l'integrazione rimuovendo il piccolo blocco `quality_inspect_v17` dal runner e conservando i due file V17 come strumenti indipendenti. Le video-ricette e le ricevute V13/V16 non cambiano schema.
