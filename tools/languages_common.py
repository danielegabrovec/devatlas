"""Small authoring utilities for individually curated language recipes."""
from textwrap import dedent
import hashlib
import json
from pathlib import Path
from catalog_support import Book, slug


def clean(source):
    return dedent(source).strip() + "\n"


def program(book, title, description, source, *, filename="main.py", command="python main.py", section="Codice applicativo", tags=(), expected="", files=None, error="", project=False, parameters=None):
    assets = {filename: clean(source)}
    assets.update({path: clean(text) for path, text in (files or {}).items()})
    recipe = book.add(slug(title), title, description, assets, section=section,
        explanation=f"## Obiettivo\n\n{description}\n\n## Procedura\n\n1. Esporta tutti i file in una nuova cartella dedicata. I sorgenti sono completi: non richiedono inserimenti in un progetto preesistente.\n2. {('Installa le dipendenze dichiarate nel file di progetto; conserva la versione della toolchain indicata.' if book.stack in ('typescript', 'csharp') else 'Predisponi la toolchain indicata nei prerequisiti; questo esempio usa la libreria standard.')}\n3. Apri PowerShell nella cartella esportata ed esegui i comandi della scheda.\n4. Confronta il risultato con quello atteso e modifica gli input nel punto in cui vengono inizializzati.\n\n## Comportamento e limiti\n\n{expected or description}\n\n{error or 'Se il comando non viene trovato, verifica che la toolchain sia installata e presente nel PATH.'}\n\nI dati sono sintetici. La verifica dichiarata riguarda soltanto le prove effettivamente registrate nella scheda; la presenza di un esempio completo non attesta esecuzioni su ogni sistema operativo.\n",
        expected=expected or description, commands=command, tags=list(tags),
        errors=[error or "Comando non trovato: installare la toolchain e riaprire il terminale."],
        project=project, parameters=parameters)
    apply_evidence(recipe)


def apply_evidence(recipe):
    evidence_path=Path(__file__).with_name("languages_verification.json")
    if evidence_path.exists():
        entry=json.loads(evidence_path.read_text(encoding="utf-8")).get(recipe["id"])
        if entry:
            actual={asset["path"]:hashlib.sha256(asset["content"].encode()).hexdigest() for asset in recipe["assets"] if asset["role"]=="file"}
            if actual==entry["assets"]:
                recipe["verification"]=entry["verification"]


def require_count(book, count):
    from languages_workflows import replace_workflows
    replace_workflows(book)
    assert len(book.recipes) == count, (book.stack, len(book.recipes), count)
    assert sum(item['project'] for item in book.recipes) == 1
    book.save()

