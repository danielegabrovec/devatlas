## Risultato

Confronta un token di sessione con hash_equals prima di accettare una richiesta POST.

## Procedura

Usa il server locale e conserva il cookie di sessione nel browser. In produzione il cookie richiede Secure con HTTPS e la configurazione di sessione del deploy. Il token non sostituisce autenticazione o autorizzazione; protegge il caso illustrato di form autenticabile a sessione.

## Risultato atteso e contratto

Il form valido è accettato; token mancante/alterato restituisce403.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
