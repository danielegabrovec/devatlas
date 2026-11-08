## Preparare l'ambiente
Installa Python 3.13 x64. Esporta i due file in una cartella nuova, apri PowerShell in quella cartella ed esegui i comandi nell'ordine mostrato. L'ambiente .venv contiene soltanto PySide6; usa sempre il suo python.exe anche per pip. La configurazione dei plugin è ricavata dalla posizione reale del pacchetto, quindi non dipende dall'interpretazione del percorso della cartella.

## Capire il primo avvio
main.py crea una sola QApplication, collega clicked prima di app.exec() e conserva il contatore sulla finestra. La chiusura della finestra termina il ciclo eventi. Il nome {project_name} si può personalizzare nel ricettario.

## Controllare il risultato
Avvia main.py, premi Incrementa tre volte e verifica il numero 3. Chiudi e riapri: il contatore torna a zero, perché questa prima app non salva dati. L'installazione richiede Internet; l'app in esecuzione non ne ha bisogno. Questa procedura riguarda Windows e non attesta prove Linux o macOS.