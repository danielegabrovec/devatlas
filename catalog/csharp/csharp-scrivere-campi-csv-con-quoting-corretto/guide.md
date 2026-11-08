## Obiettivo

Raddoppia le virgolette e racchiude i campi che contengono separatori o newline.

## Procedura

1. Esporta tutti i file in una nuova cartella dedicata. I sorgenti sono completi: non richiedono inserimenti in un progetto preesistente.
2. Installa le dipendenze dichiarate nel file di progetto; conserva la versione della toolchain indicata.
3. Apri PowerShell nella cartella esportata ed esegui i comandi della scheda.
4. Confronta il risultato con quello atteso e modifica gli input nel punto in cui vengono inizializzati.

## Comportamento e limiti

Entrambi i campi sono quotati e le virgolette interne vengono raddoppiate.

Se manca il targeting pack net8.0, installare il relativo SDK/pack; eventuali warning CS1998 indicano soltanto un Main dimostrativo senza await.

I dati sono sintetici. La verifica dichiarata riguarda soltanto le prove effettivamente registrate nella scheda; la presenza di un esempio completo non attesta esecuzioni su ogni sistema operativo.
