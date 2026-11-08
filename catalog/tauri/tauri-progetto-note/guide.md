## Dati e stato
Il comando demo accetta soltanto un titolo. Un Mutex serializza modifica e scrittura; il modello conserva la lista precedente finché la sostituzione del file temporaneo non riesce. All’avvio viene letto notes.json dal percorso dell’app e un errore non viene convertito in un archivio vuoto.

## Test e uso
Esegui cargo test per vuoto, lunghezza e ID/immutabilità. Aggiungi due note nella finestra, chiudi e riapri; aggiungendone una terza la risposta deve contenere anche le precedenti. Il frontend mostra JSON come testo e non interpreta titoli come HTML. La prova della persistenza richiede l’app reale e non èimplicita nei test del modello.