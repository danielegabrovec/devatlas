## Procedura
Apri la cartella app in VS Code con estensione Flutter. F5 usa il dispositivo scelto; metti un breakpoint nell’handler Incrementa. Hot reload conserva lo State, mentre hot restart riparte da zero. Non cambiare la struttura dei runner durante una sessione attiva.

## File e prerequisiti
Flutter SDK stable3.47 e Dart incluso. Windows richiede Visual Studio con Desktop development with C++, non soltanto VS Code. Android richiede Android SDK/JDK e dispositivo o emulatore. macOS/iOS richiedono un Mac con Xcode e non sono verificati qui.

I file lib/test originali sono sotto recipe; bootstrap li copia nel runner creato dall’SDK. Questo evita un runner nativo incompleto o dipendente dalla macchina dell’autore. I comandi vanno avviati dalla radice esportata.