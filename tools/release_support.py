"""Release invariants shared by packaging and verification tools."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from devatlas import __version__
VERSION = __version__
RELEASE_NAME = f"DevAtlas-{VERSION}"


def sha256(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def code_state(root=ROOT):
    paths = list((root / "devatlas").rglob("*.py"))
    paths += [root / p for p in ("pyproject.toml", "requirements.lock", "run_devatlas.py")]
    return {p.relative_to(root).as_posix(): sha256(p) for p in sorted(paths) if p.is_file()}


def assert_build_current(root=ROOT):
    path = root / "reports/build-state.json"
    if not path.exists():
        raise ValueError("Manca una build verificabile: esegui build_windows.py senza --package-only.")
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("version") != VERSION or state.get("source_hashes") != code_state(root):
        raise ValueError("I sorgenti sono cambiati dopo la compilazione: serve una nuova build completa.")
    binary = root / "build/run_devatlas.dist/DevAtlas.exe"
    if not binary.exists() or state.get("executable_sha256") != sha256(binary):
        raise ValueError("La build standalone non corrisponde al rapporto di compilazione.")
    return state


def release_files(root=ROOT):
    return [root / "dist" / f"{RELEASE_NAME}-Windows-x64-portabile.zip",
            root / "dist" / f"{RELEASE_NAME}-Windows-x64-Setup.exe",
            root / "dist" / f"{RELEASE_NAME}-sorgenti.zip"]


def write_checksums(root=ROOT):
    paths = release_files(root)
    if any(not p.is_file() for p in paths):
        raise ValueError("Mancano uno o più pacchetti della versione corrente.")
    manifest = root / "dist/SHA256SUMS.txt"
    manifest.write_text("".join(f"{sha256(p)}  {p.name}\n" for p in paths), encoding="utf-8")
    return manifest


def verify_checksums(root=ROOT):
    rows = (root / "dist/SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
    expected = {p.name for p in release_files(root)}
    seen = set()
    for row in rows:
        digest, name = row.split("  ", 1)
        if name not in expected or name in seen:
            raise ValueError("Il manifesto contiene file inattesi o duplicati.")
        if sha256(root / "dist" / name) != digest:
            raise ValueError(f"Checksum non corrispondente: {name}")
        seen.add(name)
    if seen != expected:
        raise ValueError("Manifesto checksum incompleto.")
    return True


def verify_portable(root=ROOT):
    with zipfile.ZipFile(release_files(root)[0]) as archive:
        if archive.testzip() is not None:
            raise ValueError("Archivio portabile danneggiato.")
        names = archive.namelist()
        if any("dati-personali" in Path(p).parts for p in names):
            raise ValueError("Il pacchetto include dati personali.")
        if "DevAtlas/DevAtlas.exe" not in names or "DevAtlas/portable.flag" not in names:
            raise ValueError("Archivio portabile incompleto.")
        catalog = archive.read("DevAtlas/devatlas/data/catalog.json")
        if hashlib.sha256(catalog).hexdigest() != sha256(root / "devatlas/data/catalog.json"):
            raise ValueError("Il catalogo nel portabile non è quello corrente.")
    return True

