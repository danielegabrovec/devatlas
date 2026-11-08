"""Independent database review: SQLite is synthetic/in-memory; Docker is read-only."""
from __future__ import annotations
import concurrent.futures
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
from catalog_support import ROOT, CATALOG, DATE, slug

STAGES={"sql":50,"sqlite":65,"postgresql":75,"mysql":60}
PRIMARY={
 "mysql_fk":"https://dev.mysql.com/doc/refman/8.4/en/ansi-diff-foreign-keys.html",
 "pg_drop":"https://www.postgresql.org/docs/18/sql-dropschema.html",
 "pg_refresh":"https://www.postgresql.org/docs/18/sql-refreshmaterializedview.html",
 "pg_select":"https://www.postgresql.org/docs/18/sql-select.html",
 "mysql_upsert":"https://dev.mysql.com/doc/refman/8.4/en/insert-on-duplicate.html",
 "mysql_json":"https://dev.mysql.com/doc/refman/8.4/en/json-table-functions.html",
 "mysql_client":"https://dev.mysql.com/doc/refman/8.4/en/mysql-commands.html",
 "mysql_client_source":"https://raw.githubusercontent.com/mysql/mysql-server/8.4/client/mysql.cc",
 "sqlite_materialized":"https://www.sqlite.org/lang_with.html",
}

def digest_other_stacks():
    checksum=hashlib.sha256()
    for path in sorted(CATALOG.rglob("*")):
        if not path.is_file() or path.relative_to(CATALOG).parts[0] in STAGES:continue
        checksum.update(path.relative_to(CATALOG).as_posix().encode())
        checksum.update(hashlib.sha256(path.read_bytes()).digest())
    return checksum.hexdigest()

def docker_probe():
    commands={"info":["docker","info","--format","{{json .ServerVersion}}"],"images":["docker","image","ls","--format","{{.Repository}}:{{.Tag}}"]}
    def run(item):
        key,command=item
        try:
            result=subprocess.run(command,capture_output=True,text=True,timeout=7)
            return key,{"command":command,"exit_code":result.returncode,"stdout":result.stdout.strip(),"stderr":result.stderr.strip()[:1800]}
        except (OSError,subprocess.TimeoutExpired) as exc:return key,{"command":command,"error":str(exc)}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:return dict(pool.map(run,commands.items()))

def load_records():
    records=[]
    for stack,expected in STAGES.items():
        paths=sorted((CATALOG/stack).glob("*/recipe.json"));assert len(paths)==expected,(stack,len(paths))
        for path in paths:
            recipe=json.loads(path.read_text(encoding="utf-8"))
            recipe["_path"]=path
            recipe["_files"]={a["path"]:(path.parent/a["source"]).read_text(encoding="utf-8") for a in recipe["assets"] if a["role"]=="file"}
            recipe["_file_hashes"]={name:hashlib.sha256(source.encode()).hexdigest() for name,source in recipe["_files"].items()}
            assert all(a.get("sha256")==recipe["_file_hashes"][a["path"]] for a in recipe["assets"] if a["role"]=="file")
            records.append(recipe)
    assert len(records)==250 and sum(r["project"] for r in records)==5
    return records

def execute_sqlite(recipe):
    files=recipe["_files"]
    details={"id":recipe["id"],"cycles":1,"passed":False}
    with sqlite3.connect(":memory:") as db:
        if recipe["project"] and recipe["stack"]=="sqlite":
            for name in ("schema.sql","seed.sql","search.sql"):db.executescript(files[name])
            assert db.execute("SELECT title FROM search WHERE search MATCH 'file'").fetchall()==[("Python",)]
            details["expected_checked"]="La ricerca FTS restituisce soltanto la nota Python su un database nuovo."
        else:
            fixture=files["schema.sql"] if recipe["project"] else files["fixture.sql"]
            query=files["report.sql"] if recipe["project"] else files["query.sql"]
            for cycle in range(2):
                db.executescript(fixture)
                db.executescript(query)
                assert db.execute("PRAGMA foreign_keys").fetchone()[0]==1
                db.execute("SAVEPOINT negative_fk")
                try:
                    db.execute("INSERT INTO orders(id,person_id,total,status,created_at) VALUES(999,99999,1,'new','2026-01-01')")
                    raise AssertionError("Foreign key non applicata")
                except sqlite3.IntegrityError:pass
                finally:db.execute("ROLLBACK TO negative_fk");db.execute("RELEASE negative_fk")
            details.update(cycles=2,expected_checked="Fixture e query completate due volte sullo stesso DB; inserimento con FK inesistente rifiutato in entrambi i cicli.")
            if recipe["project"]:
                assert db.execute("SELECT SUM(total) FROM orders WHERE status='paid'").fetchone()[0]==270
                assert db.execute("SELECT SUM(qty) FROM order_items").fetchone()[0]==6
                details["expected_checked"]+=" Report Ada=270 e quantità complessiva=6."
    details["passed"]=True
    return details

def transfer_cases(recipe):
    results=[]
    for source,missing,expected in [(8,False,(7,1)),(1,False,(0,1)),(0,False,(0,0)),(8,True,(8,None))]:
        with sqlite3.connect(":memory:") as db:
            db.executescript(recipe["_files"]["fixture.sql"])
            db.execute("UPDATE products SET stock=? WHERE id=1",(source,))
            if missing:
                db.execute("DELETE FROM order_items WHERE product_id=2")
                db.execute("DELETE FROM products WHERE id=2")
            db.commit()
            before=db.execute("SELECT SUM(stock) FROM products").fetchone()[0]
            db.executescript(recipe["_files"]["query.sql"])
            after=db.execute("SELECT SUM(stock) FROM products").fetchone()[0]
            src=db.execute("SELECT stock FROM products WHERE id=1").fetchone()[0]
            row=db.execute("SELECT stock FROM products WHERE id=2").fetchone()
            dst=row[0] if row else None
            assert (src,dst)==expected and before==after
            results.append({"source_stock":source,"destination_missing":missing,"stocks_after":[src,dst],"total_before":before,"total_after":after,"passed":True})
    return results

def semantic_sample(records):
    choices=[
      ("sql","progetto-report-vendite","Report pagati Ada=270 e somma quantità=6 confermati realmente in memoria."),
      ("sqlite","progetto-note-fts","Schema/seed/search coerenti; risultato Python verificato realmente; il progetto richiede un file nuovo e documenta il trigger insert-only."),
      ("postgresql","progetto-coda-transazionale","Claim seleziona e aggiorna lo stesso job nella stessa transazione con SKIP LOCKED; RETURNING descrive il job assegnato."),
      ("postgresql","progetto-report-materializzato","Indice UNIQUE sulla colonna month, vista inizialmente popolata e REFRESH CONCURRENTLY rispettano i prerequisiti documentati; totale iniziale atteso30."),
      ("mysql","progetto-magazzino","InnoDB e UPDATE condizionale proteggono lo stock; ROW_COUNT viene letto subito dopo UPDATE; dati iniziali8 diventano6."),
      ("postgresql","Modificare un percorso JSONB","jsonb_set usa un percorso testuale e un nuovo valore JSONB; stock atteso4."),
      ("postgresql","Applicare un join LATERAL","LEFT JOIN LATERAL mantiene Alan senza ordini; sui dati demo i totali sono Ada180,Linus20,Grace50,AlanNULL."),
      ("postgresql","Definire una funzione PLpgSQL","Firma, corpo dollar-quoted e lingua sono coerenti; stock_label(3) deve restituire disponibile."),
      ("postgresql","Creare una colonna generata","Espressione price*qty valida per STORED; INSERT omette la colonna generata e produce15."),
      ("postgresql","Creare un indice GIN su JSONB","Operatore di contenimento @> è compatibile con GIN jsonb; indice creato prima dell'inserimento, risultato atteso documento1."),
      ("postgresql","Prelevare lavoro con SKIP LOCKED","Sintassi locking PostgreSQL corretta; la scheda dimostra il lock temporaneo, mentre il capstone coda aggiunge la presa in carico persistente."),
      ("postgresql","Seguire una gerarchia ricorsiva","CTE iniziale e recursive walk coerenti: radice1 profondità0, nodo2 profondità1, nodo3 profondità2."),
      ("mysql","Fare UPSERT su chiave duplicata","Alias della nuova riga supportato da MySQL8.4; sul duplicato aggiorna solo price a55, lasciando stock8."),
      ("mysql","Espandere JSON_TABLE","Array path $[*], colonna INT PATH '$' e alias x coerenti con la funzione8.4; righe attese1,2,3."),
      ("mysql","Creare un indice funzionale","Sintassi con doppie parentesi e LOWER su VARCHAR valida; EXPLAIN non promette che il planner scelga l'indice su quattro righe."),
      ("mysql","Definire una vista di soli ordini pagati","Predicato status='paid' e WITH CHECK OPTION coerenti; fixture ora rimuove anche la vista per rendere ripetibile CREATE VIEW."),
      ("mysql","Creare colonne generate persistenti","Espressione deterministica price*qty e inserimento nelle sole colonne base coerenti; totale15, reset ora rimuove lines."),
      ("mysql","Prelevare un lavoro con SKIP LOCKED","Ordine MySQL LIMIT prima di FOR UPDATE SKIP LOCKED rispettato; il lock viene rilasciato a COMMIT, senza presa in carico persistente implicita."),
      ("mysql","Mostrare DDL esatto di una tabella","Fixture corretta a FOREIGN KEY esplicite InnoDB; inline REFERENCES precedenti erano ignorate da MySQL8.4."),
      ("sqlite","Rendere atomico un trasferimento","Corretto il credito senza addebito con sorgente esaurito; test reali8/1/0 e destinazione assente conservano il totale."),
    ]
    by_id={r["id"]:r for r in records};sample=[]
    for stack,key,review in choices:
        rid=stack+"-"+slug(key);recipe=by_id[rid]
        sample.append({"id":rid,"title":recipe["title"],"project":recipe["project"],"method":"semantic-source-review" if stack in ("mysql","postgresql") else "semantic-review-and-sqlite-memory-execution","review":review,"files_sha256":recipe["_file_hashes"]})
    assert len(sample)==20 and sum(r["project"] for r in sample)==5
    return sample

def main():
    before=digest_other_stacks()
    cache_path=ROOT/"tools/web_verification.json"
    cache=json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    untouched={k:v for k,v in cache.items() if not any(k.startswith(stack+"-") for stack in STAGES)}
    import database_catalog
    database_catalog.build_all()
    records=load_records()
    report={"date":DATE,"docker_probe":docker_probe(),"counts":{stack:sum(r["stack"]==stack for r in records) for stack in STAGES},"database_projects":sum(r["project"] for r in records),"server_execution":{"postgresql":0,"mysql":0},"sqlite_version":sqlite3.sqlite_version,"sqlite_checks":[],"failures":[],"primary_sources":PRIMARY,"resources_created":[],"limits":["Docker daemon non disponibile al controllo: nessun avvio Docker Desktop, download immagini, container o collegamento a database esistenti.","PostgreSQL75/MySQL60: nessuna esecuzione su server attestata; revisione semantica stratificata di20schede complessive, inclusi5capstoneDB.","SQLite usa database nuovi in memoria: la prova WAL non attesta concorrenza su file.","Nessun contenuto o stato di verifica degli altri stack viene rigenerato."]}
    for recipe in records:
        try:
            if recipe["stack"] in ("sql","sqlite"):
                result=execute_sqlite(recipe);report["sqlite_checks"].append(result)
                record={"status":"eseguito","date":DATE,"details":f"Esecuzione SQLite {sqlite3.sqlite_version} in memoria su dati sintetici; {result['cycles']} ciclo/i completi. Vincoli e ripetibilità DDL verificati quando applicabili. Nessuna attestazione WAL concorrente su file. Report: reports/catalog-independent-review.json.","files_sha256":recipe["_file_hashes"]}
            else:
                if not recipe["project"] and recipe["stack"]=="mysql":
                    fixture=recipe["_files"]["fixture.sql"];query=recipe["_files"]["query.sql"]
                    assert fixture.upper().count("FOREIGN KEY")==3 and fixture.count("ENGINE=InnoDB")==4
                    for kind,name in re.findall(r"CREATE\s+(TABLE|VIEW)\s+([A-Za-z_]+)",query,re.I):
                        assert f"DROP {kind.upper()} IF EXISTS {name};" in fixture
                    if "RENAME TABLE" in query:
                        assert "DROP TABLE IF EXISTS rename_old;" in fixture and "DROP TABLE IF EXISTS rename_new;" in fixture
                record={"status":"documentato","date":DATE,"details":"Revisione documentale PostgreSQL18/MySQL8.4 e fixture di laboratorio; server non eseguito perché Docker non era attivo. Report: reports/catalog-independent-review.json.","files_sha256":recipe["_file_hashes"]}
            cache[recipe["id"]]=record
            stored=json.loads(recipe["_path"].read_text(encoding="utf-8"));stored["verification"]=record
            recipe["_path"].write_text(json.dumps(stored,ensure_ascii=False,indent=2),encoding="utf-8")
        except Exception as error:
            report["failures"].append({"id":recipe["id"],"error":str(error)})
    transfer=next(r for r in records if r["id"]=="sqlite-rendere-atomico-un-trasferimento")
    try:report["transfer_cases"]=transfer_cases(transfer)
    except Exception as error:report["failures"].append({"id":transfer["id"],"error":str(error)})
    report["semantic_sample"]=semantic_sample(records)
    report["command_review"]={"postgresql":"Client psql sul loopback, ON_ERROR_STOP e sequenza di file conservati.","mysql":"Client sul loopback e charset utf8mb4 espliciti. La sequenza di comandi source separati da punto e virgola è accettata dal parser client8.4; non è stata segnalata come bug.","mysql_primary_source":PRIMARY["mysql_client_source"],"sqlite":"Sequenza fixture/query verificata sul medesimo database in memoria; invocazione CLI documentata, non eseguita con sqlite3.exe."}
    if report["docker_probe"].get("info",{}).get("exit_code")==0:
        report["limits"][0]="Daemon Docker già attivo, ma questo helper esegue soltanto info/images: non avvia container e non collega database. La verifica server resta esclusa."
    report["findings_fixed"]=[
      {"problem":"MySQL8.4 ignorava REFERENCES inline nelle fixture.","fix":"FOREIGN KEY di tabella esplicite; ENGINE=InnoDB.","source":PRIMARY["mysql_fk"]},
      {"problem":"Guida PostgreSQL descriveva reset di sole quattro tabelle, ma lo schema atlas_demo veniva eliminato con CASCADE.","fix":"Descrizione e ambito completo del reset allineati al codice; database didattico esplicito.","source":PRIMARY["pg_drop"]},
      {"problem":"Fixture SQL/SQLite/MySQL non rimuovevano tutti gli oggetti extra delle query DDL.","fix":"Reset esplicito degli oggetti del laboratorio;113ricetteSQL/SQLite ripetute due volte, MySQL controllato strutturalmente senza server."},
      {"problem":"Trasferimento SQLite con sorgente0 creava una unità di stock.","fix":"Singolo UPDATE condizionato da CTE materializzata; origine/destinazione cambiano insieme o nessuna cambia, somma conservata.","source":PRIMARY["sqlite_materialized"]},
    ]
    report["other_stacks_unchanged"]=before==digest_other_stacks()
    assert report["other_stacks_unchanged"]
    assert untouched=={k:v for k,v in cache.items() if not any(k.startswith(stack+"-") for stack in STAGES)}
    cache_path.write_text(json.dumps(cache,ensure_ascii=False,indent=2),encoding="utf-8")
    report["summary"]={"recipes":len(records),"projects":5,"sqlite_recipes_executed":len(report["sqlite_checks"]),"sqlite_cycles":sum(r["cycles"] for r in report["sqlite_checks"]),"semantic_sample":20,"failures":len(report["failures"])}
    report["source_sha256"]={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ("tools/database_catalog.py","tools/qa_database_independent.py")}
    (ROOT/"reports/catalog-independent-review.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report["summary"],ensure_ascii=False))
    for failure in report["failures"]:print(json.dumps(failure,ensure_ascii=False))
    return not report["failures"]

if __name__=="__main__":sys.exit(not main())
