## Procedura
La build usa tauri build --no-bundle per controllare frontend e backend senza creare un installer. Il binario Release ènel target Cargo. Non presumere che lo stesso binario funzioni su altre architetture.

## Prerequisiti
Windows x64 con RustMSVC1.90+, Visual Studio Desktop development with C++, Windows SDK e WebView2 Runtime. Node24 e npm per la CLI locale. Questi esempi producono Windows; non attestano build Linux/macOS/mobile.

## File
Apri la radice con package.json. La cartella src-tauri contiene il crate; le permission riguardano soltanto la finestra main. L’icona viene generata da codice originale nel build script, quindi non manca un asset binario nascosto.