## Obiettivo

Configura il programma senza inserire segreti o percorsi nel sorgente.

## Procedura

1. Esporta tutti i file in una nuova cartella dedicata. I sorgenti sono completi: non richiedono inserimenti in un progetto preesistente.
2. Predisponi la toolchain indicata nei prerequisiti; questo esempio usa la libreria standard.
3. Apri PowerShell nella cartella esportata ed esegui i comandi della scheda.
4. Confronta il risultato con quello atteso e modifica gli input nel punto in cui vengono inizializzati.

## Comportamento e limiti

8080 se APP_PORT non è impostata; valore invalido produce un errore chiaro.

Se il comando non viene trovato, verifica che la toolchain sia installata e presente nel PATH.

I dati sono sintetici. La verifica dichiarata riguarda soltanto le prove effettivamente registrate nella scheda; la presenza di un esempio completo non attesta esecuzioni su ogni sistema operativo.
