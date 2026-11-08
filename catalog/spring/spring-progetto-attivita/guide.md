## Contratto
GET /tasks restituisce una lista. POST /tasks richiede title non vuoto e risponde201 con Location. Il servizio assegna ID monotoni nella sessione e restituisce copie immutabili. I test verificano vuoto, trim, ID e snapshot.

## Prova HTTP
Avvia il JAR sul loopback8086. Crea due attività, verifica ID1/2 e lista di due elementi. Invia un titolo vuoto:400. Riavviando il processo lo stato si azzera; non viene simulata persistenza su database.