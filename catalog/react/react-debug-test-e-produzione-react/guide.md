## Obiettivo
Debug test e produzione react.

Per il debug avvia npm run dev in un terminale e premiF5 in VSCode con JavaScript Debugger. Metti il breakpoint nella funzione total. node --test verifica la logica; vite build crea dist con source map; vite preview serve il risultato su localhost4173. Preview è una verifica locale dell’artefatto, non un server pubblico da usare in produzione.

## Procedura
Esporta tutti i file mantenendo i percorsi indicati. Il codice è completo; esegui i comandi dalla radice esportata. L'installazione iniziale delle dipendenze richiede rete o una cache già disponibile. I contenuti e l'esportazione dal catalogo funzionano offline.

## Controllo
I test inclusi completano con esito positivo. La configurazione VSCode permette breakpoint sul sorgente; i comandi distinguono verifica, build e avvio di produzione.

## Integrazione
Le risorse in memoria e i dati sintetici servono alla dimostrazione. Per usarli in un progetto esistente conserva il confine tra logica, stato e risorse esterne mostrato dall'esempio.