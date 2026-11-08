## Obiettivo
Creare una cartella nuova senza sovrascrivere documenti dell'utente.

## Uso
Salva i sei file nella stessa cartella. Avvia npm install e npm start da quella cartella, poi premi Esegui dimostrazione. Il corpo specifico si trova nel gestore demo:run di main.cjs. La Promise restituisce un dato serializzabile mostrato nel pannello.

## Architettura
Il renderer non usa require: contextIsolation e sandbox restano attivi. Il preload espone una sola funzione senza passare ipcRenderer. Il main verifica l'origine del frame e gestisce dialoghi, filesystem e finestre. Navigazioni e popup non richiesti vengono bloccati.

## Risultato
Creare una cartella nuova senza sovrascrivere documenti dell'utente. Se la piattaforma limita una funzione nativa, l'esito dipende dal supporto del sistema; non è attestata una prova multipiattaforma.