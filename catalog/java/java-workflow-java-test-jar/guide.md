## Risultato

Esegue contratti senza JUnit e crea un JAR con Main-Class evitando di includere il runner dei test.

## Prerequisiti e procedura

1. Compila sorgenti e runner in out.
2. Esegui il test prima di creare il pacchetto.
3. jar include soltanto Main.class e il package math; non include CalculatorTest.class.
4. Il destinatario deve avere un runtime Java17+; il JAR non incorpora automaticamente una JVM.

## Verifica

test passato e poi5; java -jar trova il punto d'ingresso tramite il manifest generato.

## Problemi frequenti

no main manifest attribute richiede --main-class; ClassNotFoundException richiede includere il package math o correggere classpath/package.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
