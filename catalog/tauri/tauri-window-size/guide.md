## Ponte frontend/backend
Distinguere dimensioni logiche da pixel fisici su schermi con DPI differenti.

## Avvio
Esporta tutta la struttura e avvia npm run dev dalla radice. Il pulsante esegue il codice in web/main.js; i comandi registrati sono in src-tauri/src/main.rs. Aprire index.html in un browser ordinario non fornisce il ponte Tauri.

## Controllo
La finestra assume la dimensione logica richiesta.

## Permission
La capability della sola finestra main dichiara i permessi core necessari. I comandi applicativi accettano dati specifici; non espongono una shell o un percorso arbitrario. Gli esempi con file usano soltanto lo spazio della propria app.