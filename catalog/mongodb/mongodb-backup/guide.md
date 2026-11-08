## Copia selettiva
Il dump include soltanto atlas_demo_setup. La seconda operazione rimappa il namespace in atlas_demo_restored, da scegliere nuovo e vuoto. Non usa --drop. Verifica dopo il ripristino documenti e indici con mongosh.

## Consegna
Conserva versione degli strumenti e manifest dello schema insieme al backup. Le credenziali non sono incluse nei file del progetto. La ricetta non esegue alcun backup del server dell'utente.