## File e generazione dell'interfaccia
Esporta tutti i file mantenendo .vscode. form.ui descrive resultLabel e calcButton; ui_main.py contiene una implementazione originale pronta all'uso degli stessi controlli. Il comando pyside6-uic.exe rigenera quella classe dal form. Se modifichi la UI, ripeti la generazione prima di fare debug o build. Il codice applicativo è in main.py e totals.py, separato dal file rigenerabile.

## Debug dello slot
Installa in VS Code le estensioni Python e Python Debugger. Apri la cartella, seleziona .venv/Scripts/python.exe e la configurazione Debug PySide6. Metti un breakpoint sulla riga `subtotal = sum(prices)` di totals.py, premi F5 e poi Calcola. Controlla prices, avanza una riga e verifica subtotal=19.75. Non mettere il breakpoint nel file UI destinato alla rigenerazione.

## Build e consegna
Apri il terminale MSVC x64 con dumpbin disponibile prima di creare il pacchetto Nuitka. La specifica generata da pyside6-deploy va conservata insieme ai sorgenti. Distribuisci l'intera cartella standalone e verifica che il plugin platforms/qwindows.dll sia presente; provare soltanto sul PC con Qt installato non dimostra la completezza del pacchetto.

## Verifica da eseguire
Avvia il risultato su Windows della stessa architettura, senza usare la .venv di sviluppo, e prova il pulsante. Questa guida fornisce sorgenti e configurazioni; non dichiara eseguite le build Nuitka/PyInstaller né la prova su una macchina pulita.