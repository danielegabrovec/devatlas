## Progetto
Esporta l'intera struttura. Il modello rifiuta titoli vuoti, assegna il prossimo ID e restituisce una nuova lista. La UI mantiene lo stato con gli strumenti del framework e visualizza gli errori nel modulo. I dati sono soltanto di sessione, quindi ricaricare azzera la lista.

## Controlli
Invia un titolo vuoto: compare un errore. Aggiungi due attività, spunta la seconda e verifica il conteggio1; togli la spunta e verifica0. Esegui node --test per i casi del modello e npm run build per il progetto completo. Un build riuscito non attesta una sessione browser interattiva.