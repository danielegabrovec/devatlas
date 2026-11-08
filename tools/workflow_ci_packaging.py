"""CI and distribution configurations, with no provider writes on generation."""
from __future__ import annotations
import copy
import json
from catalog_support import Book, slug
from desktop_tools_common import save_book

PYTHON_APP='''def square(value: int) -> int:
    return value * value

if __name__ == "__main__":
    print(square(7))
'''
UNIT='''import unittest
from app import square
class SquareTests(unittest.TestCase):
    def test_positive(self): self.assertEqual(square(7),49)
    def test_zero(self): self.assertEqual(square(0),0)
    def test_negative(self): self.assertEqual(square(-3),9)
if __name__=="__main__":unittest.main()
'''

def workflow():
    return {"name":"Verifica locale dimostrativa","on":{"workflow_dispatch":{}},"permissions":{"contents":"read"},"jobs":{"test":{"runs-on":"ubuntu-latest","steps":[{"uses":"actions/checkout@v7","with":{"persist-credentials":False}},{"uses":"actions/setup-python@v7","with":{"python-version":"3.13"}},{"name":"Test","run":"python -m unittest -v"}]}}}

def ci_variants():
    rows=[]
    def add(title,description,change=None,extra=None):
        data=workflow()
        if change:change(data)
        rows.append((title,description,data,extra or {}))
    add("Eseguire unit test Python in GitHub Actions","Creare un workflow richiamabile manualmente con tre casi unittest.")
    add("Avviare verifiche su push e pull request","Definire trigger ordinari senza usare pull_request_target.",lambda w:w.update({"on":{"push":{},"pull_request":{}}}))
    add("Esporre un parametro nella partenza manuale","Dichiarare un input choice e trasferirlo tramite env senza interpolarlo in codice shell.",lambda w:(w.update({"on":{"workflow_dispatch":{"inputs":{"mode":{"type":"choice","options":["quick","full"],"default":"quick","description":"Modalità"}}}}}),w["jobs"]["test"].update({"env":{"RECIPE_MODE":"${{ inputs.mode }}"}})))
    add("Verificare più versioni Python con una matrice","Usare matrix.python nella configurazione dell'interprete.",lambda w:(w["jobs"]["test"].update({"strategy":{"matrix":{"python":["3.12","3.13","3.14"]}}}),w["jobs"]["test"]["steps"][1]["with"].update({"python-version":"${{ matrix.python }}"})))
    add("Verificare un progetto su sistemi operativi differenti","Usare matrix.os senza dichiarare gli esiti prima della CI effettiva.",lambda w:w["jobs"]["test"].update({"runs-on":"${{ matrix.os }}","strategy":{"matrix":{"os":["ubuntu-latest","windows-latest","macos-latest"]}}}))
    add("Raccogliere tutti gli errori di una matrice","Disabilitare fail-fast per non annullare gli altri casi al primo errore.",lambda w:w["jobs"]["test"].update({"strategy":{"fail-fast":False,"matrix":{"python":["3.12","3.13"]}}}))
    add("Annullare una run superata da una nuova versione","Definire un gruppo concurrency per workflow e riferimento.",lambda w:w.update({"concurrency":{"group":"${{ github.workflow }}-${{ github.ref }}","cancel-in-progress":True}}))
    add("Imporre un limite temporale al job","Usare timeout-minutes per impedire attese indefinite.",lambda w:w["jobs"]["test"].update({"timeout-minutes":10}))
    add("Limitare il token del job a sola lettura","Dichiarare permissions nel job, mantenendo il checkout senza credenziali persistenti.",lambda w:w["jobs"]["test"].update({"permissions":{"contents":"read"}}))
    add("Avviare la CI soltanto per percorsi pertinenti","Filtrare modifiche Python e al workflow nel trigger pull_request.",lambda w:w.update({"on":{"pull_request":{"paths":["**.py",".github/workflows/**"]},"workflow_dispatch":{}}}))
    add("Limitare i push osservati al ramo principale","Definire branches senza alterare i trigger delle pull request.",lambda w:w.update({"on":{"push":{"branches":["main"]},"pull_request":{}}}))
    add("Evitare un job costoso sulle pull request draft","Usare un'espressione if che consente gli altri eventi.",lambda w:(w.update({"on":{"pull_request":{},"workflow_dispatch":{}}}),w["jobs"]["test"].update({"if":"github.event_name != 'pull_request' || github.event.pull_request.draft == false"})))
    add("Passare configurazione al processo tramite ambiente","Dichiarare PYTHONUTF8 nel job invece di concatenare comandi dipendenti dalla shell.",lambda w:w["jobs"]["test"].update({"env":{"PYTHONUTF8":"1","RECIPE_MODE":"test"}}))
    add("Impostare la directory di lavoro dei comandi","Centralizzare defaults.run.working-directory per gli step run.",lambda w:w["jobs"]["test"].update({"defaults":{"run":{"working-directory":"."}}}))
    add("Selezionare esplicitamente la shell dei comandi","Usare Bash per uno step Linux invece di dipendere da un default implicito.",lambda w:w["jobs"]["test"]["steps"][-1].update({"shell":"bash"}))
    add("Trasferire un output tra due step","Scrivere un valore controllato in GITHUB_OUTPUT e leggerlo tramite steps.id.outputs.",lambda w:w["jobs"]["test"]["steps"].extend([{"id":"meta","run":"echo 'channel=local' >> \"$GITHUB_OUTPUT\""},{"env":{"CHANNEL":"${{ steps.meta.outputs.channel }}"},"run":"printf '%s\\n' \"$CHANNEL\""}]))
    add("Trasferire un output tra due job","Dichiarare outputs del producer e needs del consumer.",lambda w:(w["jobs"]["test"].update({"outputs":{"result":"${{ steps.result.outputs.status }}"}}),w["jobs"]["test"]["steps"].append({"id":"result","run":"echo 'status=passed' >> \"$GITHUB_OUTPUT\""}),w["jobs"].update({"report":{"needs":"test","runs-on":"ubuntu-latest","steps":[{"env":{"STATUS":"${{ needs.test.outputs.result }}"},"run":"printf '%s\\n' \"$STATUS\""}]}})))
    add("Ordinare job di build dopo i test","Usare needs per evitare la build quando i test non passano.",lambda w:w["jobs"].update({"build":{"needs":"test","runs-on":"ubuntu-latest","steps":[{"uses":"actions/checkout@v7"},{"uses":"actions/setup-python@v7","with":{"python-version":"3.13"}},{"run":"python -m compileall -q app.py"}]}}))
    add("Conservare il report test come artefatto","Caricare un report prodotto dalla run con errore se il file manca.",lambda w:(w["jobs"]["test"]["steps"][-1].update({"run":"python -m unittest -v > test-report.txt 2>&1"}),w["jobs"]["test"]["steps"].append({"uses":"actions/upload-artifact@v7","with":{"name":"test-report","path":"test-report.txt","if-no-files-found":"error"}})))
    add("Limitare la conservazione di un artefatto CI","Dichiarare retention-days su un report non sensibile.",lambda w:w["jobs"]["test"]["steps"].extend([{"run":"python --version > runtime.txt"},{"uses":"actions/upload-artifact@v7","with":{"name":"runtime-report","path":"runtime.txt","retention-days":7}}]))
    add("Conservare diagnostica anche quando un test fallisce","Usare always per l'upload e non mascherare il fallimento dello step test.",lambda w:(w["jobs"]["test"]["steps"][-1].update({"run":"python -m unittest -v > test-report.txt 2>&1"}),w["jobs"]["test"]["steps"].append({"if":"always()","uses":"actions/upload-artifact@v7","with":{"name":"diagnostics","path":"test-report.txt","if-no-files-found":"warn"}})))
    add("Scrivere un riepilogo nella pagina della run","Aggiungere Markdown a GITHUB_STEP_SUMMARY con testo controllato.",lambda w:w["jobs"]["test"]["steps"].append({"run":"printf '## Verifica\\nTest completati.\\n' >> \"$GITHUB_STEP_SUMMARY\""}))
    add("Riutilizzare la cache pip in CI","Legare la cache a un file dipendenze presente e installare esplicitamente i pacchetti.",lambda w:(w["jobs"]["test"]["steps"][1]["with"].update({"cache":"pip","cache-dependency-path":"requirements-dev.txt"}),w["jobs"]["test"]["steps"].insert(2,{"run":"python -m pip install -r requirements-dev.txt"})),{"requirements-dev.txt":"pytest==8.3.5\n"})
    add("Eseguire lint Ruff prima dei test","Installare un linter e verificarne soltanto gli errori Python bloccanti.",lambda w:w["jobs"]["test"]["steps"].insert(2,{"run":"python -m pip install ruff==0.11.13\npython -m ruff check --select E9,F63,F7,F82 app.py test_app.py"}))
    add("Costruire una wheel come verifica CI","Generare un pacchetto locale senza pubblicarlo in alcun registro.",lambda w:w["jobs"]["test"]["steps"].append({"run":"python -m pip install build==1.2.2\npython -m build --wheel"}),{"pyproject.toml":'[build-system]\nrequires=["setuptools>=75"]\nbuild-backend="setuptools.build_meta"\n[project]\nname="recipe-ci-example"\nversion="1.0.0"\n[tool.setuptools]\npy-modules=["app"]\n'})
    add("Trasferire un artefatto tra job","Usare upload e download con lo stesso nome e una dipendenza esplicita.",lambda w:(w["jobs"]["test"]["steps"].extend([{"run":"python --version > runtime.txt"},{"uses":"actions/upload-artifact@v7","with":{"name":"runtime","path":"runtime.txt"}}]),w["jobs"].update({"consume":{"needs":"test","runs-on":"ubuntu-latest","steps":[{"uses":"actions/download-artifact@v7","with":{"name":"runtime","path":"incoming"}},{"run":"cat incoming/runtime.txt"}]}})))
    add("Eseguire test dentro un job container","Selezionare un'immagine Linux per l'ambiente del job.",lambda w:w["jobs"]["test"].update({"container":"python:3.13-bookworm"}))
    add("Eseguire una fase finale indipendentemente dall'esito","Aggiungere un job needs con if always per il riepilogo di stato.",lambda w:w["jobs"].update({"finalize":{"needs":"test","if":"always()","runs-on":"ubuntu-latest","steps":[{"env":{"TEST_RESULT":"${{ needs.test.result }}"},"run":"printf 'Test: %s\\n' \"$TEST_RESULT\""}]}}))
    add("Usare un ambiente con approvazioni configurabili","Associare il job a un environment locale del repository senza effettuare deploy.",lambda w:w["jobs"]["test"].update({"environment":"review-demo"}))
    add("Eseguire checkout senza conservare credenziali Git","Impostare persist-credentials false e limitare fetch-depth allo snapshot necessario.",lambda w:w["jobs"]["test"]["steps"][0]["with"].update({"persist-credentials":False,"fetch-depth":1}))
    assert len(rows)==30,len(rows)
    return rows

def build_ci():
    book=Book("cicd","GitHub Actions; azioni ufficiali v7; Python 3.13",["https://docs.github.com/actions/writing-workflows/workflow-syntax-for-github-actions","https://github.com/actions/checkout","https://github.com/actions/setup-python","https://github.com/actions/upload-artifact"],"Repository GitHub con Actions disponibile. Nessun workflow è caricato o avviato automaticamente dall'app: i file sono configurazioni da revisionare e copiare. Runner aggiornati necessari per le azioni v7.",os=["Windows","Linux","macOS"],ide=["VS Code"])
    for title,description,data,extra in ci_variants():
        book.add(slug(title),title,description,{".github/workflows/ci.yml":json.dumps(data,ensure_ascii=False,indent=2)+"\n","app.py":PYTHON_APP,"test_app.py":UNIT,**extra},commands="python -m unittest -v",section="CI/CD",explanation=f"## Obiettivo\n{description}\n\n## Collocazione\nSalva app.py e test_app.py nella radice del progetto. Il workflow va in .github/workflows/ci.yml: il contenuto usa notazione JSON, che è un sottoinsieme valido di YAML. Esegui prima i test locali con il comando indicato.\n\n## Attivazione\nIl file non viene pubblicato dal ricettario. Dopo avere revisionato la configurazione e copiato nel proprio repository, usa l'evento indicato dal campo on. L'ambiente review-demo, dove presente, richiede di configurare le regole di approvazione nelle impostazioni GitHub: il solo nome non impone approvazioni.\n\n## Risultato\n{description} I tre test verificano zero, positivo e negativo. Il badge documentato non equivale a una run GitHub effettivamente riuscita.",expected=description,tags=["GitHub Actions","CI",slug(title)],errors=["Workflow non visibile: verificare che il file sia nel ramo appropriato e nella directory .github/workflows.","Action non compatibile con runner self-hosted vecchio: aggiornare il runner prima di usare v7."])
    save_book(book)

PACKAGE_ROWS=[]
def pack(title,description,files,commands,prereq):PACKAGE_ROWS.append((title,description,files,commands,prereq))

BASE_PYPROJECT='''[build-system]
requires = ["setuptools>=75", "wheel"]
build-backend = "setuptools.build_meta"
[project]
name = "recipe-package-demo"
version = "1.0.0"
requires-python = ">=3.12"
[tool.setuptools]
py-modules = ["app"]
'''
DOTNET='<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>\n'
PS_PREFIX="Set-StrictMode -Version Latest\n$ErrorActionPreference='Stop'\n"

def package_variants():
    if PACKAGE_ROWS:return PACKAGE_ROWS
    pack("Costruire una wheel Python","Produrre una distribuzione installabile con build backend dichiarato.",{"pyproject.toml":BASE_PYPROJECT,"app.py":PYTHON_APP},"python -m pip install build==1.2.2\npython -m build --wheel","Python 3.12+ e pip; backend scaricato da Internet durante la build isolata.")
    pack("Costruire una distribuzione sorgente Python","Creare uno sdist separato dalla wheel per conservare i sorgenti pubblicabili.",{"pyproject.toml":BASE_PYPROJECT,"app.py":PYTHON_APP},"python -m pip install build==1.2.2\npython -m build --sdist","Python 3.12+ e pip.")
    gui='''import sys
from PySide6.QtWidgets import QApplication,QLabel
if __name__=="__main__":
    app=QApplication(sys.argv)
    window=QLabel("Pacchetto PySide6")
    window.resize(400,160)
    window.show()
    sys.exit(app.exec())
'''
    pack("Distribuire PySide6 con pyside6-deploy e Nuitka","Usare lo strumento Qt e scegliere esplicitamente standalone.",{"main.py":gui,"requirements.txt":"PySide6==6.12.*\n","pyproject.toml":'[project]\nname="recipe-gui"\nversion="1.0.0"\n[tool.pyside6.deploy]\ntitle="RecipeGui"\ninput_file="main.py"\nmode="standalone"\n'},"py -3.13 -m venv .venv\n.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt\n.\\.venv\\Scripts\\pyside6-deploy.exe --init\n.\\.venv\\Scripts\\pyside6-deploy.exe --dry-run\n.\\.venv\\Scripts\\pyside6-deploy.exe --mode standalone","Python 3.13, PySide6 6.12; toolchain C/C++ richiesta da Nuitka e dumpbin nel terminale MSVC. Revisionare la specifica prima della compilazione.")
    pack("Creare un bundle directory con PyInstaller","Congelare una piccola CLI Python lasciando visibili le risorse del pacchetto.",{"app.py":PYTHON_APP},"python -m pip install pyinstaller==6.16.0\npython -m PyInstaller --clean --onedir --name RecipeCli app.py","Python 3.12/3.13 e PyInstaller 6.16.0. Costruire sul sistema di destinazione.")
    pack("Pubblicare una CLI .NET autonoma per Windows","Includere il runtime .NET nel publish scegliendo win-x64.",{"RecipeCli.csproj":DOTNET,"Program.cs":'Console.WriteLine("Applicazione autonoma");\n'},"dotnet publish -c Release -r win-x64 --self-contained true -o dist/win-x64",".NET 10 SDK, download runtime pack possibile durante restore.")
    pack("Pubblicare una CLI .NET dipendente dal runtime","Produrre un publish leggero richiedendo il runtime sul computer destinazione.",{"RecipeCli.csproj":DOTNET,"Program.cs":'Console.WriteLine("Applicazione dipendente dal runtime");\n'},"dotnet publish -c Release --self-contained false -o dist/framework-dependent",".NET 10 SDK; .NET 10 runtime sulla destinazione.")
    pack("Creare un publish .NET single-file","Abilitare PublishSingleFile per una CLI con runtime incluso.",{"RecipeCli.csproj":DOTNET,"Program.cs":'Console.WriteLine("Single-file .NET");\n'},"dotnet publish -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -o dist/single-file",".NET 10 SDK; alcune risorse/native library possono richiedere estrazione o restare esterne secondo le dipendenze.")
    electron_manifest={"name":"recipe-electron-package","version":"1.0.0","private":True,"main":"main.cjs","scripts":{"start":"electron .","package":"electron-builder --dir"},"devDependencies":{"electron":"45.1.0","electron-builder":"26.0.12"},"build":{"appId":"it.ricettario.demo","files":["main.cjs","index.html"]}}
    electron_main="const {app,BrowserWindow}=require('electron');app.whenReady().then(()=>{const win=new BrowserWindow({width:600,height:400,webPreferences:{contextIsolation:true,nodeIntegration:false,sandbox:true}});win.loadFile('index.html');});app.on('window-all-closed',()=>app.quit());\n"
    pack("Creare una cartella Electron distribuibile","Usare electron-builder --dir per revisionare il contenuto prima di creare installer.",{"package.json":json.dumps(electron_manifest,indent=2),"main.cjs":electron_main,"index.html":'<!doctype html><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'none\'"><h1>App locale</h1>\n'},"npm install\nnpm run package","Node.js 24, Electron 45.1.0 e electron-builder 26.0.12; download dei tool di packaging richiesto. Nessuna firma o pubblicazione automatica.")
    pack("Preparare un archivio ZIP portabile con PowerShell","Distinguere file applicativi e archivio di consegna in un'area temporanea.",{"package.ps1":PS_PREFIX+'$root=Join-Path ([IO.Path]::GetTempPath()) ("package-"+[guid]::NewGuid())\n$dist=Join-Path $root "dist"\nNew-Item -ItemType Directory -Path $dist | Out-Null\nSet-Content -LiteralPath (Join-Path $dist "README.txt") -Value "Pacchetto dimostrativo"\n$target=Join-Path $root "release.zip"\nCompress-Archive -Path (Join-Path $dist "*") -DestinationPath $target\nGet-Item -LiteralPath $target\n'},"pwsh -NoProfile -File .\\package.ps1","PowerShell 7.")
    pack("Generare un manifest SHA-256 dei file distribuiti","Ordinare i percorsi e serializzare digest e nomi relativi.",{"hashes.py":'''from pathlib import Path
import hashlib,json
root=Path("dist")
root.mkdir(exist_ok=True)
(root/"demo.txt").write_text("Pacchetto demo\\n",encoding="utf-8")
manifest={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob("*")) if p.is_file()}
Path("SHA256SUMS.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
print(Path("SHA256SUMS.json").resolve())
'''},"python hashes.py","Python 3.12+; esempio crea soltanto dist/demo.txt e il manifest nella cartella di lavoro.")
    pack("Verificare un pacchetto contro il manifest SHA-256","Rifiutare percorsi che escono dalla cartella e digest non corrispondenti.",{"verify.py":'''from pathlib import Path
import hashlib,json,sys
root=Path("dist").resolve()
manifest=json.loads(Path("SHA256SUMS.json").read_text(encoding="utf-8"))
failures=[]
for relative,expected in manifest.items():
    path=(root/relative).resolve()
    if not path.is_relative_to(root) or not path.is_file(): failures.append(relative);continue
    if hashlib.sha256(path.read_bytes()).hexdigest()!=expected: failures.append(relative)
print("OK" if not failures else f"File non validi: {failures}")
sys.exit(bool(failures))
''',"dist/demo.txt":"contenuto\n","SHA256SUMS.json":json.dumps({"demo.txt":__import__("hashlib").sha256(b"contenuto\n").hexdigest()},indent=2)},"python verify.py","Python 3.12+. Il manifest è un controllo d'integrità, non sostituisce una firma attendibile.")
    pack("Leggere la versione installata da importlib metadata","Mostrare la versione del pacchetto senza duplicarla in moduli differenti.",{"pyproject.toml":BASE_PYPROJECT,"app.py":'from importlib.metadata import version\nprint(version("recipe-package-demo"))\n'},"python -m pip install .\npython app.py","Ambiente virtuale Python dedicato.")
    resource_project='''[build-system]
requires=["setuptools>=75"]
build-backend="setuptools.build_meta"
[project]
name="recipe-resources"
version="1.0.0"
[tool.setuptools.package-data]
recipe_resources=["message.txt"]
'''
    pack("Includere e leggere risorse in una wheel","Usare importlib.resources invece di assumere il working directory.",{"pyproject.toml":resource_project,"recipe_resources/__init__.py":"","recipe_resources/message.txt":"Risorsa inclusa\n","read_resource.py":'from importlib.resources import files\nprint(files("recipe_resources").joinpath("message.txt").read_text(encoding="utf-8"))\n'},"python -m pip install .\npython read_resource.py","Ambiente virtuale Python 3.12+.")
    pack("Installare un comando console Python","Dichiarare project.scripts per un entry point indipendente dal percorso del sorgente.",{"pyproject.toml":BASE_PYPROJECT+'\n[project.scripts]\nrecipe-square="app:main"\n',"app.py":'def main():\n    print(7*7)\nif __name__=="__main__":main()\n'},"python -m pip install .\nrecipe-square","Ambiente virtuale Python attivo; la cartella Scripts/bin deve essere nel PATH.")
    pack("Conservare un inventario delle dipendenze installate","Usare pip freeze come fotografia dell'ambiente e non come promessa di lock multipiattaforma.",{"snapshot.ps1":PS_PREFIX+'python -m pip freeze --all | Set-Content -LiteralPath requirements-snapshot.txt -Encoding utf8\nGet-Content -LiteralPath requirements-snapshot.txt\n'},"pwsh -NoProfile -File .\\snapshot.ps1","Ambiente virtuale Python dedicato, PowerShell 7. Il risultato dipende dall'ambiente corrente.")
    pack("Preparare un avviso licenze per componenti distribuiti","Produrre un inventario leggibile a partire da metadati forniti e revisionabili.",{"licenses.py":'''import json
from pathlib import Path
items=json.loads(Path("third_party.json").read_text(encoding="utf-8"))
lines=["# Componenti di terze parti",""]
for item in items:
    lines.extend([f"## {item['name']} {item['version']}",f"Licenza dichiarata: {item['license']}",f"Fonte: {item['source']}",""])
Path("THIRD_PARTY_NOTICES.md").write_text("\\n".join(lines),encoding="utf-8")
''',"third_party.json":json.dumps([{"name":"Componente dimostrativo originale","version":"1.0.0","license":"MIT","source":"Sorgenti locali forniti nella ricetta"}],indent=2)},"python licenses.py","Python 3.12+. Sostituire l'inventario con componenti e testi licenza reali prima di distribuire; nessuna licenza viene inferita dal nome del pacchetto.")
    pack("Installare componenti CMake separatamente","Usare COMPONENT per distinguere binari runtime e header di sviluppo.",{"CMakeLists.txt":'''cmake_minimum_required(VERSION 3.24)
project(ComponentDemo LANGUAGES CXX)
add_executable(recipe main.cpp)
install(TARGETS recipe RUNTIME DESTINATION bin COMPONENT Runtime)
install(FILES api.hpp DESTINATION include COMPONENT Development)
''',"main.cpp":'int main(){return 0;}\n',"api.hpp":"#pragma once\nint demonstration();\n"},"cmake -S . -B build\ncmake --build build --config Release\ncmake --install build --config Release --prefix stage --component Runtime","CMake 3.24+, compilatore C++ nel terminale di sviluppo.")
    pack("Creare un archivio distribuibile con CPack","Produrre un ZIP dal layout install definito da CMake.",{"CMakeLists.txt":'''cmake_minimum_required(VERSION 3.24)
project(PackageDemo VERSION 1.0.0 LANGUAGES CXX)
add_executable(recipe main.cpp)
install(TARGETS recipe RUNTIME DESTINATION bin)
set(CPACK_GENERATOR ZIP)
set(CPACK_PACKAGE_VERSION ${PROJECT_VERSION})
include(CPack)
''',"main.cpp":'int main(){return 0;}\n'},"cmake -S . -B build\ncmake --build build --config Release\ncpack --config build/CPackConfig.cmake -C Release","CMake 3.24+ e compilatore C++.")
    pack("Compilare un installer locale Inno Setup","Installare soltanto nell'area utente senza richiedere privilegi amministrativi.",{"installer.iss":'''[Setup]
AppName=Recipe Demo
AppVersion=1.0.0
DefaultDirName={localappdata}\\Programs\\RecipeDemo
PrivilegesRequired=lowest
OutputDir=output
OutputBaseFilename=RecipeDemo-Setup
Compression=lzma2
SolidCompression=yes
[Files]
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion
''',"README.txt":"Installer dimostrativo: contiene soltanto questo testo.\n"},'& "${env:ProgramFiles(x86)}\\Inno Setup 6\\ISCC.exe" .\\installer.iss',"Windows, Inno Setup 6 installato nel percorso indicato. L'installer è non firmato; la ricetta non lo esegue.")
    pack("Verificare il contenuto di una wheel prima della consegna","Ispezionare l'archivio generato senza installarlo né eseguirlo.",{"pyproject.toml":BASE_PYPROJECT,"app.py":PYTHON_APP,"inspect_wheel.py":'''from pathlib import Path
from zipfile import ZipFile
paths=list(Path("dist").glob("*.whl"))
if len(paths)!=1:raise SystemExit("Attesa esattamente una wheel in dist")
with ZipFile(paths[0]) as archive:
    names=archive.namelist()
    assert "app.py" in names,"Modulo mancante"
    assert any(name.endswith(".dist-info/METADATA") for name in names),"Metadati mancanti"
    print("\\n".join(names))
'''},"python -m pip install build==1.2.2\npython -m build --wheel\npython inspect_wheel.py","Python 3.12+ e cartella dist inizialmente vuota.")
    assert len(PACKAGE_ROWS)==20,len(PACKAGE_ROWS)
    return PACKAGE_ROWS

def build_packaging():
    book=Book("packaging","Python 3.12/3.13; Qt 6.12; .NET 10; strumenti specificati per ricetta",["https://packaging.python.org/en/latest/tutorials/packaging-projects/","https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-deploy.html","https://learn.microsoft.com/dotnet/core/tools/dotnet-publish","https://www.electron.build/"],"Leggere i prerequisiti specifici nella guida. Creare una cartella nuova; i comandi compilano artefatti locali senza pubblicarli né firmarli.",os=["Windows"],ide=["VS Code","Visual Studio"])
    for title,description,files,commands,prereq in package_variants():
        book.add(slug(title),title,description,files,section="Distribuzione e packaging",commands=commands,explanation=f"## Scopo\n{description}\n\n## Prerequisiti\n{prereq}\n\n## Avvio\nSalva tutti i file esportati preservando i percorsi relativi. Esegui i comandi dalla directory che contiene il manifest o lo script principale. Usa un ambiente virtuale dedicato per non modificare le dipendenze di altri progetti.\n\n## Controllo dell'artefatto\n{description} Il successo del comando di build non attesta l'avvio su un computer pulito: avvia il risultato sulla destinazione prevista prima di consegnarlo. Questo esempio non pubblica pacchetti né firma eseguibili.",expected=description,tags=["packaging","release",slug(title)],errors=["Tool di compilazione mancante: installare la dipendenza specificata nei prerequisiti.","Rete non disponibile: i backend e i runtime non presenti non possono essere scaricati."])
    save_book(book)

def build_all():build_ci();build_packaging()
if __name__=="__main__":build_all()
