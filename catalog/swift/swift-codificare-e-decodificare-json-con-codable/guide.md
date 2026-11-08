## Risultato

Deriva un contratto dati tipizzato e verifica la presenza dei campi durante la decodifica.

## Procedura

Esporta tutti i file nella stessa cartella conservando i percorsi. Apri un terminale nella radice esportata ed esegui i comandi della scheda. Il sorgente contiene dati sintetici e un punto di ingresso completo.

## Risultato atteso e contratto

libro1250; il decoder segnala tipi/campi mancanti anziché presumere la validità.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
