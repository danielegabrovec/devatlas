"""Replace fourteen elementary GUI examples with operational lifecycle guides.

Run after build_desktop_tools.py; only the fourteen explicit retired recipe
directories may be removed. Catalog quantities and capstone projects stay fixed.
"""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from catalog_support import Book, CATALOG, ROOT, STACKS
from desktop_tools_common import save_book
from desktop_managed import avalonia_files, maui_files, winui_files

RETIRED = {
    "pyside6": ["pyside6-label", "pyside6-button"],
    "pyqt6": ["pyqt6-label", "pyqt6-button"],
    "qt-cpp": ["qt-cpp-label", "qt-cpp-button"],
    "electron": ["electron-app-version", "electron-content-bounds"],
    "avalonia": ["avalonia-text", "avalonia-button"],
    "maui": ["maui-label", "maui-button"],
    "winui": ["winui-text", "winui-button"],
}
NAME={"name":"project_name","label":"Nome dell'applicazione","type":"identifier","default":"RecipeDesktop","required":True}
QT_PATH={"name":"qt_dir","label":"Cartella Qt MSVC x64","type":"path","default":"C:/Qt/6.12.0/msvc2022_64","required":True}

def pretty(value):return json.dumps(value,ensure_ascii=False,indent=2)+"\n"

def launch(config):return pretty({"version":"0.2.0","configurations":[config]})

def tasks(command,args,label="Build Debug"):
    return pretty({"version":"2.0.0","tasks":[{"label":label,"type":"process","command":command,"args":args,"options":{"cwd":"${workspaceFolder}"},"problemMatcher":[]}]})

PLUGIN_SETUP='''def configure_plugins():
    package = Path(BINDING.__file__).resolve().parent
    for relative in ("plugins", "Qt6/plugins", "qt-plugins", "Qt/plugins"):
        candidate = package / relative
        if (candidate / "platforms").is_dir():
            QCoreApplication.setLibraryPaths([str(candidate)])
            return
'''

def qt_python_files(binding,debug=False):
    version="6.12" if binding=="PySide6" else "6.11"
    prelude=f'''import sys
from pathlib import Path
import {binding}
from {binding}.QtCore import QCoreApplication
from {binding}.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
'''+PLUGIN_SETUP.replace("BINDING",binding)+"\n"
    if not debug:
        source=prelude+'''if __name__ == "__main__":
    configure_plugins()
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("{{project_name}}")
    layout = QVBoxLayout(window)
    label = QLabel("0")
    button = QPushButton("Incrementa")
    window.count = 0
    def increment():
        window.count += 1
        label.setText(str(window.count))
    button.clicked.connect(increment)
    layout.addWidget(label)
    layout.addWidget(button)
    window.resize(480, 240)
    window.show()
    sys.exit(app.exec())
'''
        return {"main.py":source,"requirements.txt":f"{binding}=={version}.*\n"}
    source=prelude+'''from ui_main import Ui_MainForm
from totals import total

if __name__ == "__main__":
    configure_plugins()
    app = QApplication(sys.argv)
    window = QWidget()
    ui = Ui_MainForm()
    ui.setupUi(window)
    window.setWindowTitle("{{project_name}}")
    def calculate():
        value = total([12.50, 7.25])
        ui.resultLabel.setText(f"Totale: {value:.2f}")
    ui.calcButton.clicked.connect(calculate)
    window.resize(480, 240)
    window.show()
    sys.exit(app.exec())
'''
    # This original implementation is supplied so the export is runnable before
    # regeneration. The .ui compiler may replace it with equivalent generated code.
    form=f'''from {binding}.QtWidgets import QVBoxLayout, QLabel, QPushButton
class Ui_MainForm:
    def setupUi(self, form):
        form.setObjectName("MainForm")
        layout = QVBoxLayout(form)
        self.resultLabel = QLabel("Premi Calcola", form)
        self.resultLabel.setObjectName("resultLabel")
        self.calcButton = QPushButton("Calcola", form)
        self.calcButton.setObjectName("calcButton")
        layout.addWidget(self.resultLabel)
        layout.addWidget(self.calcButton)
'''
    ui='''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0"><class>MainForm</class><widget class="QWidget" name="MainForm"><layout class="QVBoxLayout" name="verticalLayout"><item><widget class="QLabel" name="resultLabel"><property name="text"><string>Premi Calcola</string></property></widget></item><item><widget class="QPushButton" name="calcButton"><property name="text"><string>Calcola</string></property></widget></item></layout></widget><resources/><connections/></ui>
'''
    data={"main.py":source,"ui_main.py":form,"form.ui":ui,"totals.py":'''def total(prices):
    subtotal = sum(prices)
    return round(subtotal, 2)
''',"requirements.txt":f"{binding}=={version}.*\n",".vscode/launch.json":launch({"name":f"Debug {binding}","type":"debugpy","request":"launch","program":"${workspaceFolder}/main.py","python":"${workspaceFolder}/.venv/Scripts/python.exe","cwd":"${workspaceFolder}","console":"integratedTerminal","justMyCode":True})}
    if binding=="PySide6":
        data["pyproject.toml"]='''[project]
name = "recipe-pyside-lifecycle"
version = "1.0.0"
[tool.pyside6.deploy]
title = "{{project_name}}"
input_file = "main.py"
mode = "standalone"
'''
    else:
        data["requirements-build.txt"]="PyInstaller==6.16.0\n"
    return data


def add_python_qt(book,binding):
    commands=r'''py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -c "import sys; print(sys.executable)"
.\.venv\Scripts\python.exe main.py'''
    book.add("inizializzazione-ambiente","Inizializzare ambiente e prima finestra "+binding,"Preparare un ambiente Python separato, installare il binding corretto e avviare un contatore Qt completo.",qt_python_files(binding),section="Inizializzazione",commands=commands,parameters=[NAME],tags=[binding,"initialize","venv","install","Qt platform plugins"],expected="Una finestra {{project_name}} mostra zero; ogni clic su Incrementa aumenta il valore.",errors=["ModuleNotFoundError: usare l'interprete .venv stampato dal comando diagnostico.","Qt platform plugin windows non trovato: controllare che il binding abbia la propria cartella plugins/platforms; il sorgente configura il percorso dal modulo installato."],explanation=f'''## Preparare l'ambiente
Installa Python 3.13 x64. Esporta i due file in una cartella nuova, apri PowerShell in quella cartella ed esegui i comandi nell'ordine mostrato. L'ambiente .venv contiene soltanto {binding}; usa sempre il suo python.exe anche per pip. La configurazione dei plugin è ricavata dalla posizione reale del pacchetto, quindi non dipende dall'interpretazione del percorso della cartella.

## Capire il primo avvio
main.py crea una sola QApplication, collega clicked prima di app.exec() e conserva il contatore sulla finestra. La chiusura della finestra termina il ciclo eventi. Il nome {{project_name}} si può personalizzare nel ricettario.

## Controllare il risultato
Avvia main.py, premi Incrementa tre volte e verifica il numero 3. Chiudi e riapri: il contatore torna a zero, perché questa prima app non salva dati. L'installazione richiede Internet; l'app in esecuzione non ne ha bisogno. Questa procedura riguarda Windows e non attesta prove Linux o macOS.''')
    if binding=="PySide6":
        compiler="pyside6-uic.exe";deploy=r'''.\.venv\Scripts\pyside6-deploy.exe main.py --init
.\.venv\Scripts\pyside6-deploy.exe --dry-run --mode standalone
.\.venv\Scripts\pyside6-deploy.exe --mode standalone'''
        distribution="Apri il terminale MSVC x64 con dumpbin disponibile prima di creare il pacchetto Nuitka. La specifica generata da pyside6-deploy va conservata insieme ai sorgenti. Distribuisci l'intera cartella standalone e verifica che il plugin platforms/qwindows.dll sia presente; provare soltanto sul PC con Qt installato non dimostra la completezza del pacchetto."
    else:
        compiler="pyuic6.exe";deploy=r'''.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\python.exe -m PyInstaller --clean --onedir --windowed --name {{project_name}} --exclude-module PySide6 main.py'''
        distribution="Il congelamento usa PyInstaller nello stesso ambiente di PyQt6. L'esclusione di PySide6 evita di trascinare un secondo binding accidentalmente disponibile. Distribuisci tutta dist/{{project_name}}, compresi i plugin Qt raccolti dagli hook. Se l'eseguibile non parte, ricostruisci temporaneamente senza --windowed per leggere il messaggio nel terminale."
    debug_commands=commands.split('\n')[:2]+[f'.\\.venv\\Scripts\\{compiler} form.ui -o ui_main.py','.\\.venv\\Scripts\\python.exe main.py']
    book.add("debug-build-distribuzione","Debug, form Designer e distribuzione "+binding,"Seguire lo slot di un pulsante nel debugger, rigenerare il form dal file UI e preparare il bundle del binding scelto.",qt_python_files(binding,True),section="Debug",commands=[{"shell":"PowerShell","os":"Windows","cwd":".","label":"Ambiente e generazione form","code":"\n".join(debug_commands)},{"shell":"PowerShell","os":"Windows","cwd":".","label":"Build distribuibile","code":deploy}],parameters=[NAME],tags=[binding,"debugpy","Designer","uic","build","deployment","breakpoint"],expected="Il pulsante Calcola mostra Totale: 19.75; il debugger si ferma in totals.py e il bundle include il solo binding scelto.",errors=["No module named ui_main: eseguire il compilatore UI dalla cartella con form.ui; una implementazione originale equivalente è già fornita.","Il breakpoint non viene raggiunto: selezionare .venv come interprete e premere Calcola dopo F5."],explanation=f'''## File e generazione dell'interfaccia
Esporta tutti i file mantenendo .vscode. form.ui descrive resultLabel e calcButton; ui_main.py contiene una implementazione originale pronta all'uso degli stessi controlli. Il comando {compiler} rigenera quella classe dal form. Se modifichi la UI, ripeti la generazione prima di fare debug o build. Il codice applicativo è in main.py e totals.py, separato dal file rigenerabile.

## Debug dello slot
Installa in VS Code le estensioni Python e Python Debugger. Apri la cartella, seleziona .venv/Scripts/python.exe e la configurazione Debug {binding}. Metti un breakpoint sulla riga `subtotal = sum(prices)` di totals.py, premi F5 e poi Calcola. Controlla prices, avanza una riga e verifica subtotal=19.75. Non mettere il breakpoint nel file UI destinato alla rigenerazione.

## Build e consegna
{distribution}

## Verifica da eseguire
Avvia il risultato su Windows della stessa architettura, senza usare la .venv di sviluppo, e prova il pulsante. Questa guida fornisce sorgenti e configurazioni; non dichiara eseguite le build Nuitka/PyInstaller né la prova su una macchina pulita.''')


CPP_MAIN='''#include <QApplication>
#include <QWidget>
#include <QVBoxLayout>
#include <QLabel>
#include <QPushButton>
int main(int argc,char **argv){
 QApplication app(argc,argv); QWidget window; window.setWindowTitle("{{project_name}}");
 auto *layout=new QVBoxLayout(&window); auto *label=new QLabel("0"); auto *button=new QPushButton("Incrementa");
 layout->addWidget(label);layout->addWidget(button);
 QObject::connect(button,&QPushButton::clicked,label,[label,count=0]() mutable {label->setText(QString::number(++count));});
 window.resize(480,240);window.show();return app.exec();
}
'''
CPP_CMAKE='''cmake_minimum_required(VERSION 3.24)
project({{project_name}} LANGUAGES CXX)
find_package(Qt6 6.10 REQUIRED COMPONENTS Widgets)
qt_standard_project_setup()
qt_add_executable({{project_name}} main.cpp)
target_compile_features({{project_name}} PRIVATE cxx_std_17)
target_link_libraries({{project_name}} PRIVATE Qt6::Widgets)
'''

def add_cpp(book):
    configure=r'''$qtPrefix = {{qt_dir|powershell}}
cmake -S . -B build/debug -G Ninja -DCMAKE_BUILD_TYPE=Debug "-DCMAKE_PREFIX_PATH=$qtPrefix"
cmake --build build/debug
& "$qtPrefix/bin/windeployqt.exe" --debug .\build\debug\{{project_name}}.exe
.\build\debug\{{project_name}}.exe'''
    book.add("inizializzazione-ambiente","Inizializzare Qt C++ con MSVC e CMake","Selezionare un kit Qt compatibile con il compilatore e avviare una finestra Widgets da un progetto CMake completo.",{"main.cpp":CPP_MAIN,"CMakeLists.txt":CPP_CMAKE},section="Inizializzazione",parameters=[NAME,QT_PATH],commands=configure,tags=["Qt6","C++","MSVC","CMake","initialize","windeployqt"],expected="CMake trova Qt Widgets, costruisce {{project_name}} e apre una finestra il cui contatore aumenta al clic.",errors=["Qt6Config.cmake non trovato: indicare qt_dir alla directory del kit, non alla cartella bin.","LNK2019 o architettura incompatibile: usare un kit Qt MSVC x64 e Developer PowerShell x64 coerenti; MinGW richiede una configurazione diversa."],explanation='''## Installare e scegliere il kit
Installa Visual Studio Build Tools con compilatore MSVC x64 e Windows SDK. Nel Qt Online Installer scegli Qt 6.12 desktop MSVC 2022 64-bit, CMake e Ninja. Apri Developer PowerShell x64 per rendere disponibili cl e il linker. Il parametro qt_dir deve indicare la directory del kit installato; il valore iniziale è soltanto un percorso comune.

## Configurare e avviare
Esporta main.cpp e CMakeLists.txt nella stessa cartella ed esegui i comandi dalla sua radice. La directory build/debug conserva cache e output separati dai sorgenti. windeployqt raccoglie accanto all'eseguibile le librerie Qt e il plugin della piattaforma per questo avvio Debug.

## Controllo e diagnosi
Verifica il compilatore scelto nel log iniziale di CMake e il riferimento Qt6_DIR in build/debug/CMakeCache.txt. La finestra deve mostrare un contatore funzionante. Se cambi compilatore o architettura, usa una directory di build nuova invece di riutilizzare la vecchia cache. La ricetta riguarda Windows/MSVC; non dichiara test MinGW o Linux.''')
    debug_main=CPP_MAIN.replace('#include <QApplication>','#include "totals.hpp"\n#include <QApplication>').replace('auto *label=new QLabel("0")','auto *label=new QLabel("Premi Calcola")').replace('new QPushButton("Incrementa")','new QPushButton("Calcola")').replace('[label,count=0]() mutable {label->setText(QString::number(++count));}','[label]{label->setText(QString::number(total({12.50,7.25}),\'f\',2));}')
    files={"main.cpp":debug_main,"totals.hpp":"#pragma once\n#include <QList>\ndouble total(const QList<double>& prices);\n","totals.cpp":'''#include "totals.hpp"
double total(const QList<double>& prices){
 double subtotal=0;
 for(double price:prices) subtotal+=price;
 return subtotal;
}
''',"CMakeLists.txt":CPP_CMAKE.replace("main.cpp)","main.cpp totals.cpp totals.hpp)"),".vscode/tasks.json":tasks("cmake",["--build","${workspaceFolder}/build/debug"]),".vscode/launch.json":launch({"name":"Qt C++ MSVC Debug","type":"cppvsdbg","request":"launch","program":"${workspaceFolder}/build/debug/{{project_name}}.exe","cwd":"${workspaceFolder}","preLaunchTask":"Build Debug","stopAtEntry":False,"externalConsole":False})}
    release=r'''$qtPrefix = {{qt_dir|powershell}}
cmake -S . -B build/release -G Ninja -DCMAKE_BUILD_TYPE=Release "-DCMAKE_PREFIX_PATH=$qtPrefix"
cmake --build build/release
New-Item -ItemType Directory -Path dist -Force | Out-Null
Copy-Item -LiteralPath .\build\release\{{project_name}}.exe -Destination .\dist\{{project_name}}.exe
& "$qtPrefix/bin/windeployqt.exe" --release --no-compiler-runtime .\dist\{{project_name}}.exe'''
    book.add("debug-build-distribuzione","Debug MSVC e distribuzione Qt C++ Release","Fermarsi nel calcolo richiamato dal pulsante e raccogliere le dipendenze Qt del binario Release.",files,section="Debug",parameters=[NAME,QT_PATH],commands=[{"shell":"PowerShell","os":"Windows","cwd":".","label":"Configura e prepara Debug","code":configure},{"shell":"PowerShell","os":"Windows","cwd":".","label":"Prepara la cartella Release","code":release}],tags=["Qt6","cppvsdbg","MSVC","PDB","Release","windeployqt"],expected="Il breakpoint in totals.cpp osserva il totale 19.75; dist contiene il binario Release con le librerie e i plugin Qt raccolti.",errors=["Breakpoint vuoto: verificare build Debug, simboli PDB e programma selezionato in launch.json.","DLL del compilatore mancante sul PC finale: installare il Microsoft Visual C++ Redistributable x64 ufficiale; la raccolta usa --no-compiler-runtime."],explanation='''## Debug del programma esatto
I file forniti costruiscono una finestra con pulsante Calcola e una funzione total separata. Prepara build/debug con il primo gruppo di comandi. In VS Code installa l'estensione C/C++, apri totals.cpp e metti un breakpoint nel ciclo che somma price. Seleziona Qt C++ MSVC Debug e premi F5. Premi Calcola: osserva prices, subtotal e il call stack dello slot.

## Build Release
Il secondo gruppo usa una directory distinta build/release: non mescola DLL Debug e Release. L'eseguibile viene copiato in dist e windeployqt raccoglie soltanto le dipendenze del runtime Qt richieste dal programma. Distribuisci tutta dist, inclusa la directory platforms. Il runtime del compilatore viene fornito con il redistributable Microsoft ufficiale, predisposto separatamente.

## Accettazione
Su un Windows x64 pulito avvia dist/{{project_name}}.exe e verifica il totale. Compilazione, raccolta DLL e prova sulla destinazione sono passaggi da eseguire: il catalogo non li dichiara già riusciti.''')


ELECTRON_HTML='''<!doctype html><html lang="it"><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'"><title>{{project_name}}</title></head><body><h1>{{project_name}}</h1><button id="calculate">Calcola</button><p id="result">0</p><script src="renderer.js"></script></body></html>
'''
ELECTRON_MAIN='''const {app,BrowserWindow,ipcMain}=require('electron');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
let window;
function createWindow(){
 window=new BrowserWindow({width:720,height:480,webPreferences:{contextIsolation:true,nodeIntegration:false,sandbox:true,PRELOAD}});
 window.webContents.setWindowOpenHandler(()=>({action:'deny'}));
 window.webContents.on('will-navigate',event=>event.preventDefault());
 return window.loadFile('index.html');
}
app.whenReady().then(async()=>{HANDLERS await createWindow();});
app.on('window-all-closed',()=>app.quit());
'''

def add_electron(book):
    manifest={"name":"recipe-electron-lifecycle","version":"1.0.0","private":True,"main":"main.cjs","scripts":{"start":"electron ."},"devDependencies":{"electron":"45.1.0"}}
    minimum={"package.json":pretty(manifest),"main.cjs":ELECTRON_MAIN.replace(",PRELOAD","").replace("HANDLERS", ""),"index.html":ELECTRON_HTML.replace("Calcola","Incrementa"),"renderer.js":"let count=0;document.querySelector('#calculate').addEventListener('click',()=>{document.querySelector('#result').textContent=String(++count);});\n"}
    book.add("inizializzazione-ambiente","Inizializzare Electron con renderer isolato","Preparare Node/npm, installare il runtime Electron dichiarato e avviare una prima finestra senza accesso Node nel renderer.",minimum,section="Inizializzazione",parameters=[NAME],commands="node --version\nnpm --version\nnpm install\nnpm start",tags=["Electron","npm","initialize","main process","renderer","contextIsolation"],expected="La finestra {{project_name}} apre un contatore locale; il renderer usa soltanto API DOM.",errors=["electron non trovato: eseguire npm install dalla cartella con package.json e usare npm start.","Download Electron interrotto: controllare la connettività e il log di installazione prima di riprovare."],explanation='''## Ambiente e manifest
Installa Node.js 24 LTS con npm, esporta i quattro file in una cartella e apri lì PowerShell. package.json definisce l'entry point main.cjs e blocca Electron alla versione 45.1.0. npm install crea package-lock.json: conservalo e usa npm ci nelle installazioni successive dello stesso progetto.

## Primi processi
main.cjs crea la BrowserWindow dopo app.whenReady. index.html carica un renderer separato; contextIsolation e sandbox restano attivi e nodeIntegration è disabilitato. Per questo contatore basta il DOM: non occorre esporre API native né installare un server web.

## Verifica
Premi Incrementa e osserva il contatore. Chiudendo la finestra termina questa app Windows dimostrativa. Non è una build del framework Electron da sorgenti: il manifest scarica il runtime precompilato della versione indicata. Non vengono attestati avvii macOS o Linux.''')
    manifest["scripts"].update(debug="electron --inspect-brk=9229 .",package="electron-builder --dir --win --x64")
    manifest["devDependencies"]["electron-builder"]="26.0.12"
    manifest["build"]={"appId":"it.ricettario.lifecycle","productName":"{{project_name}}","files":["main.cjs","preload.cjs","renderer.js","totals.cjs","index.html"]}
    handler="""const {total}=require('./totals.cjs');ipcMain.handle('invoice:total',event=>{if(event.senderFrame?.url!==pathToFileURL(path.join(__dirname,'index.html')).href) throw new Error('Origine IPC non consentita');return total([12.50,7.25]);});"""
    files={"package.json":pretty(manifest),"main.cjs":ELECTRON_MAIN.replace("PRELOAD","preload:path.join(__dirname,'preload.cjs')").replace("HANDLERS",handler),"index.html":ELECTRON_HTML,"preload.cjs":"const {contextBridge,ipcRenderer}=require('electron');contextBridge.exposeInMainWorld('invoice',{total:()=>ipcRenderer.invoke('invoice:total')});\n","renderer.js":"document.querySelector('#calculate').addEventListener('click',async()=>{try{document.querySelector('#result').textContent=String(await window.invoice.total());}catch(error){document.querySelector('#result').textContent=error.message;}});\n","totals.cjs":"function total(prices){const subtotal=prices.reduce((sum,price)=>sum+price,0);return Math.round(subtotal*100)/100;}\nmodule.exports={total};\n",".vscode/launch.json":launch({"name":"Debug Electron main","type":"node","request":"launch","cwd":"${workspaceFolder}","runtimeExecutable":"${workspaceFolder}/node_modules/.bin/electron","windows":{"runtimeExecutable":"${workspaceFolder}/node_modules/.bin/electron.cmd"},"args":["."],"outputCapture":"std"})}
    book.add("debug-build-distribuzione","Debug IPC e distribuzione Electron per Windows","Seguire una richiesta renderer-preload-main e preparare una cartella distribuibile con il runtime Electron.",files,section="Debug",parameters=[NAME],commands="npm install\nnpm start\nnpm run package",tags=["Electron","debug","IPC","preload","electron-builder","win-unpacked"],expected="Il debugger si ferma in totals.cjs su richiesta del renderer; il pulsante mostra 19.75 e la cartella win-unpacked contiene l'app distribuibile.",errors=["Il breakpoint nel main non si ferma: avviare la configurazione Node/Electron fornita, non un debugger del solo browser.","API invoice assente: controllare preload.cjs, nome esposto dal contextBridge e messaggi di DevTools; non abilitare nodeIntegration per aggirare l'errore."],explanation='''## Debug dei due lati IPC
Installa le dipendenze dalla cartella esportata. In VS Code usa Debug Electron main e imposta un breakpoint nel corpo di total in totals.cjs. Premi F5, poi Calcola nella finestra. Il percorso è renderer.js → API invoice del preload → handler invoice:total del main → totals.cjs. Il canale è fisso e il main verifica il frame chiamante. Per il renderer puoi aprire gli strumenti Chromium durante lo sviluppo; il debugger Node controlla invece il main.

## Build dell'app
npm run package crea una directory Windows x64 tramite electron-builder --dir. Non crea né pubblica un installer e non firma eseguibili. Distribuisci l'intera cartella win-unpacked generata sotto dist, non il solo file EXE: Chromium, Node, risorse e licenze fanno parte dell'app. Il manifest include esplicitamente il modulo totals.cjs richiamato dall'handler.

## Controllo finale
Avvia la cartella su un altro Windows x64 e premi Calcola: il risultato deve essere 19.75. L'esito di packaging e prova su macchina pulita non è attestato dal catalogo.''')


def managed_sources(stack,debug=False):
    if stack=="avalonia":
        label='new TextBlock{Text="0"}';button='new Button{Content="Incrementa"}';event="Click";settext='label.Text=(++count).ToString()';body=f'int count=0;var label={label};var button={button};button.{event}+=(_,_)=>{{{settext};}};panel.Children.Add(label);panel.Children.Add(button);'
        files=avalonia_files(body)
    elif stack=="maui":
        body='int count=0;var label=new Label{Text="0"};var button=new Button{Text="Incrementa"};button.Clicked+=(_,_)=>label.Text=(++count).ToString();panel.Children.Add(label);panel.Children.Add(button);'
        files=maui_files(body)
    else:
        body='int count=0;var label=new TextBlock{Text="0"};var button=new Button{Content="Incrementa"};button.Click+=(_,_)=>label.Text=(++count).ToString();panel.Children.Add(label);panel.Children.Add(button);'
        files=winui_files(body)
    project=files.pop("RecipeApp.csproj")
    if stack=="maui":
        project=project.replace("</PropertyGroup>","<UseRidGraph>true</UseRidGraph><RuntimeIdentifier>win10-x64</RuntimeIdentifier></PropertyGroup>",1)
        project=project.replace("</Project>",'''<PropertyGroup Condition="$([MSBuild]::GetTargetPlatformIdentifier('$(TargetFramework)')) == 'windows' and '$(RuntimeIdentifierOverride)' != ''"><RuntimeIdentifier>$(RuntimeIdentifierOverride)</RuntimeIdentifier></PropertyGroup></Project>''')
    files["{{project_name}}.csproj"]=project
    if debug:
        path="Program.cs" if stack=="avalonia" else "MainPage.cs" if stack=="maui" else "MainWindow.cs"
        contents=files[path].replace("int count=0;","").replace('(\'dummy\')','')
        contents=contents.replace('Text="0"','Text="Premi Calcola"').replace('Content="Incrementa"','Content="Calcola"').replace('Text="Incrementa"','Text="Calcola"')
        contents=contents.replace('label.Text=(++count).ToString()','label.Text=Invoice.Total(new decimal[]{12.50m,7.25m}).ToString("F2",System.Globalization.CultureInfo.InvariantCulture)')
        files[path]=contents
        files["Invoice.cs"]='''using System.Collections.Generic;
using System.Linq;
namespace RecipeApp;
public static class Invoice {
 public static decimal Total(IEnumerable<decimal> prices){
  decimal subtotal=prices.Sum();
  return decimal.Round(subtotal,2);
 }
}
'''
        if stack=="avalonia":framework="net8.0";rid=None;program="${workspaceFolder}/bin/Debug/net8.0/{{project_name}}.dll"
        elif stack=="maui":framework="net10.0-windows10.0.19041.0";rid="win10-x64";program="${workspaceFolder}/bin/Debug/"+framework+"/win10-x64/{{project_name}}.exe"
        else:framework="net8.0-windows10.0.19041.0";rid="win-x64";program="${workspaceFolder}/bin/Debug/"+framework+"/win-x64/{{project_name}}.exe"
        args=["build","{{project_name}}.csproj","-c","Debug","-f",framework]
        if rid:args.extend(["-r",rid])
        files[".vscode/tasks.json"]=tasks("dotnet",args)
        files[".vscode/launch.json"]=launch({"name":f"Debug {stack} C#","type":"coreclr","request":"launch","program":program,"cwd":"${workspaceFolder}","preLaunchTask":"Build Debug","stopAtEntry":False})
    return files


def add_managed(book,stack):
    labels={"avalonia":"Avalonia","maui":".NET MAUI Windows","winui":"WinUI 3"}
    label=labels[stack]
    if stack=="avalonia":
        commands="dotnet --list-sdks\ndotnet restore {{project_name}}.csproj\ndotnet run --project {{project_name}}.csproj"
        setup="Installa .NET 8 SDK x64. I file forniti inizializzano Avalonia 11.3.0 con FluentTheme e lifetime desktop; non richiedono template aggiuntivi. NuGet ripristina Avalonia.Desktop e Avalonia.Themes.Fluent dalla versione dichiarata nel progetto. Questa è una baseline 11.3 esplicita, non una promessa di usare l'ultima versione disponibile."
        deploy="dotnet publish {{project_name}}.csproj -c Release -r win-x64 --self-contained true -p:PublishSingleFile=false -o dist/win-x64"
        binding="Il runtime di rendering Avalonia e le sue librerie native arrivano dai pacchetti desktop. Conserva tutta la directory di publish: estrarre soltanto la DLL gestita non produce una distribuzione autonoma."
    elif stack=="maui":
        commands="dotnet --info\ndotnet workload list\ndotnet workload install maui-windows\ndotnet restore {{project_name}}.csproj\ndotnet run --project {{project_name}}.csproj -f net10.0-windows10.0.19041.0"
        setup="Predisponi Windows 10 build 19041 o successivo, .NET 10 SDK e Windows SDK tramite Visual Studio 2026 con workload .NET MAUI. Il comando workload install riguarda il medesimo SDK selezionato dal terminale; se l'installazione è gestita da Visual Studio, mantienila coerente con Visual Studio Installer. L'esempio contiene soltanto il target Windows, i file Platforms/Windows e Microsoft.Maui.Controls 10.0.31: Android, iOS e MacCatalyst non vengono costruiti."
        deploy="dotnet publish {{project_name}}.csproj -f net10.0-windows10.0.19041.0 -c Release -p:RuntimeIdentifierOverride=win10-x64 -p:WindowsPackageType=None -p:WindowsAppSDKSelfContained=true --self-contained true -o dist/windows-x64"
        binding="La proprietà RuntimeIdentifierOverride viene trasferita a RuntimeIdentifier dal gruppo MSBuild fornito, secondo la procedura MAUI per pubblicazione Windows unpackaged. UseRidGraph abilita il RID Windows versionato usato dalla guida. WindowsPackageType=None sceglie una cartella, mentre WindowsAppSDKSelfContained include le dipendenze Windows App SDK."
    else:
        commands="dotnet --list-sdks\ndotnet restore {{project_name}}.csproj\ndotnet build {{project_name}}.csproj -p:Platform=x64\ndotnet run --project {{project_name}}.csproj -p:Platform=x64"
        setup="Predisponi Windows 10 build 19041 o successivo, .NET 8 SDK, Windows SDK e workload WinUI in Visual Studio. Il progetto usa una baseline dichiarata Windows App SDK 1.8.12 (pacchetto 1.8.260921001), destinazione win-x64 e WindowsPackageType=None. App.xaml crea le risorse WinUI; App.xaml.cs conserva la finestra e la attiva in OnLaunched. Non confondere questa app desktop con UWP o con un progetto WPF."
        deploy="dotnet publish {{project_name}}.csproj -c Release -r win-x64 --self-contained true -p:WindowsPackageType=None -p:WindowsAppSDKSelfContained=true -o dist/windows-x64"
        binding="L'esempio usa WinUI 3 e Windows App SDK in modalità unpackaged. Il manifest .csproj rende espliciti architettura e dipendenze del runtime; WindowsAppSDKSelfContained riguarda Windows App SDK, mentre --self-contained riguarda .NET. Conserva i file native DLL e resources.pri generati nel publish."
    book.add("inizializzazione-ambiente","Inizializzare ambiente e prima app "+label,"Preparare SDK e dipendenze del framework e avviare un contatore desktop con tutti i file di ingresso.",managed_sources(stack),section="Inizializzazione",parameters=[NAME],commands=commands,tags=[label,"initialize","SDK","restore","first app"],expected="La prima app apre una finestra e il pulsante Incrementa aggiorna il contatore.",errors=["SDK o workload non trovato: confrontare dotnet --info e il workload richiesto con la versione del progetto.","Classe App duplicata: esportare in una cartella nuova mantenendo tutti i file, senza sovrapporli a un template già generato."],explanation=f'''## SDK e dipendenze
{setup}

## File da mantenere
Esporta tutti i file conservando le directory. Il nome del .csproj diventa {{project_name}}.csproj, mentre il namespace interno RecipeApp resta coerente fra i sorgenti e gli eventuali file XAML. Avvia i comandi nella cartella che contiene quel progetto.

## Primo avvio
Il costruttore della finestra o pagina costruisce due controlli e collega il clic a una variabile di sessione. Premi tre volte Incrementa: deve apparire 3. Il restore iniziale richiede Internet; l'app minima non usa servizi esterni.

## Compatibilità
La procedura è specifica Windows x64 e per le versioni dichiarate. Non attesta una build o un'esecuzione su altri sistemi e non richiede emulatori mobili.''')
    debug_setup=commands.replace("dotnet workload install maui-windows\n","")
    book.add("debug-build-distribuzione","Debug e pubblicazione desktop "+label,"Osservare nel debugger il calcolo richiamato dalla UI e pubblicare una cartella Windows x64 con i runtime necessari.",managed_sources(stack,True),section="Debug",parameters=[NAME],commands=[{"shell":"PowerShell","os":"Windows","cwd":".","label":"Restore e avvio locale","code":debug_setup},{"shell":"PowerShell","os":"Windows","cwd":".","label":"Pubblicazione in cartella","code":deploy}],tags=[label,"debug","coreclr","breakpoint","publish","self-contained","Windows"],expected="Il pulsante Calcola mostra 19.75; il debugger raggiunge Invoice.Total e il publish prepara una cartella x64 completa.",errors=["Breakpoint vuoto: usare Debug, il percorso program corrispondente al framework/RID e l'estensione C# di VS Code.","App presente solo sulla macchina di sviluppo: controllare le opzioni self-contained e consegnare tutta la directory publish."],explanation=f'''## Debug della funzione richiamata dalla UI
La ricetta include l'intero progetto: il pulsante Calcola richiama Invoice.Total in Invoice.cs. Prima predisponi SDK e workload indicati dalla guida di inizializzazione. In VS Code installa l'estensione C#, apri la cartella e seleziona Debug {stack} C#. La task Build Debug usa il framework e il RID esatti del progetto. Metti un breakpoint sulla riga `decimal subtotal=prices.Sum();`, premi F5 e poi Calcola; controlla prices e subtotal nel debugger. Per gli strumenti XAML e il debug misto nativo/gestito puoi aprire lo stesso .csproj in Visual Studio e usare F5.

## Publish specifico del framework
{binding}

Esegui il comando di pubblicazione dalla radice dei sorgenti. La destinazione è una directory distinta dalla build Debug. Non viene creata né registrata una app MSIX e non vengono usati certificati di firma.

## Controllo da completare
Avvia il risultato su Windows x64 e prova il totale 19.75. La presenza di una configurazione debugger e di un comando publish non equivale a una compilazione riuscita: questa guida dichiara soltanto le verifiche statiche riportate nel catalogo.''')


def compile_guides():
    from copy import deepcopy
    names={"pyside6":"PySide6","pyqt6":"PyQt6"}
    sources={"pyside6":["https://doc.qt.io/qtforpython-6/tutorials/basictutorial/uifiles.html","https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-deploy.html"],"pyqt6":["https://www.riverbankcomputing.com/static/Docs/PyQt6/","https://pyinstaller.org/en/stable/"],"qt-cpp":["https://doc.qt.io/qt-6/cmake-get-started.html","https://doc.qt.io/qt-6/windows-deployment.html"],"electron":["https://www.electronjs.org/docs/latest/tutorial/debugging-vscode","https://www.electronjs.org/docs/latest/tutorial/security","https://www.electron.build/"],"avalonia":["https://docs.avaloniaui.net/docs/get-started","https://docs.avaloniaui.net/docs/deployment/windows"],"maui":["https://learn.microsoft.com/dotnet/maui/get-started/first-app","https://learn.microsoft.com/dotnet/maui/windows/deployment/publish-unpackaged-cli?view=net-maui-10.0"],"winui":["https://learn.microsoft.com/windows/apps/winui/winui3/get-started-winui3-for-desktop","https://learn.microsoft.com/windows/apps/windows-app-sdk/deploy-unpackaged-apps"]}
    result=[]
    for stack,old_ids in RETIRED.items():
        candidate=next((CATALOG/stack).glob("*/recipe.json"))
        data=json.loads(candidate.read_text(encoding="utf-8"))
        book=Book(stack,data["versions"],sources[stack],data["prerequisites"],os=["Windows"],ide=["VS Code","Visual Studio"] if stack not in names else ["VS Code","Qt Designer"])
        # Each add gets a separate parameter dictionary to remain editable.
        if stack in names:add_python_qt(book,names[stack])
        elif stack=="qt-cpp":add_cpp(book)
        elif stack=="electron":add_electron(book)
        else:add_managed(book,stack)
        for recipe in book.recipes:
            recipe["parameters"]=deepcopy(recipe["parameters"])
        result.append(book)
    return result


def apply_overlay():
    protected=set()
    golden=ROOT/"reports/search-cases-desktop-tools.json"
    if golden.exists():
        protected={rid for row in json.loads(golden.read_text(encoding="utf-8")) for rid in row["expected_ids"]}
    retired=[]
    for stack,ids in RETIRED.items():
        for rid in ids:
            target=CATALOG/stack/rid
            if rid in protected:raise ValueError(f"Cannot retire search target {rid}")
            if not target.exists():continue
            resolved=target.resolve()
            if not resolved.is_relative_to(CATALOG.resolve()) or resolved.parent!=(CATALOG/stack).resolve() or target.is_symlink():
                raise ValueError(f"Unexpected retirement path: {target}")
            old=json.loads((target/"recipe.json").read_text(encoding="utf-8"))
            if old["id"]!=rid or old.get("project"):raise ValueError(f"Cannot retire project or mismatched recipe {rid}")
            retired.append(target)
    books=compile_guides()
    for book in books:save_book(book)
    # Every recursive deletion has been preflighted against the explicit list.
    for target in retired:shutil.rmtree(target)
    for stack in RETIRED:
        count=len(list((CATALOG/stack).glob("*/recipe.json")))
        if count!=STACKS[stack][2]:raise ValueError(f"{stack}: count {count}")
    projects=sum(json.loads(p.read_text(encoding="utf-8")).get("project",False) for stack in list(RETIRED)+["powershell","bash","git","cmake","docker","cicd","packaging"] for p in (CATALOG/stack).glob("*/recipe.json"))
    if projects!=11:raise ValueError(f"Expected eleven projects, found {projects}")
    print("Lifecycle overlay: fourteen guides; all quantities preserved; eleven capstones retained")
    return books


def verify(books):
    sys.path.insert(0,str(ROOT))
    from devatlas.templating import render_recipe
    report={"date":"2026-10-29","guides":[],"counts":{"python_ast":0,"javascript":0,"json":0,"xml":0,"powershell":0},"errors":[],"limitations":["Static checks only; no SDK installation, native compilation, debugger session or distributable run is claimed."]}
    with tempfile.TemporaryDirectory(prefix="lifecycle-",dir=ROOT/".cache") as folder:
        scratch=Path(folder)
        assert scratch.resolve().is_relative_to((ROOT/".cache").resolve())
        ps=[]
        for book in books:
            for recipe in book.recipes:
                rendered=render_recipe(recipe)
                report["guides"].append(recipe["id"])
                for index,asset in enumerate(rendered["assets"]):
                    source=asset["content"];name=asset["path"]
                    try:
                        suffix=Path(name).suffix
                        if suffix==".py":ast.parse(source);report["counts"]["python_ast"]+=1
                        if suffix==".json":json.loads(source);report["counts"]["json"]+=1
                        if suffix in {".ui",".xaml",".csproj"}:ET.fromstring(source);report["counts"]["xml"]+=1
                        if suffix in {".js",".cjs"}:
                            file=scratch/f"{recipe['id']}-{index}{suffix}";file.write_text(source,encoding="utf-8")
                            result=subprocess.run([shutil.which("node") or "node","--check",str(file)],capture_output=True,text=True,timeout=15)
                            if result.returncode:raise ValueError(result.stderr)
                            report["counts"]["javascript"]+=1
                        if asset["role"]=="command" and asset.get("shell")=="PowerShell":
                            if any(ord(char)<32 and char not in "\n\t" for char in source):
                                raise ValueError("Unexpected control character in command source")
                            file=scratch/f"{recipe['id']}-{index}.ps1";file.write_text(source,encoding="utf-8");ps.append(str(file))
                    except Exception as exc:report["errors"].append({"id":recipe["id"],"path":name,"error":str(exc)})
        manifest=scratch/"commands.json";manifest.write_text(pretty(ps),encoding="utf-8")
        checker=scratch/"parse.ps1";checker.write_text('''param([string]$Manifest)
$errorsFound=@()
foreach($file in (Get-Content -LiteralPath $Manifest -Raw | ConvertFrom-Json)){
 $tokens=$null;$issues=$null
 [System.Management.Automation.Language.Parser]::ParseFile($file,[ref]$tokens,[ref]$issues) | Out-Null
 foreach($issue in $issues){$errorsFound+=@{file=$file;message=$issue.Message}}
}
ConvertTo-Json -InputObject @($errorsFound) -Depth 4 -Compress
''',encoding="utf-8")
        result=subprocess.run([shutil.which("pwsh") or "pwsh","-NoProfile","-File",str(checker),str(manifest)],capture_output=True,text=True,timeout=30)
        if result.returncode:report["errors"].append({"parser":"PowerShell","error":result.stderr})
        else:report["errors"].extend(json.loads(result.stdout));report["counts"]["powershell"]=len(ps)
    report["success"]=not report["errors"]
    output=ROOT/"reports/desktop-lifecycle-qa.json";output.write_text(pretty(report),encoding="utf-8")
    if report["success"]:
        for book in books:
            for recipe in book.recipes:
                path=CATALOG/book.stack/recipe["id"]/"recipe.json"
                data=json.loads(path.read_text(encoding="utf-8"))
                data["verification"]={"status":"statico","date":"2026-10-29","details":"Controlli su configurazioni JSON/XML, AST Python, node --check e parser PowerShell secondo i file presenti. Installazioni, sessioni debugger e build distribuibili non eseguite. Report: reports/desktop-lifecycle-qa.json."}
                path.write_text(pretty(data),encoding="utf-8")
    print(pretty(report))
    return report["success"]

def build_all():
    (ROOT/".cache").mkdir(exist_ok=True)
    (ROOT/"reports").mkdir(exist_ok=True)
    return verify(apply_overlay())

if __name__=="__main__":sys.exit(not build_all())
