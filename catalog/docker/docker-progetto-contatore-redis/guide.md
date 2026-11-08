## Progetto
Un server HTTP Python usa il protocollo RESP minimo per INCR visits su Redis. La rete Compose risolve redis come hostname; Redis non pubblica porte sull'host. L'healthcheck evita di avviare il web prima della disponibilità iniziale di Redis. Il server gestisce un'indisponibilità successiva con HTTP 503.

## Prova
Visita due volte localhost:8089: il numero cresce. Esegui down e up dalla medesima cartella: il volume nominato mantiene il contatore. Non utilizzare down -v se vuoi conservare i dati. Questo esempio è locale e documentato, non distribuito online.