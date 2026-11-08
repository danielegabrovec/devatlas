"""Original desktop cookbook. Rebuild without executing catalog examples."""
from __future__ import annotations
import json
import textwrap
from catalog_support import Book, STACKS
from desktop_tools_common import save_book


def clean(s):
    return textwrap.dedent(s).strip() + "\n"


QT_TOPICS = []
def qt(key, title, description, code, expected, section="Codice applicativo"):
    QT_TOPICS.append((key, title, description, clean(code), expected, section))


qt("label", "Mostrare testo selezionabile", "Rendere copiabile un messaggio nella finestra senza un editor modificabile.", '''
label = QLabel("Messaggio selezionabile con il mouse")
label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
layout.addWidget(label)
''', "Il testo si seleziona e Ctrl+C lo copia.")
qt("button", "Aggiornare un contatore con un pulsante", "Collegare clicked a uno slot mantenendo lo stato della finestra.", '''
button = QPushButton("Incrementa")
label = QLabel("0")
root.count = 0
def increment():
    root.count += 1
    label.setText(str(root.count))
button.clicked.connect(increment)
layout.addWidget(label)
layout.addWidget(button)
''', "Ogni clic aumenta il numero di uno.")
qt("line-edit", "Leggere un campo di testo in tempo reale", "Usare textChanged per aggiornare una breve anteprima.", '''
edit = QLineEdit()
edit.setPlaceholderText("Scrivi il tuo nome")
label = QLabel()
edit.textChanged.connect(lambda value: label.setText(f"Caratteri: {len(value)}"))
layout.addWidget(edit)
layout.addWidget(label)
''', "Il conteggio segue inserimenti e cancellazioni.")
qt("password", "Alternare la visibilità di una password", "Associare una casella di controllo alla modalità echo del campo.", '''
edit = QLineEdit()
edit.setEchoMode(QLineEdit.EchoMode.Password)
check = QCheckBox("Mostra password")
check.toggled.connect(lambda yes: edit.setEchoMode(QLineEdit.EchoMode.Normal if yes else QLineEdit.EchoMode.Password))
layout.addWidget(edit)
layout.addWidget(check)
''', "La password viene mascherata finché non attivi la casella.")
qt("integer-validator", "Accettare soltanto numeri interi nel campo", "Vincolare un input mediante QIntValidator e distinguere input incompleto e valido.", '''
edit = QLineEdit()
edit.setValidator(QIntValidator(1, 120, edit))
label = QLabel("Inserisci un'età tra 1 e 120")
edit.textChanged.connect(lambda _: label.setText("Valido" if edit.hasAcceptableInput() else "Completa il valore"))
layout.addWidget(edit)
layout.addWidget(label)
''', "Il valore 42 è valido; il campo vuoto resta incompleto.")
qt("regexp-validator", "Validare un codice con espressione regolare", "Richiedere due lettere maiuscole seguite da quattro cifre.", '''
edit = QLineEdit()
edit.setPlaceholderText("AB1234")
edit.setValidator(QRegularExpressionValidator(QRegularExpression("[A-Z]{2}[0-9]{4}"), edit))
layout.addWidget(edit)
''', "AB1234 viene accettato, lettere minuscole non sono accettate.")
qt("spinbox", "Selezionare una quantità intera", "Configurare range, passo e suffisso di QSpinBox.", '''
spin = QSpinBox()
spin.setRange(0, 200)
spin.setSingleStep(5)
spin.setSuffix(" pezzi")
spin.setValue(10)
layout.addWidget(spin)
''', "Le frecce cambiano la quantità di cinque pezzi.")
qt("double-spinbox", "Inserire un prezzo decimale", "Usare QDoubleSpinBox con precisione esplicita per un input numerico.", '''
spin = QDoubleSpinBox()
spin.setRange(0, 9999)
spin.setDecimals(2)
spin.setSingleStep(0.25)
spin.setPrefix("EUR ")
layout.addWidget(spin)
''', "Il controllo mostra due cifre decimali con il separatore locale.")
qt("combo-data", "Associare identificatori alle opzioni", "Separare testo visibile e valore applicativo con itemData.", '''
combo = QComboBox()
combo.addItem("Produzione", "prod")
combo.addItem("Sviluppo", "dev")
label = QLabel("prod")
combo.currentIndexChanged.connect(lambda _: label.setText(combo.currentData()))
layout.addWidget(combo)
layout.addWidget(label)
''', "Scegliendo Sviluppo compare l'identificatore dev.")
qt("editable-combo", "Offrire opzioni modificabili", "Combinare una cronologia breve con un input libero.", '''
combo = QComboBox()
combo.setEditable(True)
combo.addItems(["localhost", "server-locale"])
combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
layout.addWidget(combo)
''', "Puoi scegliere un host esistente o scriverne uno senza modificare la lista.")
qt("checkbox-tristate", "Gestire una casella a tre stati", "Rappresentare l'ereditarietà di una preferenza mediante stato parziale.", '''
check = QCheckBox("Abilita log (parziale = eredita)")
check.setTristate(True)
check.setCheckState(Qt.CheckState.PartiallyChecked)
layout.addWidget(check)
''', "I clic scorrono tra non selezionato, parziale e selezionato.")
qt("radio-group", "Creare una scelta mutuamente esclusiva", "Raggruppare pulsanti radio con identificatori numerici.", '''
group = QButtonGroup(root)
label = QLabel("Scegli un formato")
for number, name in enumerate(["JSON", "CSV", "XML"]):
    button = QRadioButton(name)
    group.addButton(button, number)
    layout.addWidget(button)
group.idClicked.connect(lambda number: label.setText(f"Formato: {number}"))
layout.addWidget(label)
''', "Soltanto un formato è attivo alla volta.")
qt("slider", "Sincronizzare slider e indicatore", "Connettere valueChanged a un display numerico senza polling.", '''
slider = QSlider(Qt.Orientation.Horizontal)
slider.setRange(0, 100)
display = QLCDNumber()
slider.valueChanged.connect(display.display)
layout.addWidget(slider)
layout.addWidget(display)
''', "Il display segue la posizione dello slider.")
qt("date-edit", "Selezionare una data con calendario", "Attivare il popup calendario in un QDateEdit.", '''
edit = QDateEdit(QDate.currentDate())
edit.setCalendarPopup(True)
edit.setDisplayFormat("dd/MM/yyyy")
layout.addWidget(edit)
''', "Il pulsante laterale apre un calendario mensile.")
qt("time-edit", "Inserire un orario senza data", "Usare QTimeEdit per ore e minuti.", '''
edit = QTimeEdit(QTime(9, 30))
edit.setDisplayFormat("HH:mm")
layout.addWidget(edit)
''', "L'orario iniziale è 09:30.")
qt("datetime", "Scegliere data e ora insieme", "Configurare un controllo unico per un appuntamento locale.", '''
edit = QDateTimeEdit(QDateTime.currentDateTime())
edit.setCalendarPopup(True)
edit.setDisplayFormat("dd/MM/yyyy HH:mm")
layout.addWidget(edit)
''', "Il controllo permette di cambiare giorno e orario.")
qt("plain-editor", "Mostrare codice senza alterare l'indentazione", "Impostare un editor semplice con font fisso e righe non avvolte.", '''
edit = QPlainTextEdit("def saluta():\\n    return 'Ciao'\\n")
edit.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
layout.addWidget(edit)
''', "L'indentazione resta composta da quattro spazi.")
qt("rich-editor", "Inserire testo formattato", "Usare QTextEdit e un pulsante per applicare il grassetto alla selezione.", '''
edit = QTextEdit("Seleziona una parola e premi Grassetto")
button = QPushButton("Grassetto")
button.clicked.connect(lambda: edit.setFontWeight(QFont.Weight.Bold))
layout.addWidget(edit)
layout.addWidget(button)
''', "La selezione assume peso grassetto.")
qt("markdown", "Visualizzare una guida Markdown", "Renderizzare contenuti statici con il motore testuale Qt.", '''
view = QTextBrowser()
view.setMarkdown("# Guida\\n\\n- Crea il file\\n- Avvia il programma\\n\\n**Pronto**")
layout.addWidget(view)
''', "La guida mostra titolo, elenco e grassetto.")
qt("open-file", "Aprire un file di testo UTF-8", "Gestire annullamento del dialogo e errori di lettura senza chiudere l'app.", '''
edit = QPlainTextEdit()
button = QPushButton("Apri testo")
def load():
    path, _ = QFileDialog.getOpenFileName(root, "Apri", "", "Testo (*.txt);;Tutti (*)")
    if not path:
        return
    try:
        edit.setPlainText(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        QMessageBox.warning(root, "Lettura non riuscita", str(exc))
button.clicked.connect(load)
layout.addWidget(button)
layout.addWidget(edit)
''', "Un file UTF-8 viene visualizzato; Annulla lascia il contenuto invariato.", "File e persistenza")
qt("save-file", "Salvare il contenuto di un editor", "Richiedere il percorso di destinazione e scrivere UTF-8.", '''
edit = QPlainTextEdit("Testo da salvare")
button = QPushButton("Salva con nome")
def save():
    path, _ = QFileDialog.getSaveFileName(root, "Salva", "appunti.txt", "Testo (*.txt)")
    if path:
        try:
            Path(path).write_text(edit.toPlainText(), encoding="utf-8")
        except OSError as exc:
            QMessageBox.warning(root, "Salvataggio", str(exc))
button.clicked.connect(save)
layout.addWidget(edit)
layout.addWidget(button)
''', "Il file scelto contiene esattamente il testo dell'editor.", "File e persistenza")
qt("folder-dialog", "Scegliere una cartella", "Usare getExistingDirectory evitando di trattare Annulla come un percorso.", '''
label = QLabel("Nessuna cartella")
button = QPushButton("Scegli cartella")
def choose():
    path = QFileDialog.getExistingDirectory(root, "Cartella")
    if path:
        label.setText(path)
button.clicked.connect(choose)
layout.addWidget(button)
layout.addWidget(label)
''', "Compare il percorso della cartella selezionata.")
qt("color-dialog", "Selezionare un colore", "Verificare isValid prima di applicare il colore scelto.", '''
label = QLabel("Anteprima colore")
button = QPushButton("Colore")
def choose():
    color = QColorDialog.getColor(QColor("steelblue"), root)
    if color.isValid():
        label.setStyleSheet(f"background: {color.name()}; padding: 20px")
button.clicked.connect(choose)
layout.addWidget(button)
layout.addWidget(label)
''', "Lo sfondo della scritta usa il colore selezionato.")
qt("font-dialog", "Selezionare il font di una scritta", "Applicare il font soltanto dopo conferma del dialogo.", '''
label = QLabel("Anteprima carattere")
button = QPushButton("Carattere")
def choose():
    accepted, font = QFontDialog.getFont(label.font(), root)
    if accepted:
        label.setFont(font)
button.clicked.connect(choose)
layout.addWidget(button)
layout.addWidget(label)
''', "La scritta cambia famiglia e dimensione dopo OK.")
qt("confirm", "Richiedere conferma a un'azione locale", "Usare i pulsanti standard e rendere Annulla la risposta predefinita.", '''
label = QLabel("Dato di esempio")
button = QPushButton("Svuota")
def clear():
    answer = QMessageBox.question(root, "Conferma", "Svuotare il testo?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
    if answer == QMessageBox.StandardButton.Yes:
        label.clear()
button.clicked.connect(clear)
layout.addWidget(label)
layout.addWidget(button)
''', "No conserva il testo; Sì lo svuota.")
qt("input-dialog", "Richiedere una stringa con un dialogo", "Distinguere un input confermato da un annullamento.", '''
label = QLabel("Nessun nome")
button = QPushButton("Nome")
def ask():
    text, ok = QInputDialog.getText(root, "Nome", "Nome del progetto:")
    if ok and text.strip():
        label.setText(text.strip())
button.clicked.connect(ask)
layout.addWidget(button)
layout.addWidget(label)
''', "Il nome viene aggiornato solo con una stringa non vuota confermata.")
qt("custom-dialog", "Creare un dialogo con Accetta e Annulla", "Collegare QDialogButtonBox ai codici di ritorno del dialogo.", '''
button = QPushButton("Opzioni")
def show():
    dialog = QDialog(root)
    box = QVBoxLayout(dialog)
    box.addWidget(QLabel("Opzioni della sessione"))
    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    box.addWidget(buttons)
    dialog.exec()
button.clicked.connect(show)
layout.addWidget(button)
''', "OK restituisce Accepted, Annulla restituisce Rejected.")
qt("form-layout", "Allineare etichette e campi in un modulo", "Usare QFormLayout con etichette associate agli input.", '''
form = QFormLayout()
form.addRow("Nome:", QLineEdit())
form.addRow("Email:", QLineEdit())
form.addRow("Età:", QSpinBox())
layout.addLayout(form)
''', "I campi sono allineati su una colonna comune.", "Layout e grafica")
qt("grid-layout", "Costruire una griglia con celle espanse", "Usare coordinate di riga e colonna e uno span orizzontale.", '''
grid = QGridLayout()
grid.addWidget(QLabel("Intestazione"), 0, 0, 1, 2)
grid.addWidget(QPushButton("Sinistra"), 1, 0)
grid.addWidget(QPushButton("Destra"), 1, 1)
grid.setColumnStretch(1, 1)
layout.addLayout(grid)
''', "L'intestazione occupa entrambe le colonne.", "Layout e grafica")
qt("splitter", "Creare pannelli ridimensionabili", "Distribuire due editor dentro un QSplitter.", '''
split = QSplitter(Qt.Orientation.Horizontal)
split.addWidget(QPlainTextEdit("Sorgente"))
split.addWidget(QPlainTextEdit("Anteprima"))
split.setSizes([250, 350])
layout.addWidget(split)
''', "Il divisore centrale regola la larghezza dei pannelli.", "Layout e grafica")
qt("tabs", "Organizzare contenuti in schede", "Aggiungere pagine indipendenti a QTabWidget.", '''
tabs = QTabWidget()
tabs.addTab(QLabel("Configurazione generale"), "Generale")
tabs.addTab(QPlainTextEdit("Log della sessione"), "Log")
layout.addWidget(tabs)
''', "Le due linguette mostrano contenuti differenti.", "Layout e grafica")
qt("stacked", "Cambiare pagina da un selettore", "Collegare un indice a QStackedWidget per una navigazione senza finestre.", '''
combo = QComboBox()
combo.addItems(["Home", "Impostazioni"])
pages = QStackedWidget()
pages.addWidget(QLabel("Benvenuto"))
pages.addWidget(QCheckBox("Notifiche"))
combo.currentIndexChanged.connect(pages.setCurrentIndex)
layout.addWidget(combo)
layout.addWidget(pages)
''', "La scelta cambia la pagina visibile.", "Layout e grafica")
qt("scroll-area", "Rendere scorrevole un modulo lungo", "Inserire un widget contenitore dentro QScrollArea con resize abilitato.", '''
area = QScrollArea()
area.setWidgetResizable(True)
content = QWidget()
form = QFormLayout(content)
for index in range(30):
    form.addRow(f"Campo {index + 1}", QLineEdit())
area.setWidget(content)
layout.addWidget(area)
''', "La barra verticale consente di raggiungere tutti i trenta campi.", "Layout e grafica")
qt("groupbox", "Disabilitare un gruppo di impostazioni", "Usare un QGroupBox selezionabile come interruttore dei figli.", '''
group = QGroupBox("Proxy manuale")
group.setCheckable(True)
group.setChecked(False)
form = QFormLayout(group)
form.addRow("Host", QLineEdit())
form.addRow("Porta", QSpinBox())
layout.addWidget(group)
''', "I campi diventano attivi selezionando Proxy manuale.")
qt("list-widget", "Aggiungere e rimuovere elementi da una lista", "Trasferire il testo di un input a QListWidget e rimuovere la selezione.", '''
edit = QLineEdit()
items = QListWidget()
add = QPushButton("Aggiungi")
remove = QPushButton("Rimuovi selezionato")
def insert():
    if edit.text().strip():
        items.addItem(edit.text().strip())
        edit.clear()
add.clicked.connect(insert)
remove.clicked.connect(lambda: items.takeItem(items.currentRow()) if items.currentRow() >= 0 else None)
for widget in [edit, add, items, remove]:
    layout.addWidget(widget)
''', "I nomi entrano nella lista e soltanto la riga selezionata viene rimossa.")
qt("list-model", "Visualizzare una lista con modello", "Collegare QStringListModel a QListView separando dati e vista.", '''
model = QStringListModel(["Python", "C++", "C#"], root)
view = QListView()
view.setModel(model)
layout.addWidget(view)
''', "La vista presenta tre righe gestite dal modello.")
qt("filter-model", "Filtrare una lista durante la digitazione", "Usare un proxy con confronto senza distinzione maiuscole/minuscole.", '''
model = QStringListModel(["Python", "PostgreSQL", "PySide6", "Rust"], root)
proxy = QSortFilterProxyModel(root)
proxy.setSourceModel(model)
proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
edit = QLineEdit()
edit.setPlaceholderText("Filtra")
edit.textChanged.connect(proxy.setFilterFixedString)
view = QListView()
view.setModel(proxy)
layout.addWidget(edit)
layout.addWidget(view)
''', "Scrivendo py rimangono Python e PySide6.", "Ricerca e dati")
qt("table-widget", "Mostrare una tabella ordinabile", "Popolare QTableWidget e attivare l'ordinamento dopo l'inserimento.", '''
table = QTableWidget(2, 2)
table.setHorizontalHeaderLabels(["Prodotto", "Quantità"])
for row, values in enumerate([("Matite", "12"), ("Quaderni", "4")]):
    for column, value in enumerate(values):
        table.setItem(row, column, QTableWidgetItem(value))
table.setSortingEnabled(True)
layout.addWidget(table)
''', "Un clic sull'intestazione ordina le righe come testo.")
qt("table-model", "Scrivere un modello tabellare in sola lettura", "Implementare rowCount, columnCount e data senza creare un widget per cella.", '''
class Model(QAbstractTableModel):
    rows = [("Ada", 3), ("Linus", 5)]
    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.rows)
    def columnCount(self, parent=QModelIndex()):
        return 2
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid() and role == Qt.ItemDataRole.DisplayRole:
            return str(self.rows[index.row()][index.column()])
model = Model(root)
table = QTableView()
table.setModel(model)
layout.addWidget(table)
''', "La tabella mostra due persone e i relativi conteggi.")
qt("tree", "Rappresentare una struttura gerarchica", "Aggiungere categorie e figli a QTreeWidget.", '''
tree = QTreeWidget()
tree.setHeaderLabels(["Elemento"])
category = QTreeWidgetItem(tree, ["Linguaggi"])
QTreeWidgetItem(category, ["Python"])
QTreeWidgetItem(category, ["C++"])
tree.expandAll()
layout.addWidget(tree)
''', "Linguaggi contiene due elementi espandibili.")
qt("filesystem-model", "Esplorare la cartella utente", "Collegare QFileSystemModel a QTreeView e fissare l'indice radice.", '''
model = QFileSystemModel(root)
folder = str(Path.home())
model.setRootPath(folder)
view = QTreeView()
view.setModel(model)
view.setRootIndex(model.index(folder))
layout.addWidget(view)
''', "La vista elenca il contenuto della cartella utente in sola lettura.")
qt("selection", "Leggere la riga selezionata nel modello", "Usare currentChanged della selectionModel dopo setModel.", '''
model = QStringListModel(["Rosso", "Verde", "Blu"], root)
view = QListView()
view.setModel(model)
label = QLabel("Nessuna selezione")
view.selectionModel().currentChanged.connect(lambda current, previous: label.setText(str(current.data())))
layout.addWidget(view)
layout.addWidget(label)
''', "La scritta riporta il colore della riga corrente.")
qt("clipboard", "Copiare testo negli appunti di sistema", "Usare QGuiApplication.clipboard per un pulsante Copia.", '''
edit = QPlainTextEdit("print('Ciao')")
button = QPushButton("Copia codice")
button.clicked.connect(lambda: QGuiApplication.clipboard().setText(edit.toPlainText()))
layout.addWidget(edit)
layout.addWidget(button)
''', "Incollando in un editor si ottiene soltanto il codice.")
qt("clipboard-read", "Leggere gli appunti senza modificarli", "Prelevare il testo corrente al clic esplicito dell'utente.", '''
edit = QPlainTextEdit()
button = QPushButton("Leggi appunti")
button.clicked.connect(lambda: edit.setPlainText(QGuiApplication.clipboard().text()))
layout.addWidget(button)
layout.addWidget(edit)
''', "Il testo degli appunti compare nell'editor.")
qt("shortcut", "Attivare la ricerca con Ctrl+F", "Associare QShortcut alla finestra e focalizzare il campo.", '''
edit = QLineEdit()
edit.setPlaceholderText("Ricerca")
layout.addWidget(edit)
shortcut = QShortcut(QKeySequence.StandardKey.Find, root)
shortcut.activated.connect(edit.setFocus)
''', "Ctrl+F sposta il focus al campo di ricerca.")
qt("action-menu", "Aggiungere un menu con azione e scorciatoia", "Riutilizzare QAction per il comando di chiusura.", '''
bar = QMenuBar()
menu = bar.addMenu("File")
action = QAction("Chiudi", root)
action.setShortcut(QKeySequence.StandardKey.Close)
action.triggered.connect(root.close)
menu.addAction(action)
layout.setMenuBar(bar)
layout.addWidget(QLabel("Usa File → Chiudi"))
''', "Il menu o la scorciatoia chiudono la finestra.")
qt("toolbar", "Creare una barra di strumenti", "Aggiungere azioni con testo e tooltip a QToolBar.", '''
bar = QToolBar()
action = QAction("Aggiorna", root)
action.setToolTip("Aggiorna il riepilogo locale")
label = QLabel("In attesa")
action.triggered.connect(lambda: label.setText(QTime.currentTime().toString()))
bar.addAction(action)
layout.addWidget(bar)
layout.addWidget(label)
''', "Aggiorna mostra l'ora del clic.")
qt("statusbar", "Mostrare un messaggio temporaneo di stato", "Usare QStatusBar senza aprire una finestra modale.", '''
bar = QStatusBar()
button = QPushButton("Operazione locale")
button.clicked.connect(lambda: bar.showMessage("Operazione completata", 2000))
layout.addWidget(button)
layout.addWidget(bar)
''', "Il messaggio scompare dopo circa due secondi.")
qt("timer", "Aggiornare un orologio con QTimer", "Affidare gli aggiornamenti al ciclo eventi evitando sleep.", '''
label = QLabel()
timer = QTimer(root)
timer.setInterval(1000)
timer.timeout.connect(lambda: label.setText(QTime.currentTime().toString("HH:mm:ss")))
timer.start()
layout.addWidget(label)
''', "L'orario viene aggiornato ogni secondo senza bloccare l'interfaccia.")
qt("single-shot", "Eseguire un aggiornamento differito", "Usare QTimer.singleShot per mostrare un risultato una volta sola.", '''
label = QLabel("Attendi un istante")
layout.addWidget(label)
QTimer.singleShot(1200, lambda: label.setText("Aggiornamento eseguito"))
''', "La scritta cambia una sola volta dopo 1,2 secondi.")
qt("debounce", "Ritardare la ricerca fino alla pausa di digitazione", "Riavviare un timer singleShot a ogni modifica del campo.", '''
edit = QLineEdit()
label = QLabel("Nessuna query")
timer = QTimer(root)
timer.setSingleShot(True)
timer.setInterval(250)
edit.textChanged.connect(lambda _: timer.start())
timer.timeout.connect(lambda: label.setText(f"Cerca: {edit.text()}"))
layout.addWidget(edit)
layout.addWidget(label)
''', "Il testo Cercа cambia soltanto dopo una pausa di 250 ms.", "Ricerca e dati")
qt("progress", "Visualizzare un avanzamento determinato", "Aggiornare QProgressBar a piccoli passi tramite timer.", '''
bar = QProgressBar()
bar.setRange(0, 10)
bar.setValue(0)
timer = QTimer(root)
def advance():
    bar.setValue(bar.value() + 1)
    if bar.value() == bar.maximum():
        timer.stop()
timer.timeout.connect(advance)
timer.start(200)
layout.addWidget(bar)
''', "La barra raggiunge il 100% in dieci passi.")
qt("busy-progress", "Mostrare un'attesa senza percentuale", "Usare il range 0–0 per un'operazione a durata sconosciuta.", '''
bar = QProgressBar()
bar.setRange(0, 0)
layout.addWidget(bar)
QTimer.singleShot(1800, lambda: (bar.setRange(0, 1), bar.setValue(1)))
''', "La barra passa da attesa indeterminata a completata.")
qt("settings", "Conservare una preferenza tra due avvii", "Salvare un booleano con QSettings usando organizzazione e nome stabili.", '''
settings = QSettings("RicettarioDemo", "Preferenze")
check = QCheckBox("Mostra dettagli")
check.setChecked(settings.value("details", False, type=bool))
check.toggled.connect(lambda value: settings.setValue("details", value))
layout.addWidget(check)
''', "La casella ripristina lo stato all'avvio successivo.", "File e persistenza")
qt("geometry", "Ripristinare dimensione e posizione della finestra", "Usare saveGeometry e restoreGeometry su uno stesso QSettings.", '''
settings = QSettings("RicettarioDemo", "Geometria")
geometry = settings.value("geometry")
if geometry is not None:
    root.restoreGeometry(geometry)
button = QPushButton("Memorizza posizione corrente")
button.clicked.connect(lambda: settings.setValue("geometry", root.saveGeometry()))
layout.addWidget(button)
''', "Dopo Memorizza la prossima apertura ripristina la geometria salvata.", "File e persistenza")
qt("standard-path", "Trovare la cartella corretta per i dati", "Usare QStandardPaths anziché scrivere accanto all'eseguibile.", '''
QCoreApplication.setOrganizationName("RicettarioDemo")
QCoreApplication.setApplicationName("DatiLocali")
path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
label = QLabel(path)
label.setWordWrap(True)
layout.addWidget(label)
''', "La finestra mostra il percorso dati previsto dal sistema operativo.", "File e persistenza")
qt("json", "Salvare e rileggere un documento JSON", "Serializzare Unicode in un file temporaneo dedicato all'esempio.", '''
folder = Path(tempfile.mkdtemp(prefix="qt-json-"))
path = folder / "settings.json"
path.write_text(json.dumps({"tema": "chiaro", "zoom": 110}, ensure_ascii=False), encoding="utf-8")
data = json.loads(path.read_text(encoding="utf-8"))
layout.addWidget(QLabel(f"{path}\\nZoom: {data['zoom']}"))
''', "Il documento riletto contiene zoom 110.", "File e persistenza")
qt("sqlite", "Visualizzare dati SQLite senza dipendenze esterne", "Eseguire una query parametrizzata e trasferire il risultato alla vista.", '''
connection = sqlite3.connect(":memory:")
connection.execute("CREATE TABLE note (id INTEGER PRIMARY KEY, titolo TEXT)")
connection.executemany("INSERT INTO note(titolo) VALUES (?)", [("Qt",), ("SQL",)])
rows = connection.execute("SELECT titolo FROM note WHERE titolo LIKE ?", ("%Q%",)).fetchall()
connection.close()
items = QListWidget()
items.addItems([row[0] for row in rows])
layout.addWidget(items)
''', "La lista contiene Qt e SQL; la query usa un parametro.", "Ricerca e dati")
qt("completer", "Suggerire completamenti a un campo", "Installare QCompleter con confronto case-insensitive.", '''
edit = QLineEdit()
completer = QCompleter(["Python", "PySide6", "PyQt6", "PostgreSQL"], root)
completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
edit.setCompleter(completer)
layout.addWidget(edit)
''', "Digitando py compare un elenco di completamenti.", "Ricerca e dati")
qt("text-find", "Cercare nel contenuto di un editor", "Usare find e ripartire dall'inizio quando termina il documento.", '''
edit = QPlainTextEdit("Qt crea finestre. Qt gestisce eventi.")
query = QLineEdit("Qt")
button = QPushButton("Trova successivo")
def find():
    if not edit.find(query.text()):
        edit.moveCursor(QTextCursor.MoveOperation.Start)
        edit.find(query.text())
button.clicked.connect(find)
for widget in [query, button, edit]:
    layout.addWidget(widget)
''', "Ogni clic seleziona l'occorrenza successiva di Qt.", "Ricerca e dati")
qt("context-menu", "Aggiungere un menu contestuale a una lista", "Trasformare le coordinate locali in globali prima di aprire il menu.", '''
items = QListWidget()
items.addItems(["Uno", "Due"])
items.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
def menu_at(point):
    menu = QMenu(items)
    action = menu.addAction("Copia selezione")
    chosen = menu.exec(items.viewport().mapToGlobal(point))
    if chosen == action and items.currentItem():
        QGuiApplication.clipboard().setText(items.currentItem().text())
items.customContextMenuRequested.connect(menu_at)
layout.addWidget(items)
''', "Il tasto destro offre Copia selezione.")
qt("tooltip", "Fornire suggerimenti e descrizioni accessibili", "Associare tooltip e nome accessibile a un controllo.", '''
button = QPushButton("?")
button.setToolTip("Apre la guida locale dell'applicazione")
button.setAccessibleName("Guida")
button.setAccessibleDescription("Mostra informazioni sull'utilizzo")
layout.addWidget(button)
''', "Il puntatore visualizza il suggerimento; il controllo ha un nome accessibile.")
qt("tab-order", "Definire un ordine Tab prevedibile", "Impostare la sequenza tra nome, email e pulsante.", '''
name = QLineEdit()
email = QLineEdit()
button = QPushButton("Conferma")
name.setPlaceholderText("Nome")
email.setPlaceholderText("Email")
for widget in [name, email, button]:
    layout.addWidget(widget)
QWidget.setTabOrder(name, email)
QWidget.setTabOrder(email, button)
''', "Tab passa da Nome a Email a Conferma.")
qt("buddy", "Associare una scorciatoia di etichetta al campo", "Usare ampersand e setBuddy per Alt+N.", '''
edit = QLineEdit()
label = QLabel("&Nome:")
label.setBuddy(edit)
layout.addWidget(label)
layout.addWidget(edit)
''', "Alt+N porta il focus sul campo Nome.")
qt("palette", "Applicare una palette scura alla finestra", "Configurare ruoli della palette invece di assegnare colori a ogni etichetta.", '''
palette = root.palette()
palette.setColor(QPalette.ColorRole.Window, QColor("#18202b"))
palette.setColor(QPalette.ColorRole.WindowText, QColor("#eef3fa"))
root.setAutoFillBackground(True)
root.setPalette(palette)
layout.addWidget(QLabel("Palette della finestra"))
''', "Lo sfondo appare scuro con testo chiaro.", "Layout e grafica")
qt("stylesheet", "Dare uno stile coerente ai pulsanti", "Usare selettori Qt Style Sheets con stato hover.", '''
root.setStyleSheet("QPushButton { background:#2558a8; color:white; padding:10px; border-radius:6px; } QPushButton:hover { background:#3473ce; }")
layout.addWidget(QPushButton("Azione principale"))
''', "Il pulsante ha bordi arrotondati e cambia colore al passaggio.", "Layout e grafica")
qt("dynamic-property", "Evidenziare un campo con proprietà dinamica", "Applicare uno stile specifico mediante un selettore di proprietà.", '''
edit = QLineEdit("Dato non confermato")
edit.setProperty("invalid", True)
edit.setStyleSheet('QLineEdit[invalid="true"] { border:2px solid #b93636; padding:6px; }')
layout.addWidget(edit)
''', "Il campo mostra un bordo rosso senza alterare gli altri controlli.", "Layout e grafica")
qt("standard-icons", "Usare icone fornite dallo stile Qt", "Ottenere un'icona portabile senza dipendere da file esterni.", '''
button = QPushButton("Apri")
button.setIcon(root.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
layout.addWidget(button)
''', "Il pulsante mostra l'icona standard di apertura.", "Layout e grafica")
qt("pixmap", "Creare e scalare un'immagine in memoria", "Disegnare una pixmap e adattarla preservando il rapporto d'aspetto.", '''
pixmap = QPixmap(320, 180)
pixmap.fill(QColor("#245b83"))
painter = QPainter(pixmap)
painter.setPen(QColor("white"))
painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "Anteprima")
painter.end()
label = QLabel()
label.setPixmap(pixmap.scaled(240, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
layout.addWidget(label)
''', "L'immagine viene ridotta senza deformazioni.", "Layout e grafica")
qt("paint-widget", "Disegnare una figura con paintEvent", "Sottoclassare QWidget e disegnare un cerchio antialias.", '''
class Canvas(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#278a79"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(self.rect().adjusted(20, 20, -20, -20))
canvas = Canvas()
canvas.setMinimumSize(200, 160)
layout.addWidget(canvas)
''', "Il canvas mostra un'ellisse verde senza bordi seghettati.", "Layout e grafica")
qt("graphics-scene", "Spostare oggetti in una scena grafica", "Usare QGraphicsScene con un rettangolo trascinabile.", '''
scene = QGraphicsScene(root)
item = scene.addRect(0, 0, 120, 70, QPen(QColor("navy")), QBrush(QColor("lightblue")))
item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
view = QGraphicsView(scene)
scene.setSceneRect(-100, -100, 400, 300)
layout.addWidget(view)
''', "Il rettangolo si sposta trascinandolo con il mouse.", "Layout e grafica")
qt("animation", "Animare il valore di una barra", "Configurare QPropertyAnimation mantenendone il riferimento.", '''
bar = QProgressBar()
bar.setRange(0, 100)
layout.addWidget(bar)
root.animation = QPropertyAnimation(bar, b"value", root)
root.animation.setDuration(1500)
root.animation.setStartValue(0)
root.animation.setEndValue(100)
root.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
root.animation.start()
''', "La barra raggiunge il 100% con movimento graduale.", "Layout e grafica")
qt("opacity", "Applicare un effetto di trasparenza", "Usare QGraphicsOpacityEffect su un singolo widget.", '''
label = QLabel("Anteprima attenuata")
effect = QGraphicsOpacityEffect(label)
effect.setOpacity(0.45)
label.setGraphicsEffect(effect)
layout.addWidget(label)
''', "La scritta appare attenuata rispetto agli altri controlli.", "Layout e grafica")
qt("event-filter", "Intercettare Escape in un campo", "Installare un QObject event filter che consuma soltanto il tasto richiesto.", '''
edit = QLineEdit("Premi Escape per svuotare")
class Filter(QObject):
    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Escape:
            edit.clear()
            return True
        return False
root.filter = Filter(root)
edit.installEventFilter(root.filter)
layout.addWidget(edit)
''', "Escape svuota il campo; gli altri tasti funzionano normalmente.")
qt("drag-drop", "Accettare file trascinati nella finestra", "Rifiutare trascinamenti senza URL locali e mostrare i percorsi ricevuti.", '''
class DropArea(QLabel):
    def __init__(self):
        super().__init__("Trascina qui un file")
        self.setAcceptDrops(True)
        self.setMinimumHeight(120)
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and all(url.isLocalFile() for url in event.mimeData().urls()):
            event.acceptProposedAction()
    def dropEvent(self, event):
        self.setText("\\n".join(url.toLocalFile() for url in event.mimeData().urls()))
        event.acceptProposedAction()
layout.addWidget(DropArea())
''', "Il rilascio mostra percorsi locali e non apre né esegue i file.")
qt("worker-thread", "Completare un lavoro in un thread separato", "Inviare il risultato tramite segnale e liberare worker e thread alla fine.", '''
class Worker(QObject):
    done = Signal(str)
    @Slot()
    def run(self):
        result = sum(index * index for index in range(100000))
        self.done.emit(str(result))
label = QLabel("Calcolo")
layout.addWidget(label)
root.thread = QThread(root)
root.worker = Worker()
root.worker.moveToThread(root.thread)
root.thread.started.connect(root.worker.run)
root.worker.done.connect(label.setText)
root.worker.done.connect(root.thread.quit)
root.worker.done.connect(root.worker.deleteLater)
root.thread.finished.connect(root.thread.deleteLater)
root.thread.start()
root.destroyed.connect(lambda: None)
''', "Il risultato arriva con un segnale; nessun widget viene modificato dal worker.", "Concorrenza")
qt("threadpool", "Lanciare un compito con QThreadPool", "Separare QRunnable e QObject che espone i segnali.", '''
class Signals(QObject):
    result = Signal(str)
class Task(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = Signals()
    def run(self):
        self.signals.result.emit(str(sum(range(10000))))
label = QLabel("In attesa")
layout.addWidget(label)
root.task = Task()
root.task.signals.result.connect(label.setText)
QThreadPool.globalInstance().start(root.task)
''', "La somma 49995000 viene mostrata nel thread dell'interfaccia.", "Concorrenza")
qt("process", "Leggere l'output di un sottoprocesso", "Usare QProcess in modo asincrono per interrogare la versione di Python.", '''
edit = QPlainTextEdit()
edit.setReadOnly(True)
root.process = QProcess(root)
root.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
root.process.readyReadStandardOutput.connect(lambda: edit.appendPlainText(bytes(root.process.readAllStandardOutput()).decode("utf-8", errors="replace")))
root.process.errorOccurred.connect(lambda _: edit.appendPlainText(root.process.errorString()))
layout.addWidget(edit)
root.process.start(sys.executable, ["--version"])
''', "Compare la versione dell'interprete senza bloccare la finestra.", "Concorrenza")
qt("url", "Aprire un URL nel browser predefinito", "Delegare un collegamento HTTPS a QDesktopServices su richiesta esplicita.", '''
button = QPushButton("Documentazione Qt")
button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://doc.qt.io/qtforpython-6/")))
layout.addWidget(button)
''', "Il clic apre la documentazione nel browser di sistema.")
qt("locale", "Formattare un numero secondo la lingua italiana", "Usare QLocale esplicito per separatori e decimali.", '''
locale = QLocale(QLocale.Language.Italian, QLocale.Country.Italy)
layout.addWidget(QLabel(locale.toString(12345.67, "f", 2)))
''', "La scritta mostra 12.345,67.")
qt("translation", "Preparare stringhe per la traduzione", "Usare QCoreApplication.translate con un contesto stabile.", '''
text = QCoreApplication.translate("MainWindow", "Apri progetto")
layout.addWidget(QPushButton(text))
''', "Senza traduttore installato appare Apri progetto; il contesto è pronto per lupdate.")
qt("logging", "Inviare messaggi di log a un pannello", "Usare un segnale per trasferire righe di logging al widget.", '''
class LogHandler(logging.Handler):
    def emit(self, record):
        root.log_line.emit(self.format(record))
class Bus(QObject):
    line = Signal(str)
bus = Bus(root)
root.log_line = bus.line
edit = QPlainTextEdit()
edit.setReadOnly(True)
edit.setMaximumBlockCount(500)
bus.line.connect(edit.appendPlainText)
logger = logging.getLogger("qt.demo")
handler = LogHandler()
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.info("Pannello log pronto")
layout.addWidget(edit)
''', "Il pannello riceve la riga di log e mantiene al massimo 500 blocchi.")
qt("exception", "Mostrare un'eccezione applicativa senza terminare", "Catturare un errore previsto nello slot e comunicarlo con dettagli.", '''
button = QPushButton("Analizza JSON non valido")
def parse():
    try:
        json.loads("{non valido}")
    except json.JSONDecodeError as exc:
        QMessageBox.warning(root, "JSON", f"Riga {exc.lineno}: {exc.msg}")
button.clicked.connect(parse)
layout.addWidget(button)
''', "Il dialogo indica l'errore di parsing e la finestra resta utilizzabile.", "Debug e diagnostica")
qt("signal-blocker", "Aggiornare controlli senza emettere segnali ricorsivi", "Usare QSignalBlocker durante la sincronizzazione di due input.", '''
first = QSpinBox()
second = QSpinBox()
def sync(value):
    with QSignalBlocker(second):
        second.setValue(value)
first.valueChanged.connect(sync)
layout.addWidget(first)
layout.addWidget(second)
''', "Il primo controllo aggiorna il secondo senza emetterne valueChanged.")
qt("signal-custom", "Definire un segnale con dati tipizzati", "Incapsulare la notifica di un conteggio dentro un QObject.", '''
class Counter(QObject):
    changed = Signal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
    @Slot()
    def increment(self):
        self.value += 1
        self.changed.emit(self.value)
counter = Counter(root)
button = QPushButton("Incrementa")
label = QLabel("0")
counter.changed.connect(lambda value: label.setText(str(value)))
button.clicked.connect(counter.increment)
layout.addWidget(button)
layout.addWidget(label)
''', "Il modello del contatore notifica il nuovo intero alla vista.")
qt("object-discovery", "Trovare un controllo per objectName", "Usare findChild per recuperare un campo denominato.", '''
edit = QLineEdit()
edit.setObjectName("searchInput")
layout.addWidget(edit)
found = root.findChild(QLineEdit, "searchInput")
found.setPlaceholderText("Trovato tramite objectName")
''', "Il campo trovato riceve il placeholder.", "Debug e diagnostica")
qt("size-policy", "Controllare come cresce un widget", "Combinare sizePolicy e fattore stretch del layout.", '''
label = QLabel("Titolo compatto")
label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
edit = QPlainTextEdit("Questa area riceve lo spazio verticale libero")
layout.addWidget(label)
layout.addWidget(edit, 1)
''', "Ridimensionando la finestra cresce l'editor mentre il titolo resta compatto.", "Layout e grafica")
qt("spacer", "Allineare un'azione al bordo inferiore", "Inserire stretch prima del pulsante nel layout verticale.", '''
layout.addWidget(QLabel("Contenuto"))
layout.addStretch(1)
layout.addWidget(QPushButton("Azione in basso"))
''', "Il pulsante resta in basso quando aumenta l'altezza della finestra.", "Layout e grafica")
qt("numeric-sort", "Ordinare una colonna per valore numerico", "Usare QStandardItem con dati interi nel ruolo display.", '''
model = QStandardItemModel(root)
model.setHorizontalHeaderLabels(["Quantità"])
for value in [100, 2, 15]:
    item = QStandardItem()
    item.setData(value, Qt.ItemDataRole.DisplayRole)
    model.appendRow(item)
proxy = QSortFilterProxyModel(root)
proxy.setSourceModel(model)
view = QTableView()
view.setModel(proxy)
view.setSortingEnabled(True)
view.sortByColumn(0, Qt.SortOrder.AscendingOrder)
layout.addWidget(view)
''', "L'ordine è 2, 15, 100 anziché quello lessicografico.", "Ricerca e dati")
qt("user-role", "Conservare un identificatore nascosto in una riga", "Usare UserRole senza mostrare l'ID nella lista.", '''
items = QListWidget()
item = QListWidgetItem("Documento contabile")
item.setData(Qt.ItemDataRole.UserRole, 734)
items.addItem(item)
label = QLabel()
items.itemClicked.connect(lambda selected: label.setText(f"ID: {selected.data(Qt.ItemDataRole.UserRole)}"))
layout.addWidget(items)
layout.addWidget(label)
''', "Il clic mostra ID: 734.", "Ricerca e dati")
qt("editable-model", "Modificare celle con QStandardItemModel", "Costruire un modello modificabile e lasciare l'editor di cella alla vista.", '''
model = QStandardItemModel(2, 2, root)
model.setHorizontalHeaderLabels(["Nome", "Nota"])
model.setItem(0, 0, QStandardItem("Ada"))
model.setItem(0, 1, QStandardItem("Doppio clic per modificare"))
view = QTableView()
view.setModel(model)
layout.addWidget(view)
''', "Il doppio clic apre l'editor della cella.", "Ricerca e dati")
qt("delegate", "Scegliere un intero con un delegato di cella", "Sostituire l'editor standard mediante QStyledItemDelegate.", '''
class Delegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QSpinBox(parent)
        editor.setRange(0, 100)
        return editor
model = QStandardItemModel(1, 1, root)
item = QStandardItem()
item.setData(12, Qt.ItemDataRole.EditRole)
model.setItem(0, 0, item)
view = QTableView()
view.setModel(model)
view.setItemDelegate(Delegate(view))
layout.addWidget(view)
''', "Modificando la cella compare uno spinbox limitato a 0–100.", "Ricerca e dati")
qt("syntax-highlight", "Evidenziare commenti in un editor", "Implementare highlightBlock per colorare commenti a riga singola.", '''
class Highlighter(QSyntaxHighlighter):
    def highlightBlock(self, text):
        start = text.find("#")
        if start >= 0:
            style = QTextCharFormat()
            style.setForeground(QColor("#278553"))
            self.setFormat(start, len(text) - start, style)
edit = QPlainTextEdit("# Commento\\nvalue = 42")
root.highlighter = Highlighter(edit.document())
layout.addWidget(edit)
''', "Il commento è verde; è un evidenziatore dimostrativo, non un parser Python completo.", "Layout e grafica")
qt("undo-stack", "Aggiungere Undo e Redo a un'azione applicativa", "Modellare una modifica con QUndoCommand e QUndoStack.", '''
label = QLabel("0")
stack = QUndoStack(root)
class Change(QUndoCommand):
    def __init__(self, before, after):
        super().__init__("Cambia valore")
        self.before, self.after = before, after
    def undo(self):
        label.setText(self.before)
    def redo(self):
        label.setText(self.after)
add = QPushButton("Incrementa")
add.clicked.connect(lambda: stack.push(Change(label.text(), str(int(label.text()) + 1))))
undo = QPushButton("Annulla")
redo = QPushButton("Ripeti")
undo.clicked.connect(stack.undo)
redo.clicked.connect(stack.redo)
for widget in [label, add, undo, redo]:
    layout.addWidget(widget)
''', "Annulla ripristina il valore precedente e Ripeti riapplica la modifica.")
qt("savefile", "Scrivere un file con sostituzione atomica", "Usare QSaveFile e commit per evitare un documento scritto a metà.", '''
folder = Path(tempfile.mkdtemp(prefix="qt-save-"))
path = folder / "documento.txt"
file = QSaveFile(str(path))
ok = file.open(QIODevice.OpenModeFlag.WriteOnly)
if ok:
    file.write("Documento completo\\n".encode("utf-8"))
    ok = file.commit()
layout.addWidget(QLabel(str(path) if ok else file.errorString()))
''', "Compare il percorso di un file completo scritto mediante commit.", "File e persistenza")
qt("file-watcher", "Ricevere notifiche quando cambia un file", "Osservare un file temporaneo con QFileSystemWatcher.", '''
folder = Path(tempfile.mkdtemp(prefix="qt-watch-"))
path = folder / "watch.txt"
path.write_text("inizio", encoding="utf-8")
watcher = QFileSystemWatcher([str(path)], root)
label = QLabel(str(path))
watcher.fileChanged.connect(lambda changed: label.setText(f"Modificato: {changed}"))
button = QPushButton("Scrivi nel file osservato")
button.clicked.connect(lambda: path.write_text(QTime.currentTime().toString(), encoding="utf-8"))
layout.addWidget(label)
layout.addWidget(button)
''', "Premendo il pulsante arriva la notifica di modifica.", "File e persistenza")
qt("temporary-file", "Creare un file temporaneo gestito da Qt", "Mantenere il QTemporaryFile vivo per tutta la durata di utilizzo.", '''
root.temp = QTemporaryFile()
if root.temp.open():
    root.temp.write(b"temporary data")
    root.temp.flush()
    layout.addWidget(QLabel(root.temp.fileName()))
else:
    layout.addWidget(QLabel(root.temp.errorString()))
''', "Il percorso temporaneo esiste e verrà rimosso distruggendo l'oggetto.", "File e persistenza")
qt("elapsed", "Misurare la durata di un'operazione", "Usare QElapsedTimer per un intervallo monotono.", '''
timer = QElapsedTimer()
timer.start()
result = sum(range(50000))
layout.addWidget(QLabel(f"Risultato {result}; tempo {timer.nsecsElapsed() / 1_000_000:.3f} ms"))
''', "Compare la somma con una durata misurata sul computer corrente.", "Debug e diagnostica")
qt("version-info", "Visualizzare versioni Python e Qt", "Raccogliere dati diagnostici senza presumere la versione installata.", '''
layout.addWidget(QLabel(f"Python: {sys.version.split()[0]}\\nQt runtime: {qVersion()}"))
''', "La finestra riporta le versioni effettivamente in uso.", "Debug e diagnostica")
qt("screen", "Individuare geometria e scala dello schermo", "Leggere availableGeometry e devicePixelRatio dello schermo primario.", '''
screen = QGuiApplication.primaryScreen()
geometry = screen.availableGeometry()
layout.addWidget(QLabel(f"Area: {geometry.width()} × {geometry.height()}\\nScala: {screen.devicePixelRatio()}"))
''', "Sono mostrati i valori dello schermo attivo, senza forzare coordinate assolute.", "Debug e diagnostica")
qt("menu-button", "Associare un menu a un pulsante", "Creare un QToolButton con menu popup immediato.", '''
button = QToolButton()
button.setText("Esporta")
menu = QMenu(button)
label = QLabel("Scegli formato")
for name in ["JSON", "CSV"]:
    action = menu.addAction(name)
    action.triggered.connect(lambda checked=False, value=name: label.setText(value))
button.setMenu(menu)
button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
layout.addWidget(button)
layout.addWidget(label)
''', "Il menu distingue i formati e preserva il valore corretto in ogni callback.")
qt("button-box", "Disporre pulsanti standard secondo la piattaforma", "Usare QDialogButtonBox anche dentro una pagina di preferenze.", '''
buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Apply | QDialogButtonBox.StandardButton.Reset)
label = QLabel("Invariato")
buttons.clicked.connect(lambda button: label.setText(button.text()))
layout.addWidget(label)
layout.addWidget(buttons)
''', "Applica e Ripristina seguono l'ordinamento dello stile di sistema.")
qt("calendar", "Limitare le date selezionabili nel calendario", "Impostare un intervallo e mostrare la data selezionata.", '''
calendar = QCalendarWidget()
today = QDate.currentDate()
calendar.setDateRange(today, today.addDays(30))
label = QLabel(today.toString(Qt.DateFormat.ISODate))
calendar.selectionChanged.connect(lambda: label.setText(calendar.selectedDate().toString(Qt.DateFormat.ISODate)))
layout.addWidget(calendar)
layout.addWidget(label)
''', "Si selezionano soltanto i prossimi trenta giorni.")
qt("text-limit", "Limitare la lunghezza di un campo", "Imporre maxLength e rendere visibile il limite all'utente.", '''
edit = QLineEdit()
edit.setMaxLength(20)
label = QLabel("0 / 20")
edit.textChanged.connect(lambda value: label.setText(f"{len(value)} / 20"))
layout.addWidget(edit)
layout.addWidget(label)
''', "Il ventunesimo carattere non viene inserito.")
qt("multi-selection", "Leggere più righe selezionate", "Attivare ExtendedSelection e aggregare i testi selezionati.", '''
items = QListWidget()
items.addItems(["API", "GUI", "Database", "Test"])
items.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
label = QLabel()
items.itemSelectionChanged.connect(lambda: label.setText(", ".join(item.text() for item in items.selectedItems())))
layout.addWidget(items)
layout.addWidget(label)
''', "Ctrl+clic permette selezioni multiple e il riepilogo le elenca.")
qt("item-check", "Gestire una lista di attività spuntabili", "Usare ItemIsUserCheckable e CheckStateRole.", '''
items = QListWidget()
for name in ["Compila", "Esegui test", "Crea pacchetto"]:
    item = QListWidgetItem(name)
    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
    item.setCheckState(Qt.CheckState.Unchecked)
    items.addItem(item)
layout.addWidget(items)
''', "Ogni attività possiede una casella indipendente.")
qt("header-resize", "Adattare le colonne di una tabella", "Combinare ResizeToContents e Stretch per intestazioni leggibili.", '''
table = QTableWidget(1, 2)
table.setHorizontalHeaderLabels(["ID", "Descrizione"])
table.setItem(0, 0, QTableWidgetItem("12"))
table.setItem(0, 1, QTableWidgetItem("Colonna elastica"))
table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
layout.addWidget(table)
''', "ID occupa il minimo e Descrizione usa lo spazio rimasto.", "Layout e grafica")
qt("progress-cancel", "Annullare un'attività incrementale", "Controllare wasCanceled a ogni passo di un QProgressDialog non bloccante.", '''
dialog = QProgressDialog("Elaborazione locale", "Annulla", 0, 100, root)
dialog.setMinimumDuration(0)
dialog.setValue(0)
timer = QTimer(root)
def step():
    if dialog.wasCanceled() or dialog.value() >= 100:
        timer.stop()
        return
    dialog.setValue(dialog.value() + 1)
timer.timeout.connect(step)
timer.start(50)
layout.addWidget(QLabel("Usa Annulla nel dialogo di avanzamento"))
''', "Annulla ferma i passi successivi senza attendere un ciclo bloccante.", "Concorrenza")


def qt_source(binding, body):
    aliases = "Signal = pyqtSignal\nSlot = pyqtSlot\n" if binding == "PyQt6" else ""
    return clean(f'''import sys, json, sqlite3, tempfile, logging
from pathlib import Path
from {binding}.QtCore import *
from {binding}.QtGui import *
from {binding}.QtWidgets import *
{aliases}
def build(root, layout):
{textwrap.indent(body.rstrip(), "    ")}

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Ricetta Qt")
    window.resize(720, 480)
    layout = QVBoxLayout(window)
    build(window, layout)
    window.show()
    sys.exit(app.exec())
''')


def qt_notes_source(binding):
    return clean(f'''import sys, json
from pathlib import Path
from {binding}.QtCore import QStandardPaths, QCoreApplication
from {binding}.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QListWidget, QPushButton, QMessageBox

class Notes(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Note locali")
        QCoreApplication.setOrganizationName("Ricettario")
        QCoreApplication.setApplicationName("NoteLocali{binding}")
        self.path = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)) / "notes.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        layout = QVBoxLayout(self)
        self.edit = QLineEdit()
        self.edit.setPlaceholderText("Nuova nota")
        self.items = QListWidget()
        button = QPushButton("Aggiungi e salva")
        layout.addWidget(self.edit)
        layout.addWidget(button)
        layout.addWidget(self.items)
        button.clicked.connect(self.add)
        if self.path.exists():
            try:
                values = json.loads(self.path.read_text(encoding="utf-8"))
                if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
                    raise ValueError("Il file deve contenere un elenco di stringhe")
                self.items.addItems(values)
            except (OSError, ValueError) as exc:
                QMessageBox.warning(self, "Caricamento note", str(exc))
    def add(self):
        value = self.edit.text().strip()
        if not value:
            return
        values = [self.items.item(i).text() for i in range(self.items.count())] + [value]
        try:
            temporary = self.path.with_suffix(".tmp")
            temporary.write_text(json.dumps(values, ensure_ascii=False, indent=2), encoding="utf-8")
            temporary.replace(self.path)
        except OSError as exc:
            QMessageBox.warning(self, "Salvataggio note", str(exc))
            return
        self.items.addItem(value)
        self.edit.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Notes()
    window.resize(640, 420)
    window.show()
    sys.exit(app.exec())
''')


def build_python_qt():
    assert len(QT_TOPICS) >= 98, len(QT_TOPICS)
    for stack, binding, version, count in [("pyside6", "PySide6", "6.12", 98), ("pyqt6", "PyQt6", "6.11", 59)]:
        sources = ["https://doc.qt.io/qtforpython-6/", "https://doc.qt.io/qt-6/qtwidgets-index.html"]
        if stack == "pyqt6":
            sources = ["https://www.riverbankcomputing.com/static/Docs/PyQt6/", "https://doc.qt.io/qt-6/qtwidgets-index.html"]
        book = Book(stack, f"Python 3.13; {binding} {version}.x", sources, f"Python 3.13, ambiente virtuale dedicato e {binding}=={version}.*. Non installare entrambi i binding nello stesso ambiente.")
        commands = f"py -3.13 -m venv .venv\n.\\.venv\\Scripts\\python.exe -m pip install \"{binding}=={version}.*\"\n.\\.venv\\Scripts\\python.exe main.py"
        for key, title, description, code, expected, section in QT_TOPICS[:count]:
            if binding == "PyQt6":
                code = code.replace("accepted, font = QFontDialog.getFont", "font, accepted = QFontDialog.getFont")
            book.add(key, title, description, {"main.py": qt_source(binding, code)}, section=section, explanation=f"## Obiettivo\n{description}\n\n## Uso\nSalva main.py in una cartella nuova. Esegui i comandi da quella cartella. Il codice della ricetta si trova nella funzione `build`: i controlli appartengono alla finestra, i callback sono collegati prima di avviare il ciclo eventi.\n\n## Comportamento\n{expected}\n\n## Limiti\nEsempio desktop originale; esecuzione su macOS e Linux non attestata. I file temporanei, quando previsti, sono creati esclusivamente per questa dimostrazione.", expected=expected, commands=commands, tags=[key, "Qt Widgets", "signals", binding], errors=["ModuleNotFoundError: eseguire pip con lo stesso interprete .venv usato per avviare main.py.", "Non creare QApplication due volte nello stesso processo; riavviare l'esempio in un processo separato."])
        book.add("progetto-note", "Progetto completo: note locali con salvataggio atomico", "Una piccola app conserva note UTF-8 tra avvii e segnala gli errori di lettura o scrittura.", {"main.py": qt_notes_source(binding), "requirements.txt": f"{binding}=={version}.*\n", "README.md": "# Note locali\nAvvia main.py nell'ambiente dedicato. I dati risiedono in AppDataLocation. Il file notes.json contiene soltanto stringhe e non viene eseguito.\n"}, section="Progetti completi", project=True, commands=commands, explanation="## Progetto\nSalva tutti i file nella stessa cartella. Il pulsante aggiunge la nota soltanto dopo il successo della scrittura. Il caricamento valida l'elenco JSON; un errore viene mostrato senza interrompere l'interfaccia. Il file temporaneo viene sostituito nella stessa cartella per ridurre il rischio di salvataggi parziali.\n\n## Prova manuale\nAggiungi due note, chiudi e riapri. Le note devono ricomparire. Prova una stringa vuota: non deve essere aggiunta.", expected="Le note salvate ricompaiono dopo il riavvio.", tags=["project", "JSON", "persistence", "atomic save"], errors=["Accesso negato nella cartella dati: controllare i permessi AppDataLocation."])
        if stack == "pyside6":
            search = qt_source(binding, clean('''
connection = sqlite3.connect(":memory:")
connection.execute("CREATE VIRTUAL TABLE recipes USING fts5(title, body)")
connection.executemany("INSERT INTO recipes(title, body) VALUES (?, ?)", [("Avvia Python", "venv installazione"), ("Compila Qt", "cmake build debug"), ("Cerca SQLite", "database query fts")])
root.connection = connection
query = QLineEdit()
query.setPlaceholderText("Cerca titolo o contenuto")
items = QListWidget()
def search(text):
    items.clear()
    tokens = text.split()
    safe = " AND ".join('"' + token.replace('"', '""') + '"' for token in tokens)
    rows = connection.execute("SELECT title FROM recipes WHERE recipes MATCH ? ORDER BY bm25(recipes)", (safe,)).fetchall() if safe else connection.execute("SELECT title FROM recipes ORDER BY title").fetchall()
    items.addItems([row[0] for row in rows])
query.textChanged.connect(search)
layout.addWidget(query)
layout.addWidget(items)
search("")
'''))
            book.add("progetto-ricerca", "Progetto completo: ricerca locale SQLite FTS5", "Un catalogo dimostrativo ricerca titoli e contenuti senza interpretare operatori digitati dall'utente.", {"main.py": search, "requirements.txt": "PySide6==6.12.*\n", "README.md": "# Ricerca locale\nTre documenti in un database in memoria; nessuna rete e nessuna modifica a database esistenti.\n"}, project=True, section="Progetti completi", commands=commands, explanation="## Avvio\nSalva i tre file, installa requirements.txt nell'ambiente dedicato e avvia main.py. L'indice FTS5 contiene tre documenti dimostrativi. La query viene trasformata in termini quotati e passata come parametro SQL; quote e simboli non diventano istruzioni.\n\n## Prova\nCerca cmake: deve restare Compila Qt. Svuota il campo per ripristinare tutti i risultati. Questo esempio illustra la ricerca lessicale, senza sinonimi né correzione degli errori.", expected="cmake restituisce Compila Qt; campo vuoto mostra tre risultati.", tags=["project", "FTS5", "search"], errors=["no such module: fts5: usare un runtime Python con SQLite FTS5 incluso."])
        assert len(book.recipes) == STACKS[stack][2]
        save_book(book)


CPP_TOPICS = [
("label", "Testo selezionabile in QLabel", "Abilitare la selezione del testo senza un editor.", 'auto *w = new QLabel("Testo copiabile"); w->setTextInteractionFlags(Qt::TextSelectableByMouse); layout->addWidget(w);'),
("button", "Collegare un pulsante a una lambda", "Aggiornare un'etichetta tramite QObject::connect.", 'auto *b=new QPushButton("Saluta"); auto *label=new QLabel; layout->addWidget(b); layout->addWidget(label); QObject::connect(b,&QPushButton::clicked,label,[label]{label->setText("Ciao Qt");});'),
("lineedit", "Osservare le modifiche di un campo", "Ricevere textChanged senza interrogare periodicamente il controllo.", 'auto *edit=new QLineEdit; auto *label=new QLabel; layout->addWidget(edit); layout->addWidget(label); QObject::connect(edit,&QLineEdit::textChanged,label,&QLabel::setText);'),
("password", "Mascherare l'input di una password", "Impostare la modalità Password di QLineEdit.", 'auto *edit=new QLineEdit; edit->setPlaceholderText("Password"); edit->setEchoMode(QLineEdit::Password); layout->addWidget(edit);'),
("intvalidator", "Validare un intervallo di interi", "Limitare un input testuale mediante QIntValidator.", 'auto *edit=new QLineEdit; edit->setValidator(new QIntValidator(1,120,edit)); edit->setPlaceholderText("1–120"); layout->addWidget(edit);'),
("regex", "Validare un codice alfanumerico", "Accettare due lettere maiuscole e quattro cifre.", 'auto *edit=new QLineEdit; edit->setValidator(new QRegularExpressionValidator(QRegularExpression("[A-Z]{2}[0-9]{4}"),edit)); edit->setPlaceholderText("AB1234"); layout->addWidget(edit);'),
("spin", "Inserire una quantità a passi", "Configurare QSpinBox con limiti e suffisso.", 'auto *spin=new QSpinBox; spin->setRange(0,200); spin->setSingleStep(5); spin->setSuffix(" pezzi"); layout->addWidget(spin);'),
("decimal", "Inserire un importo decimale", "Configurare precisione e prefisso in QDoubleSpinBox.", 'auto *spin=new QDoubleSpinBox; spin->setRange(0,9999); spin->setDecimals(2); spin->setPrefix("EUR "); layout->addWidget(spin);'),
("combodata", "Associare dati alle voci di QComboBox", "Recuperare un identificatore diverso dal testo mostrato.", 'auto *combo=new QComboBox; combo->addItem("Sviluppo","dev"); combo->addItem("Produzione","prod"); auto *label=new QLabel("dev"); QObject::connect(combo,&QComboBox::currentIndexChanged,label,[combo,label](int){label->setText(combo->currentData().toString());}); layout->addWidget(combo); layout->addWidget(label);'),
("editablecombo", "Permettere un valore libero in un selettore", "Rendere modificabile la combo senza inserire automaticamente nuove righe.", 'auto *combo=new QComboBox; combo->addItems({"localhost","server"}); combo->setEditable(true); combo->setInsertPolicy(QComboBox::NoInsert); layout->addWidget(combo);'),
("tristate", "Rappresentare una preferenza ereditata", "Usare la condizione PartiallyChecked di QCheckBox.", 'auto *check=new QCheckBox("Log: parziale significa eredita"); check->setTristate(true); check->setCheckState(Qt::PartiallyChecked); layout->addWidget(check);'),
("radiobutton", "Creare opzioni radio esclusive", "Assegnare i controlli a un QButtonGroup con parent.", 'auto *group=new QButtonGroup(&window); for(const auto &name: {"JSON","CSV","XML"}) { auto *radio=new QRadioButton(name); group->addButton(radio); layout->addWidget(radio); }'),
("slider", "Pilotare una barra con uno slider", "Collegare direttamente segnali e slot compatibili.", 'auto *slider=new QSlider(Qt::Horizontal); auto *bar=new QProgressBar; slider->setRange(0,100); QObject::connect(slider,&QSlider::valueChanged,bar,&QProgressBar::setValue); layout->addWidget(slider); layout->addWidget(bar);'),
("date", "Scegliere una data dal calendario popup", "Mostrare date nel formato italiano senza parsing manuale.", 'auto *edit=new QDateEdit(QDate::currentDate()); edit->setCalendarPopup(true); edit->setDisplayFormat("dd/MM/yyyy"); layout->addWidget(edit);'),
("time", "Selezionare un orario", "Usare QTimeEdit in formato ore e minuti.", 'auto *edit=new QTimeEdit(QTime(9,30)); edit->setDisplayFormat("HH:mm"); layout->addWidget(edit);'),
("datetime", "Gestire una data con ora locale", "Usare QDateTimeEdit per un appuntamento.", 'auto *edit=new QDateTimeEdit(QDateTime::currentDateTime()); edit->setDisplayFormat("dd/MM/yyyy HH:mm"); edit->setCalendarPopup(true); layout->addWidget(edit);'),
("plain", "Mostrare sorgente monospazio", "Impedire il ritorno a capo automatico in QPlainTextEdit.", 'auto *edit=new QPlainTextEdit("int value = 42;\\n"); edit->setFont(QFontDatabase::systemFont(QFontDatabase::FixedFont)); edit->setLineWrapMode(QPlainTextEdit::NoWrap); layout->addWidget(edit);'),
("rich", "Renderizzare testo HTML statico", "Mostrare formattazione controllata in QTextBrowser.", 'auto *view=new QTextBrowser; view->setHtml("<h1>Guida</h1><p><b>Passo 1:</b> crea il progetto.</p>"); layout->addWidget(view);'),
("markdown", "Renderizzare una guida Markdown", "Usare il supporto Markdown di QTextBrowser.", 'auto *view=new QTextBrowser; view->setMarkdown("# Guida\\n\\n- Compila\\n- Avvia"); layout->addWidget(view);'),
("open", "Aprire un file di testo", "Leggere UTF-8 soltanto dopo la conferma del dialogo.", 'auto *edit=new QPlainTextEdit; auto *b=new QPushButton("Apri"); layout->addWidget(b); layout->addWidget(edit); QObject::connect(b,&QPushButton::clicked,&window,[&window,edit]{const auto path=QFileDialog::getOpenFileName(&window,"Apri"); if(path.isEmpty()) return; QFile f(path); if(f.open(QIODevice::ReadOnly)) edit->setPlainText(QString::fromUtf8(f.readAll())); else QMessageBox::warning(&window,"Lettura",f.errorString());});'),
("save", "Salvare testo con QSaveFile", "Scrivere UTF-8 e finalizzare il file mediante commit.", 'auto *edit=new QPlainTextEdit("Appunto"); auto *b=new QPushButton("Salva"); layout->addWidget(edit); layout->addWidget(b); QObject::connect(b,&QPushButton::clicked,&window,[&window,edit]{const auto path=QFileDialog::getSaveFileName(&window,"Salva"); if(path.isEmpty()) return; QSaveFile f(path); if(!f.open(QIODevice::WriteOnly) || f.write(edit->toPlainText().toUtf8())<0 || !f.commit()) QMessageBox::warning(&window,"Salvataggio",f.errorString());});'),
("directory", "Richiedere una cartella esistente", "Gestire il percorso scelto senza modificare il filesystem.", 'auto *b=new QPushButton("Cartella"); auto *label=new QLabel; layout->addWidget(b); layout->addWidget(label); QObject::connect(b,&QPushButton::clicked,&window,[&window,label]{auto path=QFileDialog::getExistingDirectory(&window,"Cartella"); if(!path.isEmpty()) label->setText(path);});'),
("color", "Applicare un colore scelto dall'utente", "Controllare QColor::isValid prima di aggiornare lo stile.", 'auto *b=new QPushButton("Colore"); layout->addWidget(b); QObject::connect(b,&QPushButton::clicked,&window,[&window,b]{auto c=QColorDialog::getColor(Qt::blue,&window); if(c.isValid()) b->setStyleSheet("background:"+c.name());});'),
("font", "Cambiare font con il dialogo standard", "Usare il parametro di esito del selettore caratteri.", 'auto *label=new QLabel("Clic per scegliere il carattere"); auto *b=new QPushButton("Font"); layout->addWidget(label); layout->addWidget(b); QObject::connect(b,&QPushButton::clicked,&window,[&window,label]{bool ok=false; auto font=QFontDialog::getFont(&ok,label->font(),&window); if(ok) label->setFont(font);});'),
("confirm", "Confermare lo svuotamento di un campo", "Usare No come risposta iniziale del dialogo.", 'auto *edit=new QLineEdit("Dato"); auto *b=new QPushButton("Svuota"); layout->addWidget(edit); layout->addWidget(b); QObject::connect(b,&QPushButton::clicked,&window,[&window,edit]{if(QMessageBox::question(&window,"Conferma","Svuotare?",QMessageBox::Yes|QMessageBox::No,QMessageBox::No)==QMessageBox::Yes) edit->clear();});'),
("input", "Richiedere un nome in un dialogo", "Distinguere una stringa confermata da Annulla.", 'auto *b=new QPushButton("Nome"); auto *label=new QLabel; layout->addWidget(b); layout->addWidget(label); QObject::connect(b,&QPushButton::clicked,&window,[&window,label]{bool ok=false; auto text=QInputDialog::getText(&window,"Nome","Nome:",QLineEdit::Normal,{},&ok); if(ok) label->setText(text);});'),
("form", "Allineare i campi di un modulo", "Inserire un QFormLayout nel layout principale.", 'auto *form=new QFormLayout; form->addRow("Nome",new QLineEdit); form->addRow("Email",new QLineEdit); layout->addLayout(form);'),
("grid", "Disporre controlli su una griglia", "Usare uno span per l'intestazione.", 'auto *grid=new QGridLayout; grid->addWidget(new QLabel("Titolo"),0,0,1,2); grid->addWidget(new QPushButton("A"),1,0); grid->addWidget(new QPushButton("B"),1,1); layout->addLayout(grid);'),
("split", "Ridimensionare pannelli con QSplitter", "Dare all'utente un divisore trascinabile.", 'auto *split=new QSplitter; split->addWidget(new QPlainTextEdit("Sorgente")); split->addWidget(new QPlainTextEdit("Risultato")); layout->addWidget(split);'),
("tabs", "Aggiungere pagine a QTabWidget", "Raggruppare editor e impostazioni in linguette.", 'auto *tabs=new QTabWidget; tabs->addTab(new QPlainTextEdit,"Codice"); tabs->addTab(new QLabel("Opzioni"),"Impostazioni"); layout->addWidget(tabs);'),
("stack", "Cambiare una pagina con QComboBox", "Collegare l'indice corrente allo stack di pagine.", 'auto *combo=new QComboBox; combo->addItems({"Home","Opzioni"}); auto *pages=new QStackedWidget; pages->addWidget(new QLabel("Benvenuto")); pages->addWidget(new QCheckBox("Log")); QObject::connect(combo,&QComboBox::currentIndexChanged,pages,&QStackedWidget::setCurrentIndex); layout->addWidget(combo); layout->addWidget(pages);'),
("scroll", "Scorrere un contenitore lungo", "Usare widgetResizable per adattare il contenuto all'area.", 'auto *area=new QScrollArea; auto *content=new QWidget; auto *form=new QFormLayout(content); for(int i=0;i<30;++i) form->addRow(QString("Campo %1").arg(i),new QLineEdit); area->setWidget(content); area->setWidgetResizable(true); layout->addWidget(area);'),
("group", "Abilitare un gruppo di opzioni", "Usare un QGroupBox checkable.", 'auto *group=new QGroupBox("Proxy"); group->setCheckable(true); auto *form=new QFormLayout(group); form->addRow("Host",new QLineEdit); layout->addWidget(group);'),
("list", "Popolare una lista semplice", "Usare QListWidget per pochi elementi statici.", 'auto *list=new QListWidget; list->addItems({"Python","C++","Rust"}); layout->addWidget(list);'),
("model", "Separare lista e modello stringhe", "Collegare QStringListModel a QListView.", 'auto *model=new QStringListModel(QStringList{"Ada","Linus"},&window); auto *view=new QListView; view->setModel(model); layout->addWidget(view);'),
("proxy", "Filtrare righe con QSortFilterProxyModel", "Applicare una ricerca case-insensitive al modello.", 'auto *model=new QStringListModel(QStringList{"Python","PySide6","Rust"},&window); auto *proxy=new QSortFilterProxyModel(&window); proxy->setSourceModel(model); proxy->setFilterCaseSensitivity(Qt::CaseInsensitive); auto *edit=new QLineEdit; QObject::connect(edit,&QLineEdit::textChanged,proxy,&QSortFilterProxyModel::setFilterFixedString); auto *view=new QListView; view->setModel(proxy); layout->addWidget(edit); layout->addWidget(view);'),
("table", "Creare una tabella di celle", "Mostrare intestazioni e contenuti in QTableWidget.", 'auto *table=new QTableWidget(2,2); table->setHorizontalHeaderLabels({"Nome","Valore"}); table->setItem(0,0,new QTableWidgetItem("Uno")); table->setItem(0,1,new QTableWidgetItem("1")); layout->addWidget(table);'),
("standard-model", "Popolare un modello tabellare standard", "Aggiungere righe QStandardItem a QTableView.", 'auto *model=new QStandardItemModel(&window); model->setHorizontalHeaderLabels({"Nome","Ruolo"}); model->appendRow({new QStandardItem("Ada"),new QStandardItem("Sviluppo")}); auto *view=new QTableView; view->setModel(model); layout->addWidget(view);'),
("tree", "Rappresentare categorie gerarchiche", "Aggiungere nodi figli a QTreeWidgetItem.", 'auto *tree=new QTreeWidget; tree->setHeaderLabel("Catalogo"); auto *parent=new QTreeWidgetItem(tree,{"Desktop"}); new QTreeWidgetItem(parent,{"Qt"}); tree->expandAll(); layout->addWidget(tree);'),
("filesystem", "Esplorare la cartella home", "Impostare rootPath e rootIndex di QFileSystemModel.", 'auto *model=new QFileSystemModel(&window); model->setRootPath(QDir::homePath()); model->setReadOnly(true); auto *view=new QTreeView; view->setModel(model); view->setRootIndex(model->index(QDir::homePath())); layout->addWidget(view);'),
("selection", "Leggere il dato della selezione corrente", "Collegarsi a currentChanged dopo avere assegnato il modello.", 'auto *model=new QStringListModel(QStringList{"Uno","Due"},&window); auto *view=new QListView; view->setModel(model); auto *label=new QLabel; QObject::connect(view->selectionModel(),&QItemSelectionModel::currentChanged,label,[label](const QModelIndex &now,const QModelIndex &){label->setText(now.data().toString());}); layout->addWidget(view); layout->addWidget(label);'),
("copy", "Copiare il contenuto di un editor", "Scrivere testo semplice negli appunti di sistema.", 'auto *edit=new QPlainTextEdit("int value = 42;"); auto *b=new QPushButton("Copia"); QObject::connect(b,&QPushButton::clicked,edit,[edit]{QGuiApplication::clipboard()->setText(edit->toPlainText());}); layout->addWidget(edit); layout->addWidget(b);'),
("paste", "Leggere gli appunti su richiesta", "Evitare il monitoraggio continuo del contenuto copiato.", 'auto *label=new QLabel; auto *b=new QPushButton("Leggi appunti"); QObject::connect(b,&QPushButton::clicked,label,[label]{label->setText(QGuiApplication::clipboard()->text());}); layout->addWidget(b); layout->addWidget(label);'),
("shortcut", "Assegnare Ctrl+F a un campo", "Creare QShortcut con contesto finestra.", 'auto *edit=new QLineEdit; edit->setPlaceholderText("Ricerca"); auto *shortcut=new QShortcut(QKeySequence::Find,&window); QObject::connect(shortcut,&QShortcut::activated,edit,[edit]{edit->setFocus();}); layout->addWidget(edit);'),
("menu", "Creare un menu File", "Usare QAction riutilizzabile con scorciatoia di chiusura.", 'auto *bar=new QMenuBar; auto *menu=bar->addMenu("File"); auto *action=menu->addAction("Chiudi"); action->setShortcut(QKeySequence::Close); QObject::connect(action,&QAction::triggered,&window,&QWidget::close); layout->setMenuBar(bar);'),
("toolbar", "Aggiungere una barra di strumenti", "Associare un'azione al riepilogo della finestra.", 'auto *bar=new QToolBar; auto *label=new QLabel("In attesa"); auto *action=bar->addAction("Aggiorna"); QObject::connect(action,&QAction::triggered,label,[label]{label->setText(QTime::currentTime().toString());}); layout->addWidget(bar); layout->addWidget(label);'),
("status", "Mostrare messaggi di stato temporanei", "Usare QStatusBar::showMessage con timeout.", 'auto *bar=new QStatusBar; auto *b=new QPushButton("Completa"); QObject::connect(b,&QPushButton::clicked,bar,[bar]{bar->showMessage("Completato",2000);}); layout->addWidget(b); layout->addWidget(bar);'),
("timer", "Aggiornare un orologio con il ciclo eventi", "Usare QTimer con parent per la durata del timer.", 'auto *label=new QLabel; auto *timer=new QTimer(&window); QObject::connect(timer,&QTimer::timeout,label,[label]{label->setText(QTime::currentTime().toString());}); timer->start(1000); layout->addWidget(label);'),
("once", "Eseguire un aggiornamento una sola volta", "Passare un contesto QObject a QTimer::singleShot.", 'auto *label=new QLabel("Attesa"); layout->addWidget(label); QTimer::singleShot(1000,label,[label]{label->setText("Pronto");});'),
("debounce", "Ritardare una ricerca durante la digitazione", "Riavviare un timer singleShot su textChanged.", 'auto *edit=new QLineEdit; auto *label=new QLabel; auto *timer=new QTimer(&window); timer->setSingleShot(true); timer->setInterval(250); QObject::connect(edit,&QLineEdit::textChanged,timer,[timer]{timer->start();}); QObject::connect(timer,&QTimer::timeout,label,[edit,label]{label->setText("Cerca: "+edit->text());}); layout->addWidget(edit); layout->addWidget(label);'),
("progress", "Incrementare un indicatore percentuale", "Fermare il timer quando la progress bar raggiunge il massimo.", 'auto *bar=new QProgressBar; bar->setValue(0); auto *timer=new QTimer(&window); QObject::connect(timer,&QTimer::timeout,bar,[bar,timer]{bar->setValue(bar->value()+10); if(bar->value()>=100) timer->stop();}); timer->start(200); layout->addWidget(bar);'),
("busy", "Mostrare attesa indeterminata", "Usare range 0–0 e ripristinare un range determinato alla fine.", 'auto *bar=new QProgressBar; bar->setRange(0,0); layout->addWidget(bar); QTimer::singleShot(1500,bar,[bar]{bar->setRange(0,1); bar->setValue(1);});'),
("settings", "Conservare una preferenza con QSettings", "Scrivere un valore quando la casella cambia stato.", 'auto *settings=new QSettings("Ricettario","CppDemo",&window); auto *check=new QCheckBox("Dettagli"); check->setChecked(settings->value("details",false).toBool()); QObject::connect(check,&QCheckBox::toggled,settings,[settings](bool v){settings->setValue("details",v);}); layout->addWidget(check);'),
("paths", "Ottenere la cartella dati applicativa", "Delegare la posizione dei dati a QStandardPaths.", 'QCoreApplication::setApplicationName("CppDemo"); auto path=QStandardPaths::writableLocation(QStandardPaths::AppDataLocation); layout->addWidget(new QLabel(path));'),
("json", "Serializzare un oggetto JSON Qt", "Costruire QJsonObject senza concatenare stringhe JSON.", 'QJsonObject object{{"nome","Ada"},{"attivo",true}}; auto *edit=new QPlainTextEdit(QString::fromUtf8(QJsonDocument(object).toJson(QJsonDocument::Indented))); edit->setReadOnly(true); layout->addWidget(edit);'),
("completion", "Suggerire parole durante l'input", "Installare un QCompleter nel campo.", 'auto *edit=new QLineEdit; auto *completion=new QCompleter(QStringList{"Python","PySide6","PostgreSQL"},&window); completion->setCaseSensitivity(Qt::CaseInsensitive); edit->setCompleter(completion); layout->addWidget(edit);'),
("find", "Cercare il testo selezionando il risultato", "Usare find di QPlainTextEdit per la prima occorrenza.", 'auto *edit=new QPlainTextEdit("Qt crea finestre. Qt gestisce eventi."); auto *b=new QPushButton("Trova Qt"); QObject::connect(b,&QPushButton::clicked,edit,[edit]{if(!edit->find("Qt")){edit->moveCursor(QTextCursor::Start);edit->find("Qt");}}); layout->addWidget(b); layout->addWidget(edit);'),
("tooltip", "Descrivere un controllo per mouse e lettore schermo", "Impostare tooltip e accessibleName espliciti.", 'auto *b=new QPushButton("?"); b->setToolTip("Apri la guida locale"); b->setAccessibleName("Guida"); layout->addWidget(b);'),
("locale", "Formattare importi con QLocale", "Usare locale italiana senza sostituire manualmente separatori.", 'QLocale locale(QLocale::Italian,QLocale::Italy); layout->addWidget(new QLabel(locale.toString(12345.67,\'f\',2)));'),
]

CPP_CMAKE = '''cmake_minimum_required(VERSION 3.24)
project(RicettaQt LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
find_package(Qt6 6.10 REQUIRED COMPONENTS Widgets)
qt_standard_project_setup()
qt_add_executable(RicettaQt main.cpp)
target_link_libraries(RicettaQt PRIVATE Qt6::Widgets)
'''

def build_cpp_qt():
    assert len(CPP_TOPICS) == 59, len(CPP_TOPICS)
    book = Book("qt-cpp", "C++17; Qt 6.10–6.12; CMake 3.24+", ["https://doc.qt.io/qt-6/qtwidgets-index.html", "https://doc.qt.io/qt-6/cmake-manual.html"], "Qt 6.10 o 6.12 desktop con compilatore coerente (MSVC2022 x64 su Windows), CMake e Ninja. Aprire il terminale Qt/MSVC già configurato.", ide=["Qt Creator", "Visual Studio", "VS Code"])
    commands = 'cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Debug\ncmake --build build\n.\\build\\RicettaQt.exe'
    for key, title, description, body in CPP_TOPICS:
        source = '#include <QtWidgets>\n#include <QtCore>\n#include <QtGui>\n\nint main(int argc, char **argv) {\n QApplication app(argc,argv);\n QWidget window; window.resize(720,480);\n auto *layout=new QVBoxLayout(&window);\n '+body+'\n window.show(); return app.exec();\n}\n'
        book.add(key, title, description, {"main.cpp": source, "CMakeLists.txt": CPP_CMAKE}, explanation=f"## Scopo\n{description}\n\n## Integrazione\nQuesto esempio è un eseguibile autonomo: salva main.cpp e CMakeLists.txt nella stessa cartella. Il corpo di main costruisce i controlli prima di entrare in app.exec(). I QObject hanno un parent o vengono adottati dal layout.\n\n## Avvio\nUsa un terminale Qt coerente con il compilatore selezionato. I comandi sono per Windows/Ninja; esecuzione su altri sistemi non attestata.\n\n## Risultato\n{title}. Il controllo aggiunto alla finestra dimostra esclusivamente il comportamento descritto.", commands=commands, expected=description, tags=[key, "Qt Widgets", "CMake", "C++17"], errors=["Qt6Config.cmake non trovato: usare il terminale Qt o impostare CMAKE_PREFIX_PATH alla propria installazione Qt.", "Non mescolare librerie Qt MinGW con un progetto compilato tramite MSVC."])
    notes = '''#include <QtWidgets>
int main(int argc,char **argv){
 QApplication app(argc,argv); QApplication::setOrganizationName("Ricettario"); QApplication::setApplicationName("CppNotes");
 QWidget window; window.setWindowTitle("Note C++"); auto *layout=new QVBoxLayout(&window);
 auto *edit=new QLineEdit; auto *list=new QListWidget; auto *button=new QPushButton("Aggiungi");
 QSettings settings; list->addItems(settings.value("notes").toStringList());
 layout->addWidget(edit); layout->addWidget(button); layout->addWidget(list);
 QObject::connect(button,&QPushButton::clicked,&window,[&settings,edit,list]{
  auto text=edit->text().trimmed(); if(text.isEmpty()) return;
  QStringList values; for(int i=0;i<list->count();++i) values<<list->item(i)->text(); values<<text;
  settings.setValue("notes",values); settings.sync();
  if(settings.status()!=QSettings::NoError){QMessageBox::warning(list,"Note","Impossibile salvare");return;}
  list->addItem(text); edit->clear();
 });
 window.resize(640,420); window.show(); return app.exec();
}
'''
    book.add("progetto-note", "Progetto completo: note persistenti in C++ Qt", "Gestire una lista di note con persistenza QSettings e controllo degli errori.", {"main.cpp": notes, "CMakeLists.txt": CPP_CMAKE, "README.md": "# Note C++\nCompila con Qt Widgets e CMake. QSettings conserva la lista notes nello spazio Ricettario/CppNotes.\n"}, section="Progetti completi", project=True, explanation="## Uso\nSalva tutti i file nella cartella, configura con CMake e avvia. Inserisci due note, chiudi e riapri per verificarne il ripristino. Il salvataggio avviene soltanto sul comando Aggiungi; il campo vuoto viene ignorato. QSettings usa il formato nativo della piattaforma. Nessuna verifica su Linux o macOS è dichiarata.", expected="Le note rimangono dopo il riavvio.", commands=commands, tags=["project", "QSettings", "persistence"], errors=["QSettings AccessError: la configurazione utente non è scrivibile."])
    assert len(book.recipes) == 60
    save_book(book)


def build_all():
    build_python_qt()
    build_cpp_qt()
    from desktop_managed import build_all as build_managed
    from desktop_electron import build_all as build_electron
    from build_workflow_tools import build_shells_git
    from workflow_build_containers import build_all as build_containers
    from workflow_ci_packaging import build_all as build_release
    build_managed()
    build_electron()
    build_shells_git()
    build_containers()
    build_release()
    from desktop_lifecycle import build_all as build_lifecycle
    build_lifecycle()


if __name__ == "__main__":
    build_all()
