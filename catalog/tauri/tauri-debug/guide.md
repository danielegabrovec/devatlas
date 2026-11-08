## Procedura
In VS Code installa rust-analyzer e un debugger Rust compatibile MSVC. In development gli strumenti WebView e i breakpoint Rust controllano lati differenti del ponte. La configurazione LLDB allegata avvia il binario Debug dopo una prima compilazione; una versione del debugger che non supporta MSVC va sostituita con gli strumenti Visual Studio.

## Prerequisiti
Windows x64 con RustMSVC1.90+, Visual Studio Desktop development with C++, Windows SDK e WebView2 Runtime. Node24 e npm per la CLI locale. Questi esempi producono Windows; non attestano build Linux/macOS/mobile.

## File
Apri la radice con package.json. La cartella src-tauri contiene il crate; le permission riguardano soltanto la finestra main. L’icona viene generata da codice originale nel build script, quindi non manca un asset binario nascosto.