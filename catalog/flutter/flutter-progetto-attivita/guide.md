## Progetto
Il modello valida il titolo, assegna il prossimo ID e restituisce una lista nuova. La UI aggiunge righe e mostra quante sono completate; dispose rilascia il controller. Tre test unitari controllano vuoto, ID/immutabilità e toggle; il widget test verifica la costruzione della pagina.

## Controllo manuale
Prova un titolo vuoto, aggiungi due attività e spuntane una: il conteggio deve essere1. Hot restart azzera lo stato, perché questo capstone non aggiunge un plugin di persistenza. I runner Windows/Android vengono generati dall’SDK locale con bootstrap riproducibile.