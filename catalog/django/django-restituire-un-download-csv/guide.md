## Obiettivo
Restituire un download CSV.

Il progetto completo usa l’app notes e SQLite locale. Le modifiche specifiche sono nei file notes/views.py. I template mantengono autoescape e i form POST includono CSRF. Per admin/login crea un utente con createsuperuser; non sono presenti password predefinite.

## Procedura
Esporta tutti i file mantenendo i percorsi indicati. Il codice è completo; esegui i comandi dalla radice esportata. L'installazione iniziale delle dipendenze richiede rete o una cache già disponibile. I contenuti e l'esportazione dal catalogo funzionano offline.

## Controllo
Interagisci con il controllo o richiama la rotta indicata nel sorgente e osserva il risultato. Confronta gli input validi e invalidi prima di integrare il codice.

## Integrazione
Le risorse in memoria e i dati sintetici servono alla dimostrazione. Per usarli in un progetto esistente conserva il confine tra logica, stato e risorse esterne mostrato dall'esempio.