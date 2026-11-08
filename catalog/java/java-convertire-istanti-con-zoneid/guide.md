## Obiettivo

Applica le regole del fuso Europe/Rome a un istante UTC.

## Procedura

1. Esporta tutti i file in una nuova cartella dedicata. I sorgenti sono completi: non richiedono inserimenti in un progetto preesistente.
2. Predisponi la toolchain indicata nei prerequisiti; questo esempio usa la libreria standard.
3. Apri PowerShell nella cartella esportata ed esegui i comandi della scheda.
4. Confronta il risultato con quello atteso e modifica gli input nel punto in cui vengono inizializzati.

## Comportamento e limiti

2026-01-10T13:00+01:00[Europe/Rome]; usa il database fusi del JDK.

Il nome della classe pubblica deve corrispondere a Main.java. Usare JDK17+ e non abilitare feature preview per questi esempi.

I dati sono sintetici. La verifica dichiarata riguarda soltanto le prove effettivamente registrate nella scheda; la presenza di un esempio completo non attesta esecuzioni su ogni sistema operativo.
