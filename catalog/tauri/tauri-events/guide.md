## Ponte frontend/backend
Registrare il listener prima di chiamare il comando e rimuoverlo dopo la risposta.

## Avvio
Esporta tutta la struttura e avvia npm run dev dalla radice. Il pulsante esegue il codice in web/main.js; i comandi registrati sono in src-tauri/src/main.rs. Aprire index.html in un browser ordinario non fornisce il ponte Tauri.

## Controllo
L’evento èricevuto e il listener viene rilasciato anche su timeout.

## Permission
La capability della sola finestra main dichiara i permessi core necessari. I comandi applicativi accettano dati specifici; non espongono una shell o un percorso arbitrario. Gli esempi con file usano soltanto lo spazio della propria app.