## Scopo
Usare lo strumento Qt e scegliere esplicitamente standalone.

## Prerequisiti
Python 3.13, PySide6 6.12; toolchain C/C++ richiesta da Nuitka e dumpbin nel terminale MSVC. Revisionare la specifica prima della compilazione.

## Avvio
Salva tutti i file esportati preservando i percorsi relativi. Esegui i comandi dalla directory che contiene il manifest o lo script principale. Usa un ambiente virtuale dedicato per non modificare le dipendenze di altri progetti.

## Controllo dell'artefatto
Usare lo strumento Qt e scegliere esplicitamente standalone. Il successo del comando di build non attesta l'avvio su un computer pulito: avvia il risultato sulla destinazione prevista prima di consegnarlo. Questo esempio non pubblica pacchetti né firma eseguibili.