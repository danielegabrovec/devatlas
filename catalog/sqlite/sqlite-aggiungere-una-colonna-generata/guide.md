## Obiettivo
Aggiungere una colonna generata.

## Preparazione e reset del laboratorio
Esporta fixture.sql e query.sql nella stessa cartella. La fixture elimina gli oggetti dei laboratori SQL/SQLite dal solo file didattico demo.sqlite e li ricrea: dati principali, viste, tabelle aggiuntive, FTS e trigger dimostrativi vengono rimossi. I loro dati vengono persi. Usa un file dedicato senza dati personali o di produzione. Le foreign key sono attive e il reset elimina prima gli oggetti dipendenti.

## Lettura del codice
La query in query.sql è completa e lavora sui dati della fixture; i comandi vanno eseguiti dalla cartella esportata. Individua nel risultato le colonne o i metadati richiesti dal titolo. Prima di ogni nuova prova riesegui fixture.sql e poi query.sql: il reset comprende anche gli oggetti extra creati dalle query DDL del laboratorio. 

## Compatibilità
Sintassi prevista per SQLite 3.45+ con JSON1/FTS5. Le funzioni specifiche del motore non vanno trasferite senza adattamento ad altri database.