## Avvio
Salva i sette file e avvia dal manifest package.json. Inserisci due note, chiudi e riapri. Il main conserva il file JSON nella cartella userData; la UI usa textContent e non esegue il contenuto delle note. La funzione IPC valida tipo, lunghezza e origine del frame.

## Errori
Un JSON non valido interrompe l'avvio e stampa un errore nel terminale senza sovrascriverlo. Una scrittura non riuscita viene mostrata nello stato; l'input resta disponibile per riprovare. Il pulsante evita salvataggi contemporanei.

## Verifica
Esempio documentato, non dichiarato eseguito su altri sistemi.