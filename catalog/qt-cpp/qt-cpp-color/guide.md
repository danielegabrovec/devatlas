## Scopo
Controllare QColor::isValid prima di aggiornare lo stile.

## Integrazione
Questo esempio è un eseguibile autonomo: salva main.cpp e CMakeLists.txt nella stessa cartella. Il corpo di main costruisce i controlli prima di entrare in app.exec(). I QObject hanno un parent o vengono adottati dal layout.

## Avvio
Usa un terminale Qt coerente con il compilatore selezionato. I comandi sono per Windows/Ninja; esecuzione su altri sistemi non attestata.

## Risultato
Applicare un colore scelto dall'utente. Il controllo aggiunto alla finestra dimostra esclusivamente il comportamento descritto.