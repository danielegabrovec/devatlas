## Risultato

Mantiene simboli di debug e fornisce una configurazione Java con arresto all'ingresso.

## Prerequisiti e procedura

1. Il JDK include jdb; per VS Code installa Extension Pack for Java/Debugger for Java.
2. -g include informazioni di debug.
3. In jdb usa `stop in Main.total`, `run`, `next`, `locals`, `cont`, `exit`.
4. In VS Code apri il progetto e premi F5 con un breakpoint nella funzione.

## Verifica

Il debugger mostra stack e variabili locali; completando il programma si ottiene10.

## Problemi frequenti

Se locals non mostra i nomi ricompila con -g. jdb rimane interattivo e il classpath deve puntare alla directory contenente Main.class.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
