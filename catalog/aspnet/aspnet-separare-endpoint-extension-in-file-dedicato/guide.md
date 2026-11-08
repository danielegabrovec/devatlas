## Obiettivo
Separare endpoint extension in file dedicato.

Demo.csproj definisce il progetto Web; Program.cs registra servizi prima di Build e middleware/rotte prima di Run. Richiama la rotta indicata dal metodo Map con curl o browser; usa JSON per i body dei record. I cookie Secure=false sono soltanto per il laboratorio HTTP locale.

## Procedura
Esporta tutti i file mantenendo i percorsi indicati. Il codice è completo; esegui i comandi dalla radice esportata. L'installazione iniziale delle dipendenze richiede rete o una cache già disponibile. I contenuti e l'esportazione dal catalogo funzionano offline.

## Controllo
Interagisci con il controllo o richiama la rotta indicata nel sorgente e osserva il risultato. Confronta gli input validi e invalidi prima di integrare il codice.

## Integrazione
Le risorse in memoria e i dati sintetici servono alla dimostrazione. Per usarli in un progetto esistente conserva il confine tra logica, stato e risorse esterne mostrato dall'esempio.