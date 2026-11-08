## SDK e dipendenze
Predisponi Windows 10 build 19041 o successivo, .NET 10 SDK e Windows SDK tramite Visual Studio 2026 con workload .NET MAUI. Il comando workload install riguarda il medesimo SDK selezionato dal terminale; se l'installazione è gestita da Visual Studio, mantienila coerente con Visual Studio Installer. L'esempio contiene soltanto il target Windows, i file Platforms/Windows e Microsoft.Maui.Controls 10.0.31: Android, iOS e MacCatalyst non vengono costruiti.

## File da mantenere
Esporta tutti i file conservando le directory. Il nome del .csproj diventa {project_name}.csproj, mentre il namespace interno RecipeApp resta coerente fra i sorgenti e gli eventuali file XAML. Avvia i comandi nella cartella che contiene quel progetto.

## Primo avvio
Il costruttore della finestra o pagina costruisce due controlli e collega il clic a una variabile di sessione. Premi tre volte Incrementa: deve apparire 3. Il restore iniziale richiede Internet; l'app minima non usa servizi esterni.

## Compatibilità
La procedura è specifica Windows x64 e per le versioni dichiarate. Non attesta una build o un'esecuzione su altri sistemi e non richiede emulatori mobili.