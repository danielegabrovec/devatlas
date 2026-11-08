## Installare e scegliere il kit
Installa Visual Studio Build Tools con compilatore MSVC x64 e Windows SDK. Nel Qt Online Installer scegli Qt 6.12 desktop MSVC 2022 64-bit, CMake e Ninja. Apri Developer PowerShell x64 per rendere disponibili cl e il linker. Il parametro qt_dir deve indicare la directory del kit installato; il valore iniziale è soltanto un percorso comune.

## Configurare e avviare
Esporta main.cpp e CMakeLists.txt nella stessa cartella ed esegui i comandi dalla sua radice. La directory build/debug conserva cache e output separati dai sorgenti. windeployqt raccoglie accanto all'eseguibile le librerie Qt e il plugin della piattaforma per questo avvio Debug.

## Controllo e diagnosi
Verifica il compilatore scelto nel log iniziale di CMake e il riferimento Qt6_DIR in build/debug/CMakeCache.txt. La finestra deve mostrare un contatore funzionante. Se cambi compilatore o architettura, usa una directory di build nuova invece di riutilizzare la vecchia cache. La ricetta riguarda Windows/MSVC; non dichiara test MinGW o Linux.