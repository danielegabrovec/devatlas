## Obiettivo
Creare un indice GIN su JSONB.

## Preparazione e reset del laboratorio
Esporta fixture.sql e query.sql nella stessa cartella. La fixture elimina integralmente lo schema di laboratorio atlas_demo con DROP SCHEMA ... CASCADE e lo ricrea. Oggetti dipendenti possono essere rimossi anche fuori dallo schema: usa soltanto il database didattico dedicato cookbook_demo, senza oggetti o dati di produzione. Il reset rimuove anche tabelle, tipi, funzioni, indici e viste creati dalle altre prove PostgreSQL del laboratorio.

## Lettura del codice
La query in query.sql è completa e lavora sui dati della fixture; i comandi vanno eseguiti dalla cartella esportata. Individua nel risultato le colonne o i metadati richiesti dal titolo. Prima di ogni nuova prova riesegui fixture.sql e poi query.sql: il reset comprende anche gli oggetti extra creati dalle query DDL del laboratorio. 

## Compatibilità
Sintassi prevista per PostgreSQL 18; psql. Le funzioni specifiche del motore non vanno trasferite senza adattamento ad altri database.