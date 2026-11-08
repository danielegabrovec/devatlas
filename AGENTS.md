# DevAtlas

- Applicazione Windows offline PySide6; interfaccia e documentazione in italiano.
- Usare l'ambiente `.venv` Python 3.13. Non modificare gli interpreti condivisi del PC.
- I dati personali devono restare separati dal catalogo e dall'indice SQLite ricostruibile.
- Conservare ID stabili delle ricette già distribuite; un obiettivo nuovo richiede un ID nuovo.
- Contenuti canonici in `catalog/`, builder in `tools/`, pacchetto runtime da `tools/compile_catalog.py`.
- Non gonfiare il conteggio con sole modifiche a nomi/dati o conversioni banali fra binding Qt.
- Non attestare esecuzioni, compilazioni, piattaforme o versioni non effettivamente verificate. Salvare ambiente e risultato nei rapporti.
- Dopo cambiamenti al core usare pytest con `--basetemp=.cache/pytest`; dopo contenuti eseguire audit, ricerca e QA pertinenti.
- Modifiche al codice richiedono una build standalone nuova; aggiornamenti solo editoriali possono usare `--package-only` dopo `compile_catalog.py`.
- Le risorse Qt devono funzionare anche in percorsi Windows con spazi e virgole; non rimuovere qt_bootstrap.
- Le quote correnti derivano da STACKS/PROJECT_TARGETS in tools/catalog_support.py; non usare totali storici hardcoded. La baseline1.1 conserva i 1.800 ID, percorsi e sorgenti precedenti.
- Le nuove famiglie si ricostruiscono con tools/build_expansion.py; verificare anche le query curate aggiunte e i round-trip reali degli export.
- Non installare globalmente SDK per far passare esempi: tool di QA isolati in .cache oppure limiti statici/documentali espliciti.
- I pacchetti restano separati per versione; migrare il profilo precedente con snapshot senza alterare l'originale e non includere dati personali negli archivi.
- Copia ed esportazione devono usare lo stesso sorgente renderizzato e non sovrascrivere destinazioni esistenti.

