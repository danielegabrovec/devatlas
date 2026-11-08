## Ambiente
Node24.15.0+ e npm; dipendenze del manifest. Angular22 richiede TypeScript>=6.0 e<6.1, non il latest7. L'esempio client funziona su loopback; nessuna pubblicazione automatica.

## File
Esporta tutti i file nella stessa cartella. Il manifest fissa le versioni dirette; npm install genera il lockfile da conservare. I file del componente sono in src.

## Avvio
Apri il terminale nella cartella del manifest, controlla Node, installa e avvia il server. Segui l'URL 127.0.0.1 stampato dal tool. Il pulsante incrementa un valore di sessione. Interrompi il server con Ctrl+C. Non viene creato un servizio pubblico.