## Risultato

Valida il parametro page e restituisce status/content-type coerenti senza framework.

## Procedura

Avvia il server incorporato nella cartella esportata e visita http://127.0.0.1:8084/?page=2. Il processo rimane attivo fino a Ctrl+C. Il server PHP incorporato serve il laboratorio e non sostituisce una configurazione di produzione con webserver/FPM.

## Risultato atteso e contratto

GET /?page=2 restituisce page2; page=abc restituisce400.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
