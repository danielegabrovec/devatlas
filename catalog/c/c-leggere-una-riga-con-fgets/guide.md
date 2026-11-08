## Obiettivo

Legge da un flusso sintetico con limite di dimensione e rimuove il newline finale.

## Procedura

1. Esporta tutti i file in una nuova cartella dedicata. I sorgenti sono completi: non richiedono inserimenti in un progetto preesistente.
2. Predisponi la toolchain indicata nei prerequisiti; questo esempio usa la libreria standard.
3. Apri PowerShell nella cartella esportata ed esegui i comandi della scheda.
4. Confronta il risultato con quello atteso e modifica gli input nel punto in cui vengono inizializzati.

## Comportamento e limiti

Ada Rossi; righe più lunghe del buffer richiedono gestione esplicita della continuazione.

Non ignorare warning su puntatori e dimensioni. Controllare sempre il risultato di allocazioni e operazioni I/O prima di usare il dato.

I dati sono sintetici. La verifica dichiarata riguarda soltanto le prove effettivamente registrate nella scheda; la presenza di un esempio completo non attesta esecuzioni su ogni sistema operativo.
