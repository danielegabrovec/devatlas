## Progetto
I file mantengono separati validazione, connessione, operazione atomica e CLI. La URL è accettata soltanto per il protocollo/loopback/porta del laboratorio. Il database o prefisso dei dati è dedicato a questo capstone. Non sono incluse credenziali.

## Prova
Esegui npm test prima di usare il server: copre input e risposte simulate. Su un server locale nuovo esegui seed e poi reserve keyboard2: la quantità8 deve diventare6. Ripetendo consuma altre unità, mentre quantità insufficiente produce errore e non va trattata come successo.

## Confine
MongoDB usa un singolo findOneAndUpdate condizionale; Redis esegue controllo e DECRBY nello stesso script Lua. Queste operazioni evitano il read-then-write nel client. Nessuna esecuzione del server viene attestata se il report dichiara l'ambiente assente.