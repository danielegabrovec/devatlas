## Risultato

Individua php.ini e abilita diagnostica locale senza stampare errori al pubblico.

## Procedura

Installa PHP8.4/8.5 CLI e aggiungi il binario al PATH. Il file development.ini configura soltanto il laboratorio; non è una configurazione FPM/produzione né include le estensioni del tuo php.ini standard. Se servono estensioni mantieni l'opportuno extension_dir e le relative righe di caricamento.

## Risultato atteso e contratto

Versione PHP e messaggio pronto; il file di configurazione effettivo è visibile con --ini.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
