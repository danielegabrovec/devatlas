"""Inventari SQL curati: ogni voce contiene un'operazione differente."""
from catalog_support import Book
from web_support import verification

FIXTURE = """DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS people;
CREATE TABLE people(id INTEGER PRIMARY KEY, name VARCHAR(80) NOT NULL, city VARCHAR(80), age INTEGER, email VARCHAR(120) UNIQUE);
CREATE TABLE products(id INTEGER PRIMARY KEY,name VARCHAR(80),price DECIMAL(10,2),stock INTEGER);
CREATE TABLE orders(id INTEGER PRIMARY KEY,person_id INTEGER,total DECIMAL(10,2),status VARCHAR(20),created_at VARCHAR(30),FOREIGN KEY(person_id) REFERENCES people(id));
CREATE TABLE order_items(order_id INTEGER,product_id INTEGER,qty INTEGER,PRIMARY KEY(order_id,product_id),FOREIGN KEY(order_id) REFERENCES orders(id),FOREIGN KEY(product_id) REFERENCES products(id));
INSERT INTO people VALUES(1,'Ada','Roma',35,'ada@example.test'),(2,'Linus','Milano',42,'linus@example.test'),(3,'Grace',NULL,35,'grace@example.test'),(4,'Alan','Roma',NULL,'alan@example.test');
INSERT INTO products VALUES(1,'Tastiera',50,8),(2,'Mouse',20,0),(3,'Monitor',180,3);
INSERT INTO orders VALUES(1,1,90,'paid','2026-01-10'),(2,1,180,'paid','2026-02-10'),(3,2,20,'new','2026-02-15'),(4,3,50,'cancelled','2026-03-01');
INSERT INTO order_items VALUES(1,1,1),(1,2,2),(2,3,1),(3,2,1),(4,1,1);
"""

SQLITE_RESET = """PRAGMA foreign_keys=ON;
DROP TRIGGER IF EXISTS stock_audit;
DROP TRIGGER IF EXISTS prevent_stock;
DROP VIEW IF EXISTS pagati;
DROP TABLE IF EXISTS adulti;
DROP TABLE IF EXISTS misure;
DROP TABLE IF EXISTS presenze;
DROP TABLE IF EXISTS letture;
DROP TABLE IF EXISTS etichette;
DROP TABLE IF EXISTS righe;
DROP TABLE IF EXISTS docs;
DROP TABLE IF EXISTS names;
DROP TABLE IF EXISTS audit;
"""
MYSQL_RESET = """DROP VIEW IF EXISTS paid_orders;
DROP TABLE IF EXISTS notes;
DROP TABLE IF EXISTS lines;
DROP TABLE IF EXISTS people_copy;
DROP TABLE IF EXISTS paid_copy;
DROP TABLE IF EXISTS rename_a;
DROP TABLE IF EXISTS rename_b;
DROP TABLE IF EXISTS rename_old;
DROP TABLE IF EXISTS rename_new;
"""


def fixture_for(stack):
    if stack in ("sql", "sqlite"):
        return SQLITE_RESET + FIXTURE
    if stack == "postgresql":
        return "DROP SCHEMA IF EXISTS atlas_demo CASCADE;\nCREATE SCHEMA atlas_demo;\nSET search_path=atlas_demo;\n" + FIXTURE
    # MySQL 8.4 ignores column-level REFERENCES. FIXTURE uses explicit
    # table constraints; the engine is also explicit so FK/transactions apply.
    import re
    fixture = re.sub(r"(CREATE TABLE [^;]+)\);", r"\1) ENGINE=InnoDB;", FIXTURE)
    return MYSQL_RESET + fixture


def fixture_guide(stack):
    if stack == "postgresql":
        return "La fixture elimina integralmente lo schema di laboratorio atlas_demo con DROP SCHEMA ... CASCADE e lo ricrea. Oggetti dipendenti possono essere rimossi anche fuori dallo schema: usa soltanto il database didattico dedicato cookbook_demo, senza oggetti o dati di produzione. Il reset rimuove anche tabelle, tipi, funzioni, indici e viste creati dalle altre prove PostgreSQL del laboratorio."
    if stack == "mysql":
        return "La fixture elimina tutte le tabelle e viste nominate da questi laboratori nel database didattico cookbook_demo: oltre a people, products, orders e order_items, ripulisce notes, lines, people_copy, paid_copy, paid_orders e le tabelle rename_*. Tutti i loro dati vengono persi. Non esegue DROP DATABASE né rimuove database estranei. Usa un database dedicato senza dati di produzione. Le tabelle principali usano InnoDB e FOREIGN KEY esplicite, perché MySQL 8.4 ignora REFERENCES inline sulle colonne."
    return "La fixture elimina gli oggetti dei laboratori SQL/SQLite dal solo file didattico demo.sqlite e li ricrea: dati principali, viste, tabelle aggiuntive, FTS e trigger dimostrativi vengono rimossi. I loro dati vengono persi. Usa un file dedicato senza dati personali o di produzione. Le foreign key sono attive e il reset elimina prima gli oggetti dipendenti."

# titolo | SQL: inventario esplicito, non prodotto cartesiano di varianti.
SQL = [
("Proiettare soltanto le colonne necessarie","SELECT name,city FROM people ORDER BY id;"),
("Eliminare duplicati dalle città","SELECT DISTINCT city FROM people WHERE city IS NOT NULL ORDER BY city;"),
("Filtrare con condizioni congiunte","SELECT name FROM people WHERE age>=35 AND city='Roma';"),
("Combinare alternative con OR","SELECT name FROM people WHERE city='Roma' OR city='Milano';"),
("Escludere uno stato","SELECT id FROM orders WHERE status<>'cancelled';"),
("Verificare un intervallo inclusivo","SELECT name FROM products WHERE price BETWEEN 20 AND 50;"),
("Selezionare un insieme di stati","SELECT id FROM orders WHERE status IN ('new','paid');"),
("Cercare un prefisso testuale","SELECT name FROM people WHERE name LIKE 'A%';"),
("Individuare valori mancanti","SELECT name FROM people WHERE age IS NULL;"),
("Sostituire NULL in visualizzazione","SELECT name,COALESCE(city,'Non indicata') AS city FROM people;"),
("Classificare importi con CASE","SELECT id,CASE WHEN total>=100 THEN 'grande' ELSE 'piccolo' END AS fascia FROM orders;"),
("Ordinare per più criteri","SELECT name,age FROM people ORDER BY age DESC,name ASC;"),
("Contare righe e valori presenti","SELECT COUNT(*) AS righe,COUNT(age) AS eta_presenti FROM people;"),
("Calcolare il totale degli ordini pagati","SELECT SUM(total) AS fatturato FROM orders WHERE status='paid';"),
("Calcolare la media ignorando NULL","SELECT AVG(age) AS eta_media FROM people;"),
("Trovare gli estremi del listino","SELECT MIN(price) AS minimo,MAX(price) AS massimo FROM products;"),
("Raggruppare clienti per città","SELECT city,COUNT(*) AS clienti FROM people GROUP BY city;"),
("Filtrare gruppi con HAVING","SELECT person_id,SUM(total) AS spesa FROM orders GROUP BY person_id HAVING SUM(total)>100;"),
("Unire ordini e clienti","SELECT o.id,p.name,o.total FROM orders o JOIN people p ON p.id=o.person_id;"),
("Conservare clienti senza ordini","SELECT p.name,o.id FROM people p LEFT JOIN orders o ON o.person_id=p.id ORDER BY p.id,o.id;"),
("Trovare clienti privi di ordini","SELECT p.name FROM people p WHERE NOT EXISTS(SELECT 1 FROM orders o WHERE o.person_id=p.id);"),
("Verificare esistenza di un acquisto","SELECT p.name FROM people p WHERE EXISTS(SELECT 1 FROM orders o WHERE o.person_id=p.id AND o.status='paid');"),
("Confrontare con una media calcolata","SELECT name,price FROM products WHERE price>(SELECT AVG(price) FROM products);"),
("Calcolare una subquery correlata","SELECT p.name,(SELECT COUNT(*) FROM orders o WHERE o.person_id=p.id) AS ordini FROM people p;"),
("Sommare quantità attraverso tre tabelle","SELECT p.name,SUM(i.qty) AS pezzi FROM products p JOIN order_items i ON i.product_id=p.id JOIN orders o ON o.id=i.order_id WHERE o.status='paid' GROUP BY p.id,p.name;"),
("Unire insiemi senza duplicati","SELECT city AS luogo FROM people WHERE city IS NOT NULL UNION SELECT 'Torino';"),
("Conservare duplicati con UNION ALL","SELECT person_id FROM orders WHERE status='paid' UNION ALL SELECT person_id FROM orders WHERE status='new';"),
("Attribuire alias leggibili ai calcoli","SELECT name,price*stock AS valore_magazzino FROM products;"),
("Proteggere una divisione per zero","SELECT name,price/NULLIF(stock,0) AS prezzo_per_unita_stock FROM products;"),
("Usare una CTE per separare aggregazione e filtro","WITH spese AS (SELECT person_id,SUM(total) AS valore FROM orders GROUP BY person_id) SELECT p.name,s.valore FROM people p JOIN spese s ON s.person_id=p.id WHERE s.valore>=50;"),
("Numerare righe con ROW_NUMBER","SELECT id,total,ROW_NUMBER() OVER(ORDER BY total DESC,id) AS posizione FROM orders;"),
("Assegnare ranghi senza buchi","SELECT id,total,DENSE_RANK() OVER(ORDER BY total DESC) AS rango FROM orders;"),
("Calcolare un totale progressivo","SELECT id,total,SUM(total) OVER(ORDER BY id ROWS UNBOUNDED PRECEDING) AS cumulato FROM orders;"),
("Leggere il valore precedente","SELECT id,total,LAG(total) OVER(ORDER BY id) AS precedente FROM orders;"),
("Calcolare la quota del totale","SELECT id,total,100.0*total/SUM(total) OVER() AS percentuale FROM orders;"),
("Ottenere il primo ordine per cliente","WITH r AS(SELECT id,person_id,ROW_NUMBER() OVER(PARTITION BY person_id ORDER BY created_at,id) AS n FROM orders) SELECT id,person_id FROM r WHERE n=1;"),
("Inserire righe con colonne esplicite","INSERT INTO people(id,name,city,age,email) VALUES(5,'Barbara','Torino',39,'barbara@example.test'); SELECT name FROM people WHERE id=5;"),
("Inserire il risultato di una SELECT","CREATE TABLE adulti(name VARCHAR(80)); INSERT INTO adulti(name) SELECT name FROM people WHERE age>=18; SELECT * FROM adulti;"),
("Aggiornare prezzi con espressione","UPDATE products SET price=price*1.10 WHERE id=1; SELECT price FROM products WHERE id=1;"),
("Cancellare soltanto righe annullate","DELETE FROM orders WHERE status='cancelled' AND NOT EXISTS(SELECT 1 FROM order_items i WHERE i.order_id=orders.id); SELECT COUNT(*) FROM orders;"),
("Creare un vincolo CHECK","CREATE TABLE misure(id INTEGER PRIMARY KEY,valore DECIMAL(8,2) CHECK(valore>=0)); INSERT INTO misure VALUES(1,2.5); SELECT * FROM misure;"),
("Creare una chiave composta","CREATE TABLE presenze(person_id INTEGER,giorno VARCHAR(10),PRIMARY KEY(person_id,giorno)); INSERT INTO presenze VALUES(1,'2026-10-29'); SELECT * FROM presenze;"),
("Esporre una vista di lettura","CREATE VIEW pagati AS SELECT id,person_id,total FROM orders WHERE status='paid'; SELECT * FROM pagati;"),
("Indicizzare una colonna di ricerca","CREATE INDEX idx_orders_person ON orders(person_id); SELECT id FROM orders WHERE person_id=1;"),
("Rilevare email ripetute in dati importati","WITH imported(email) AS(SELECT 'ada@example.test' UNION ALL SELECT 'ada@example.test' UNION ALL SELECT 'grace@example.test') SELECT email,COUNT(*) AS duplicati FROM imported GROUP BY email HAVING COUNT(*)>1;"),
("Confrontare righe mediante self join","SELECT a.name,b.name FROM people a JOIN people b ON a.city=b.city AND a.id<b.id;"),
("Trovare l'ultimo acquisto senza funzioni finestra","SELECT o.id FROM orders o WHERE NOT EXISTS(SELECT 1 FROM orders n WHERE n.person_id=o.person_id AND (n.created_at>o.created_at OR(n.created_at=o.created_at AND n.id>o.id)));"),
("Aggregare condizionalmente più stati","SELECT SUM(CASE WHEN status='paid' THEN total ELSE 0 END) AS pagato,SUM(CASE WHEN status='new' THEN total ELSE 0 END) AS aperto FROM orders;"),
("Creare un prodotto cartesiano controllato","SELECT p.name,s.stato FROM people p CROSS JOIN(SELECT 'email' AS stato UNION ALL SELECT 'telefono') s ORDER BY p.id,s.stato;"),
]

SQLITE = [
("Attivare i vincoli referenziali","PRAGMA foreign_keys=ON; PRAGMA foreign_keys;"),
("Controllare integrità del database","PRAGMA integrity_check;"),
("Ispezionare struttura e tipi di tabella","PRAGMA table_info(people);"),
("Elencare gli indici di una tabella","PRAGMA index_list(people);"),
("Misurare pagine e dimensione pagina","PRAGMA page_count; PRAGMA page_size;"),
("Usare journal WAL per letture concorrenti","PRAGMA journal_mode=WAL; PRAGMA journal_mode;"),
("Limitare attesa su database occupato","PRAGMA busy_timeout=3000; PRAGMA busy_timeout;"),
("Verificare violazioni delle foreign key","PRAGMA foreign_key_check;"),
("Rendere atomico un trasferimento","BEGIN IMMEDIATE; WITH allowed AS MATERIALIZED(SELECT id FROM products WHERE id=1 AND stock>=1 AND EXISTS(SELECT 1 FROM products WHERE id=2 AND stock>=0)) UPDATE products SET stock=stock+CASE WHEN id=1 THEN -1 ELSE 1 END WHERE id IN(1,2) AND EXISTS(SELECT 1 FROM allowed) RETURNING id,stock; COMMIT; SELECT id,stock FROM products ORDER BY id;"),
("Annullare una transazione","BEGIN; UPDATE products SET stock=0; ROLLBACK; SELECT stock FROM products WHERE id=1;"),
("Annullare una parte con SAVEPOINT","SAVEPOINT prova; UPDATE people SET city='Napoli' WHERE id=1; ROLLBACK TO prova; RELEASE prova; SELECT city FROM people WHERE id=1;"),
("Eseguire UPSERT su chiave primaria","INSERT INTO products VALUES(1,'Tastiera',55,9) ON CONFLICT(id) DO UPDATE SET price=excluded.price,stock=excluded.stock; SELECT * FROM products WHERE id=1;"),
("Ignorare un inserimento già presente","INSERT INTO products VALUES(1,'Duplicato',10,1) ON CONFLICT(id) DO NOTHING; SELECT COUNT(*) FROM products;"),
("Restituire la riga appena inserita","INSERT INTO people VALUES(5,'Barbara','Torino',39,'barbara@example.test') RETURNING id,name;"),
("Recuperare ID intero autoassegnato","INSERT INTO products(name,price,stock) VALUES('Hub',25,4); SELECT last_insert_rowid();"),
("Misurare quante righe sono cambiate","UPDATE products SET stock=stock+1 WHERE stock>0; SELECT changes();"),
("Creare una tabella STRICT","CREATE TABLE letture(id INTEGER PRIMARY KEY,valore REAL NOT NULL) STRICT; INSERT INTO letture VALUES(1,3.5); SELECT * FROM letture;"),
("Risparmiare spazio con WITHOUT ROWID","CREATE TABLE etichette(k TEXT PRIMARY KEY,v TEXT) WITHOUT ROWID; INSERT INTO etichette VALUES('tema','chiaro'); SELECT * FROM etichette;"),
("Aggiungere una colonna generata","CREATE TABLE righe(prezzo REAL,quantita INTEGER,totale REAL GENERATED ALWAYS AS(prezzo*quantita) STORED); INSERT INTO righe(prezzo,quantita) VALUES(5,3); SELECT totale FROM righe;"),
("Creare un indice parziale","CREATE INDEX idx_open_orders ON orders(created_at) WHERE status='new'; EXPLAIN QUERY PLAN SELECT id FROM orders WHERE status='new' ORDER BY created_at;"),
("Creare un indice su espressione","CREATE INDEX idx_email_lower ON people(lower(email)); EXPLAIN QUERY PLAN SELECT id FROM people WHERE lower(email)='ada@example.test';"),
("Analizzare il piano di una query","EXPLAIN QUERY PLAN SELECT * FROM orders WHERE person_id=1;"),
("Aggiornare statistiche per il planner","ANALYZE; SELECT tbl,idx,stat FROM sqlite_stat1;"),
("Ispezionare gli oggetti del catalogo","SELECT type,name,tbl_name FROM sqlite_schema WHERE name NOT LIKE 'sqlite_%' ORDER BY type,name;"),
("Estrarre un campo JSON","SELECT json_extract('{\"user\":{\"name\":\"Ada\"}}','$.user.name');"),
("Espandere un array JSON in righe","SELECT value FROM json_each('[10,20,30]');"),
("Aggregare risultati in un array JSON","SELECT json_group_array(name) FROM people;"),
("Costruire oggetti JSON da colonne","SELECT json_object('id',id,'nome',name) FROM products;"),
("Modificare un documento JSON","SELECT json_set('{\"stock\":3}','$.stock',4);"),
("Validare JSON prima dell'importazione","SELECT json_valid('{\"ok\":true}') AS valido,json_valid('{x}') AS invalido;"),
("Creare ricerca full text FTS5","CREATE VIRTUAL TABLE docs USING fts5(title,body); INSERT INTO docs VALUES('Python','Leggere file e cartelle'); SELECT title FROM docs WHERE docs MATCH 'file';"),
("Pesare risultati FTS5 con BM25","CREATE VIRTUAL TABLE docs USING fts5(title,body); INSERT INTO docs VALUES('File','file file'),('Altro','file'); SELECT title,bm25(docs,5,1) AS score FROM docs WHERE docs MATCH 'file' ORDER BY score;"),
("Evidenziare parole trovate in FTS5","CREATE VIRTUAL TABLE docs USING fts5(body); INSERT INTO docs VALUES('Una guida Python'); SELECT highlight(docs,0,'[',']') FROM docs WHERE docs MATCH 'Python';"),
("Cercare sottostringhe con trigram","CREATE VIRTUAL TABLE names USING fts5(name,tokenize='trigram'); INSERT INTO names VALUES('programmazione'); SELECT name FROM names WHERE names MATCH 'gram';"),
("Calcolare una data relativa","SELECT date('2026-10-29','+7 days');"),
("Formattare un timestamp UTC","SELECT strftime('%Y-%m-%dT%H:%M:%SZ','2026-10-29 08:30:00');"),
("Convertire epoch Unix in data","SELECT datetime(0,'unixepoch');"),
("Misurare differenza in giorni","SELECT julianday('2026-11-02')-julianday('2026-10-29');"),
("Raggruppare fatturato per mese","SELECT strftime('%Y-%m',created_at) AS mese,SUM(total) FROM orders GROUP BY mese;"),
("Concatenare righe con separatore","SELECT group_concat(name,' | ') FROM(SELECT name FROM people ORDER BY name);"),
("Estrarre una porzione di stringa","SELECT substr(email,1,instr(email,'@')-1) FROM people;"),
("Ripulire spazi e caratteri esterni","SELECT trim('--- guida ---','- ');"),
("Confrontare testo ASCII senza caso","SELECT name FROM people WHERE name='ada' COLLATE NOCASE;"),
("Cercare con pattern GLOB","SELECT name FROM people WHERE name GLOB '[AG]*';"),
("Arrotondare importi per il report","SELECT name,round(price*1.22,2) FROM products;"),
("Generare una serie ricorsiva","WITH RECURSIVE n(x) AS(VALUES(1) UNION ALL SELECT x+1 FROM n WHERE x<7) SELECT x FROM n;"),
("Calcolare mediana con funzioni finestra","WITH v AS(SELECT total,row_number() OVER(ORDER BY total) r,count(*) OVER() n FROM orders) SELECT avg(total) FROM v WHERE r IN((n+1)/2,(n+2)/2);"),
("Filtrare un aggregato con FILTER","SELECT sum(total) FILTER(WHERE status='paid') FROM orders;"),
("Aggiornare con una tabella sorgente","UPDATE products SET stock=stock-i.qty FROM order_items i WHERE i.product_id=products.id AND i.order_id=1; SELECT id,stock FROM products;"),
("Rinominare una colonna","ALTER TABLE people RENAME COLUMN city TO citta; SELECT citta FROM people;"),
("Aggiungere una colonna con default","ALTER TABLE people ADD COLUMN active INTEGER NOT NULL DEFAULT 1; SELECT name,active FROM people;"),
("Scatenare un audit dopo un aggiornamento","CREATE TABLE audit(product_id INTEGER,old_stock INTEGER,new_stock INTEGER); CREATE TRIGGER stock_audit AFTER UPDATE OF stock ON products BEGIN INSERT INTO audit VALUES(old.id,old.stock,new.stock); END; UPDATE products SET stock=7 WHERE id=1; SELECT * FROM audit;"),
("Impedire stock negativo con trigger","CREATE TRIGGER prevent_stock BEFORE UPDATE OF stock ON products WHEN new.stock<0 BEGIN SELECT RAISE(ABORT,'Stock negativo'); END; UPDATE products SET stock=5 WHERE id=1; SELECT stock FROM products WHERE id=1;"),
("Mostrare dettagli delle foreign key","PRAGMA foreign_key_list(order_items);"),
("Verificare versione e opzioni SQLite","SELECT sqlite_version(); PRAGMA compile_options;"),
("Calcolare classificazione per partizione","SELECT person_id,total,rank() OVER(PARTITION BY person_id ORDER BY total DESC) FROM orders;"),
("Estrarre primi e ultimi valori finestra","SELECT id,first_value(total) OVER(ORDER BY id),last_value(total) OVER(ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) FROM orders;"),
("Dividere righe in fasce NTILE","SELECT id,total,ntile(2) OVER(ORDER BY total) AS fascia FROM orders;"),
("Esportare una stringa SQL quotata","SELECT quote(name),quote(NULL),quote(X'CAFE') FROM people LIMIT 1;"),
("Ispezionare tipi dinamici delle espressioni","SELECT typeof(1),typeof(1.5),typeof('1'),typeof(NULL);"),
("Codificare un BLOB in esadecimale","SELECT hex(X'0001CAFE'),length(X'0001CAFE');"),
("Combinare righe con INTERSECT","SELECT person_id FROM orders WHERE status='paid' INTERSECT SELECT id FROM people WHERE city='Roma';"),
("Sottrarre insiemi con EXCEPT","SELECT id FROM people EXCEPT SELECT person_id FROM orders;"),
("Paginare stabilmente tramite chiave","SELECT id,name FROM people WHERE id>2 ORDER BY id LIMIT 2;"),
]

POSTGRES = [
("Generare una serie di interi","SELECT * FROM generate_series(1,5);"),
("Generare un calendario giornaliero","SELECT d::date FROM generate_series('2026-10-01'::date,'2026-10-07'::date,interval '1 day') d;"),
("Estrarre campi da JSONB","SELECT '{\"user\":{\"name\":\"Ada\"}}'::jsonb #>> '{user,name}';"),
("Verificare contenimento JSONB","SELECT '{\"active\":true,\"level\":2}'::jsonb @> '{\"active\":true}'::jsonb;"),
("Espandere array JSONB","SELECT value FROM jsonb_array_elements('[1,2,3]'::jsonb);"),
("Modificare un percorso JSONB","SELECT jsonb_set('{\"stock\":3}'::jsonb,'{stock}','4');"),
("Aggregare righe in JSONB","SELECT jsonb_agg(jsonb_build_object('id',id,'name',name)) FROM people;"),
("Cercare con JSONPath","SELECT jsonb_path_query_array('[{\"p\":3},{\"p\":8}]'::jsonb,'$[*] ? (@.p > 5)');"),
("Creare un array tipizzato","SELECT ARRAY[1,2,3]::integer[];"),
("Espandere un array con ordinale","SELECT * FROM unnest(ARRAY['a','b']) WITH ORDINALITY;"),
("Filtrare con ANY su un array","SELECT name FROM people WHERE id=ANY(ARRAY[1,3]);"),
("Controllare sovrapposizione tra array","SELECT ARRAY['python','sql'] && ARRAY['sql','go'];"),
("Aggregare valori in array ordinato","SELECT array_agg(name ORDER BY name) FROM people;"),
("Trovare lunghezza e posizione in array","SELECT cardinality(ARRAY[4,8,12]),array_position(ARRAY[4,8,12],8);"),
("Estrarre l'ultimo ordine con DISTINCT ON","SELECT DISTINCT ON(person_id) person_id,id,total FROM orders ORDER BY person_id,created_at DESC,id DESC;"),
("Restituire righe da UPDATE","UPDATE products SET stock=stock+1 WHERE id=1 RETURNING id,stock;"),
("Fare UPSERT con EXCLUDED","INSERT INTO products VALUES(1,'Tastiera',60,4) ON CONFLICT(id) DO UPDATE SET price=EXCLUDED.price RETURNING id,price;"),
("Inserire righe evitando conflitti","INSERT INTO products VALUES(1,'Duplicato',5,1) ON CONFLICT DO NOTHING RETURNING id;"),
("Usare una CTE che modifica dati","WITH changed AS(UPDATE products SET stock=stock+1 WHERE id=1 RETURNING *) SELECT name,stock FROM changed;"),
("Applicare un join LATERAL","SELECT p.name,o.total FROM people p LEFT JOIN LATERAL(SELECT total FROM orders WHERE person_id=p.id ORDER BY created_at DESC LIMIT 1)o ON true;"),
("Cercare testo con ILIKE","SELECT name FROM people WHERE name ILIKE 'a%';"),
("Estrarre gruppi di regex","SELECT regexp_match('ordine-123','ordine-([0-9]+)');"),
("Separare stringhe con regex","SELECT regexp_split_to_table('uno, due;tre','[,;]\\s*');"),
("Sostituire tutte le corrispondenze regex","SELECT regexp_replace('tel: 123-456','[^0-9]','','g');"),
("Cercare full text italiano","SELECT to_tsvector('italian','programmare applicazioni') @@ plainto_tsquery('italian','applicazione');"),
("Pesare una ricerca full text","SELECT ts_rank(to_tsvector('italian','guida database sql'),plainto_tsquery('italian','database'));"),
("Evidenziare risultati full text","SELECT ts_headline('italian','Una guida ai database',plainto_tsquery('italian','database'));"),
("Calcolare il percentile continuo","SELECT percentile_cont(0.5) WITHIN GROUP(ORDER BY total) FROM orders;"),
("Aggregare più dimensioni con GROUPING SETS","SELECT status,person_id,SUM(total) FROM orders GROUP BY GROUPING SETS((status),(person_id),());"),
("Aggiungere subtotali con ROLLUP","SELECT status,person_id,SUM(total) FROM orders GROUP BY ROLLUP(status,person_id);"),
("Calcolare correlazione statistica","SELECT corr(price::float,stock::float) FROM products;"),
("Calcolare deviazione standard campionaria","SELECT stddev_samp(total) FROM orders;"),
("Costruire intervalli temporali","SELECT make_interval(days=>7,hours=>2);"),
("Troncare timestamp al mese","SELECT date_trunc('month','2026-10-29 10:15'::timestamp);"),
("Convertire un fuso orario","SELECT '2026-01-10 12:00+00'::timestamptz AT TIME ZONE 'Europe/Rome';"),
("Estrarre il giorno ISO della settimana","SELECT extract(isodow FROM date '2026-10-29');"),
("Calcolare distanza tra date","SELECT date '2026-11-02'-date '2026-10-29';"),
("Usare intervalli e sovrapposizioni range","SELECT daterange('2026-01-01','2026-02-01') && daterange('2026-01-20','2026-03-01');"),
("Verificare appartenenza a range","SELECT int4range(1,10) @> 5;"),
("Convertire indirizzi di rete","SELECT '192.168.1.25/24'::inet <<= '192.168.1.0/24'::cidr;"),
("Manipolare valori UUID tipizzati","SELECT '123e4567-e89b-12d3-a456-426614174000'::uuid;"),
("Creare un dominio vincolato","CREATE DOMAIN positive_amount AS numeric CHECK(VALUE>=0); SELECT 12.50::positive_amount;"),
("Creare un tipo enumerato","CREATE TYPE priority AS ENUM('low','normal','high'); SELECT 'normal'::priority;"),
("Definire una funzione SQL immutabile","CREATE FUNCTION vat(numeric) RETURNS numeric LANGUAGE SQL IMMUTABLE AS 'SELECT round($1*1.22,2)'; SELECT vat(10);"),
("Definire una funzione PLpgSQL","CREATE FUNCTION stock_label(integer) RETURNS text LANGUAGE plpgsql AS $$ BEGIN IF $1>0 THEN RETURN 'disponibile'; ELSE RETURN 'esaurito'; END IF; END $$; SELECT stock_label(3);"),
("Esporre una vista materializzata","CREATE MATERIALIZED VIEW sales_totals AS SELECT person_id,SUM(total) AS total FROM orders GROUP BY person_id; SELECT * FROM sales_totals;"),
("Aggiornare una vista materializzata","CREATE MATERIALIZED VIEW stock_summary AS SELECT SUM(stock) AS n FROM products; UPDATE products SET stock=9 WHERE id=1; REFRESH MATERIALIZED VIEW stock_summary; SELECT * FROM stock_summary;"),
("Definire una colonna identity","CREATE TABLE notes(id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,body text); INSERT INTO notes(body) VALUES('prima') RETURNING *;"),
("Creare una colonna generata","CREATE TABLE lines(price numeric,qty integer,total numeric GENERATED ALWAYS AS(price*qty) STORED); INSERT INTO lines(price,qty) VALUES(5,3) RETURNING *;"),
("Creare indice parziale su righe attive","CREATE INDEX paid_total ON orders(total) WHERE status='paid'; EXPLAIN SELECT * FROM orders WHERE status='paid' AND total>100;"),
("Creare un indice GIN su JSONB","CREATE TABLE documents(id integer,payload jsonb); CREATE INDEX docs_payload ON documents USING gin(payload); INSERT INTO documents VALUES(1,'{\"active\":true}'); SELECT * FROM documents WHERE payload @> '{\"active\":true}';"),
("Ispezionare un piano senza eseguire la query","EXPLAIN(COSTS true,FORMAT JSON) SELECT * FROM orders WHERE person_id=1;"),
("Analizzare un piano reale su dati sintetici","EXPLAIN(ANALYZE,BUFFERS) SELECT * FROM products WHERE price>10;"),
("Misurare dimensione di una relazione","SELECT pg_size_pretty(pg_total_relation_size('people'));"),
("Elencare colonne tramite information_schema","SELECT column_name,data_type FROM information_schema.columns WHERE table_schema=current_schema() AND table_name='people';"),
("Ispezionare i vincoli della tabella","SELECT conname,pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid='orders'::regclass;"),
("Trovare indici disponibili nello schema","SELECT tablename,indexname,indexdef FROM pg_indexes WHERE schemaname=current_schema();"),
("Usare un advisory lock transazionale","BEGIN; SELECT pg_advisory_xact_lock(42); SELECT 'lavoro serializzato'; COMMIT;"),
("Limitare il tempo di una query","BEGIN; SET LOCAL statement_timeout='2s'; SELECT count(*) FROM products; COMMIT;"),
("Impostare isolamento repeatable read","BEGIN ISOLATION LEVEL REPEATABLE READ; SELECT count(*) FROM orders; COMMIT;"),
("Bloccare righe per un aggiornamento","BEGIN; SELECT * FROM products WHERE id=1 FOR UPDATE; UPDATE products SET stock=stock-1 WHERE id=1 AND stock>0; COMMIT;"),
("Prelevare lavoro con SKIP LOCKED","BEGIN; SELECT id FROM orders WHERE status='new' ORDER BY id FOR UPDATE SKIP LOCKED LIMIT 1; COMMIT;"),
("Preparare una query parametrica","PREPARE by_person(integer) AS SELECT id,total FROM orders WHERE person_id=$1; EXECUTE by_person(1); DEALLOCATE by_person;"),
("Confrontare NULL con IS DISTINCT FROM","SELECT name FROM people WHERE city IS DISTINCT FROM 'Roma';"),
("Concatenare testi ignorando NULL","SELECT concat_ws(' - ',name,city) FROM people;"),
("Creare un identificatore SQL con format","SELECT format('SELECT %I FROM %I WHERE name=%L','id','people','Ada');"),
("Espandere un record JSON tipizzato","SELECT * FROM jsonb_to_record('{\"name\":\"Ada\",\"age\":35}'::jsonb) AS x(name text,age integer);"),
("Seguire una gerarchia ricorsiva","WITH RECURSIVE tree(id,parent) AS(VALUES(1,NULL::integer),(2,1),(3,2)),walk AS(SELECT id,parent,0 AS depth FROM tree WHERE parent IS NULL UNION ALL SELECT t.id,t.parent,w.depth+1 FROM tree t JOIN walk w ON t.parent=w.id) SELECT * FROM walk;"),
("Eseguire un blocco DO con messaggio","DO $$ BEGIN RAISE NOTICE 'Schema demo: %',current_schema(); END $$;"),
("Aggiungere una constraint non ancora validata","ALTER TABLE products ADD CONSTRAINT valid_stock CHECK(stock>=0) NOT VALID; ALTER TABLE products VALIDATE CONSTRAINT valid_stock;"),
("Creare una tabella partizionata","CREATE TABLE readings(day date,value numeric) PARTITION BY RANGE(day); CREATE TABLE readings_2026 PARTITION OF readings FOR VALUES FROM('2026-01-01') TO('2027-01-01'); INSERT INTO readings VALUES('2026-10-29',3); SELECT tableoid::regclass,* FROM readings;"),
("Verificare permessi sullo schema corrente","SELECT has_schema_privilege(current_user,current_schema(),'USAGE');"),
("Mostrare configurazione locale utile al debug","SELECT current_database(),current_user,current_schema(); SHOW server_version; SHOW TimeZone;"),
]

MYSQL = [
("Fare UPSERT su chiave duplicata","INSERT INTO products VALUES(1,'Tastiera',55,9) AS new ON DUPLICATE KEY UPDATE price=new.price; SELECT * FROM products WHERE id=1;"),
("Inserire evitando duplicati con IGNORE","INSERT IGNORE INTO products VALUES(1,'Duplicato',2,1); SHOW WARNINGS;"),
("Generare un ID AUTO_INCREMENT","CREATE TABLE notes(id bigint AUTO_INCREMENT PRIMARY KEY,body text); INSERT INTO notes(body) VALUES('prima'); SELECT LAST_INSERT_ID();"),
("Leggere righe modificate dal comando","UPDATE products SET stock=stock+1 WHERE id=1; SELECT ROW_COUNT();"),
("Estrarre un campo JSON","SELECT JSON_UNQUOTE(JSON_EXTRACT('{\"user\":\"Ada\"}','$.user'));"),
("Costruire un oggetto JSON","SELECT JSON_OBJECT('id',id,'name',name) FROM people;"),
("Aggregare righe in JSON","SELECT JSON_ARRAYAGG(name) FROM people;"),
("Modificare un documento JSON","SELECT JSON_SET('{\"stock\":3}','$.stock',4);"),
("Verificare contenimento JSON","SELECT JSON_CONTAINS('[1,2,3]','2');"),
("Espandere JSON_TABLE","SELECT x.n FROM JSON_TABLE('[1,2,3]','$[*]' COLUMNS(n INT PATH '$')) AS x;"),
("Validare un documento JSON","SELECT JSON_VALID('{\"a\":1}'),JSON_VALID('{x}');"),
("Contare elementi di un documento JSON","SELECT JSON_LENGTH('[1,2,3]');"),
("Separare stringhe con SUBSTRING_INDEX","SELECT SUBSTRING_INDEX(email,'@',1) FROM people;"),
("Concatenare valori con GROUP_CONCAT","SELECT GROUP_CONCAT(name ORDER BY name SEPARATOR ' | ') FROM people;"),
("Cercare con REGEXP_LIKE","SELECT name FROM people WHERE REGEXP_LIKE(name,'^[AG]');"),
("Estrarre una corrispondenza regex","SELECT REGEXP_SUBSTR('ordine-123','[0-9]+');"),
("Sostituire con REGEXP_REPLACE","SELECT REGEXP_REPLACE('123-456','[^0-9]','');"),
("Gestire NULL con IFNULL","SELECT name,IFNULL(city,'Non indicata') FROM people;"),
("Confrontare NULL in modo sicuro","SELECT NULL <=> NULL AS uguali,1 <=> NULL AS diversi;"),
("Classificare righe con IF","SELECT name,IF(stock>0,'disponibile','esaurito') FROM products;"),
("Calcolare intervalli con DATE_ADD","SELECT DATE_ADD('2026-10-29',INTERVAL 7 DAY);"),
("Calcolare differenza in giorni","SELECT DATEDIFF('2026-11-02','2026-10-29');"),
("Formattare date per mese","SELECT DATE_FORMAT(created_at,'%Y-%m'),SUM(total) FROM orders GROUP BY DATE_FORMAT(created_at,'%Y-%m');"),
("Interpretare una data italiana","SELECT STR_TO_DATE('29/10/2026','%d/%m/%Y');"),
("Convertire timestamp Unix","SELECT FROM_UNIXTIME(0);"),
("Calcolare l'ultimo giorno del mese","SELECT LAST_DAY('2026-02-10');"),
("Calcolare distribuzione cumulativa dei totali","SELECT id,total,CUME_DIST() OVER(ORDER BY total) AS quota_cumulativa FROM orders;"),
("Calcolare un totale cumulato","SELECT id,SUM(total) OVER(ORDER BY id ROWS UNBOUNDED PRECEDING) FROM orders;"),
("Misurare differenze con LAG","SELECT id,total-LAG(total) OVER(ORDER BY id) AS differenza FROM orders;"),
("Generare una sequenza ricorsiva","WITH RECURSIVE n AS(SELECT 1 AS x UNION ALL SELECT x+1 FROM n WHERE x<7) SELECT x FROM n;"),
("Selezionare prima riga per gruppo","WITH r AS(SELECT id,person_id,ROW_NUMBER() OVER(PARTITION BY person_id ORDER BY created_at) AS n FROM orders) SELECT * FROM r WHERE n=1;"),
("Usare CTE per un report aggregato","WITH totals AS(SELECT person_id,SUM(total) AS total FROM orders GROUP BY person_id) SELECT p.name,t.total FROM people p JOIN totals t ON t.person_id=p.id;"),
("Creare colonne generate persistenti","CREATE TABLE lines(price DECIMAL(10,2),qty INT,total DECIMAL(12,2) GENERATED ALWAYS AS(price*qty) STORED); INSERT INTO lines(price,qty) VALUES(5,3); SELECT * FROM lines;"),
("Creare un indice funzionale","CREATE INDEX email_lower ON people((LOWER(email))); EXPLAIN SELECT id FROM people WHERE LOWER(email)='ada@example.test';"),
("Creare un indice composto","CREATE INDEX status_date ON orders(status,created_at); EXPLAIN SELECT * FROM orders WHERE status='paid' ORDER BY created_at;"),
("Ispezionare il piano con EXPLAIN JSON","EXPLAIN FORMAT=JSON SELECT * FROM products WHERE price>20;"),
("Aggiornare statistiche di una tabella","ANALYZE TABLE products;"),
("Elencare indici con SHOW INDEX","SHOW INDEX FROM people;"),
("Mostrare DDL esatto di una tabella","SHOW CREATE TABLE orders;"),
("Leggere colonne da information_schema","SELECT COLUMN_NAME,DATA_TYPE FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='people';"),
("Ispezionare motore e dimensioni delle tabelle","SELECT TABLE_NAME,ENGINE,DATA_LENGTH FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE();"),
("Definire una vista di soli ordini pagati","CREATE VIEW paid_orders AS SELECT id,person_id,total FROM orders WHERE status='paid' WITH CHECK OPTION; SELECT * FROM paid_orders;"),
("Aggiornare con JOIN","UPDATE products p JOIN order_items i ON i.product_id=p.id SET p.stock=p.stock-i.qty WHERE i.order_id=1; SELECT id,stock FROM products;"),
("Copiare struttura senza copiare dati","CREATE TABLE people_copy LIKE people; SHOW CREATE TABLE people_copy;"),
("Copiare dati da una query","CREATE TABLE paid_copy AS SELECT * FROM orders WHERE status='paid'; SELECT * FROM paid_copy;"),
("Modificare il tipo di una colonna","ALTER TABLE people MODIFY COLUMN name VARCHAR(120) NOT NULL; SHOW COLUMNS FROM people;"),
("Rinominare atomicamente due tabelle MySQL","CREATE TABLE rename_a(id INT); CREATE TABLE rename_b(id INT); RENAME TABLE rename_a TO rename_old,rename_b TO rename_new; SHOW TABLES LIKE 'rename_%';"),
("Aggiungere vincolo CHECK","ALTER TABLE products ADD CONSTRAINT stock_nonnegative CHECK(stock>=0); SELECT stock FROM products;"),
("Eseguire una transazione con rollback","START TRANSACTION; UPDATE products SET stock=0; ROLLBACK; SELECT stock FROM products WHERE id=1;"),
("Usare un savepoint interno","START TRANSACTION; SAVEPOINT prova; UPDATE products SET stock=0 WHERE id=1; ROLLBACK TO SAVEPOINT prova; COMMIT; SELECT stock FROM products WHERE id=1;"),
("Bloccare una riga con FOR UPDATE","START TRANSACTION; SELECT * FROM products WHERE id=1 FOR UPDATE; UPDATE products SET stock=stock-1 WHERE id=1 AND stock>0; COMMIT;"),
("Prelevare un lavoro con SKIP LOCKED","START TRANSACTION; SELECT id FROM orders WHERE status='new' ORDER BY id LIMIT 1 FOR UPDATE SKIP LOCKED; COMMIT;"),
("Preparare query con parametro","PREPARE q FROM 'SELECT name FROM people WHERE id=?'; SET @person=1; EXECUTE q USING @person; DEALLOCATE PREPARE q;"),
("Impostare isolamento per transazione","SET TRANSACTION ISOLATION LEVEL READ COMMITTED; START TRANSACTION; SELECT COUNT(*) FROM people; COMMIT;"),
("Controllare modalità SQL rigorosa","SELECT @@SESSION.sql_mode;"),
("Impostare charset connessione UTF8MB4","SET NAMES utf8mb4; SELECT @@character_set_connection;"),
("Generare e convertire un UUID binario","SET @u=UUID(); SELECT @u,BIN_TO_UUID(UUID_TO_BIN(@u));"),
("Calcolare checksum SHA2 per un dato","SELECT SHA2('contenuto',256);"),
("Codificare e decodificare base64","SELECT TO_BASE64('guida'),FROM_BASE64('Z3VpZGE=');"),
]

def project(b, key, title, files, command, purpose):
    if b.stack=="postgresql":command=command.replace("psql --dbname", "psql --host=127.0.0.1 --dbname")
    if b.stack=="mysql":command=command.replace("mysql --database", "mysql --host=127.0.0.1 --default-character-set=utf8mb4 --database")
    b.add(key,title,purpose,files,section="Database",project=True,commands=command,
          explanation=f"## Obiettivo\n{purpose}\n\n## Procedura\nEsporta tutti i file in una cartella dedicata. Usa esclusivamente un database didattico vuoto: lo schema contiene dati sintetici. Il README specifica ordine, controlli e risultato. Esegui i comandi dalla cartella esportata.\n\n## Verifica\nConfronta i risultati con le query di controllo incluse; nessun server remoto è necessario per le varianti SQLite.",
          expected="Le query di controllo restituiscono i risultati indicati nel README.",verification=verification(b.stack,key,files),tags=["project","schema","seed","report"],errors=["Non usare uno schema con dati reali: gli script ricreano gli oggetti del laboratorio."])

def build_all():
    specs=[("sql",SQL,50,"SQL comune; esecuzione dimostrativa SQLite 3.45+",["https://www.sqlite.org/lang.html"]),
           ("sqlite",SQLITE,65,"SQLite 3.45+ con JSON1/FTS5",["https://www.sqlite.org/lang.html","https://www.sqlite.org/fts5.html"]),
           ("postgresql",POSTGRES,75,"PostgreSQL 18; psql",["https://www.postgresql.org/docs/18/sql.html","https://www.postgresql.org/docs/18/sql-dropschema.html"]),
           ("mysql",MYSQL,60,"MySQL 8.4 LTS; differenze MariaDB da verificare",["https://dev.mysql.com/doc/refman/8.4/en/","https://dev.mysql.com/doc/refman/8.4/en/ansi-diff-foreign-keys.html"])]
    for stack,rows,target,version,sources in specs:
        prereq=("Client sqlite3 nel PATH; cartella scrivibile. Il catalogo è offline; il client DB va installato separatamente." if stack in("sql","sqlite") else "Server locale e client installati; database didattico cookbook_demo già creato; credenziali fornite dal client, mai nel sorgente.")
        b=Book(stack,version,sources,prereq)
        fixture=fixture_for(stack)
        for title,query in rows:
            operation_note=("La CTE allowed materializzata congela la disponibilità prima della modifica. Un solo UPDATE sposta l'unità su entrambe le righe oppure non modifica nulla: sorgente esaurito, destinazione mancante o stock non valido non devono creare o perdere quantità. Con i dati iniziali gli stock passano da 8/0 a 7/1; con sorgente 1 passano a 0/1; con sorgente 0 rimangono invariati. La somma degli stock deve restare uguale." if stack=="sqlite" and title=="Rendere atomico un trasferimento" else "")
            if stack in("sql","sqlite"):
                command='sqlite3 demo.sqlite ".read fixture.sql" ".read query.sql"'
            elif stack=="postgresql": command='psql --host=127.0.0.1 --dbname cookbook_demo --set ON_ERROR_STOP=1 --file fixture.sql --file query.sql'
            else: command='mysql --host=127.0.0.1 --default-character-set=utf8mb4 --database=cookbook_demo --execute="source fixture.sql; source query.sql;"'
            # Uno schema viene ricreato per ciascuna ricetta, così l'esempio è esportabile da solo.
            b.add(title,title,"Laboratorio con dati sintetici: "+title.lower()+".",{"fixture.sql":fixture,"query.sql":query},
                  section="Database",commands=command,tags=["database","query",stack]+title.lower().split()[:3],
                  explanation=f"## Obiettivo\n{title}.\n\n## Preparazione e reset del laboratorio\nEsporta fixture.sql e query.sql nella stessa cartella. {fixture_guide(stack)}\n\n## Lettura del codice\nLa query in query.sql è completa e lavora sui dati della fixture; i comandi vanno eseguiti dalla cartella esportata. Individua nel risultato le colonne o i metadati richiesti dal titolo. Prima di ogni nuova prova riesegui fixture.sql e poi query.sql: il reset comprende anche gli oggetti extra creati dalle query DDL del laboratorio. {operation_note}\n\n## Compatibilità\nSintassi prevista per {version}. Le funzioni specifiche del motore non vanno trasferite senza adattamento ad altri database.",
                  expected="La query termina senza errori e mostra il risultato dell'operazione indicata; per DDL il client conferma la creazione dell'oggetto.",
                  verification=verification(stack,title,{"fixture.sql":fixture,"query.sql":query}),errors=["Tabella già esistente: rieseguire la fixture in un database di laboratorio vuoto.","Funzione o estensione assente: controllare versione e opzioni del motore indicati nei prerequisiti."])
        if stack=="sql":
            project(b,"progetto-report-vendite","Progetto: report vendite con schema relazionale",{"schema.sql":fixture_for("sql"),"report.sql":"SELECT p.name,SUM(o.total) AS totale FROM people p JOIN orders o ON o.person_id=p.id WHERE o.status='paid' GROUP BY p.id,p.name;\nSELECT SUM(qty) AS pezzi FROM order_items;","README.md":"# Report vendite\nUsare soltanto un file demo.sqlite dedicato: schema.sql elimina gli oggetti del laboratorio e tutti i loro dati.\nEseguire schema.sql poi report.sql con sqlite3 su demo.sqlite.\nIl report pagati restituisce Ada con totale270; i pezzi complessivi sono6.\nSchema e dati sono solo didattici."},'sqlite3 demo.sqlite ".read schema.sql" ".read report.sql"',"Costruire un report ripetibile distinguendo schema, dati e interrogazioni.")
        elif stack=="sqlite":
            project(b,"progetto-note-fts","Progetto: archivio note SQLite con ricerca FTS",{"schema.sql":"PRAGMA foreign_keys=ON; CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY,title TEXT NOT NULL,body TEXT NOT NULL); CREATE VIRTUAL TABLE IF NOT EXISTS search USING fts5(title,body,content='notes',content_rowid='id'); CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON notes BEGIN INSERT INTO search(rowid,title,body) VALUES(new.id,new.title,new.body); END;","seed.sql":"INSERT INTO notes(title,body) VALUES('Python','Leggere file'),('SQL','Cercare nei dati');","search.sql":"SELECT rowid,title,bm25(search) FROM search WHERE search MATCH 'file' ORDER BY bm25(search);","README.md":"# Note FTS5\nSu un file note.sqlite nuovo eseguire schema, seed, search in questo ordine.\nRisultato: la nota Python. Il trigger mantiene l'indice per gli inserimenti; questo laboratorio non prevede update/delete.\nRichiede FTS5."},'sqlite3 note.sqlite ".read schema.sql" ".read seed.sql" ".read search.sql"',"Creare un archivio persistente con indice full text aggiornato agli inserimenti.")
        elif stack=="postgresql":
            project(b,"progetto-coda-transazionale","Progetto: coda lavori transazionale PostgreSQL",{"schema.sql":"CREATE SCHEMA IF NOT EXISTS queue_demo; CREATE TABLE IF NOT EXISTS queue_demo.jobs(id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,payload jsonb NOT NULL,status text NOT NULL DEFAULT 'ready');","seed.sql":"INSERT INTO queue_demo.jobs(payload) VALUES('{\"task\":\"report\"}'),('{\"task\":\"export\"}');","claim.sql":"BEGIN; WITH next AS(SELECT id FROM queue_demo.jobs WHERE status='ready' ORDER BY id FOR UPDATE SKIP LOCKED LIMIT 1) UPDATE queue_demo.jobs SET status='running' FROM next WHERE jobs.id=next.id RETURNING jobs.*; COMMIT;","README.md":"# Coda lavori\nDatabase cookbook_demo dedicato. Eseguire schema.sql, seed.sql e claim.sql.\nclaim.sql restituisce un solo lavoro e lo porta a running. Ripetendo viene prelevato il successivo.\nUsare connessioni distinte per osservare SKIP LOCKED."},'psql --dbname cookbook_demo -v ON_ERROR_STOP=1 -f schema.sql -f seed.sql -f claim.sql',"Prelevare un solo lavoro senza assegnarlo contemporaneamente a due worker.")
            project(b,"progetto-report-materializzato","Progetto: report PostgreSQL con vista materializzata",{"schema.sql":"CREATE SCHEMA IF NOT EXISTS report_demo; CREATE TABLE IF NOT EXISTS report_demo.sales(id bigint GENERATED ALWAYS AS IDENTITY,day date NOT NULL,amount numeric(12,2) NOT NULL CHECK(amount>=0));","seed.sql":"INSERT INTO report_demo.sales(day,amount) VALUES('2026-01-10',10),('2026-01-11',20);","report.sql":"CREATE MATERIALIZED VIEW report_demo.monthly AS SELECT date_trunc('month',day)::date AS month,SUM(amount) AS total FROM report_demo.sales GROUP BY 1; CREATE UNIQUE INDEX ON report_demo.monthly(month); SELECT * FROM report_demo.monthly;","refresh.sql":"REFRESH MATERIALIZED VIEW CONCURRENTLY report_demo.monthly; SELECT * FROM report_demo.monthly;","README.md":"# Report materializzato\nSchema report_demo vuoto. Eseguire schema, seed, report, refresh.\nRisultato iniziale: gennaio2026 totale30. L'indice univoco consente refresh concurrently. report.sql va eseguito una volta soltanto."},'psql --dbname cookbook_demo -v ON_ERROR_STOP=1 -f schema.sql -f seed.sql -f report.sql -f refresh.sql',"Separare acquisizione dati e report persistente con aggiornamento concorrente.")
        else:
            project(b,"progetto-magazzino","Progetto: magazzino MySQL con transazione controllata",{"schema.sql":"CREATE TABLE IF NOT EXISTS stock_demo(id INT PRIMARY KEY,name VARCHAR(80) NOT NULL,qty INT NOT NULL CHECK(qty>=0)) ENGINE=InnoDB;","seed.sql":"INSERT INTO stock_demo VALUES(1,'Tastiera',8),(2,'Mouse',4) AS new ON DUPLICATE KEY UPDATE qty=new.qty;","reserve.sql":"START TRANSACTION; UPDATE stock_demo SET qty=qty-2 WHERE id=1 AND qty>=2; SELECT ROW_COUNT() AS prenotato; COMMIT; SELECT * FROM stock_demo WHERE id=1;","README.md":"# Magazzino\nDatabase cookbook_demo dedicato. Eseguire schema, seed, reserve.\nRisultato: prenotato1 e quantità6. Il controllo qty>=2 evita overselling in questo singolo UPDATE atomico.\nPer un nuovo scenario ripetere seed."},'mysql --database=cookbook_demo --execute="source schema.sql; source seed.sql; source reserve.sql;"',"Prenotare quantità disponibili evitando stock negativo con aggiornamento atomico.")
        assert len(b.recipes)==target,(stack,len(b.recipes),target)
        b.save()

if __name__=="__main__": build_all()
