## Obiettivo

Realizza un dominio in memoria con record readonly, validazione, modifiche controllate, modulo di presentazione e test senza librerie esterne.

## Procedura

1. Esporta tutti i file in una nuova cartella dedicata. I sorgenti sono completi: non richiedono inserimenti in un progetto preesistente.
2. Installa le dipendenze dichiarate nel file di progetto; conserva la versione della toolchain indicata.
3. Apri PowerShell nella cartella esportata ed esegui i comandi della scheda.
4. Confronta il risultato con quello atteso e modifica gli input nel punto in cui vengono inizializzati.

## Comportamento e limiti

Test: 2 contratti verificati; il programma stampa una attività con done true.

Se il comando non viene trovato, verifica che la toolchain sia installata e presente nel PATH.

I dati sono sintetici. La verifica dichiarata riguarda soltanto le prove effettivamente registrate nella scheda; la presenza di un esempio completo non attesta esecuzioni su ogni sistema operativo.
