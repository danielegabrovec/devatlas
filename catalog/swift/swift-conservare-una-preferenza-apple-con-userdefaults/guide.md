## Risultato

Usa un dominio dimostrativo separato e ripristina il valore tramite la medesima chiave.

## Procedura

Su macOS esegui lo script. In un'app iOS riusa le operazioni set/bool nel modello del target; non incollare istruzioni top-level in un file qualsiasi della app. Il dominio scelto è dedicato al laboratorio e viene eliminato: non sostituirlo con il dominio di un'app reale.

## Risultato atteso e contratto

true; il dominio dimostrativo viene rimosso alla fine.

## Diagnostica

Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.

La consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.
