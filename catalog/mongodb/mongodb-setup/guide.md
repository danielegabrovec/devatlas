## Ambiente
Installa MongoDB Community8.0 e mongosh2.x. La configurazione usa dati in .mongo-data e soltanto loopback27018; non punta a un servizio esistente. Avvia il server nel primo terminale e lascialo aperto. Esegui il client nel secondo.

## Isolamento
demo.js opera soltanto sulla collezione items di atlas_demo_setup e la ricrea, perdendone i dati. I nomi sono riservati al laboratorio. Arresta il processo server con Ctrl+C al termine; il catalogo non lo avvia automaticamente.