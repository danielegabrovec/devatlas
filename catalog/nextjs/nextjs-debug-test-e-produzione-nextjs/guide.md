## Obiettivo
Debug test e produzione nextjs.

Apri la cartella in VSCode e avvia Next server dev conF5; richiamando la home puoi fermarti in lib/pricing.mjs. Per componenti client usa anche i breakpoint di DevTools del browser. node --test controlla la funzione, next build compila/prerenderizza, next start esegue il risultato di produzione localmente. Non utilizzare next dev per distribuire il servizio.

## Procedura
Esporta tutti i file mantenendo i percorsi indicati. Il codice è completo; esegui i comandi dalla radice esportata. L'installazione iniziale delle dipendenze richiede rete o una cache già disponibile. I contenuti e l'esportazione dal catalogo funzionano offline.

## Controllo
I test inclusi completano con esito positivo. La configurazione VSCode permette breakpoint sul sorgente; i comandi distinguono verifica, build e avvio di produzione.

## Integrazione
Le risorse in memoria e i dati sintetici servono alla dimostrazione. Per usarli in un progetto esistente conserva il confine tra logica, stato e risorse esterne mostrato dall'esempio.