## Scopo
Passare un contesto QObject a QTimer::singleShot.

## Integrazione
Questo esempio è un eseguibile autonomo: salva main.cpp e CMakeLists.txt nella stessa cartella. Il corpo di main costruisce i controlli prima di entrare in app.exec(). I QObject hanno un parent o vengono adottati dal layout.

## Avvio
Usa un terminale Qt coerente con il compilatore selezionato. I comandi sono per Windows/Ninja; esecuzione su altri sistemi non attestata.

## Risultato
Eseguire un aggiornamento una sola volta. Il controllo aggiunto alla finestra dimostra esclusivamente il comportamento descritto.