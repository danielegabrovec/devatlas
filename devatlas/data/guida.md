# Benvenuto in DevAtlas

DevAtlas è una biblioteca operativa offline. Le schede spiegano come ottenere un risultato concreto e forniscono sorgenti e comandi da copiare.

## Trova quello che ti serve

Scrivi un obiettivo nella ricerca, ad esempio **python leggere json**, **c++ compilare**, **react form** o un messaggio di errore. Sono riconosciuti nomi italiani e inglesi e alias come C++/cpp, C#/csharp e Node.js/nodejs. I suggerimenti per i refusi sono visibili e vengono applicati solo quando li scegli.

La navigazione distingue linguaggi, framework, database e strumenti. I filtri combinano sezione, difficoltà, sistema operativo, shell, IDE e verifica. I risultati sono caricati a gruppi: usa **Carica altri risultati** per continuare.

I filtri attivi compaiono sopra i risultati e si rimuovono singolarmente. L'ordinamento permette di scegliere pertinenza, titolo, difficoltà o schede consultate di recente. La modalità lettura lascia più spazio alla scheda e può essere disattivata per tornare alla biblioteca.

**Ctrl+P** apre la palette: cerca un'azione o una tecnologia, usa le frecce per selezionare e Invio per aprire; Esc annulla. Le azioni non disponibili non vengono eseguite.

**Dove cercare** permette di cercare ovunque, soltanto nel codice e nei comandi, oppure soltanto nei titoli. È utile per trovare un nome API esatto senza includere le spiegazioni che lo citano.

## Ricerche salvate

**Salva ricerca corrente** conserva un nome, il testo e i filtri attivi. Le ricerche compaiono in **Ricerche salvate** e possono essere riaperte, aggiornate, rinominate o eliminate. Preferiti, schede personali e raccolte vengono ricalcolati quando riapri la ricerca; se un riferimento non esiste più viene mostrato un avviso. Il backup conserva le ricerche e rimappa le raccolte durante il ripristino.

## Leggi e copia

La **Vista rapida** mostra prerequisiti, codice, comandi e risultato atteso. La **Vista guidata** aggiunge passaggi, errori frequenti, fonti e stato delle verifiche.

Il pulsante **Copia** restituisce il solo sorgente: non include numeri di riga, etichette o prompt. I blocchi *frammento* richiedono inserimento nel punto indicato dalla guida; i *file completi* possono essere esportati direttamente.

Con il focus nel codice, **Ctrl+F** apre la ricerca locale; **F3** e **Shift+F3** passano all'occorrenza successiva o precedente. Puoi attivare il ritorno a capo, ampliare un blocco e copiare la selezione senza modificare il sorgente.

**F8** attiva o disattiva il focus lettura e ripristina i pannelli precedenti. Dal menu **Visualizza → Densità della biblioteca** scegli una disposizione comoda o compatta; tema, zoom e densità restano nel profilo.

Un progetto completo contiene i file necessari all'esempio. Occorre comunque predisporre compilatori, SDK e dipendenze indicati. Il primo download delle dipendenze può richiedere Internet; l'applicazione e il catalogo non ne hanno bisogno.

## Personalizza ed esporta

Se una ricetta prevede parametri, modificali prima della copia o dell'esportazione. L'anteprima viene aggiornata e segnala i valori non validi. **Esporta progetto** prepara una cartella o un archivio ZIP con codice e README italiano.

L'esportazione non sostituisce file esistenti: scegli una nuova destinazione. L'app non esegue automaticamente i comandi del catalogo.

## Confronta due sorgenti

Da **Azioni → Confronta codice con un’altra scheda** seleziona due ricette e i relativi file o blocchi di comandi. Il confronto affiancato evidenzia righe aggiunte, rimosse o cambiate. I due lati possono avere parametri diversi; la copia restituisce il sorgente renderizzato del lato scelto.

Il confronto è in sola lettura e non esegue codice. Per file troppo grandi o confronti particolarmente costosi l'app segnala il limite, così puoi scegliere blocchi più piccoli.

## Le tue schede

Con **Nuova scheda** crei una ricetta personale; con **Azioni → Modifica / crea copia personale** duplichi una scheda inclusa. Il catalogo originale resta separato. Nell'editor puoi modificare obiettivo, guida Markdown, file, comandi, parametri e tag.

L'editor riconosce il linguaggio dall'estensione di un nuovo file e offre modelli iniziali da inserire esplicitamente nei file vuoti. Gli errori di validazione sono segnalati accanto al campo da correggere. **Ctrl+S** salva la scheda; la ricerca locale nel codice non modifica i contenuti.

Usa **Preferiti**, **Note personali** e le raccolte per organizzare il materiale. Le annotazioni sono locali e non vengono trasmesse a servizi esterni.

Per rinominare o eliminare una raccolta, selezionala e usa il menu File o il menu contestuale della navigazione. Eliminare la raccolta rimuove soltanto il contenitore: schede, preferiti e note restano conservati.

I **Percorsi guidati** mostrano ora la sequenza dei passi: usa **Passo →**, **← Passo** e **Segna completato**. La prossima apertura riprende dal primo passo non completato; l'avanzamento resta nel tuo profilo e nei backup.

## Scambia e conserva

- **Esporta scheda modificabile** e **Esporta raccolta corrente** producono pacchetti `.devatlas.zip`.
- **Crea backup personale** conserva schede personali, note, preferiti, raccolte e impostazioni.
- **Importa schede o backup** mostra un riepilogo prima di salvare. I conflitti generano copie personali; le annotazioni esistenti sono conservate.
- **Aggiorna catalogo da pacchetto locale** aggiorna i contenuti inclusi senza toccare il database personale.
- **Ricostruisci indice** rigenera soltanto il motore di ricerca.

I dati vengono conservati in `%LOCALAPPDATA%\DevAtlas`; puoi scegliere una cartella con l'opzione `--data-dir`. Nel pacchetto portabile la presenza di `portable.flag` conserva i dati accanto all'eseguibile. Se la cartella non è scrivibile, sposta il pacchetto in una cartella del tuo utente.

La preparazione dell'indice avviene in background: durante il lavoro puoi leggere e modificare le ricette; la ricerca riprende quando l'indice è pronto. Un secondo avvio sullo stesso profilo riporta in primo piano la finestra già aperta.

Se un aggiornamento locale del catalogo non è leggibile, l'app mostra un avviso e apre i contenuti inclusi, conservando il file originale e i dati personali. Le impostazioni non valide vengono ignorate in lettura; il backup può conservarne il testo originale per il recupero.

## Significato delle verifiche

- **Revisionato**: codice e procedura controllati editorialmente; esecuzione non attestata.
- **Controllo statico**: controllo di sintassi o analisi indicata nel dettaglio.
- **Compilato**: compilazione eseguita nell'ambiente dichiarato.
- **Eseguito**: esecuzione verificata nell'ambiente dichiarato.

Una verifica su Windows non attesta macOS, Linux o Android. Le versioni e i limiti sono riportati nelle ricette e nei rapporti allegati.

## Scorciatoie

| Comando | Scorciatoia |
|---|---|
| Cerca nel catalogo | Ctrl+K |
| Palette comandi e navigazione | Ctrl+P |
| Cerca nel codice della ricetta | Ctrl+F |
| Occorrenza successiva / precedente | F3 / Shift+F3 |
| Attiva / disattiva focus lettura | F8 |
| Nuova scheda | Ctrl+N |
| Salva nell'editor personale | Ctrl+S |
| Importa pacchetto | Ctrl+I |
| Zoom | Ctrl+più / Ctrl+meno |
| Dimensione originale | Ctrl+0 |
| Mostra/nascondi risultati | Ctrl+Shift+L |
| Guida | F1 |

I collegamenti alle fonti si aprono nel browser solo quando li selezioni. Font, icone e contenuti dell'app sono locali.

