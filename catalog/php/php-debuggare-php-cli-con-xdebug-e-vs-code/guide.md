## Risultato

Collega il processo CLI a un listener locale mantenendo il php.ini già configurato con Xdebug.

## Procedura

Installa Xdebug3 compatibile con versione/architettura di PHP e abilitalo nel php.ini effettivo, poi verifica --ri xdebug. Installa PHP Debug per VS Code, avvia Listen Xdebug e imposta un breakpoint prima della somma. Il comando -d conserva le altre estensioni di php.ini e abilita il debug soltanto per questa invocazione.

## Risultato atteso e contratto

Con il listener avviato il breakpoint permette di ispezionare values/total; output10.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
