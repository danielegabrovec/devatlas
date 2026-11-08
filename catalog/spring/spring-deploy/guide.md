## Procedura
application-demo.properties modifica una proprietà mantenendo il bind sul loopback. Per un hosting reale occorre predisporre l’ambiente del server, reverse proxy e configurazioni esterne; il ricettario non esegue deploy. Verifica GET http://127.0.0.1:8086/channel: con profilo demo restituisce channel=didattico; senza profilo restituisce local.

## Versioni
Il POM usa parent4.1.2 e compilazione Java21. La prima risoluzione richiede Maven Central o una cache completa. I file sono autonomi nella cartella esportata; non sovrapporli a una applicazione esistente.