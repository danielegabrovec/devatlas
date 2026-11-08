"""Finalize only a release whose sources, payload and reports actually agree."""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from devatlas.catalog import Catalog
from tools.release_support import VERSION, RELEASE_NAME, assert_build_current, release_files, sha256, write_checksums, verify_checksums, verify_portable


def read_report(name):
    return json.loads((ROOT / "reports" / name).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true", help="Prepara rapporto e documentazione prima dell'ultimo packaging")
    parser.add_argument("--checksums-only", action="store_true")
    args = parser.parse_args()
    if args.checksums_only:
        write_checksums()
        verify_checksums()
        print("Checksum dei tre pacchetti verificati.")
        return
    state = assert_build_current()
    catalog = Catalog()
    audit, search = read_report("catalog-audit.json"), read_report("search-evaluation.json")
    distribution = read_report("distribution-smoke.json")
    installer = read_report("installer-verification.json")
    exports = read_report("catalog-export-roundtrip.json")
    tests = ET.parse(ROOT / "reports/app-tests.xml").getroot()
    suites = tests.findall("testsuite") if tests.tag == "testsuites" else [tests]
    tested = sum(int(s.attrib.get("tests", 0)) for s in suites)
    failed = sum(int(s.attrib.get("failures", 0)) + int(s.attrib.get("errors", 0)) for s in suites)
    skipped = sum(int(s.attrib.get("skipped", 0)) for s in suites)
    if failed or audit["failures"] or not exports["success"] or not distribution["success"] or not installer["success"] or search["top3_rate"] < .9:
        raise SystemExit("Verifiche incomplete o fallite: la consegna non viene attestata.")
    if search.get("cold_p95_ms", search["p95_ms"]) > 150:
        raise SystemExit("La ricerca non rispetta il limite di latenza previsto: ripetere la verifica del motore.")
    for report in (audit, search, exports, distribution, installer):
        if report.get("catalog_sha256") != catalog.fingerprint:
            raise SystemExit("Un rapporto si riferisce a un catalogo precedente.")
    if distribution.get("source_hashes") != state["source_hashes"] or distribution["executable_sha256"] != state["executable_sha256"]:
        raise SystemExit("La prova standalone non corrisponde ai sorgenti compilati.")
    if installer["payload_executable_sha256"] != state["executable_sha256"] or installer["installer_script_sha256"] != sha256(ROOT / "deploy/DevAtlas.iss"):
        raise SystemExit("La prova dell'installer non corrisponde al payload o allo script attuale.")
    if installer.get("production_installer_sha256") != sha256(ROOT / "dist" / f"{RELEASE_NAME}-Windows-x64-Setup.exe"):
        raise SystemExit("L'installer è cambiato dopo la verifica: ripetere il collaudo prima della consegna.")
    statuses = Counter(r.verification["status"] for r in catalog.recipes.values())
    baseline = read_report("baseline-search-evaluation.json")
    details = {}
    for name in ("data-review.json", "ui-review.json", "search-improvement.json", "profile-recovery-review.json", "catalog-independent-review.json", "editorial-improvements.json", "expansion-languages-qa.json", "expansion-frameworks-qa.json", "productivity-qa.json", "ux13-qa.json", "reader13-qa.json", "command-palette-qa.json", "accessibility13-review.json", "search-order13-qa.json", "desktop-shortcut.json"):
        if (ROOT / "reports" / name).exists():
            details[name] = read_report(name)
    delivery = {"version": VERSION, "date": "2026-10-29", "recipes": len(catalog.recipes), "stacks": len(catalog.stacks),
        "projects": sum(r.project for r in catalog.recipes.values()), "app_tests": tested, "app_test_failures": failed, "app_tests_skipped": skipped,
        "catalog_failures": len(audit["failures"]), "catalog_export_roundtrips": exports["zip_roundtrips"],
        "search_cases": search["cases"], "search_top3_passed": search["passed"], "search_top3_rate": search["top3_rate"],
        "search_p95_ms": search.get("cold_p95_ms", search["p95_ms"]), "verification_statuses": dict(statuses),
        "standalone_success": distribution["success"], "installer_verified": installer["success"],
        "catalog_sha256": catalog.fingerprint, "source_hashes": state["source_hashes"], "executable_sha256": state["executable_sha256"]}
    (ROOT / "reports/final-verification.json").write_text(json.dumps(delivery, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "reports/full-review.json").write_text(json.dumps({"release": delivery, "details": details,
        "limits": ["Verifiche sul PC Windows corrente, non su una nuova macchina virtuale o su Linux/macOS.",
                   "Le ricette non eseguite su servizi/SDK assenti conservano una verifica documentale o statica esplicita."]}, ensure_ascii=False, indent=2), encoding="utf-8")
    cold = search.get("cold_p95_ms", search["p95_ms"])
    lines = [f"# DevAtlas {VERSION} — Verifica e consegna", "", "Versione Windows x64 del 29 ottobre 2026.", "",
        "## Avvio", "", "Avviare `Avvia DevAtlas.cmd`, oppure l'eseguibile nella cartella `dist/" + RELEASE_NAME + "`.",
        "Le distribuzioni precedenti restano conservate. Il profilo portabile viene copiato dalla versione precedente più recente con uno snapshot SQLite, senza modificare l'originale; i profili già presenti nella nuova versione hanno precedenza.", "",
        "## Correzioni e aggiunte", "",
        "- Interfaccia rinnovata con gerarchie più chiare, superfici e tipografia coerenti, card leggibili e filtri attivi rimovibili.",
        "- Palette di comandi Ctrl+P, ordinamento dei risultati sull'intero insieme filtrato, modalità lettura e disposizione adattabile.",
        "- Ricerca locale nei sorgenti con navigazione fra occorrenze, ritorno a capo, blocchi espandibili e copia della selezione fedele al testo originale.",
        "- Catalogo della versione 1.2 confermato: 2.140 schede in 46 percorsi e 52 progetti; ID, codice e livelli di verifica preservati durante la revisione grafica.",
        "- Ricerche salvate con nome, testo e filtri, riapribili e organizzabili; confronto di due sorgenti con differenze affiancate e parametri indipendenti.",
        "- Filtro di ricerca su tutto il contenuto, soltanto codice/comandi o soltanto titoli; alias dei nuovi linguaggi e framework.",
        "- Ricerca migliorata per concetti, API, nomi simbolici e refusi; filtri e paginazione coerenti, cache separata per generazione dell'indice.",
        "- I motori che condividono lo stesso indice nel processo adottano lo snapshot aggiornato dopo una ricostruzione: ordinamento, metadati e cache restano coerenti.",
        "- Indicizzazione in background con stato visibile, recupero dagli errori e interfaccia utilizzabile durante il lavoro.",
        "- Raccolte rinominabili ed eliminabili conservando le schede; percorsi guidati ordinati con avanzamento, completamento e ripresa.",
        "- Editor con linguaggio riconosciuto dall'estensione, modelli espliciti per file vuoti, errori accanto ai campi e salvataggio Ctrl+S. Le modifiche ai soli metadati conservano CRLF, Unicode e spazi dei sorgenti originali.",
        "- Import, backup ed export con validazione completa, transazioni/snapshot coerenti e pubblicazione dei file senza sovrascritture o residui parziali.",
        "- Lettura robusta delle preferenze, recupero visibile dei cataloghi locali e delle singole schede personali danneggiate; backup dei testi originali e blocco delle aperture concorrenti sullo stesso profilo.",
        "- Conservate le descrizioni specifiche e le correzioni dei contenuti verificate nelle versioni precedenti.",
        "- Correzioni delle fixture e delle istruzioni SQL/MySQL/PostgreSQL indicate nel rapporto indipendente.",
        "- Build tracciata rispetto ai sorgenti, staging pulito, verifica del portabile e checksum effettivamente prodotti.", "",
        "## Risultati effettivi", "",
        f"- **{tested} test automatici superati**, {failed} errori, {skipped} saltati.",
        f"- **{str(format(len(catalog.recipes), ',' )).replace(',', '.')} schede, {len(catalog.stacks)} percorsi e {sum(r.project for r in catalog.recipes.values())} progetti**, con quote, metadati, riferimenti e checksum dei sorgenti verificati; codice delle 1.800 schede precedenti conservato.",
        f"- **{exports['zip_roundtrips']} esportazioni ZIP** rilette confrontando il contenuto UTF-8; {exports['complete_project_directories']} progetti esportati anche come cartelle.",
        f"- Ricerca: **{search['passed']}/{search['cases']} query** con la risposta attesa nelle prime tre posizioni (**{search['top3_rate']*100:.1f}%**). La versione 1.0 raggiungeva {baseline['passed']}/{baseline['cases']} ({baseline['top3_rate']*100:.1f}%).",
        f"- Percentile 95 delle query senza risultato già in cache: **{cold:.2f} ms**; tempi delle richieste ripetute riportati separatamente nel rapporto.",
        "- Standalone provato da cartella isolata con spazi, virgole e Unicode, PATH senza Python e DLL caricate dal pacchetto, alle scale Qt 100% e 200%.",
        "- Installazione, avvio e disinstallazione verificati con lo stesso script e payload, un AppId di prova univoco e una cartella isolata. Il profilo personale esterno resta conservato e la registrazione di prova viene rimossa.", "",
        "### Stato dei contenuti", "", "| Verifica dichiarata | Schede |", "|---|---:|",
        f"| Esecuzione nell'ambiente indicato | {statuses['eseguito']} |", f"| Compilazione nell'ambiente indicato | {statuses['compilato']} |",
        f"| Controllo statico | {statuses['statico']} |", f"| Documentazione, esecuzione non attestata | {statuses['documentato']} |", "",
        "Le verifiche valgono per le versioni e gli ambienti descritti nelle singole schede. Le sessioni interattive di tutti i debugger, gli SDK mobili assenti e servizi non disponibili non sono attestati. La prova standalone usa un ambiente isolato sul PC corrente, non una nuova macchina virtuale.",
        "Le catture dell'interfaccia e le prove DPI sono eseguite tramite Qt; non attestano monitor fisici o una revisione manuale di ogni combinazione di finestre.", "",
        "## File", "", f"- `dist/{RELEASE_NAME}-Windows-x64-Setup.exe`.", f"- `dist/{RELEASE_NAME}-Windows-x64-portabile.zip`.",
        f"- `dist/{RELEASE_NAME}-sorgenti.zip`.", "- `dist/SHA256SUMS.txt`: checksum dei tre pacchetti, ricalcolati e verificati dopo il confezionamento.",
        "- `reports/full-review.json` e `reports/final-verification.json`: conclusioni ed evidenze.",
        "- Rapporti specifici: test XML, audit del catalogo, round-trip export, ricerca, revisione dati/UI, installer e standalone.", "",
        "## Estensioni possibili", "",
        "Pacchetti Linux/macOS, nuove attestazioni su dispositivi mobili e servizi database richiedono ambienti dedicati. L'app conserva l'impostazione offline; non sono stati introdotti account, servizi AI o sincronizzazione cloud.", ""]
    (ROOT / "CONSEGNA.md").write_text("\n".join(lines), encoding="utf-8")
    if args.prepare:
        print("Rapporto e documentazione pronti per l'ultimo packaging.")
        return
    source_zip = release_files()[2]
    temporary = source_zip.with_suffix(".zip.tmp")
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name in ("devatlas", "catalog", "tools", "tests", "deploy", "reports"):
            for path in sorted((ROOT / name).rglob("*")):
                if path.is_file() and "__pycache__" not in path.parts:
                    archive.write(path, path.relative_to(ROOT))
        for name in ("README.md", "CONSEGNA.md", "AGENTS.md", "LICENSE.txt", "requirements.lock", "pyproject.toml", "run_devatlas.py", "Avvia DevAtlas.cmd", ".gitignore"):
            archive.write(ROOT / name, name)
    with zipfile.ZipFile(temporary) as archive:
        if archive.testzip():
            raise ValueError("Archivio sorgenti danneggiato.")
    temporary.replace(source_zip)
    verify_portable()
    write_checksums()
    verify_checksums()
    print(json.dumps({k: v for k, v in delivery.items() if k != "source_hashes"}, indent=2))


if __name__ == "__main__":
    main()

