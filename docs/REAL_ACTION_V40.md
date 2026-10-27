# V40 — REAL ACTION: oggetti e persone che si muovono davvero

**Stato: PROPOSTA, 27/10/2026. Non approvato artisticamente e non attivo sui video correnti.**

Il prototipo V39 ha prodotto clip percepite come banali. Non considerare più come scene animate gli zoom su foto, i blur, le transizioni o il parallax senza azioni reali. Gli originali V39 restano a scopo storico; non vengono promossi a Gold Master.

## Due famiglie DIFFERENTI

1. **V40 Real Action**, pronto a montare filmati reali in cui un oggetto, persona o elemento naturale COMPIONO UN'AZIONE. Esempi: orologeria in funzione, pagine che si girano, un personaggio che apre un uscio, fuoco/acqua in movimento. Filtrare per soggetto, epoca e coerenza narrativa: un filmato moderno non è automaticamente adatto a un libro ambientato nel 1800.
2. **V41 AI Motion**, non integrato: vera trasformazione da immagine in nuova azione tramite Wan/LTX o altri servizi ZeroGPU, SOLO se accesso, licenza, quote e risultato pratico sono verificati. Non confondere demo di altri con funzionalità installate; nessuna promessa di GPU gratis sempre disponibile.

**Filmato pertinente > immagine leggermente animata.** Ma stock incongruente è peggio di una bella illustrazione statica; usarlo solo quando è pertinente alla frase.

## Fonti concrete (esempi da selezionare, NON scaricati automaticamente)

- Orologeria in funzione: https://www.pexels.com/video/close-up-on-working-gears-9966041/
- Libro d'epoca con pagine che si sfogliano: https://www.pexels.com/video/flipping-pages-in-old-book-11384843/
- Candela reale in ambiente scuro: https://www.pexels.com/video/blown-out-candle-7034152/

Verificare la licenza e l'eventuale presenza di soggetti con diritti residui al momento dell'acquisizione; usare footage solo se autorizzato. Inserire fonte e crediti nel dossier privato e nei post se richiesti. Per un quadro autentico non usare stock o AI spacciandoli per elementi del quadro, né sovrapposizioni trasparenti.

## Motore implementato

`src/real_action_v40.py` legge SOLO un vero file video già acquisito sotto `episodes/NOME_EPISODIO/`, misura differenze tra fotogrammi e moto residuo rispetto al movimento camera (controllo solo indicativo), ritaglia a formato verticale con punto di interesse selezionato, esporta H.264 24 fps senza audio originale, e crea JSON con hash, provenienza, durata, tipo di azione e revisione obbligatoria.

`src/effetti_v4.py` riconosce un campo `real_action` ESPLICITO nel cue V4. Non sposta audio/tempo, non utilizza ghosting, usa un taglio netto prima della ripresa e, se necessario, torna all'immagine normale per il resto della scena. No reveal o frei0r sovrapposto nello stesso cue.

### Configurazione esempio per una scena specifica

Nel file `episodes/IL_TUO_EPISODIO/effetti_v4.json`, all'interno dell'oggetto cue scelto:

```json
{
  "cue": 8,
  "effect": "cinematic_pan",
  "real_action": {
    "file": "clips/clock_gears.mp4",
    "provider": "pexels",
    "license": "pexels",
    "source_url": "https://www.pexels.com/video/close-up-on-working-gears-9966041/",
    "rights_reviewed": true,
    "visual_reviewed": true,
    "scene_action": "Ingranaggi metallici in rotazione davanti alla camera",
    "narrative_reason": "Il meccanismo del racconto si mette finalmente in moto",
    "narration_anchor": "Il protagonista azionò il meccanismo",
    "seconds": 6,
    "start": 0.5,
    "crop_x": 0.5,
    "crop_y": 0.5
  }
}
```

Questi campi richiedono una verifica reale della frase, dell'opera e del file. Il video della macchina del tempo è un esempio illustrativo e **non equivale a una scena finale approvata**. Il file `clips/clock_gears.mp4` deve esistere realmente. Questo commit non aggiunge file audiovisivi, non scarica video da internet, non consuma servizi a pagamento e non publica nulla.

## Procedura di controllo

1. Studiare il romanzo e identificare il punto esatto in cui una vera AZIONE vale la pena.
2. Cercare il footage, verificarne diritti e coerenza di costumi/oggetti/luce/epoca. Fotografare con fonti autentiche le opere d'arte, non falsificarle.
3. Scaricare footage e verificare l'inquadratura verticale. Se il ritaglio taglia il soggetto, scartare.
4. Registrare `real_action` nella scena corretta, controllare fonte e ancora di narrazione, non usare filler né effetti sovrapposti.
5. Generare il montaggio con V4, ascoltare la voce Gacrux e guardare ogni raccordo a velocità normale.
6. Consegnare MP4 reale e ZIP verificati con il protocollo Android V36 e la regola permanente del repository. Nessun "file not found" mascherato da consegna riuscita.

Test di codice: `python -m unittest discover -s tests -p 'test_real_action_v40.py' -v`. La qualità estetica rimane da certificare nel video reale. Un test con un rettangolo artificiale è valido SOLO come verifica del software, mai come provino artistico.

## Vincoli e limiti tecnici

Un filmato reale sul server non implica il diritto di pubblicarlo; verificare licenza e richieste di attribuzione. I flags rights_reviewed e visual_reviewed sono autocertificazioni dell'operatore, **non verifiche automatiche di legittimità**. I numeri di optical flow non certificano coerenza narrativa, bellezza o azione naturale. Non modificare master esistenti. PR di prova prima di merge e studio di integrazione video nello storage del sito; il workflow esistente V4 non importa da solo video web.
