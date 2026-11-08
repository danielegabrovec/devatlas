## Obiettivo
Aggiungere vincolo CHECK.

## Preparazione e reset del laboratorio
Esporta fixture.sql e query.sql nella stessa cartella. La fixture elimina tutte le tabelle e viste nominate da questi laboratori nel database didattico cookbook_demo: oltre a people, products, orders e order_items, ripulisce notes, lines, people_copy, paid_copy, paid_orders e le tabelle rename_*. Tutti i loro dati vengono persi. Non esegue DROP DATABASE né rimuove database estranei. Usa un database dedicato senza dati di produzione. Le tabelle principali usano InnoDB e FOREIGN KEY esplicite, perché MySQL 8.4 ignora REFERENCES inline sulle colonne.

## Lettura del codice
La query in query.sql è completa e lavora sui dati della fixture; i comandi vanno eseguiti dalla cartella esportata. Individua nel risultato le colonne o i metadati richiesti dal titolo. Prima di ogni nuova prova riesegui fixture.sql e poi query.sql: il reset comprende anche gli oggetti extra creati dalle query DDL del laboratorio. 

## Compatibilità
Sintassi prevista per MySQL 8.4 LTS; differenze MariaDB da verificare. Le funzioni specifiche del motore non vanno trasferite senza adattamento ad altri database.