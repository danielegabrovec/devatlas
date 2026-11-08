## Comportamento
Usare ExpansionTile per una sezione espandibile accessibile.

## Avvio
Esporta tutti i file. bootstrap.ps1 crea app e copia recipe/lib e recipe/test nel progetto nativo. Il codice specifico ènello State in lib/main.dart. Per cambiare piattaforma servono i relativi toolchain; non basta modificare il nome del dispositivo.

## Controllo
La sezione si apre e richiude.

## Ciclo di vita
Il Builder sotto MaterialApp fornisce il contesto corretto a Navigator, dialoghi e ScaffoldMessenger. I controller posseduti dallo State vengono rilasciati esplicitamente dove presenti.