## Progetto
La libreria calc espone un header pubblico e implementa square. Il target calc_test verifica zero, positivo e negativo e restituisce un codice di uscita controllabile da CTest. L'installazione copia libreria e header sotto stage, senza modificare directory di sistema.

## Prova
Esegui i quattro comandi in ordine. CTest deve completare square_values; stage/include contiene calc.hpp. Nessuna build su piattaforme non presenti è attestata.