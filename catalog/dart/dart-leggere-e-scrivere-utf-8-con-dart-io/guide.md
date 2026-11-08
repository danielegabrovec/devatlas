## Risultato

Usa una directory temporanea dedicata e la rimuove dopo il round-trip.

## Procedura

Esporta tutti i file nella stessa cartella conservando i percorsi. Apri un terminale nella radice esportata ed esegui i comandi della scheda. Il sorgente contiene dati sintetici e un punto di ingresso completo.

## Risultato atteso e contratto

Città; questo sorgente richiede un runtime Dart nativo, non il browser.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
