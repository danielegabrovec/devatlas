"""Reproduce only the eight new framework collections; never rebuild v1.1 IDs."""
from catalog_support import ROOT
import json

STACKS={'vue':35,'svelte':30,'angular':30,'spring':30,'flutter':30,'tauri':25,'mongodb':25,'redis':25}

QUERIES=[
('Vue pausa digitazione timer ricerca','vue-debounce'),
('Vue stato riusabile due contatori separati','vue-composable'),
('Vue input del figlio v-model defineModel','vue-component-model'),
('Vue dialogo sotto body Teleport','vue-teleport'),
('Vue test modello attività ID immutabili','vue-progetto-attivita'),
('Svelte5 derivare prezzo quantità','svelte-derived'),
('Svelte cancellare timeout effetto precedente','svelte-effect-cleanup'),
('Svelte restituire valore tramite bindable','svelte-bindable'),
('Svelte chiamare un blocco snippet parametrico','svelte-snippet'),
('Svelte checkbox attività completate','svelte-progetto-attivita'),
('Angular Observable vista unsubscribe automatico','angular-asyncpipe'),
('Angular service inject contatore condiviso','angular-service'),
('Angular input signal componente figlio','angular-input'),
('Angular reazione alle modifiche signal effect','angular-effect'),
('Angular attività test stesso modello ESM','angular-progetto-attivita'),
('Spring DTO titolo vuoto risposta400','spring-validation'),
('Spring eccezione dominio gestore comune','spring-advice'),
('Spring stock H2 transazione insufficiente','spring-jdbc-transaction'),
('Spring collegare debugger JVM porta locale','spring-debug'),
('Spring servizio attività lista snapshot test','spring-progetto-attivita'),
('Flutter modulo messaggio campo non valido','flutter-form'),
('Flutter seconda pagina restituisce risultato','flutter-navigation'),
('Flutter attesa Future senza riavviare richiesta','flutter-future'),
('Flutter runner Windows primo progetto doctor','flutter-setup'),
('Flutter attività modello immutabile test','flutter-progetto-attivita'),
('Tauri stato Mutex tra chiamate','tauri-state'),
('Tauri evento Rust listener rimosso','tauri-events'),
('Tauri errore con codice e messaggio','tauri-structured-error'),
('Tauri file directory dati applicazione','tauri-app-data'),
('Tauri note conservate dopo chiusura','tauri-progetto-note'),
('MongoDB arrayFilters solo depositoA','mongodb-array-filter'),
('MongoDB join collezioni lookup quantità','mongodb-lookup'),
('MongoDB facet pagina e conteggio insieme','mongodb-facet'),
('MongoDB indice scadenza documenti TTL','mongodb-ttl'),
('MongoDB prenotazione stock atomica Node','mongodb-progetto-magazzino'),
('Redis incremento prima scadenza Lua','redis-lua-rate'),
('Redis transazione unica connessione MULTI EXEC','redis-transaction'),
('Redis aggiornamento valore conserva TTL','redis-ttl-update'),
('Redis stream confermare messaggio pending','redis-consumer-group'),
('Redis stock insufficiente decremento atomico','redis-progetto-magazzino'),
]

def write_queries():
    data=[]
    for query,rid in QUERIES:
        stack=next(stack for stack in STACKS if rid.startswith(stack+'-'))
        assert (ROOT/'catalog'/stack/rid/'recipe.json').exists(),rid
        data.append({'query':query,'expected_ids':[rid]})
    assert len(data)==40
    (ROOT/'reports/search-cases-expansion-frameworks.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

def build_all():
    from expansion_web import build_all as web
    from expansion_spring import build_all as spring
    from expansion_flutter import build_all as flutter
    from expansion_tauri import build_all as tauri
    from expansion_nosql import build_all as nosql
    for build in (web,spring,flutter,tauri,nosql):build()
    for stack,count in STACKS.items():assert len(list((ROOT/'catalog'/stack).glob('*/recipe.json')))==count
    write_queries()
    print('230framework recipes;8capstones;40independent intent queries')

if __name__=='__main__':build_all()
