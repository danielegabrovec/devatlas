## SDK e dipendenze
Installa .NET 8 SDK x64. I file forniti inizializzano Avalonia 11.3.0 con FluentTheme e lifetime desktop; non richiedono template aggiuntivi. NuGet ripristina Avalonia.Desktop e Avalonia.Themes.Fluent dalla versione dichiarata nel progetto. Questa è una baseline 11.3 esplicita, non una promessa di usare l'ultima versione disponibile.

## File da mantenere
Esporta tutti i file conservando le directory. Il nome del .csproj diventa {project_name}.csproj, mentre il namespace interno RecipeApp resta coerente fra i sorgenti e gli eventuali file XAML. Avvia i comandi nella cartella che contiene quel progetto.

## Primo avvio
Il costruttore della finestra o pagina costruisce due controlli e collega il clic a una variabile di sessione. Premi tre volte Incrementa: deve apparire 3. Il restore iniziale richiede Internet; l'app minima non usa servizi esterni.

## Compatibilità
La procedura è specifica Windows x64 e per le versioni dichiarate. Non attesta una build o un'esecuzione su altri sistemi e non richiede emulatori mobili.