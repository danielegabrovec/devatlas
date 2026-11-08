## Procedura
Distribuisci tutta la directory Release prodotta sotto build/windows, incluse DLL e data. Verifica su un Windows compatibile. La ricetta non crea firma o installer; Android richiede flutter build apk e la propria configurazione di firma, iOS richiede macOS/Xcode.

## File e prerequisiti
Flutter SDK stable3.47 e Dart incluso. Windows richiede Visual Studio con Desktop development with C++, non soltanto VS Code. Android richiede Android SDK/JDK e dispositivo o emulatore. macOS/iOS richiedono un Mac con Xcode e non sono verificati qui.

I file lib/test originali sono sotto recipe; bootstrap li copia nel runner creato dall’SDK. Questo evita un runner nativo incompleto o dipendente dalla macchina dell’autore. I comandi vanno avviati dalla radice esportata.