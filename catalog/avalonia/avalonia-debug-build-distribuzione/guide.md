## Debug della funzione richiamata dalla UI
La ricetta include l'intero progetto: il pulsante Calcola richiama Invoice.Total in Invoice.cs. Prima predisponi SDK e workload indicati dalla guida di inizializzazione. In VS Code installa l'estensione C#, apri la cartella e seleziona Debug avalonia C#. La task Build Debug usa il framework e il RID esatti del progetto. Metti un breakpoint sulla riga `decimal subtotal=prices.Sum();`, premi F5 e poi Calcola; controlla prices e subtotal nel debugger. Per gli strumenti XAML e il debug misto nativo/gestito puoi aprire lo stesso .csproj in Visual Studio e usare F5.

## Publish specifico del framework
Il runtime di rendering Avalonia e le sue librerie native arrivano dai pacchetti desktop. Conserva tutta la directory di publish: estrarre soltanto la DLL gestita non produce una distribuzione autonoma.

Esegui il comando di pubblicazione dalla radice dei sorgenti. La destinazione è una directory distinta dalla build Debug. Non viene creata né registrata una app MSIX e non vengono usati certificati di firma.

## Controllo da completare
Avvia il risultato su Windows x64 e prova il totale 19.75. La presenza di una configurazione debugger e di un comando publish non equivale a una compilazione riuscita: questa guida dichiara soltanto le verifiche statiche riportate nel catalogo.