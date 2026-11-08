## Obiettivo
Installare un QObject event filter che consuma soltanto il tasto richiesto.

## Uso
Salva main.py in una cartella nuova. Esegui i comandi da quella cartella. Il codice della ricetta si trova nella funzione `build`: i controlli appartengono alla finestra, i callback sono collegati prima di avviare il ciclo eventi.

## Comportamento
Escape svuota il campo; gli altri tasti funzionano normalmente.

## Limiti
Esempio desktop originale; esecuzione su macOS e Linux non attestata. I file temporanei, quando previsti, sono creati esclusivamente per questa dimostrazione.