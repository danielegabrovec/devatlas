"""Fetch public OFL fonts and the official Inno build tool into this workspace."""
from pathlib import Path
import hashlib
import json
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = {
    "devatlas/assets/Inter.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf",
    "devatlas/assets/Inter-OFL.txt": "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/OFL.txt",
    "devatlas/assets/JetBrainsMono.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf",
    "devatlas/assets/JetBrainsMono-OFL.txt": "https://raw.githubusercontent.com/google/fonts/main/ofl/jetbrainsmono/OFL.txt",
    ".cache/tools/innosetup-7.1.1-x64.exe": "https://github.com/jrsoftware/issrc/releases/download/is-7_1_1/innosetup-7.1.1-x64.exe",
}


def main():
    receipt = []
    for target, url in DOWNLOADS.items():
        path = ROOT / target
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            with urllib.request.urlopen(url, timeout=90) as response:
                path.write_bytes(response.read())
        receipt.append({"path": target, "source": url, "bytes": path.stat().st_size,
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        print(target, path.stat().st_size)
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "build-assets.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

