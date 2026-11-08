## Risultato

Prepara un ambiente isolato e installa un package src-layout in modalità modificabile.

## Prerequisiti e procedura

1. Installa CPython3.13 con Python Launcher su Windows; `py -0p` elenca gli interpreti.
2. Esporta questa struttura e crea .venv con il comando fornito; usare il percorso completo dell'interprete evita di modificare ExecutionPolicy.
3. pip install -e . installa il progetto locale e può scaricare setuptools per il build isolato.
4. Su Linux/macOS usare `python3 -m venv .venv` e `.venv/bin/python` al posto del percorso Scripts.

## Verifica

Il modulo stampa Ciao Ada; modificando src/catalog_hello/__init__.py cambia l'esecuzione successiva senza reinstallare il package.

## Problemi frequenti

Se compare No module named catalog_hello, esegui installazione ed avvio con lo stesso interprete .venv. Non nominare un file locale setuptools.py.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
