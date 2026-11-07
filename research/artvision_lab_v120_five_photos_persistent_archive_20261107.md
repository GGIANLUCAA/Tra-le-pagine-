# ArtVision Museum Lab — cinque fotografie V120 recuperate e conservate (7 novembre 2026)

Questa attività appartiene esclusivamente al **laboratorio tecnico**, non all'owner della coda ArtVision. Il precedente archivio GitHub Actions V120, [run 41395451028](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41395451028), artifact ID **13119426005** `ARTVISION_V120_FIVE_REAL_GALLERY_SOURCES_REVIEW`, era ancora disponibile ma scadrà il **2 dicembre 2026**. Sono stati recuperati i byte originali della sua raccolta di cinque vere fotografie museali, confrontati con il manifest `PROVENANCE_AND_RIGHTS.json` e salvati per conservarli oltre la scadenza dell'artifact temporaneo.

## Archivio persistente
Cartella della **Libreria privata ChatGPT**, non del sito pubblico:
`/ArtVision/Museum_Lab/V120_RESEARCH_SOURCES/`

Sono stati caricati i cinque JPG originali più `PROVENIENZA_LICENZE_SHA256.md` (crediti/licenze/identità). **Controllo effettivo di ritorno:** dopo l'upload, tutti e cinque i JPG sono stati materializzati nuovamente dalla Libreria e ricalcolati SHA-256; **5/5 PASS byte-per-byte** rispetto all'artifact V120.

| File | Autore, licenza dichiarata | Pixel | Byte | SHA-256 confermato | Libreria file |
|---|---|---:|---:|---|---|
| `GAL01_PHOTOGRAPH.jpg` | Daderot, CC0 1.0 | 4320×3240 | 2.198.286 | `eaea76f5ff2c3162397b45cd18c751373d47e6cd5462fa3d72285338c4a2f926` | `libfile_02f565b0c09081918e62594abb6125ab` |
| `GAL02_PHOTOGRAPH.jpg` | Daniel Naber, CC BY 4.0 | 3648×2736 | 1.431.648 | `ea95335ef66afa225351e1dd423c49d5e84aeb15574e97b965fa25c1d5b91db2` | `libfile_cd78fc56a4cc81918007e7e04eaa8cbe` |
| `GAL03_PHOTOGRAPH.jpg` | Roundtheworld, CC0 1.0 | 3216×4288 | 1.667.950 | `cee7b171449cad4143ef2f0117e6ec90e12b3b46b265b123977c2bfd38932f9e` | `libfile_2fac46f72da08191a8da430ca8e37814` |
| `GAL04_PHOTOGRAPH.jpg` | 14GTR, CC0 1.0 | 5019×3456 | 2.554.633 | `3e035baac12291ce5e7cbed35525d6dae7fe0f75b58e5984f7b4530cf0110920` | `libfile_91a90cdae4d881919220d5179effb387` |
| `GAL05_PHOTOGRAPH.jpg` | Loralielo, CC0 1.0 | 3024×4032 | 1.214.978 | `97011035822dfb20889b93204df53a5851ef0379393917652ab4301ef1ef4f8a` | `libfile_1218fd70e6d08191a356433215943d9d` |

Fonti pagina foto:
- GAL01: [Corcoran Gallery historical interior](https://commons.wikimedia.org/wiki/File:Interior_-_Corcoran_Gallery_of_Art_-_DSC01195.JPG), con opere già appese.
- GAL02: [Museum Barberini, sala vuota](https://commons.wikimedia.org/wiki/File:Museum_Barberini_Innenraum_leer.jpg), con porta centrale; attribuire Daniel Naber e mantenere CC BY 4.0 se usata.
- GAL03: [Museo delle Mura, mostra](https://commons.wikimedia.org/wiki/File:MuseumoftheWalls_exhibition.jpg), pannelli e allestimenti presenti.
- GAL04: [V&A Room 70](https://commons.wikimedia.org/wiki/File:Room_70_Begining_the_Collection.jpg), numerosi oggetti e segnaletica.
- GAL05: [Game Room gallery](https://commons.wikimedia.org/wiki/File:Game_Room_-_Interior_of_the_gallery.jpg), altri oggetti/colonne.

## Risultato per il blocco V209
La copia V120 **GAL02 fisica** ha SHA256 `ea95335ef66afa225351e1dd423c49d5e84aeb15574e97b965fa25c1d5b91db2`, cioè proprio l'impronta attesa nel workflow V209; la fotografia V209 ricaricata da Commons ha SHA256 `4eccd18f1fc714305902369d8c2b118f763fc6dec129b89820a3d20242c40e64` e quindi **non è byte-identica alla versione storica**. Entrambe le rilevazioni provengono da letture effettive, non da solo metadati. Causa della divergenza (revisione Commons, derivazione, altra normalizzazione) ancora da accertare: per un test ripetibile usare la sorgente V120 salvata con SHA fissato ed esplicita provenienza, senza sostituire silenziosamente l'hash atteso in un flusso che scarica un'altra versione. Resta poi irrisolto il problema visivo della porta centrale e dell'assenza di cornice per la precisa opera.

## Limite fondamentale
**Cinque fotografie recuperate NON sono cinque ambienti 3D costruiti.** Non sono scene in cui altri quadri siano storicamente esposti; rimangono studi scenografici candidati, senza preview MP4 idoneo, misure/scala e approvazione artistica. Conservare V80/V118/V119 e mai pubblicare come installazione autentica. Nessuna mutazione di queue, automazioni, master, diritti o crediti è stata effettuata.
