## Procedura
La configurazione targets nsis usa l’icona generata e include le risorse. Il bundler può dover ottenere i tool NSIS e il bootstrapper WebView2; la guida non attesta quel download né la firma. Prima di consegnare, installa in un Windows di prova e verifica dipendenze e disinstallazione.

## Prerequisiti
Windows x64 con RustMSVC1.90+, Visual Studio Desktop development with C++, Windows SDK e WebView2 Runtime. Node24 e npm per la CLI locale. Questi esempi producono Windows; non attestano build Linux/macOS/mobile.

## File
Apri la radice con package.json. La cartella src-tauri contiene il crate; le permission riguardano soltanto la finestra main. L’icona viene generata da codice originale nel build script, quindi non manca un asset binario nascosto.