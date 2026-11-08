## Scopo
Usare restore --staged mantenendo la modifica nel file.

## Esecuzione
Salva example.ps1 in una cartella nuova ed esegui il comando da quella stessa cartella. Lo script crea un repository temporaneo, configura un autore soltanto localmente e vi si posiziona. Non contatta server remoti; gli eventuali remote sono bare repository locali.

## Lettura del risultato
Usare restore --staged mantenendo la modifica nel file. Il codice è fornito per intero: leggi gli argomenti e i percorsi prima dell'esecuzione. Gli esempi che scrivono dati creano file temporanei o operano soltanto nel repository dimostrativo indicato.

## Compatibilità
Git 2.45+ e PowerShell 7. La ricetta crea un repository nuovo nella cartella temporanea; non eseguirla dentro un repository di produzione per risparmiare il setup.