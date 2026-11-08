## Risultato

Crea una libreria installabile e produce artefatti locali soltanto dopo il test del contratto.

## Prerequisiti e procedura

1. Usa un ambiente nuovo. Installa il frontend build; i requisiti del backend sono dichiarati in pyproject.toml.
2. Esegui i due test prima della build; se falliscono correggi il sorgente.
3. `python -m build` genera sia wheel sia sdist in dist.
4. Per una prova su un altro ambiente, installa il wheel con `python -m pip install percorso-del-wheel.whl`; non pubblicare su PyPI per una distribuzione locale.

## Verifica

Due test passano; dist contiene un .whl e un .tar.gz. Il wheel di questo esempio puro Python non contiene estensioni native.

## Problemi frequenti

Un errore relativo a build o setuptools richiede l'installazione dei requisiti nel contesto corretto. Non confondere il sorgente modificabile con il wheel già costruito.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
