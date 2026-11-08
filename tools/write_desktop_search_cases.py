"""Independent intent queries; this script does not invoke or tune app search."""
import json
from pathlib import Path
from catalog_support import ROOT,slug

CASES=[
("PySide ricerca solo quando smetto di scrivere","pyside6","debounce"),
("PySide clipboard copia sorgente","pyside6","clipboard"),
("PySide aprire testo UTF8 con dialogo","pyside6","open-file"),
("PyQt filtro lista ignora maiuscole","pyqt6","filter-model"),
("PyQt ricordare opzione prossima apertura QSettings","pyqt6","settings"),
("PyQt tre scelte una sola attiva","pyqt6","radio-group"),
("Qt C++ esplora cartella home QFileSystemModel","qt-cpp","filesystem"),
("Qt C++ scrittura atomica QSaveFile","qt-cpp","save"),
("Qt C++ orologio aggiornato senza sleep","qt-cpp","timer"),
("Electron pagina in PDF A4","electron","pdf"),
("Electron screenshot finestra PNG","electron","capture"),
("Electron dialogo scegli cartella","electron","folder"),
("Avalonia add item ObservableCollection","avalonia","observable"),
("Avalonia UI freeze durante calcolo","avalonia","background"),
("Avalonia salvare preferenze JSON AppData","avalonia","json"),
("MAUI copiare negli appunti","maui","clipboard"),
("MAUI Entry sapere quanti caratteri","maui","entry"),
("MAUI DisplayAlertAsync richiesta conferma","maui","confirm"),
("WinUI ContentDialog errore XamlRoot","winui","dialog"),
("WinUI NumberBox valori min max","winui","number"),
("WinUI AutoSuggestBox cerca mentre digito","winui","search"),
("PowerShell digest file SHA256","powershell","Calcolare SHA-256 di un file locale"),
("PowerShell parallel limitare tre task","powershell","Eseguire operazioni in parallelo con limite"),
("PowerShell CSV caratteri accentati","powershell","Esportare e reimportare un CSV"),
("Bash cancellare temporanei anche con errore trap","bash","Creare file temporanei e pulirli con trap"),
("Bash find nomi file con spazi print0","bash","Iterare nomi file tramite separatore NUL"),
("Bash opzioni linea comando getopts","bash","Analizzare opzioni brevi con getopts"),
("Git lavorare su due branch contemporaneamente","git","Aprire un secondo working tree su un ramo nuovo"),
("Git stash anche file nuovi untracked","git","Accantonare anche file non tracciati"),
("Git annullare commit senza riscrivere storia","git","Annullare un commit con revert"),
("CMake header generato dipendenza OUTPUT DEPENDS","cmake","Dichiarare un header generato come dipendenza"),
("CMake richiedere cxx_std_20","cmake","Richiedere uno standard C++ sul target"),
("CMake file compile_commands per clangd","cmake","Esportare compile_commands per strumenti di analisi"),
("Docker Redis conteggio persistente dopo down","docker","progetto-contatore-redis"),
("Docker filesystem read only tmpfs","docker","Usare un filesystem container in sola lettura"),
("Docker Compose servizio prima healthy","docker","Attendere il superamento dell'healthcheck"),
("GitHub Actions valore da job producer a consumer","cicd","Trasferire un output tra due job"),
("CI cache dipendenze pip requirements","cicd","Riutilizzare la cache pip in CI"),
("GitHub conservare report quando test fallisce","cicd","Conservare diagnostica anche quando un test fallisce"),
("PySide deploy standalone Nuitka","packaging","Distribuire PySide6 con pyside6-deploy e Nuitka"),
("pacchetto digest diverso verificare SHA256","packaging","Verificare un pacchetto contro il manifest SHA-256"),
("dotnet publish win-x64 self-contained runtime incluso","packaging","Pubblicare una CLI .NET autonoma per Windows"),
]

def main():
    assert len(CASES)==42
    rows=[]
    for query,stack,key in CASES:
        rid=stack+"-"+slug(key)
        assert (ROOT/"catalog"/stack/rid/"recipe.json").is_file(),rid
        rows.append({"query":query,"expected_ids":[rid]})
    path=ROOT/"reports"/"search-cases-desktop-tools.json"
    path.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"{len(rows)} intent queries written; no search executed")

if __name__=="__main__":main()
