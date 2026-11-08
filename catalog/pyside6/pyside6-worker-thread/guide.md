## Obiettivo
Inviare il risultato tramite segnale e liberare worker e thread alla fine.

## Uso
Salva main.py in una cartella nuova. Esegui i comandi da quella cartella. Il codice della ricetta si trova nella funzione `build`: i controlli appartengono alla finestra, i callback sono collegati prima di avviare il ciclo eventi.

## Comportamento
Il risultato arriva con un segnale; nessun widget viene modificato dal worker.

## Limiti
Esempio desktop originale; esecuzione su macOS e Linux non attestata. I file temporanei, quando previsti, sono creati esclusivamente per questa dimostrazione.