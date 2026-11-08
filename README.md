# DevAtlas — Atlante del Codice

Versione **1.3.0**. Biblioteca desktop italiana in **Python 3.13 / PySide6 6.12**, completamente offline: 2.140 ricette, 46 percorsi e 52 progetti completi. Include ricerca per obiettivo, linguaggio, framework, database e strumenti, codice copiabile, guide, parametri ed esportazione cartella/ZIP.

## Avvio su Windows

- Aprire `dist/DevAtlas-1.3.0/DevAtlas.exe`, oppure fare doppio clic su **Avvia DevAtlas.cmd**.
- Per la versione portabile distribuire `dist/DevAtlas-1.3.0-Windows-x64-portabile.zip`, estrarre l'intera cartella e aprire l'eseguibile. Non richiede Python installato.
- Per l'installazione usare `dist/DevAtlas-1.3.0-Windows-x64-Setup.exe`: installazione per utente, menu Start, collegamento desktop facoltativo e disinstallazione.

Windows x64, Windows 10 1809 o successivo / Windows 11. L'app non installa SDK, non esegue i comandi del catalogo e non richiede account o servizi AI. Toolchain e dipendenze degli esempi vanno predisposte separatamente; le ricette spiegano come.

## Uso

La versione 1.3 riorganizza l'interfaccia per rendere più leggibili navigazione, risultati e codice. I filtri attivi sono visibili e rimovibili; i risultati si possono ordinare per pertinenza, titolo, difficoltà o consultazioni recenti. **F8** concentra lo spazio sulla scheda e ripristina i pannelli alla seconda pressione. **Ctrl+P** apre la palette di comandi e navigazione. Il menu Visualizza offre densità comoda o compatta.

Nei blocchi di codice la ricerca locale usa **Ctrl+F**, **F3** e **Shift+F3**. I controlli per andare a capo, ampliare il blocco e copiare una selezione aiutano a leggere anche i sorgenti lunghi; la copia integrale conserva sempre il contenuto originale dell'asset.

La versione 1.2 aggiunge Kotlin, Swift, PHP, Dart, Vue, Svelte, Angular, Spring Boot, Flutter, Tauri, MongoDB e Redis. Include ricerche salvate e confronto affiancato del codice; **Dove cercare** limita la ricerca ai titoli o al codice e ai comandi. I nuovi percorsi comprendono avvio, build, debug, test e distribuzione dove applicabili, con le piattaforme effettivamente supportate indicate nelle schede.

Per una prova rapida: avvia il programma dal launcher, cerca `vue form` o `kotlin nullable`, salva la ricerca con i suoi filtri e riaprila dalla navigazione. Apri poi una scheda, usa **Azioni → Confronta codice con un’altra scheda** e scegli due file; infine esporta un esempio in una cartella nuova. Il menu Aiuto mostra la versione e la guida completa.

La versione 1.1 aggiunge indicizzazione in background, gestione completa delle raccolte, avanzamento dei percorsi guidati, recupero dei cataloghi locali non validi e protezione dalle aperture contemporanee dello stesso profilo. L'interfaccia resta disponibile mentre la ricerca prepara o aggiorna l'indice.

**Ctrl+K** cerca un'attività, un'API o un errore. Esempi: `C++ compilare`, `python leggere csv`, `react form`, `postgres upsert`. Nomi simbolici, sinonimi italiano/inglese e flessioni delle parole sono riconosciuti; i refusi generano suggerimenti espliciti.

Selezionare tecnologie, obiettivi o percorsi guidati nella colonna sinistra. **Filtri** combina sezione, difficoltà, sistema, shell, IDE e verifica. I risultati vengono caricati progressivamente.

**Vista rapida** mette in evidenza codice e comandi; **Vista guidata** aggiunge procedura, errori, fonti e dettaglio della verifica. I pulsanti **Copia** conservano spazi, Unicode e ritorni a capo senza includere numeri di riga. **Ctrl+F** cerca nel codice della ricetta selezionata.

**Nuova scheda** apre l'editor personale. Per modificare una ricetta inclusa usare **Azioni → Modifica / crea copia personale**. Preferiti, note, raccolte e cronologia restano locali.

Le raccolte si rinominano o eliminano dal menu File e dal menu contestuale della navigazione. Eliminare una raccolta conserva tutte le ricette e le note. I percorsi guidati mostrano il passo corrente, i pulsanti precedente/successivo e **Segna completato**; l'avanzamento viene conservato nel profilo e nei backup.

**Esporta progetto** crea file e istruzioni in una cartella o in uno ZIP. I parametri vengono controllati e mostrati nell'anteprima. File esistenti non vengono sostituiti.

L'editor riconosce le estensioni dei nuovi file, offre modelli iniziali nei file vuoti e mostra gli errori accanto ai campi. **Ctrl+S** salva; cambiare soltanto i metadati conserva anche i ritorni a capo e gli spazi originali dei sorgenti.

La guida completa è inclusa nel menu **Aiuto → Guida e scorciatoie** e in `devatlas/data/guida.md`.

## Dati personali, backup e aggiornamenti

L'installazione usa `%LOCALAPPDATA%\DevAtlas`. Il pacchetto portabile include `portable.flag` e conserva i dati in `dati-personali` accanto all'eseguibile. `--data-dir "C:\percorso"` seleziona una cartella diversa.

- `personali.sqlite`: schede personali, preferiti, note, raccolte, cronologia e impostazioni.
- `ricerca.sqlite`: indice derivato, ricostruibile dall'app senza perdere annotazioni.
- `catalogo-locale.json`: eventuale aggiornamento locale del catalogo incluso.
- `devatlas.log`: registro locale degli errori.

Il menu File crea e importa pacchetti `RecipeBundle v1` (`.devatlas.zip`). L'importazione mostra un riepilogo e conserva le versioni esistenti attraverso copie con ID nuovi. Il backup comprende schede personali, annotazioni, raccolte e impostazioni; le impostazioni già presenti nel profilo di destinazione hanno precedenza.

Le ricerche salvate sono contenuti: durante il ripristino vengono unite a quelle esistenti, con nuovi ID e nomi distinti se differiscono. I riferimenti alle raccolte seguono gli ID ripristinati. Se l'unione supera i limiti di 100 ricerche o 512 KiB, l'importazione viene annullata interamente senza perdere o sostituire contenuti.

Le preferenze non leggibili non impediscono più un backup: il pacchetto può conservarne il testo originale in `settings_recovery`, senza riapplicarlo come impostazione attiva. Cataloghi locali non validi restano sul disco mentre l'app apre il catalogo incluso e mostra un avviso.

Una singola scheda personale con JSON danneggiato non blocca le altre: viene segnalata e conservata nel database. Il backup ne include il testo originale in `recipes_recovery`; il ripristino rende attive soltanto le schede valide, lasciando i testi da recuperare nel pacchetto originale.

Il launcher preferisce `dist/DevAtlas-1.3.0`, mantenendo la cartella della versione 1.0. La preparazione della release copia una sola volta il vecchio profilo portabile con uno snapshot SQLite coerente e conserva l'originale. Eventuali modifiche locali al catalogo hanno precedenza, mentre le schede incluse non personalizzate ricevono le nuove descrizioni.

Gli aggiornamenti del catalogo si importano da pacchetti locali, con identificatori stabili. Nessuna connessione viene aperta automaticamente: le fonti esterne si aprono nel browser solo dopo un clic.

## Sviluppo

Preparazione con Python 3.13:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m devatlas
```

Sono inclusi font OFL, icone SVG e risorse locali. L'ambiente virtuale e la cache di compilazione sono separati dalle installazioni Python di sistema.

### Catalogo modificabile

Ogni ricetta in `catalog/<tecnologia>/<id>/` contiene `recipe.json`, `guide.md` e gli asset sorgenti. Il file JSON indica tecnologia, sezione, requisiti, parametri, risorse, riferimenti e verifica. La guida usa Markdown; il codice ha una sola sorgente condivisa fra lettura, copia, export e controlli.

Gli script di authoring sono `tools/build_languages.py`, `tools/build_desktop_tools.py` e `tools/build_web_database.py`. Dopo modifiche editoriali eseguire i verificatori pertinenti: ricostruire un gruppo riporta le verifiche dei suoi nuovi esempi allo stato documentale finché non vengono ripetute.

Per ricostruire soltanto i dodici nuovi percorsi della 1.2 usare `tools/build_expansion.py`. La baseline `catalog/baseline-1.1.json` permette all'audit di verificare che ID, codice e percorsi delle 1.800 schede precedenti siano rimasti invariati.

```powershell
.\.venv\Scripts\python.exe tools\compile_catalog.py
.\.venv\Scripts\python.exe tools\audit_catalog.py
.\.venv\Scripts\python.exe tools\evaluate_search.py
.\.venv\Scripts\python.exe tools\verify_catalog_exports.py
.\.venv\Scripts\python.exe -m pytest -q --basetemp=.cache\pytest
```

Il catalogo runtime è generato in `devatlas/data/catalog.json`. L'app usa SQLite FTS5, BM25, stemming italiano/inglese, sinonimi e ranking dei concetti, con connessioni separate fra i thread. Le query utente vengono trasformate in espressioni FTS valide; non sono SQL o espressioni Python eseguibili.

### Formato di scambio

Un pacchetto contiene solo `bundle.json`, con `format: "RecipeBundle"`, `version: 1` e `recipes`. I backup aggiungono `personal`. Gli asset hanno contenuto UTF-8, percorso relativo, linguaggio e ruolo `file`, `snippet` o `command`; i comandi dichiarano shell, sistema e directory.

I parametri dichiarati usano `{{nome}}`. Per valori testuali contestuali usare `{{nome|json}}`, `{{nome|powershell}}` o `{{nome|bash}}`. I segnaposto di framework non dichiarati, come `{{ request.user }}`, restano intatti. I tipi disponibili sono identifier, namespace, port, path e string. Il codice sostituito viene sempre mostrato prima dell'esportazione.

## Build Windows

La build usa il backend Nuitka documentato da Qt e produce una cartella standalone con librerie Qt dinamiche. Richiede MSVC e Windows SDK; i download dei tool di build restano nella cache del progetto.

```powershell
.\.venv\Scripts\python.exe tools\build_windows.py
```

Inno Setup portabile deve essere disponibile in `.cache/tools/inno/ISCC.exe`. La configurazione dell'installer è `deploy/DevAtlas.iss`. Per rigenerare solo ZIP e installer dopo cambiamenti ai contenuti usare `tools/build_windows.py --package-only`; modifiche al codice applicativo richiedono la build completa.

La build registra hash dei sorgenti e dell'eseguibile: `--package-only` rifiuta una compilazione precedente quando il codice è cambiato. I pacchetti sono creati da uno staging pulito che esclude i dati personali; la distribuzione sostituita resta recuperabile nella cache. `tools/verify_installer.py` prova installazione e disinstallazione con un AppId isolato e conserva il profilo esterno di prova. La finalizzazione verifica rapporti coerenti e genera realmente `dist/SHA256SUMS.txt`.

Le librerie conservano le rispettive licenze, incluse nel pacchetto; codice ed esempi originali sono forniti con licenza MIT. I font Inter e JetBrains Mono sono distribuiti con licenza SIL OFL. Non sono redistribuiti i font proprietari di Windows.

## Verifiche e limiti

I rapporti in `reports/` documentano test dell'app, audit delle schede, ricerca, compilazione ed esecuzioni degli esempi. **CONSEGNA.md** riporta gli esiti della versione confezionata e i limiti effettivi.

Il badge **Eseguito** vale per l'ambiente dichiarato. **Controllo statico** non implica compilazione o esecuzione. Le guide Linux/macOS e le procedure che richiedono hardware, servizi o SDK assenti non ricevono un'attestazione di esecuzione universale.


## Download

[Installer e versione portabile Windows](https://github.com/danielegabrovec/devatlas/releases/latest). Il codice originale mantiene la licenza MIT descritta in LICENSE.txt; le dipendenze mantengono le rispettive licenze.
