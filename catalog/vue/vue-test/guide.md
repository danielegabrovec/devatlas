## Confine del test
src/model.mjs contiene operazioni pure di una lista attività. test/model.test.mjs controlla input vuoto, ID crescente, origine immutata e conteggio. node --test non richiede un DOM e non sostituisce una prova degli eventi del componente.

## Esecuzione
Esegui i test dalla radice; poi installa e compila per controllare anche gli import del framework. Un test fallito deve interrompere la consegna del modello.