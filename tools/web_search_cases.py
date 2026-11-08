"""Query editoriali per misurare il recupero, indipendenti dal ranking."""
import json
from pathlib import Path
from catalog_support import ROOT,slug

CASES=[
('nodejs','Leggere un file per righe','node leggere un log riga per riga'),
('nodejs','Eseguire processo senza shell','node execFile avviare programma con argomenti'),
('nodejs','Limitare concorrenza con coda worker','node promise massimo due lavori contemporanei'),
('react','Leggere un form con FormData','react ottenere campi del modulo al submit'),
('react','Applicare debounce a un campo ricerca','react aspettare digitazione prima di cercare'),
('react','Liberare object URL delle anteprime','react revokeObjectURL pulire preview file'),
('nextjs','Leggere cookie con API asincrona','next leggere preferenza salvata nei cookies'),
('nextjs','Leggere params asincroni nel route handler','next api endpoint parametro id await params'),
('nextjs','Rivalidare un tag con profilo max','next revalidateTag aggiornare cache catalogo'),
('aspnet','Applicare rate limiting a una rotta','aspnet limitare richieste al minuto'),
('aspnet','Restituire Problem Details','aspnet errore http application problem json'),
('aspnet','Rispettare cancellazione della richiesta','aspnet CancellationToken client interrompe richiesta'),
('fastapi','Validare modelli annidati','fastapi body persona con indirizzo nested model'),
('fastapi','Rilasciare risorse con dipendenza yield','fastapi cleanup dependency yield finally'),
('fastapi','Limitare dimensione upload leggendo chunk','fastapi rifiutare file oltre un megabyte'),
('html-css','Creare una griglia responsive automatica','css schede su colonne adattive auto fit minmax'),
('html-css','Offrire un link salta contenuto','html accessibilità saltare navigazione tastiera'),
('html-css','Disattivare animazioni per movimento ridotto','css prefers reduced motion evitare movimento'),
('django','Aggiornare valori atomicamente con F','django ORM incremento contatore senza race condition'),
('django','Inviare ModelForm con protezione CSRF','django creare record form post csrf token'),
('django','Aggiungere un comando management personalizzato','django manage py comando conteggio personalizzato'),
('sql','Trovare clienti privi di ordini','sql clienti senza acquisti not exists'),
('sql','Sostituire NULL in visualizzazione','sql mostrare testo quando campo mancante coalesce'),
('sql','Calcolare un totale progressivo','sql somma cumulativa per ordine window'),
('sqlite','Limitare attesa su database occupato','sqlite database is locked busy timeout'),
('sqlite','Cercare sottostringhe con trigram','sqlite fts5 ricerca frammenti parola trigram'),
('sqlite','Verificare violazioni delle foreign key','sqlite controllare riferimenti orfani foreign key check'),
('postgresql','Fare UPSERT con EXCLUDED','postgres inserire o aggiornare on conflict'),
('postgresql','Prelevare lavoro con SKIP LOCKED','postgres coda worker evitare righe bloccate'),
('postgresql',"Estrarre l'ultimo ordine con DISTINCT ON",'postgres una riga più recente per cliente'),
('mysql','Espandere JSON_TABLE','mysql array json trasformare elementi in righe'),
('mysql','Confrontare NULL in modo sicuro','mysql null safe equality confronto valori mancanti'),
('mysql','Rinominare atomicamente due tabelle MySQL','mysql rename table scambiare nomi atomicamente'),
]

def main():
    cases=[]
    for stack,title,query in CASES:
        rid=stack+'-'+slug(title)
        assert (ROOT/'catalog'/stack/rid/'recipe.json').exists(),rid
        cases.append({'query':query,'expected_ids':[rid]})
    assert len(cases)==33
    (ROOT/'reports/search-cases-web-db.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2),encoding='utf8')
    print('33query curate salvate senza eseguire o tarare il ranking.')

if __name__=='__main__':main()
