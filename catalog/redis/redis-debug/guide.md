## Lettura
TYPE controlla il dato prima di scegliere i comandi. PTTL restituisce millisecondi, -1 per chiave senza scadenza e -2 per chiave assente. INFO stats e SLOWLOG GET mostrano dati del processo dedicato; un log vuoto non prova che ogni query sia veloce.

## Ambiente
Non modifica soglie SLOWLOG o configurazioni di un server esistente.