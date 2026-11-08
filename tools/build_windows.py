"""Build a traced release using a clean staging tree; never collect user data."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sqlite3
import sys
import uuid
import zipfile
import re

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.release_support import VERSION, RELEASE_NAME, assert_build_current, code_state, sha256


def guarded(path, parent):
    if path.is_symlink() or not path.resolve().is_relative_to(parent.resolve()) or path.resolve() == parent.resolve():
        raise ValueError(f"Percorso di build fuori dalla cartella prevista: {path}")


def migrate_legacy_profile(stage, destination):
    """Copy the newest earlier portable profile without editing the original."""
    if (destination / "dati-personali").exists():
        return False
    current_version = tuple(int(part) for part in VERSION.split("."))
    candidates = []
    for directory in (ROOT / "dist").glob("DevAtlas-*"):
        match = re.fullmatch(r"DevAtlas-(\d+)\.(\d+)\.(\d+)", directory.name)
        if match and directory.is_dir() and tuple(map(int, match.groups())) < current_version and (directory / "dati-personali/personali.sqlite").is_file():
            candidates.append((tuple(map(int, match.groups())), directory))
    old_release = max(candidates)[1] if candidates else ROOT / "dist/DevAtlas"
    legacy = old_release / "dati-personali"
    if not (legacy / "personali.sqlite").is_file():
        return False
    guarded(legacy, ROOT / "dist")
    profile = stage / "dati-personali"
    profile.mkdir(exist_ok=True)
    source = sqlite3.connect((legacy / "personali.sqlite").resolve().as_uri() + "?mode=ro", uri=True)
    target = sqlite3.connect(profile / "personali.sqlite")
    try:
        source.backup(target)
        if target.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("Il profilo precedente non supera il controllo di integrità.")
    finally:
        target.close()
        source.close()
    local_catalog = legacy / "catalogo-locale.json"
    catalog_mode = "nessun catalogo locale"
    if local_catalog.is_file() and not local_catalog.is_symlink():
        # 1.0 stored an entire catalog even when only one recipe was customized.
        # Carry forward actual local differences, not an outdated stock catalog.
        from devatlas.catalog import Catalog
        try:
            old = Catalog(old_release / "devatlas/data/catalog.json")
            local = Catalog(local_catalog)
            current = Catalog(ROOT / "devatlas/data/catalog.json")
            merged = {rid: recipe.to_dict() for rid, recipe in current.recipes.items()}
            for rid, recipe in local.recipes.items():
                if rid not in old.recipes or recipe.data != old.recipes[rid].data:
                    merged[rid] = recipe.to_dict()
            payload = {"format": "RecipeBundle", "version": 1, "stacks": {**current.stacks, **local.stacks}, "recipes": list(merged.values())}
            migrated_catalog = profile / local_catalog.name
            migrated_catalog.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            Catalog(migrated_catalog)
            catalog_mode = "Differenze locali conservate sopra il nuovo catalogo incluso"
        except (ValueError, OSError, KeyError):
            # Preserve the original for the app's visible recovery path.
            shutil.copy2(local_catalog, profile / local_catalog.name)
            catalog_mode = "Originale conservato; l'app verificherà il catalogo locale all'avvio"
    (profile / "migrazione-profilo.json").write_text(json.dumps({"source": str(legacy), "method": "SQLite online backup",
        "original_preserved": True, "catalog_mode": catalog_mode}, indent=2), encoding="utf-8")
    return True


def publish(stage, destination):
    """Keep the previous tree recoverable and carry forward its portable profile."""
    guarded(stage, ROOT / ".cache")
    guarded(destination, ROOT / "dist")
    backup = None
    if destination.exists():
        profile = destination / "dati-personali"
        if profile.exists():
            from PySide6.QtCore import QLockFile
            lock = QLockFile(str(profile / "devatlas.lock"))
            lock.setStaleLockTime(0)
            if not lock.tryLock(0):
                raise ValueError("DevAtlas usa ancora questo profilo: chiudi l'app prima di aggiornare la distribuzione.")
            lock.unlock()
        backup = ROOT / ".cache/releases" / (RELEASE_NAME + "-" + uuid.uuid4().hex[:8])
        backup.parent.mkdir(parents=True, exist_ok=True)
        guarded(backup, ROOT / ".cache")
        destination.rename(backup)
    try:
        stage.rename(destination)
        if backup and (backup / "dati-personali").exists():
            profile = backup / "dati-personali"
            if profile.is_symlink():
                raise ValueError("Il profilo portabile non può essere un collegamento simbolico durante la build.")
            profile.rename(destination / "dati-personali")
    except Exception:
        if destination.exists():
            destination.rename(stage)
        if backup:
            backup.rename(destination)
        raise
    return str(backup) if backup else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-only", action="store_true")
    parser.add_argument("--compile-only", action="store_true", help="Compila e registra gli hash senza pubblicare una distribuzione parziale")
    args = parser.parse_args()
    if args.package_only and args.compile_only:
        parser.error("Scegli --package-only oppure --compile-only.")
    os.chdir(ROOT)
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    os.environ["NUITKA_CACHE_DIR"] = str(ROOT / ".cache/nuitka")
    os.environ["NUITKA_UPDATE_CHECK"] = "never"
    os.environ["TEMP"] = os.environ["TMP"] = str(ROOT / ".cache/tmp")
    Path(os.environ["TEMP"]).mkdir(parents=True, exist_ok=True)
    if not args.package_only:
        from devatlas.qt_bootstrap import configure_qt_plugins
        configure_qt_plugins()
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QIcon
        app = QApplication([])
        QIcon(str(ROOT / "devatlas/assets/devatlas.svg")).pixmap(256, 256).save(str(ROOT / "devatlas/assets/devatlas.ico"), "ICO")
        app.quit()
        before = code_state()
        numeric_version = VERSION + ".0"
        command = [sys.executable, "-m", "nuitka", "--standalone", "--enable-plugin=pyside6",
            "--include-qt-plugins=platforms,styles,iconengines,imageformats", "--msvc=latest", "--jobs=4",
            "--windows-console-mode=disable", "--assume-yes-for-downloads", "--update-check=never",
            "--include-package=pygments.lexers", "--include-package=pygments.styles",
            "--include-data-dir=devatlas/data=devatlas/data", "--include-data-dir=devatlas/assets=devatlas/assets",
            "--windows-icon-from-ico=devatlas/assets/devatlas.ico", "--output-dir=build", "--output-filename=DevAtlas.exe",
            "--company-name=DevAtlas", "--product-name=DevAtlas", "--file-description=Atlante del Codice offline",
            "--file-version=" + numeric_version, "--product-version=" + numeric_version,
            "--report=reports/nuitka-build.xml", "run_devatlas.py"]
        print(f"Compilazione DevAtlas {VERSION} con Python {sys.version.split()[0]}", flush=True)
        with (reports / "build-windows.log").open("w", encoding="utf-8") as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
        if result.returncode:
            print((reports / "build-windows.log").read_text(encoding="utf-8", errors="replace")[-8000:])
            raise SystemExit(result.returncode)
        if before != code_state():
            raise SystemExit("Sorgenti cambiati durante la compilazione: ripetere la build prima della consegna.")
        (reports / "build-state.json").write_text(json.dumps({"version": VERSION, "source_hashes": before,
            "executable_sha256": sha256(ROOT / "build/run_devatlas.dist/DevAtlas.exe")}, indent=2), encoding="utf-8")
    assert_build_current()
    if args.compile_only:
        print("Build compilata e tracciata; pubblicazione rinviata al catalogo verificato.")
        return
    stage = ROOT / ".cache/stage" / uuid.uuid4().hex[:8] / "DevAtlas"
    shutil.copytree(ROOT / "build/run_devatlas.dist", stage, ignore=shutil.ignore_patterns("dati-personali"))
    shutil.copytree(ROOT / "devatlas/data", stage / "devatlas/data", dirs_exist_ok=True)
    shutil.copytree(ROOT / "devatlas/assets", stage / "devatlas/assets", dirs_exist_ok=True)
    for name in ("README.md", "CONSEGNA.md", "LICENSE.txt", "requirements.lock"):
        if (ROOT / name).exists():
            shutil.copy2(ROOT / name, stage / name)
    licenses = stage / "licenze"
    licenses.mkdir(exist_ok=True)
    if (Path(sys.base_prefix) / "LICENSE.txt").exists():
        shutil.copy2(Path(sys.base_prefix) / "LICENSE.txt", licenses / "Python-PSF.txt")
    packages = ROOT / ".venv/Lib/site-packages"
    for pattern in ("pyside6_essentials-*.dist-info", "pygments-*.dist-info", "shiboken6-*.dist-info", "snowballstemmer-*.dist-info"):
        for directory in packages.glob(pattern):
            if (directory / "licenses").exists():
                shutil.copytree(directory / "licenses", licenses / directory.name, dirs_exist_ok=True)
    for path in (ROOT / "devatlas/assets").glob("*-OFL.txt"):
        shutil.copy2(path, licenses / path.name)
    (stage / "portable.flag").write_text("Dati personali nella cartella dati-personali.\n", encoding="utf-8")
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    portable = dist / f"{RELEASE_NAME}-Windows-x64-portabile.zip"
    temporary_zip = portable.with_suffix(".zip.tmp")
    with zipfile.ZipFile(temporary_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(stage.rglob("*")):
            if path.is_file():
                archive.write(path, Path("DevAtlas") / path.relative_to(stage))
    with zipfile.ZipFile(temporary_zip) as archive:
        if archive.testzip():
            raise ValueError("La verifica dell'archivio portabile non è riuscita.")
    compiler = ROOT / ".cache/tools/inno/ISCC.exe"
    if not compiler.exists():
        raise SystemExit("ISCC.exe mancante: prepara Inno Setup portabile.")
    with (reports / "installer-build.log").open("w", encoding="utf-8") as log:
        subprocess.run([str(compiler), "/DAppVersion=" + VERSION, "/DPayloadDir=" + str(stage),
                        str(ROOT / "deploy/DevAtlas.iss")], check=True, stdout=log, stderr=subprocess.STDOUT)
    # Create archives before copying any personal data. Distribution archives
    # must always be clean, even when the local portable installation is upgraded.
    migrated = migrate_legacy_profile(stage, dist / RELEASE_NAME)
    backup = publish(stage, dist / RELEASE_NAME)
    temporary_zip.replace(portable)
    (reports / "package-state.json").write_text(json.dumps({"version": VERSION,
        "executable_sha256": sha256(dist / RELEASE_NAME / "DevAtlas.exe"),
        "catalog_sha256": sha256(dist / RELEASE_NAME / "devatlas/data/catalog.json"),
        "previous_distribution": backup, "legacy_profile_copied": migrated}, indent=2), encoding="utf-8")
    print(f"Pacchetti pronti: {portable}")


if __name__ == "__main__":
    main()

