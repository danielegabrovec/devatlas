# DevAtlas 1.3.0 — Verifica e consegna

Versione Windows x64 del 29 ottobre 2026.

## Avvio

Avviare `Avvia DevAtlas.cmd`, oppure l'eseguibile nella cartella `dist/DevAtlas-1.3.0`.
Le distribuzioni precedenti restano conservate. Il profilo portabile viene copiato dalla versione precedente più recente con uno snapshot SQLite, senza modificare l'originale; i profili già presenti nella nuova versione hanno precedenza.

## Correzioni e aggiunte

- Interfaccia rinnovata con gerarchie più chiare, superfici e tipografia coerenti, card leggibili e filtri attivi rimovibili.
- Palette di comandi Ctrl+P, ordinamento dei risultati sull'intero insieme filtrato, modalità lettura e disposizione adattabile.
- Ricerca locale nei sorgenti con navigazione fra occorrenze, ritorno a capo, blocchi espandibili e copia della selezione fedele al testo originale.
- Catalogo della versione 1.2 confermato: 2.140 schede in 46 percorsi e 52 progetti; ID, codice e livelli di verifica preservati durante la revisione grafica.
- Ricerche salvate con nome, testo e filtri, riapribili e organizzabili; confronto di due sorgenti con differenze affiancate e parametri indipendenti.
- Filtro di ricerca su tutto il contenuto, soltanto codice/comandi o soltanto titoli; alias dei nuovi linguaggi e framework.
- Ricerca migliorata per concetti, API, nomi simbolici e refusi; filtri e paginazione coerenti, cache separata per generazione dell'indice.
- I motori che condividono lo stesso indice nel processo adottano lo snapshot aggiornato dopo una ricostruzione: ordinamento, metadati e cache restano coerenti.
- Indicizzazione in background con stato visibile, recupero dagli errori e interfaccia utilizzabile durante il lavoro.
- Raccolte rinominabili ed eliminabili conservando le schede; percorsi guidati ordinati con avanzamento, completamento e ripresa.
- Editor con linguaggio riconosciuto dall'estensione, modelli espliciti per file vuoti, errori accanto ai campi e salvataggio Ctrl+S. Le modifiche ai soli metadati conservano CRLF, Unicode e spazi dei sorgenti originali.
- Import, backup ed export con validazione completa, transazioni/snapshot coerenti e pubblicazione dei file senza sovrascritture o residui parziali.
- Lettura robusta delle preferenze, recupero visibile dei cataloghi locali e delle singole schede personali danneggiate; backup dei testi originali e blocco delle aperture concorrenti sullo stesso profilo.
- Conservate le descrizioni specifiche e le correzioni dei contenuti verificate nelle versioni precedenti.
- Correzioni delle fixture e delle istruzioni SQL/MySQL/PostgreSQL indicate nel rapporto indipendente.
- Build tracciata rispetto ai sorgenti, staging pulito, verifica del portabile e checksum effettivamente prodotti.

## Risultati effettivi

- **329 test automatici superati**, 0 errori, 0 saltati.
- **2.140 schede, 46 percorsi e 52 progetti**, con quote, metadati, riferimenti e checksum dei sorgenti verificati; codice delle 1.800 schede precedenti conservato.
- **2140 esportazioni ZIP** rilette confrontando il contenuto UTF-8; 52 progetti esportati anche come cartelle.
- Ricerca: **201/201 query** con la risposta attesa nelle prime tre posizioni (**100.0%**). La versione 1.0 raggiungeva 97/107 (90.7%).
- Percentile 95 delle query senza risultato già in cache: **37.61 ms**; tempi delle richieste ripetute riportati separatamente nel rapporto.
- Standalone provato da cartella isolata con spazi, virgole e Unicode, PATH senza Python e DLL caricate dal pacchetto, alle scale Qt 100% e 200%.
- Installazione, avvio e disinstallazione verificati con lo stesso script e payload, un AppId di prova univoco e una cartella isolata. Il profilo personale esterno resta conservato e la registrazione di prova viene rimossa.

### Stato dei contenuti

| Verifica dichiarata | Schede |
|---|---:|
| Esecuzione nell'ambiente indicato | 787 |
| Compilazione nell'ambiente indicato | 172 |
| Controllo statico | 871 |
| Documentazione, esecuzione non attestata | 310 |

Le verifiche valgono per le versioni e gli ambienti descritti nelle singole schede. Le sessioni interattive di tutti i debugger, gli SDK mobili assenti e servizi non disponibili non sono attestati. La prova standalone usa un ambiente isolato sul PC corrente, non una nuova macchina virtuale.
Le catture dell'interfaccia e le prove DPI sono eseguite tramite Qt; non attestano monitor fisici o una revisione manuale di ogni combinazione di finestre.

## File

- `dist/DevAtlas-1.3.0-Windows-x64-Setup.exe`.
- `dist/DevAtlas-1.3.0-Windows-x64-portabile.zip`.
- `dist/DevAtlas-1.3.0-sorgenti.zip`.
- `dist/SHA256SUMS.txt`: checksum dei tre pacchetti, ricalcolati e verificati dopo il confezionamento.
- `reports/full-review.json` e `reports/final-verification.json`: conclusioni ed evidenze.
- Rapporti specifici: test XML, audit del catalogo, round-trip export, ricerca, revisione dati/UI, installer e standalone.

## Estensioni possibili

Pacchetti Linux/macOS, nuove attestazioni su dispositivi mobili e servizi database richiedono ambienti dedicati. L'app conserva l'impostazione offline; non sono stati introdotti account, servizi AI o sincronizzazione cloud.
