"""Run the frozen distribution independently of installed Python and the venv."""
from __future__ import annotations
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import uuid
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.release_support import VERSION, RELEASE_NAME, assert_build_current, sha256


def python_modules(pid):
    class Entry(ctypes.Structure):
        _fields_ = [("dwSize", wintypes.DWORD), ("th32ModuleID", wintypes.DWORD), ("th32ProcessID", wintypes.DWORD),
                    ("GlblcntUsage", wintypes.DWORD), ("ProccntUsage", wintypes.DWORD), ("modBaseAddr", ctypes.c_void_p),
                    ("modBaseSize", wintypes.DWORD), ("hModule", wintypes.HMODULE),
                    ("szModule", wintypes.WCHAR * 256), ("szExePath", wintypes.WCHAR * 260)]
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel.Module32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Entry)]
    kernel.Module32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Entry)]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    snapshot = kernel.CreateToolhelp32Snapshot(0x8 | 0x10, pid)
    if snapshot == ctypes.c_void_p(-1).value:
        return []
    paths = []
    try:
        entry = Entry()
        entry.dwSize = ctypes.sizeof(entry)
        present = kernel.Module32FirstW(snapshot, ctypes.byref(entry))
        while present:
            if entry.szModule.lower().startswith("python"):
                paths.append(entry.szExePath)
            present = kernel.Module32NextW(snapshot, ctypes.byref(entry))
    finally:
        kernel.CloseHandle(snapshot)
    return paths


def main():
    state = assert_build_current()
    payload = ROOT / "dist" / RELEASE_NAME
    if sha256(payload / "DevAtlas.exe") != state["executable_sha256"]:
        raise ValueError("Il pacchetto non corrisponde alla build corrente.")
    isolated = ROOT / ".cache/distribution-smoke" / uuid.uuid4().hex[:8] / "DevAtlas copia, è"
    shutil.copytree(payload, isolated, ignore=shutil.ignore_patterns("dati-personali"))
    source_catalog = (ROOT / "devatlas/data/catalog.json").read_bytes()
    bundled_catalog = (isolated / "devatlas/data/catalog.json").read_bytes()
    report = {"version": VERSION, "source_hashes": state["source_hashes"], "platform": "Windows x64", "catalog_matches": hashlib.sha256(source_catalog).hexdigest() == hashlib.sha256(bundled_catalog).hexdigest(),
              "catalog_sha256": hashlib.sha256(source_catalog).hexdigest(), "executable_sha256": hashlib.sha256((isolated / "DevAtlas.exe").read_bytes()).hexdigest(),
              "isolated_directory": str(isolated), "checks": []}
    for scale in ("1", "2"):
        environment = dict(os.environ)
        for key in ("PYTHONHOME", "PYTHONPATH", "VIRTUAL_ENV", "QT_PLUGIN_PATH", "QT_QPA_PLATFORM_PLUGIN_PATH"):
            environment.pop(key, None)
        environment["PATH"] = str(Path(os.environ.get("SystemRoot", "C:/Windows")) / "System32")
        environment["QT_QPA_PLATFORM"] = "offscreen"
        environment["QT_SCALE_FACTOR"] = scale
        environment["HTTP_PROXY"] = environment["HTTPS_PROXY"] = "http://127.0.0.1:9"
        data = isolated.parent / ("dati-test-" + scale)
        start = time.perf_counter()
        process = subprocess.Popen([str(isolated / "DevAtlas.exe"), "--data-dir", str(data), "--smoke-test"], cwd=isolated,
                                   env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        modules = []
        while process.poll() is None and time.perf_counter() - start < 55:
            if not modules:
                modules = python_modules(process.pid)
            time.sleep(.15)
        try:
            stdout, stderr = process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
        log = data / "devatlas.log"
        errors = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
        receipt_path = data / "smoke-test.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.exists() else {}
        entry = {"scale": scale, "returncode": process.returncode, "seconds": round(time.perf_counter() - start, 3),
                 "path_has_no_python": shutil.which("python", path=environment["PATH"]) is None,
                 "python_dlls": modules, "python_runtime_bundled": bool(modules) and all(Path(m).is_relative_to(isolated) for m in modules),
                 "personal_database_created": (data / "personali.sqlite").exists(),
                 "search_index_created": (data / "ricerca.sqlite").exists(), "application_log": errors,
                 "flow": receipt,
                 "stderr": stderr.decode("utf-8", errors="replace")[-3000:]}
        entry["success"] = (entry["returncode"] == 0 and entry["path_has_no_python"] and entry["python_runtime_bundled"]
                            and entry["personal_database_created"] and entry["search_index_created"] and not errors
                            and receipt.get("status") == "passed" and receipt.get("index_ready") is True
                            and receipt.get("results", 0) > 0 and receipt.get("code_blocks", 0) > 0 and receipt.get("version") == VERSION)
        report["checks"].append(entry)
    report["success"] = report["catalog_matches"] and all(c["success"] for c in report["checks"])
    report["limits"] = "Prova sul PC Windows corrente con directory isolata, PATH senza Python e DLL Python caricate dal pacchetto; non è una prova in macchina virtuale nuova. Scala Qt 100%/200%, nessun collaudo Linux/macOS o monitor fisico aggiuntivo. Proxy di rete non raggiungibile, nessun accesso web richiesto."
    (ROOT / "reports/distribution-smoke.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return not report["success"]


if __name__ == "__main__":
    raise SystemExit(main())

