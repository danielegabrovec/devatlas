"""Install/uninstall an isolated identity of the exact release payload.

Uses the production Inno script and files with a fresh test AppId, so it cannot
overwrite an installed DevAtlas or its uninstall registration. No UI automation.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid
import winreg

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.release_support import VERSION, RELEASE_NAME, assert_build_current, sha256


def main():
    state = assert_build_current()
    payload = ROOT / "dist" / RELEASE_NAME
    directory = ROOT / ".cache/installer-check" / uuid.uuid4().hex[:8]
    directory.mkdir(parents=True)
    target = directory / "installazione di prova"
    if not target.resolve().is_relative_to((ROOT / ".cache/installer-check").resolve()):
        raise ValueError("Percorso di verifica fuori dalla cache prevista.")
    identity = "DevAtlas-QA-" + uuid.uuid4().hex
    registry_key = "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\" + identity + "_is1"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_key):
            raise ValueError("Identità di verifica già registrata.")
    except FileNotFoundError:
        pass
    compiler = ROOT / ".cache/tools/inno/ISCC.exe"
    test_installer = directory / "DevAtlas-QA-Setup.exe"
    with (directory / "compile.log").open("w", encoding="utf-8") as log:
        subprocess.run([str(compiler), "/DAppVersion=" + VERSION, "/DAppIdentifier=" + identity,
            "/DPayloadDir=" + str(payload), "/O" + str(directory), "/FDevAtlas-QA-Setup", str(ROOT / "deploy/DevAtlas.iss")],
            check=True, stdout=log, stderr=subprocess.STDOUT, timeout=120)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = str(directory)
    flags = ["/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/SP-", "/CURRENTUSER", "/NOICONS", "/TASKS=", "/DIR=" + str(target), "/GROUP=" + identity, "/LOG=" + str(directory / "install.log")]
    installed = subprocess.run([str(test_installer), *flags], env=env, timeout=90)
    checks = {"install_returncode": installed.returncode}
    try:
        checks["files_installed"] = (target / "DevAtlas.exe").is_file()
        checks["executable_matches"] = checks["files_installed"] and sha256(target / "DevAtlas.exe") == state["executable_sha256"]
        checks["catalog_matches"] = sha256(target / "devatlas/data/catalog.json") == sha256(payload / "devatlas/data/catalog.json")
        checks["portable_flag_excluded"] = not (target / "portable.flag").exists()
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_key) as key:
            checks["registered_version"] = winreg.QueryValueEx(key, "DisplayVersion")[0]
        data = directory / "profilo esterno"
        env["QT_QPA_PLATFORM"] = "offscreen"
        env["PATH"] = str(Path(os.environ["SystemRoot"]) / "System32")
        run = subprocess.run([str(target / "DevAtlas.exe"), "--data-dir", str(data), "--smoke-test"], env=env, timeout=50)
        checks["installed_app_returncode"] = run.returncode
        checks["external_profile_created"] = (data / "personali.sqlite").is_file()
        flow_path = data / "smoke-test.json"
        flow = json.loads(flow_path.read_text(encoding="utf-8")) if flow_path.exists() else {}
        checks["installed_flow_verified"] = flow.get("status") == "passed" and flow.get("results", 0) > 0 and flow.get("code_blocks", 0) > 0
    finally:
        uninstaller = target / "unins000.exe"
        if uninstaller.exists():
            if not uninstaller.resolve().is_relative_to(directory.resolve()):
                raise ValueError("Disinstallatore fuori dalla cartella di prova.")
            removed = subprocess.run([str(uninstaller), "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/LOG=" + str(directory / "uninstall.log")], env=env, timeout=90)
            checks["uninstall_returncode"] = removed.returncode
    checks["application_removed"] = not (target / "DevAtlas.exe").exists()
    checks["personal_data_preserved"] = (directory / "profilo esterno/personali.sqlite").is_file()
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_key):
            checks["test_registration_removed"] = False
    except FileNotFoundError:
        checks["test_registration_removed"] = True
    success = all([checks.get("install_returncode") == 0, checks.get("executable_matches"), checks.get("catalog_matches"),
        checks.get("portable_flag_excluded"), checks.get("registered_version") == VERSION, checks.get("installed_app_returncode") == 0, checks.get("installed_flow_verified"),
        checks.get("uninstall_returncode") == 0, checks.get("application_removed"), checks.get("personal_data_preserved"), checks.get("test_registration_removed")])
    report = {"version": VERSION, "success": success, "checks": checks,
        "payload_executable_sha256": state["executable_sha256"], "catalog_sha256": sha256(payload / "devatlas/data/catalog.json"),
        "installer_script_sha256": sha256(ROOT / "deploy/DevAtlas.iss"),
        "production_installer_sha256": sha256(ROOT / "dist" / f"{RELEASE_NAME}-Windows-x64-Setup.exe"),
        "limits": "Stesso script e payload della release, AppId di prova isolato, installazione per utente sul PC corrente. Nessuna installazione reale di DevAtlas né suo registro di disinstallazione vengono sostituiti; profilo esterno conservato."}
    (ROOT / "reports/installer-verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return not success


if __name__ == "__main__":
    raise SystemExit(main())

