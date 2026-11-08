## Ponte frontend/backend
Usare checked_mul e convertire il fallimento in Result serializzabile.

## Avvio
Esporta tutta la struttura e avvia npm run dev dalla radice. Il pulsante esegue il codice in web/main.js; i comandi registrati sono in src-tauri/src/main.rs. Aprire index.html in un browser ordinario non fornisce il ponte Tauri.

## Controllo
4 restituisce16; valori troppo grandi vengono rifiutati.

## Permission
La capability della sola finestra main dichiara i permessi core necessari. I comandi applicativi accettano dati specifici; non espongono una shell o un percorso arbitrario. Gli esempi con file usano soltanto lo spazio della propria app.