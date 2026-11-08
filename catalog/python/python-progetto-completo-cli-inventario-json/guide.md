## Obiettivo

Realizza una CLI con persistenza JSON, validazione e test separati; i file vengono scritti soltanto nel percorso passato dall'utente.

## Procedura

1. Esporta tutti i file in una nuova cartella dedicata. I sorgenti sono completi: non richiedono inserimenti in un progetto preesistente.
2. Predisponi la toolchain indicata nei prerequisiti; questo esempio usa la libreria standard.
3. Apri PowerShell nella cartella esportata ed esegui i comandi della scheda.
4. Confronta il risultato con quello atteso e modifica gli input nel punto in cui vengono inizializzati.

## Comportamento e limiti

Due test passano. Alla prima esecuzione la CLI stampa viti: 3; i dati rimangono nel JSON per l'avvio successivo.

Se il comando non viene trovato, verifica che la toolchain sia installata e presente nel PATH.

I dati sono sintetici. La verifica dichiarata riguarda soltanto le prove effettivamente registrate nella scheda; la presenza di un esempio completo non attesta esecuzioni su ogni sistema operativo.
