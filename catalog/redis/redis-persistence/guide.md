## Configurazione
appendonly yes abilita AOF per questo server dedicato. Dopo l'avvio, in un secondo terminale esegui bash demo.sh e leggi INFO persistence. Arresta normalmente il processo e riaprilo con la stessa directory per verificare GET atlas_demo:persistence:message.

## Limiti
Le garanzie di durabilità dipendono dalla politica appendfsync e dal filesystem; questa guida non dichiara test di perdita di alimentazione.