## File e generazione dell'interfaccia
Esporta tutti i file mantenendo .vscode. form.ui descrive resultLabel e calcButton; ui_main.py contiene una implementazione originale pronta all'uso degli stessi controlli. Il comando pyuic6.exe rigenera quella classe dal form. Se modifichi la UI, ripeti la generazione prima di fare debug o build. Il codice applicativo è in main.py e totals.py, separato dal file rigenerabile.

## Debug dello slot
Installa in VS Code le estensioni Python e Python Debugger. Apri la cartella, seleziona .venv/Scripts/python.exe e la configurazione Debug PyQt6. Metti un breakpoint sulla riga `subtotal = sum(prices)` di totals.py, premi F5 e poi Calcola. Controlla prices, avanza una riga e verifica subtotal=19.75. Non mettere il breakpoint nel file UI destinato alla rigenerazione.

## Build e consegna
Il congelamento usa PyInstaller nello stesso ambiente di PyQt6. L'esclusione di PySide6 evita di trascinare un secondo binding accidentalmente disponibile. Distribuisci tutta dist/{{project_name}}, compresi i plugin Qt raccolti dagli hook. Se l'eseguibile non parte, ricostruisci temporaneamente senza --windowed per leggere il messaggio nel terminale.

## Verifica da eseguire
Avvia il risultato su Windows della stessa architettura, senza usare la .venv di sviluppo, e prova il pulsante. Questa guida fornisce sorgenti e configurazioni; non dichiara eseguite le build Nuitka/PyInstaller né la prova su una macchina pulita.