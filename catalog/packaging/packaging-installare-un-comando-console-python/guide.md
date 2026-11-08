## Scopo
Dichiarare project.scripts per un entry point indipendente dal percorso del sorgente.

## Prerequisiti
Ambiente virtuale Python attivo; la cartella Scripts/bin deve essere nel PATH.

## Avvio
Salva tutti i file esportati preservando i percorsi relativi. Esegui i comandi dalla directory che contiene il manifest o lo script principale. Usa un ambiente virtuale dedicato per non modificare le dipendenze di altri progetti.

## Controllo dell'artefatto
Dichiarare project.scripts per un entry point indipendente dal percorso del sorgente. Il successo del comando di build non attesta l'avvio su un computer pulito: avvia il risultato sulla destinazione prevista prima di consegnarlo. Questo esempio non pubblica pacchetti né firma eseguibili.