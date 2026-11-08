## Obiettivo
Rendere atomico un trasferimento.

## Preparazione e reset del laboratorio
Esporta fixture.sql e query.sql nella stessa cartella. La fixture elimina gli oggetti dei laboratori SQL/SQLite dal solo file didattico demo.sqlite e li ricrea: dati principali, viste, tabelle aggiuntive, FTS e trigger dimostrativi vengono rimossi. I loro dati vengono persi. Usa un file dedicato senza dati personali o di produzione. Le foreign key sono attive e il reset elimina prima gli oggetti dipendenti.

## Lettura del codice
La query in query.sql è completa e lavora sui dati della fixture; i comandi vanno eseguiti dalla cartella esportata. Individua nel risultato le colonne o i metadati richiesti dal titolo. Prima di ogni nuova prova riesegui fixture.sql e poi query.sql: il reset comprende anche gli oggetti extra creati dalle query DDL del laboratorio. La CTE allowed materializzata congela la disponibilità prima della modifica. Un solo UPDATE sposta l'unità su entrambe le righe oppure non modifica nulla: sorgente esaurito, destinazione mancante o stock non valido non devono creare o perdere quantità. Con i dati iniziali gli stock passano da 8/0 a 7/1; con sorgente 1 passano a 0/1; con sorgente 0 rimangono invariati. La somma degli stock deve restare uguale.

## Compatibilità
Sintassi prevista per SQLite 3.45+ con JSON1/FTS5. Le funzioni specifiche del motore non vanno trasferite senza adattamento ad altri database.