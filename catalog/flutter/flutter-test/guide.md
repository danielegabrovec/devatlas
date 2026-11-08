## Procedura
Il widget test costruisce AtlasApp in un ambiente di test e interagisce con il pulsante. Non avvia un emulatore e non attesta il rendering su Android o su uno schermo fisico.

## File e prerequisiti
Flutter SDK stable3.47 e Dart incluso. Windows richiede Visual Studio con Desktop development with C++, non soltanto VS Code. Android richiede Android SDK/JDK e dispositivo o emulatore. macOS/iOS richiedono un Mac con Xcode e non sono verificati qui.

I file lib/test originali sono sotto recipe; bootstrap li copia nel runner creato dall’SDK. Questo evita un runner nativo incompleto o dipendente dalla macchina dell’autore. I comandi vanno avviati dalla radice esportata.