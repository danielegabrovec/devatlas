## Obiettivo
Legare la cache a un file dipendenze presente e installare esplicitamente i pacchetti.

## Collocazione
Salva app.py e test_app.py nella radice del progetto. Il workflow va in .github/workflows/ci.yml: il contenuto usa notazione JSON, che è un sottoinsieme valido di YAML. Esegui prima i test locali con il comando indicato.

## Attivazione
Il file non viene pubblicato dal ricettario. Dopo avere revisionato la configurazione e copiato nel proprio repository, usa l'evento indicato dal campo on. L'ambiente review-demo, dove presente, richiede di configurare le regole di approvazione nelle impostazioni GitHub: il solo nome non impone approvazioni.

## Risultato
Legare la cache a un file dipendenze presente e installare esplicitamente i pacchetti. I tre test verificano zero, positivo e negativo. Il badge documentato non equivale a una run GitHub effettivamente riuscita.