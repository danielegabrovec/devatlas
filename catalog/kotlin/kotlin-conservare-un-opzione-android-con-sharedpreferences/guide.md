## Risultato

Isola la persistenza di una preferenza in una classe completa per un target Android già configurato.

## Procedura

Inserisci Preferences.kt nel source set main di un progetto Android esistente, adattando package alla tua app. Da Activity usa Preferences(this).showDetails=true; per leggerlo crea la stessa classe con il medesimo context. La scheda non contiene un progetto Android completo né sostituisce AndroidManifest/Gradle del target.

## Risultato atteso e contratto

Il valore sopravvive alla ricreazione dell'Activity; apply salva in modo asincrono.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
