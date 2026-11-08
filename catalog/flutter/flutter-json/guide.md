## Comportamento
Validare forma e tipo prima di usare i dati nell'interfaccia.

## Avvio
Esporta tutti i file. bootstrap.ps1 crea app e copia recipe/lib e recipe/test nel progetto nativo. Il codice specifico ènello State in lib/main.dart. Per cambiare piattaforma servono i relativi toolchain; non basta modificare il nome del dispositivo.

## Controllo
La pagina mostra Ada ·35; dati incompatibili producono FormatException.

## Ciclo di vita
Il Builder sotto MaterialApp fornisce il contesto corretto a Navigator, dialoghi e ScaffoldMessenger. I controller posseduti dallo State vengono rilasciati esplicitamente dove presenti.