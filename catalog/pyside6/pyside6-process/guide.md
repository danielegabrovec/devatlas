## Obiettivo
Usare QProcess in modo asincrono per interrogare la versione di Python.

## Uso
Salva main.py in una cartella nuova. Esegui i comandi da quella cartella. Il codice della ricetta si trova nella funzione `build`: i controlli appartengono alla finestra, i callback sono collegati prima di avviare il ciclo eventi.

## Comportamento
Compare la versione dell'interprete senza bloccare la finestra.

## Limiti
Esempio desktop originale; esecuzione su macOS e Linux non attestata. I file temporanei, quando previsti, sono creati esclusivamente per questa dimostrazione.