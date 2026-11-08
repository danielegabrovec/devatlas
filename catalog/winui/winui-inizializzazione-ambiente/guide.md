## SDK e dipendenze
Predisponi Windows 10 build 19041 o successivo, .NET 8 SDK, Windows SDK e workload WinUI in Visual Studio. Il progetto usa una baseline dichiarata Windows App SDK 1.8.12 (pacchetto 1.8.260921001), destinazione win-x64 e WindowsPackageType=None. App.xaml crea le risorse WinUI; App.xaml.cs conserva la finestra e la attiva in OnLaunched. Non confondere questa app desktop con UWP o con un progetto WPF.

## File da mantenere
Esporta tutti i file conservando le directory. Il nome del .csproj diventa {project_name}.csproj, mentre il namespace interno RecipeApp resta coerente fra i sorgenti e gli eventuali file XAML. Avvia i comandi nella cartella che contiene quel progetto.

## Primo avvio
Il costruttore della finestra o pagina costruisce due controlli e collega il clic a una variabile di sessione. Premi tre volte Incrementa: deve apparire 3. Il restore iniziale richiede Internet; l'app minima non usa servizi esterni.

## Compatibilità
La procedura è specifica Windows x64 e per le versioni dichiarate. Non attesta una build o un'esecuzione su altri sistemi e non richiede emulatori mobili.