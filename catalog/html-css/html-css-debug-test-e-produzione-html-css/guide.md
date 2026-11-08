## Obiettivo
Debug test e produzione html-css.

Avvia il server HTTP del primo esempio, poi F5 in VSCode con JavaScript Debugger oppure F12 nel browser; metti un breakpoint in lib.js e ricarica. node --test controlla la funzione senza DOM. Non esiste compilazione obbligatoria per questi file statici: lo ZIP include esattamente le risorse pubblicabili, escludendo test e configurazione debugger. Il server Python è soltanto di sviluppo.

## Procedura
Esporta tutti i file mantenendo i percorsi indicati. Il codice è completo; esegui i comandi dalla radice esportata. L'installazione iniziale delle dipendenze richiede rete o una cache già disponibile. I contenuti e l'esportazione dal catalogo funzionano offline.

## Controllo
I test inclusi completano con esito positivo. La configurazione VSCode permette breakpoint sul sorgente; i comandi distinguono verifica, build e avvio di produzione.

## Integrazione
Le risorse in memoria e i dati sintetici servono alla dimostrazione. Per usarli in un progetto esistente conserva il confine tra logica, stato e risorse esterne mostrato dall'esempio.