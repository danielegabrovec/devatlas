from __future__ import annotations
import argparse
import hashlib
import html
from dataclasses import replace
from datetime import date
import json
import logging
import os
from pathlib import Path
import sys
import time
import traceback
import uuid
import unicodedata

from PySide6.QtCore import (QAbstractListModel, QEvent, QLockFile, QModelIndex, QObject, QRunnable, QSignalBlocker, QSize, Qt,
    QThreadPool, QTimer, QUrl, Signal)
from PySide6.QtGui import QAction, QActionGroup, QColor, QDesktopServices, QFont, QIcon, QKeySequence, QPainter
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QDialogButtonBox, QFileDialog,
    QFormLayout, QFrame, QGridLayout, QHBoxLayout, QHeaderView, QInputDialog, QLabel, QLineEdit, QListView,
    QMainWindow, QMenu, QMessageBox, QProgressBar, QPushButton, QScrollArea, QSizePolicy, QSplitter,
    QStackedWidget, QStyledItemDelegate, QTextEdit, QToolButton, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget)

from devatlas import __version__
from devatlas.bundles import export_project, load_bundle, readme, save_bundle, validate_recipe
from devatlas.catalog import Catalog
from devatlas.codewidgets import CodeBlock, CodeEditor, OfflineBrowser
from devatlas.editor import RecipeEditor
from devatlas.models import Recipe, SearchQuery, SECTIONS, STATUSES
from devatlas.paths import PACKAGE, user_directory
from devatlas.personal import PersonalStore
from devatlas.search import SearchIndex
from devatlas.templating import render_recipe
from devatlas.theme import apply_theme, THEMES
from devatlas.ui_components import (CardDelegate, FilterChip, FlowLayout, GridScrollPanel, LibraryLink,
    ResponsivePanel, StatePanel, local_icon)
from devatlas.qt_bootstrap import configure_qt_plugins, load_bundled_fonts, install_italian_translation


from devatlas.saved_searches import (SAVED_SEARCH_KEY, SAVED_SEARCH_FILTERS, SAVED_SEARCH_NAVIGATION,
    MAX_SAVED_SEARCHES, validate_saved_searches)


class ProfileInstance(QObject):
    """One index writer per profile; a second launch activates the existing UI."""
    activated = Signal()

    def __init__(self, directory: Path, parent=None):
        super().__init__(parent)
        self.lock = QLockFile(str(directory / "devatlas.lock"))
        self.lock.setStaleLockTime(0)
        identity = os.path.normcase(str(directory.resolve())).encode("utf-8")
        self.name = "devatlas-" + hashlib.sha256(identity).hexdigest()[:32]
        self.server = QLocalServer(self)
        self.server.setSocketOptions(QLocalServer.SocketOption.UserAccessOption)
        self.server.newConnection.connect(self.activate_pending)
        self.owned = False

    def acquire(self):
        self.owned = self.lock.tryLock(0)
        if not self.owned:
            if self.lock.error() != QLockFile.LockError.LockFailedError:
                raise OSError("Impossibile proteggere la cartella dati da aperture contemporanee.")
            socket = QLocalSocket(self)
            socket.connectToServer(self.name)
            if socket.waitForConnected(300):
                socket.write(b"activate")
                socket.waitForBytesWritten(300)
                socket.disconnectFromServer()
            socket.deleteLater()
            return False
        QLocalServer.removeServer(self.name)  # Only the lock owner may remove a stale endpoint.
        if not self.server.listen(self.name):
            self.lock.unlock()
            self.owned = False
            raise OSError("Impossibile inizializzare l’attivazione locale della finestra.")
        return True

    def activate_pending(self):
        while self.server.hasPendingConnections():
            socket = self.server.nextPendingConnection()
            socket.close()
            socket.deleteLater()
            self.activated.emit()

    def close(self):
        self.server.close()
        if self.owned:
            self.lock.unlock()
            self.owned = False


def startup_catalog(directory: Path, explicit: Path | None = None):
    if explicit is not None:
        return Catalog(explicit), ""
    local = directory / "catalogo-locale.json"
    if local.exists():
        try:
            return Catalog(local), ""
        except Exception as error:
            logging.warning("Catalogo locale non caricato: %s", error)
            return Catalog(), ("Il catalogo locale non è leggibile: è stato aperto il catalogo incluso. "
                "Il file catalogo-locale.json e i dati personali sono conservati nella cartella dati.")
    return Catalog(), ""


def label(text, name="", wrap=True):
    result = QLabel(text)
    result.setTextFormat(Qt.TextFormat.PlainText)
    result.setWordWrap(wrap)
    if name:
        result.setObjectName(name)
    return result


class ResultModel(QAbstractListModel):
    def __init__(self, recipes, stacks, parent=None):
        super().__init__(parent)
        self.recipes, self.stacks, self.ids = recipes, stacks, []

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.ids)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or index.row() >= len(self.ids):
            return None
        recipe = self.recipes.get(self.ids[index.row()])
        if recipe is None:
            return None
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.AccessibleTextRole):
            return recipe.title + ". " + recipe.summary
        if role == Qt.ItemDataRole.ToolTipRole:
            return recipe.summary
        if role == Qt.ItemDataRole.UserRole:
            return recipe
        return None

    def set_ids(self, ids, append=False):
        self.beginResetModel()
        self.ids = self.ids + ids if append else ids
        self.endResetModel()


class ResultDelegate(CardDelegate):
    """Compatibility name for the library card renderer."""


class SearchSignals(QObject):
    completed = Signal(int, object, str, bool)


class SearchWorker(QRunnable):
    def __init__(self, index, query, request, append):
        super().__init__()
        self.index, self.query, self.request, self.append = index, query, request, append
        self.signals = SearchSignals()

    def run(self):
        try:
            result = self.index.search(self.query)
            self.signals.completed.emit(self.request, result, "", self.append)
        except Exception as error:
            self.signals.completed.emit(self.request, None, str(error), self.append)


class IndexSignals(QObject):
    completed = Signal(int, str)


class IndexWorker(QRunnable):
    def __init__(self, index, recipes, fingerprint, generation, force=False):
        super().__init__()
        self.index, self.recipes, self.fingerprint = index, recipes, fingerprint
        self.generation, self.force = generation, force
        self.signals = IndexSignals()

    def run(self):
        try:
            self.index.rebuild(self.recipes, self.fingerprint, force=self.force)
            self.signals.completed.emit(self.generation, "")
        except Exception as error:
            self.signals.completed.emit(self.generation, str(error))


class MainWindow(QMainWindow):
    def __init__(self, catalog: Catalog, directory: Path):
        super().__init__()
        self.catalog, self.directory = catalog, directory
        self.store = PersonalStore(directory / "personali.sqlite")
        self.recipes = catalog.merged(self.store.list_recipes())
        self.index = SearchIndex(directory / "ricerca.sqlite")
        self.index_ready = False
        self.index_generation = 0
        self.index_job = None
        self.pending_index = None
        self.index_threadpool = QThreadPool(self)
        self.index_threadpool.setMaxThreadCount(1)
        self.threadpool = QThreadPool(self)
        self.threadpool.setMaxThreadCount(2)
        self.workers = {}
        self.request = 0
        self.last_search_request = -1
        self.last_search_text = ""
        self.last_search_result = None
        self.last_search_error = ""
        self.selection_filter = {}
        self.active_saved_search = None
        self.focus_mode = False
        self.focus_restore = None
        self.density = self.store.setting("density", "comfortable")
        if self.density not in ("comfortable", "compact"):
            self.density = "comfortable"
        QApplication.instance().setProperty("devatlasDensity", self.density)
        self.chip_signature = None
        self.active_chip_buttons = {}
        self.open_intent = None
        self.has_more_results = False
        self.results_state = "loading"
        self.state_action = None
        self.current_recipe = None
        self.current_parameters = {}
        self.parameter_cache = {}
        self.code_blocks = []
        self.notice_messages = []
        self.index_notice = ""
        self._sidebar_was_auto_hidden = False
        self.history = []
        self.history_position = -1
        self.record_navigation = True
        try:
            self.zoom = min(5, max(-2, int(self.store.setting("zoom", 0))))
        except (ValueError, TypeError):
            self.zoom = 0
        self.setWindowTitle("DevAtlas — Atlante del Codice")
        load_bundled_fonts()
        install_italian_translation(QApplication.instance())
        self.setWindowIcon(QIcon(str(PACKAGE / "assets" / "devatlas.svg")))
        self.resize(1540, 940)
        self.setMinimumSize(800, 520)
        self.build_ui()
        self.build_menus()
        apply_theme(QApplication.instance(), self.theme_combo.currentData(), self.zoom)
        QApplication.instance().styleHints().colorSchemeChanged.connect(self.system_theme_changed)
        self.rebuild_navigation()
        self.show_welcome()
        self.notice_personal_errors()
        self.schedule_search()
        geometry = self.store.setting("geometry")
        if isinstance(geometry, str) and geometry:
            from PySide6.QtCore import QByteArray
            self.restoreGeometry(QByteArray.fromBase64(geometry.encode()))
        split = self.store.setting("splitter")
        if isinstance(split, list) and len(split) == 3 and all(isinstance(n, int) and n >= 0 for n in split):
            self.splitter.setSizes(split)
        visibility = self.store.setting("panels_visibility")
        if isinstance(visibility, dict) and all(type(visibility.get(key)) is bool for key in ("sidebar", "results")):
            self.sidebar.setVisible(visibility["sidebar"] and self.width() >= 1000)
            self._sidebar_was_auto_hidden = visibility["sidebar"] and self.width() < 1000
            self.splitter.widget(1).setVisible(visibility["results"])
        self.statusBar().showMessage("Catalogo locale · nessuna connessione richiesta")
        self.queue_index()

    def build_ui(self):
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        header = QWidget()
        header.setObjectName("header")
        top = QHBoxLayout(header)
        top.setContentsMargins(18, 14, 18, 14)
        self.nav_toggle = QPushButton()
        self.nav_toggle.setIcon(QIcon(str(PACKAGE / "assets/menu.svg")))
        self.nav_toggle.setToolTip("Mostra o nascondi la navigazione")
        self.nav_toggle.setAccessibleName("Mostra navigazione")
        self.nav_toggle.clicked.connect(self.toggle_sidebar)
        top.addWidget(self.nav_toggle)
        brand = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(self.windowIcon().pixmap(38, 38))
        brand.addWidget(icon)
        brand_text = QVBoxLayout()
        brand_text.setSpacing(0)
        self.brand_name = label("DevAtlas", "brand", False)
        self.brand_caption = label("ATLANTE DEL CODICE", "eyebrow", False)
        brand_text.addWidget(self.brand_name)
        brand_text.addWidget(self.brand_caption)
        brand.addLayout(brand_text)
        top.addLayout(brand)
        top.addSpacing(22)
        self.search_edit = QLineEdit()
        self.search_edit.setObjectName("search")
        self.search_edit.setPlaceholderText("Cerca un obiettivo, un’API o un errore…   Ctrl+K")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.setAccessibleName("Cerca nel catalogo")
        self.search_edit.textChanged.connect(self.schedule_search)
        self.search_edit.returnPressed.connect(self.open_first_result)
        self.search_edit.installEventFilter(self)
        self.search_icon_action = self.search_edit.addAction(local_icon("search"), QLineEdit.ActionPosition.LeadingPosition)
        top.addWidget(self.search_edit, 1)
        self.theme_combo = QComboBox()
        self.theme_combo.setAccessibleName("Tema dell’interfaccia")
        for text, value in (("Sistema", "system"), ("Chiaro", "light"), ("Scuro", "dark")):
            self.theme_combo.addItem(text, value)
        self.theme_combo.setCurrentIndex(max(0, self.theme_combo.findData(self.store.setting("theme", "system"))))
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        top.addWidget(self.theme_combo)
        self.new_button = QPushButton("+ Nuova scheda")
        self.new_button.setObjectName("primary")
        self.new_button.clicked.connect(lambda: self.edit_recipe(None))
        top.addWidget(self.new_button)
        layout.addWidget(header)
        self.notice_frame = QFrame()
        self.notice_frame.setObjectName("notice")
        notice_row = QHBoxLayout(self.notice_frame)
        self.notice_label = label("")
        notice_row.addWidget(self.notice_label, 1)
        dismiss = QPushButton("Chiudi avviso")
        dismiss.clicked.connect(self.notice_frame.hide)
        notice_row.addWidget(dismiss)
        self.notice_frame.hide()
        layout.addWidget(self.notice_frame)
        self.destination_notice = QFrame()
        self.destination_notice.setObjectName("destinationNotice")
        destination_row = QHBoxLayout(self.destination_notice)
        self.destination_label = label("")
        destination_row.addWidget(self.destination_label, 1)
        self.destination_button = QPushButton("Mostra cartella")
        self.destination_button.clicked.connect(self.open_export_destination)
        destination_row.addWidget(self.destination_button)
        close_destination = QPushButton("×")
        close_destination.setAccessibleName("Chiudi conferma esportazione")
        close_destination.clicked.connect(self.destination_notice.hide)
        destination_row.addWidget(close_destination)
        self.destination_directory = None
        self.destination_notice.hide()
        layout.addWidget(self.destination_notice)
        self.index_status = QWidget()
        index_row = QHBoxLayout(self.index_status)
        index_row.setContentsMargins(18, 5, 18, 5)
        self.index_status_label = label("Preparazione della ricerca locale…", "muted")
        index_row.addWidget(self.index_status_label, 1)
        self.index_progress = QProgressBar()
        self.index_progress.setRange(0, 0)
        self.index_progress.setMaximumWidth(140)
        self.index_progress.setAccessibleName("Preparazione dell’indice locale")
        index_row.addWidget(self.index_progress)
        layout.addWidget(self.index_status)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setMinimumWidth(248)
        side = QVBoxLayout(self.sidebar)
        side.setContentsMargins(8, 14, 8, 12)
        side.addWidget(label("  LA TUA BIBLIOTECA", "eyebrow"))
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setColumnCount(2)
        self.tree.header().setStretchLastSection(False)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.header().setMinimumSectionSize(36)
        self.tree.setIndentation(15)
        self.tree.setAccessibleName("Navigazione del catalogo")
        self.tree.currentItemChanged.connect(self.select_navigation)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.collection_context_menu)
        side.addWidget(self.tree, 1)
        collection = QPushButton("+ Crea raccolta")
        collection.clicked.connect(self.create_collection)
        side.addWidget(collection)
        self.library_summary = label("", "muted")
        side.addWidget(self.library_summary)
        self.splitter.addWidget(self.sidebar)
        results = QWidget()
        results.setObjectName("resultsPanel")
        rv = QVBoxLayout(results)
        rv.setContentsMargins(14, 14, 14, 12)
        row = QHBoxLayout()
        self.count_label = label("Esplora il catalogo", "sectionTitle")
        row.addWidget(self.count_label, 1)
        self.filters_button = QPushButton("Filtri")
        self.filters_button.setCheckable(True)
        self.filters_button.setAccessibleName("Mostra o nascondi filtri")
        row.addWidget(self.filters_button)
        self.save_search_button = QPushButton("☆ Salva")
        self.save_search_button.setToolTip("Salva testo, filtri e biblioteca corrente")
        self.save_search_button.setAccessibleName("Salva ricerca corrente")
        self.save_search_button.clicked.connect(self.save_current_search)
        row.addWidget(self.save_search_button)
        rv.addLayout(row)
        self.active_label = label("Tutte le tecnologie", "muted")
        rv.addWidget(self.active_label)
        sort_row = QHBoxLayout()
        sort_row.addWidget(label("Ordina", "muted", False))
        self.sort_combo = QComboBox()
        self.sort_combo.setAccessibleName("Ordina risultati")
        self.sort_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.sort_combo.setMinimumContentsLength(9)
        for caption, value in (("Rilevanza", "relevance"), ("Titolo A–Z", "title"), ("Difficoltà", "difficulty"), ("Consultate prima", "recent")):
            self.sort_combo.addItem(caption, value)
        self.sort_combo.currentIndexChanged.connect(self.schedule_search)
        sort_row.addWidget(self.sort_combo, 1)
        rv.addLayout(sort_row)
        self.active_chip_scroll = QScrollArea()
        self.active_chip_scroll.setWidgetResizable(True)
        self.active_chip_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.active_chip_scroll.setMaximumHeight(96)
        self.active_chip_scroll.setAccessibleName("Filtri attivi rimovibili")
        self.active_chip_widget = QWidget()
        self.chip_layout = FlowLayout(self.active_chip_widget)
        self.active_chip_scroll.setWidget(self.active_chip_widget)
        self.active_chip_scroll.hide()
        rv.addWidget(self.active_chip_scroll)
        self.filter_panel = GridScrollPanel()
        fg = self.filter_panel.grid
        self.filter_grid = fg
        fg.setContentsMargins(0, 0, 0, 4)
        self.filters = {}
        options = {
            "section": [(s, s) for s in SECTIONS], "difficulty": [(s, s) for s in ("Base", "Intermedio", "Avanzato")],
            "os": [(s, s) for s in self.available_systems()],
            "shell": [(s, s) for s in ("PowerShell", "Bash", "CMD")],
            "ide": [(s, s) for s in sorted({i for r in self.recipes.values() for i in r.ide})],
            "status": [(v, k) for k, v in STATUSES.items()],
            "scope": [("Solo codice", "code"), ("Solo titoli", "title")],
        }
        names = {"section": "Sezione", "difficulty": "Difficoltà", "os": "Sistema", "shell": "Shell", "ide": "IDE", "status": "Verifica", "scope": "Dove cercare"}
        for number, (key, choices) in enumerate(options.items()):
            combo = QComboBox()
            combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
            combo.setMinimumContentsLength(12)
            combo.addItem(names[key] + (": ovunque" if key == "scope" else ": tutti"), "")
            for text, value in choices:
                combo.addItem(text, value)
            combo.setAccessibleName("Filtro " + names[key])
            combo.currentIndexChanged.connect(self.schedule_search)
            fg.addWidget(combo, number // 2, number % 2)
            self.filters[key] = combo
        reset = QPushButton("Azzera ricerca e filtri")
        self.reset_filters_button = reset
        reset.clicked.connect(self.reset_filters)
        fg.addWidget(reset, (len(options) + 1) // 2, 0, 1, 2)
        self.filter_columns = 2
        self.filter_panel.hide()
        self.filters_button.toggled.connect(self.filter_panel.setVisible)
        self.filter_panel.visibilityChanged.connect(self.sync_results_presentation)
        rv.addWidget(self.filter_panel)
        self.suggestion_button = QPushButton()
        self.suggestion_button.hide()
        self.suggestion_button.clicked.connect(lambda: self.search_edit.setText(self.suggestion_button.property("query")))
        rv.addWidget(self.suggestion_button)
        self.results_list = QListView()
        self.results_list.setAccessibleName("Risultati della ricerca")
        self.results_list.setUniformItemSizes(True)
        self.results_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.results_list.setWordWrap(True)
        self.model = ResultModel(self.recipes, self.catalog.stacks, self)
        self.results_list.setModel(self.model)
        self.result_delegate = ResultDelegate(self.catalog.stacks, self.results_list)
        self.results_list.setItemDelegate(self.result_delegate)
        self.results_list.selectionModel().currentChanged.connect(self.select_result)
        self.results_stack = QStackedWidget()
        self.results_stack.addWidget(self.results_list)
        self.result_state_panel = StatePanel()
        self.result_state_panel.actionRequested.connect(self.trigger_state_action)
        self.results_stack.addWidget(self.result_state_panel)
        self.empty_label = self.result_state_panel.description
        rv.addWidget(self.results_stack, 1)
        self.more_button = QPushButton("Carica altri risultati")
        self.more_button.clicked.connect(lambda: self.run_search(append=True))
        rv.addWidget(self.more_button)
        self.splitter.addWidget(results)
        reader_panel = ResponsivePanel()
        self.reader_panel = reader_panel
        reader_panel.setObjectName("reader")
        rp = QVBoxLayout(reader_panel)
        rp.setContentsMargins(0, 0, 0, 0)
        self.reader_toolbar = QWidget()
        self.reader_toolbar_grid = QGridLayout(self.reader_toolbar)
        self.reader_toolbar_grid.setContentsMargins(12, 10, 12, 10)
        self.reader_toolbar_grid.setSpacing(4)
        self.reader_nav_group = QWidget()
        rt = QHBoxLayout(self.reader_nav_group)
        rt.setContentsMargins(0, 0, 0, 0)
        rt.setSpacing(4)
        self.back_button = QPushButton("←")
        self.back_button.setAccessibleName("Ricetta precedente")
        self.back_button.clicked.connect(lambda: self.navigate(-1))
        self.forward_button = QPushButton("→")
        self.forward_button.setAccessibleName("Ricetta successiva")
        self.forward_button.clicked.connect(lambda: self.navigate(1))
        for button in (self.back_button, self.forward_button):
            button.setObjectName("iconButton")
            button.setFixedWidth(32)
        rt.addWidget(self.back_button)
        rt.addWidget(self.forward_button)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Vista rapida", "Vista guidata"])
        reader_mode = self.store.setting("reader_mode", 0)
        self.mode_combo.setCurrentIndex(reader_mode if reader_mode in (0, 1) else 0)
        self.mode_combo.setAccessibleName("Modalità di lettura")
        self.mode_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.mode_combo.setMinimumContentsLength(10)
        self.mode_combo.currentIndexChanged.connect(self.render_current)
        rt.addWidget(self.mode_combo)
        rt.addStretch()
        self.reader_actions_group = QWidget()
        rt = QHBoxLayout(self.reader_actions_group)
        rt.setContentsMargins(0, 0, 0, 0)
        rt.setSpacing(4)
        self.favorite_button = QPushButton("☆")
        self.favorite_button.setObjectName("iconButton")
        self.favorite_button.setFixedWidth(32)
        self.favorite_button.setAccessibleName("Aggiungi o rimuovi dai preferiti")
        self.favorite_button.clicked.connect(self.toggle_favorite)
        rt.addWidget(self.favorite_button)
        self.focus_button = QToolButton()
        self.focus_button.setObjectName("iconButton")
        self.focus_button.setCheckable(True)
        self.focus_button.setFixedWidth(32)
        self.focus_button.setAccessibleName("Modalità focus lettura")
        self.focus_button.setToolTip("Concentra la lettura · F8")
        self.focus_button.clicked.connect(self.toggle_focus_mode)
        rt.addWidget(self.focus_button)
        self.recipe_menu_button = QPushButton("Azioni ▾")
        menu = QMenu(self)
        menu.addAction("Modifica / crea copia personale", lambda: self.edit_recipe(self.current_recipe))
        menu.addAction("Confronta codice con un’altra scheda…", self.compare_current)
        menu.addAction("Aggiungi a una raccolta…", self.add_to_collection)
        menu.addAction("Rimuovi dalla raccolta corrente", self.remove_from_collection)
        menu.addAction("Note personali…", self.edit_note)
        menu.addAction("Esporta scheda modificabile…", self.export_recipe_bundle)
        menu.addAction("Copia guida Markdown", self.copy_guide)
        menu.addSeparator()
        menu.addAction("Elimina scheda personale…", self.delete_personal)
        self.recipe_menu_button.setMenu(menu)
        rt.addWidget(self.recipe_menu_button)
        self.export_button = QPushButton("Esporta progetto ▾")
        self.export_button.setObjectName("primary")
        export_menu = QMenu(self)
        export_menu.addAction("Cartella con file e istruzioni…", lambda: self.export_current(False))
        export_menu.addAction("Archivio ZIP con file e istruzioni…", lambda: self.export_current(True))
        self.export_button.setMenu(export_menu)
        rt.addWidget(self.export_button)
        self.reader_toolbar_grid.addWidget(self.reader_nav_group, 0, 0)
        self.reader_toolbar_grid.addWidget(self.reader_actions_group, 0, 1)
        self.reader_controls_wrapped = False
        reader_panel.resized.connect(self.layout_reader_controls)
        rp.addWidget(self.reader_toolbar)
        self.guided_toolbar = QWidget()
        guided_row = QHBoxLayout(self.guided_toolbar)
        guided_row.setContentsMargins(20, 6, 20, 8)
        self.guided_previous = QPushButton("← Passo")
        self.guided_previous.setAccessibleName("Passo precedente del percorso")
        self.guided_previous.clicked.connect(lambda: self.guided_navigate(-1))
        guided_row.addWidget(self.guided_previous)
        self.guided_label = label("", "muted")
        guided_row.addWidget(self.guided_label, 1)
        self.guided_completed = QPushButton("Segna completato")
        self.guided_completed.setCheckable(True)
        self.guided_completed.clicked.connect(self.toggle_guided_completed)
        guided_row.addWidget(self.guided_completed)
        self.guided_next = QPushButton("Passo →")
        self.guided_next.setAccessibleName("Passo successivo del percorso")
        self.guided_next.clicked.connect(lambda: self.guided_navigate(1))
        guided_row.addWidget(self.guided_next)
        self.guided_toolbar.hide()
        rp.addWidget(self.guided_toolbar)
        self.reader_scroll = QScrollArea()
        self.reader_scroll.setWidgetResizable(True)
        self.reader_scroll.setAccessibleName("Lettore della ricetta")
        rp.addWidget(self.reader_scroll, 1)
        self.splitter.addWidget(reader_panel)
        self.splitter.setSizes([248, 380, 900])
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setStretchFactor(2, 3)
        self.splitter.splitterMoved.connect(self.resize_active_chips)
        layout.addWidget(self.splitter, 1)
        self.setCentralWidget(central)
        self.debounce = QTimer(self)
        self.debounce.setSingleShot(True)
        self.debounce.setInterval(160)
        self.debounce.timeout.connect(self.run_search)
        self.parameter_timer = QTimer(self)
        self.parameter_timer.setSingleShot(True)
        self.parameter_timer.setInterval(400)
        self.parameter_timer.timeout.connect(self.refresh_parameter_preview)

    def layout_reader_controls(self):
        if not hasattr(self, "reader_actions_group"):
            return
        required = self.reader_nav_group.minimumSizeHint().width() + self.reader_actions_group.minimumSizeHint().width() + 32
        wrapped = self.reader_panel.width() < required
        if wrapped != self.reader_controls_wrapped:
            self.reader_controls_wrapped = wrapped
            self.reader_toolbar_grid.removeWidget(self.reader_nav_group)
            self.reader_toolbar_grid.removeWidget(self.reader_actions_group)
            self.reader_toolbar_grid.addWidget(self.reader_nav_group, 0, 0, 1, 2 if wrapped else 1)
            self.reader_toolbar_grid.addWidget(self.reader_actions_group, 1 if wrapped else 0, 0 if wrapped else 1,
                                                1, 2 if wrapped else 1)

    def set_results_state(self, state, title="", description="", action="", callback=None):
        self.results_state = state
        self.state_action = callback
        if state == "results":
            self.results_stack.setCurrentWidget(self.results_list)
        else:
            self.result_state_panel.set_state(title, description, action)
            self.results_stack.setCurrentWidget(self.result_state_panel)
        self.sync_results_presentation()

    def trigger_state_action(self):
        if self.state_action:
            self.state_action()

    def show_export_destination(self, directory):
        self.destination_directory = Path(directory).resolve()
        text = str(self.destination_directory)
        self.destination_label.setText("Esportazione completata · " + (text if len(text) < 100 else text[:45] + "…" + text[-45:]))
        self.destination_label.setToolTip("<p>" + html.escape(text) + "</p>")
        self.destination_notice.show()

    def open_export_destination(self):
        if self.destination_directory is not None:
            if self.destination_directory.is_dir():
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.destination_directory)))
            else:
                self.statusBar().showMessage("La cartella esportata non è più disponibile.")

    def sync_results_presentation(self, *args):
        if not hasattr(self, "results_stack") or not hasattr(self, "more_button"):
            return
        filters_open = self.filter_panel.isVisible()
        editing = filters_open and (self.width() < 1100 or self.height() < 720)
        self.filter_panel.setMaximumHeight(16777215 if editing else 240)
        self.filter_panel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding if editing else QSizePolicy.Policy.Preferred)
        self.results_stack.setVisible(not editing)
        self.active_chip_scroll.setVisible(bool(self.active_chip_buttons) and not filters_open)
        self.more_button.setVisible(self.has_more_results and self.results_state == "results" and not editing)
        self.filters_button.setText("Risultati" if editing else "Filtri" + (f" ({len(self.active_chip_buttons)})" if self.active_chip_buttons else ""))
        if self.filters_button.isChecked() != filters_open:
            with QSignalBlocker(self.filters_button):
                self.filters_button.setChecked(filters_open)

    def active_filter_specs(self):
        specs = []
        nav = self.selection_filter
        if nav.get("stack"):
            caption = self.catalog.stacks.get(nav["stack"], {}).get("label", nav["stack"])
            specs.append(("stack", ("Percorso: " if nav.get("guided") else "") + caption))
        if nav.get("group"):
            specs.append(("group", nav["group"]))
        special = nav.get("special")
        if special:
            specs.append(("special", {"favorites": "Preferiti", "history": "Cronologia", "personal": "Schede personali"}.get(special, special)))
        if nav.get("collection"):
            specs.append(("collection", "Raccolta: " + dict(self.store.collections()).get(nav["collection"], "non disponibile")))
        if nav.get("only_projects"):
            specs.append(("only_projects", "Progetti completi"))
        prefixes = {"section": "Obiettivo", "difficulty": "Livello", "os": "Sistema", "shell": "Shell", "ide": "IDE", "status": "Verifica", "scope": "Cerca"}
        for key, combo in self.filters.items():
            value = nav.get("section") if key == "section" and nav.get("section") else combo.currentData()
            if value:
                caption = combo.itemText(combo.findData(value)) if combo.findData(value) >= 0 else str(value)
                specs.append((key, prefixes[key] + ": " + caption))
        return specs

    def refresh_active_filters(self):
        if not hasattr(self, "chip_layout"):
            return
        specs = self.active_filter_specs()
        signature = tuple(specs)
        if signature != self.chip_signature:
            self.chip_signature = signature
            while self.chip_layout.count():
                item = self.chip_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.active_chip_buttons = {}
            for key, caption in specs:
                chip = FilterChip(caption)
                chip.clicked.connect(lambda checked=False, value=key: self.remove_active_filter(value))
                self.chip_layout.addWidget(chip)
                self.active_chip_buttons[key] = chip
        self.resize_active_chips()
        self.sync_results_presentation()

    def resize_active_chips(self, *args):
        if hasattr(self, "active_chip_scroll"):
            width = max(140, self.active_chip_scroll.viewport().width())
            height = self.chip_layout.heightForWidth(width) + 4
            self.active_chip_scroll.setFixedHeight(min(96, max(34, height)))

    def remove_active_filter(self, key):
        if key in self.filters:
            self.filters[key].setCurrentIndex(0)
        self.selection_filter.pop(key, None)
        if key == "stack":
            self.selection_filter.pop("guided", None)
        if not self.active_saved_search:
            item = self.navigation_item(self.selection_filter)
            with QSignalBlocker(self.tree):
                self.tree.setCurrentItem(item)
            self.active_label.setText(item.text(0) if item else "Ricerca personalizzata")
        self.update_collection_actions()
        self.update_guided_navigation()
        self.schedule_search()

    def criteria_signature(self):
        return (self.search_edit.text(), tuple((key, combo.currentData()) for key, combo in self.filters.items()),
                self.sort_combo.currentData(), json.dumps(self.selection_filter, sort_keys=True))

    def results_are_current(self):
        return self.index_ready and self.last_search_request == self.request and not self.debounce.isActive()

    def select_first_current_result(self):
        if not self.results_are_current() or not self.model.ids:
            return False
        rid = self.model.ids[0]
        self.results_list.setCurrentIndex(self.model.index(0))
        if not self.current_recipe or self.current_recipe.id != rid:
            self.open_recipe(rid)
        self.results_list.setFocus()
        return True

    def open_first_result(self):
        if self.select_first_current_result():
            return
        self.open_intent = self.criteria_signature()
        if self.index_ready and self.request not in self.workers:
            self.debounce.stop()
            self.run_search()

    def eventFilter(self, watched, event):
        if watched is self.search_edit and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Down and self.results_are_current() and self.model.ids:
                self.select_first_current_result()
                return True
            if event.key() == Qt.Key.Key_Escape and self.focus_mode:
                self.toggle_focus_mode(False)
                return True
        return super().eventFilter(watched, event)

    def toggle_focus_mode(self, enabled=None):
        enabled = not self.focus_mode if enabled is None else bool(enabled)
        if enabled == self.focus_mode or enabled and not self.current_recipe:
            return
        if enabled:
            self.focus_restore = {"sidebar": self.sidebar.isVisible(), "results": self.splitter.widget(1).isVisible(), "sizes": self.splitter.sizes()}
            self.sidebar.hide()
            self.splitter.widget(1).hide()
        else:
            restore = self.focus_restore or {"sidebar": True, "results": True, "sizes": [248, 380, 900]}
            self.sidebar.setVisible(restore["sidebar"] and self.width() >= 1000)
            self._sidebar_was_auto_hidden = restore["sidebar"] and self.width() < 1000
            self.splitter.widget(1).setVisible(restore["results"])
            self.splitter.setSizes(restore["sizes"])
        self.focus_mode = enabled
        self.focus_button.setChecked(enabled)
        self.focus_action.setChecked(enabled)
        self.focus_escape_action.setEnabled(enabled)
        self.focus_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon if enabled else Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.focus_button.setText("Esci dal focus" if enabled else "")
        self.focus_button.setFixedWidth(self.fontMetrics().horizontalAdvance("Esci dal focus") + 50 if enabled else 32)
        self.layout_reader_controls()

    def change_density(self, value):
        if value not in ("comfortable", "compact"):
            return
        self.density = value
        self.store.set_setting("density", value)
        QApplication.instance().setProperty("devatlasDensity", value)
        apply_theme(QApplication.instance(), self.theme_combo.currentData(), self.zoom)
        self.results_list.doItemsLayout()
        self.results_list.viewport().update()
        self.refresh_visuals()

    def refresh_visuals(self):
        theme = THEMES[QApplication.instance().property("devatlasTheme") or "light"]
        self.nav_toggle.setIcon(local_icon("library", theme["accent"]))
        self.focus_button.setIcon(local_icon("focus", theme["accent"]))
        self.filters_button.setIcon(local_icon("filter", theme["muted"], 16))
        self.search_icon_action.setIcon(local_icon("search", theme["muted"]))
        self.tree.setIconSize(QSize(18, 18))
        root_font = QFont(QApplication.font())
        root_font.setWeight(QFont.Weight.DemiBold)
        root_font.setPointSizeF(max(8, root_font.pointSizeF() - 1))
        def decorate(item, top=False):
            if not item.text(1):
                item.setFirstColumnSpanned(True)
            data = item.data(0, Qt.ItemDataRole.UserRole) or {}
            group = data.get("group", "")
            if data.get("stack"):
                group = self.catalog.stacks.get(data["stack"], {}).get("group", "")
            symbol = {"Linguaggi": "code", "Desktop e GUI": "desktop", "Web e backend": "web", "Database": "database", "Strumenti": "tools"}.get(group)
            if not symbol:
                symbol = "bookmark" if data.get("saved_search") or item.text(0) == "Ricerche salvate" else "folder" if data.get("collection") or item.text(0) == "Le mie raccolte" else "route" if data.get("guided") or item.text(0) == "Percorsi guidati" else "project" if data.get("only_projects") else {"favorites": "star", "history": "clock", "personal": "person"}.get(data.get("special"), "library")
            item.setIcon(0, local_icon(symbol, theme["accent"] if data.get("stack") else theme["muted"], 18))
            item.setForeground(1, QColor(theme["muted"]))
            if top:
                item.setFont(0, root_font)
            for number in range(item.childCount()):
                decorate(item.child(number))
        for index in range(self.tree.topLevelItemCount()):
            decorate(self.tree.topLevelItem(index), True)
        self.adapt_header()
        self.layout_reader_controls()

    def adapt_header(self):
        if hasattr(self, "brand_caption"):
            self.brand_caption.setVisible(self.width() >= 1200 and self.zoom < 3)
            self.brand_name.setVisible(self.width() >= 1000 or self.zoom < 2)

    def build_menus(self):
        file = self.menuBar().addMenu("File")
        def action(menu, title, callback, shortcut=None):
            item = QAction(title, self)
            item.triggered.connect(callback)
            if shortcut:
                item.setShortcut(QKeySequence(shortcut))
            menu.addAction(item)
            return item
        action(file, "Nuova scheda personale…", lambda: self.edit_recipe(None), "Ctrl+N")
        action(file, "Importa schede o backup…", self.import_bundle, "Ctrl+I")
        self.export_collection_action = action(file, "Esporta raccolta corrente…", self.export_collection)
        self.rename_collection_action = action(file, "Rinomina raccolta corrente…", lambda: self.rename_collection())
        self.delete_collection_action = action(file, "Elimina raccolta corrente…", lambda: self.delete_collection())
        file.addSeparator()
        action(file, "Salva ricerca corrente…", self.save_current_search)
        self.update_saved_action = action(file, "Aggiorna ricerca salvata corrente", self.update_saved_search)
        self.rename_saved_action = action(file, "Rinomina ricerca salvata…", self.rename_saved_search)
        self.delete_saved_action = action(file, "Elimina ricerca salvata…", self.delete_saved_search)
        action(file, "Crea backup personale…", self.backup_personal)
        file.addSeparator()
        action(file, "Aggiorna catalogo da pacchetto locale…", self.update_catalog)
        action(file, "Ricostruisci indice di ricerca", self.rebuild_index)
        file.addSeparator()
        action(file, "Esci", self.close, "Ctrl+Q")
        view = self.menuBar().addMenu("Visualizza")
        action(view, "Cerca", self.focus_search, "Ctrl+K")
        self.command_action = action(view, "Palette comandi…", self.show_command_palette, "Ctrl+P")
        action(view, "Cerca nel codice della ricetta…", self.find_in_recipe, "Ctrl+F")
        self.focus_action = action(view, "Focus lettura", self.toggle_focus_mode, "F8")
        self.focus_action.setCheckable(True)
        self.focus_escape_action = action(view, "Esci dal focus lettura", lambda: self.toggle_focus_mode(False), "Esc")
        self.focus_escape_action.setEnabled(False)
        action(view, "Aumenta caratteri", lambda: self.adjust_zoom(1), "Ctrl++")
        action(view, "Riduci caratteri", lambda: self.adjust_zoom(-1), "Ctrl+-")
        action(view, "Dimensione originale", lambda: self.adjust_zoom(-self.zoom), "Ctrl+0")
        action(view, "Mostra / nascondi risultati", lambda: self.splitter.widget(1).setVisible(not self.splitter.widget(1).isVisible()), "Ctrl+Shift+L")
        density_menu = view.addMenu("Densità della biblioteca")
        self.density_actions = {}
        density_group = QActionGroup(self)
        density_group.setExclusive(True)
        for caption, value in (("Comoda", "comfortable"), ("Compatta", "compact")):
            item = QAction(caption, self)
            item.setCheckable(True)
            item.setChecked(self.density == value)
            item.triggered.connect(lambda checked=False, v=value: self.change_density(v))
            density_group.addAction(item)
            density_menu.addAction(item)
            self.density_actions[value] = item
        help_menu = self.menuBar().addMenu("Aiuto")
        action(help_menu, "Guida e scorciatoie", self.show_help, "F1")
        action(help_menu, "Informazioni su DevAtlas", self.about)

    def palette_commands(self):
        from devatlas.commandpalette import Command
        commands = []
        def collect(menu, category):
            for number, item in enumerate(menu.actions()):
                if item.isSeparator():
                    continue
                if item.menu():
                    collect(item.menu(), item.text().replace("&", ""))
                elif item is not self.command_action:
                    commands.append(Command(id=f"menu:{category}:{number}:{item.text()}", title=item.text().replace("&", ""), category=category,
                        callback=item.trigger, shortcut=item.shortcut().toString(), enabled=item.isEnabled()))
        for item in self.menuBar().actions():
            if item.menu():
                collect(item.menu(), item.text().replace("&", ""))
        for key, caption, callback in (("compare", "Confronta codice", self.compare_current), ("note", "Note personali", self.edit_note),
                                      ("favorite", "Aggiungi o rimuovi preferito", self.toggle_favorite)):
            commands.append(Command(id="reader:" + key, title=caption, category="Scheda", callback=callback, enabled=self.current_recipe is not None))
        for sid, spec in sorted(self.catalog.stacks.items(), key=lambda pair: pair[1]["label"].casefold()):
            if len(commands) >= 230:
                break
            commands.append(Command(id="technology:" + sid, title=spec["label"], category="Tecnologie", description="Esplora le schede di questa tecnologia",
                callback=lambda s=sid: self.select_stack(s), keywords=(sid,)))
        for rid in self.store.history()[:10]:
            recipe = self.recipes.get(rid)
            if recipe:
                commands.append(Command(id="recent:" + rid, title=recipe.title, category="Consultate di recente",
                    description=self.catalog.stacks.get(recipe.stack, {}).get("label", recipe.stack), callback=lambda r=rid: self.open_recipe(r)))
        for entry in self.saved_searches():
            if len(commands) >= 250:
                break
            commands.append(Command(id="saved:" + entry["id"], title=entry["name"], category="Ricerche salvate",
                description=entry["text"] or "Applica i filtri salvati", callback=lambda r=entry["id"]: self.activate_saved_search(r)))
        return commands[:250]

    def activate_saved_search(self, rid):
        item = self.navigation_item({"saved_search": rid})
        if item is not None and self.tree.currentItem() is not item:
            self.tree.setCurrentItem(item)
        else:
            self.restore_saved_search(rid)

    def show_command_palette(self):
        from devatlas.commandpalette import CommandPalette
        dialog = CommandPalette(self.palette_commands(), self)
        try:
            dialog.exec()
        finally:
            dialog.deleteLater()

    def rebuild_navigation(self):
        selected = {"saved_search": self.active_saved_search} if self.active_saved_search else dict(self.selection_filter)
        expanded = {self.tree.topLevelItem(i).text(0): self.tree.topLevelItem(i).isExpanded() for i in range(self.tree.topLevelItemCount())}
        with QSignalBlocker(self.tree):
            self.tree.clear()
            for text, data in (("Tutto il catalogo", {}), ("Preferiti", {"special": "favorites"}),
                ("Cronologia", {"special": "history"}), ("Schede personali", {"special": "personal"}),
                ("Progetti completi", {"only_projects": True})):
                item = QTreeWidgetItem([text])
                item.setData(0, Qt.ItemDataRole.UserRole, data)
                self.tree.addTopLevelItem(item)
            saved = QTreeWidgetItem(["Ricerche salvate"])
            self.tree.addTopLevelItem(saved)
            for entry in sorted(self.saved_searches(), key=lambda e: e["name"].casefold()):
                item = QTreeWidgetItem([entry["name"]])
                item.setData(0, Qt.ItemDataRole.UserRole, {"saved_search": entry["id"]})
                item.setToolTip(0, "<p>" + html.escape(entry["text"] or "Ricerca con filtri salvati") + "</p>")
                saved.addChild(item)
            saved.setExpanded(True)
            groups = ["Linguaggi", "Desktop e GUI", "Web e backend", "Database", "Strumenti"]
            groups += sorted({s["group"] for s in self.catalog.stacks.values()} - set(groups))
            for group in groups:
                root = QTreeWidgetItem([group])
                root.setData(0, Qt.ItemDataRole.UserRole, {"group": group})
                self.tree.addTopLevelItem(root)
                for sid, spec in self.catalog.stacks.items():
                    if spec["group"] != group:
                        continue
                    count = sum(r.stack == sid for r in self.recipes.values())
                    item = QTreeWidgetItem([spec["label"], str(count)])
                    item.setTextAlignment(1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    item.setData(0, Qt.ItemDataRole.UserRole, {"stack": sid})
                    root.addChild(item)
                root.setExpanded(group == "Web e backend")
            sections = QTreeWidgetItem(["Per obiettivo"])
            self.tree.addTopLevelItem(sections)
            for section in SECTIONS:
                item = QTreeWidgetItem([section])
                item.setData(0, Qt.ItemDataRole.UserRole, {"section": section})
                sections.addChild(item)
            paths = QTreeWidgetItem(["Percorsi guidati"])
            self.tree.addTopLevelItem(paths)
            for stack, spec in sorted(self.catalog.stacks.items(), key=lambda pair: pair[1]["label"].casefold()):
                if sum(r.stack == stack for r in self.catalog.recipes.values()) < 2:
                    continue
                item = QTreeWidgetItem([spec["label"]])
                item.setData(0, Qt.ItemDataRole.UserRole, {"stack": stack, "guided": True})
                paths.addChild(item)
            collections = QTreeWidgetItem(["Le mie raccolte"])
            self.tree.addTopLevelItem(collections)
            for cid, name in self.store.collections():
                item = QTreeWidgetItem([name])
                item.setData(0, Qt.ItemDataRole.UserRole, {"collection": cid})
                collections.addChild(item)
            collections.setExpanded(True)
            for i in range(self.tree.topLevelItemCount()):
                item = self.tree.topLevelItem(i)
                if item.text(0) in expanded:
                    item.setExpanded(expanded[item.text(0)])
            found = self.navigation_item(selected)
            if found is not None:
                self.tree.setCurrentItem(found)
                self.active_label.setText(("Ricerca: " if self.active_saved_search else "") + found.text(0))
        self.update_collection_actions()
        self.update_saved_actions()
        self.library_summary.setText(f"{len(self.catalog.recipes):,} schede · {len(self.catalog.stacks)} percorsi\nContenuti disponibili offline".replace(",", "."))
        self.refresh_visuals()

    def available_systems(self):
        systems = {system for recipe in self.recipes.values() for system in recipe.os if system.strip()}
        preferred = ["Windows", "Linux", "macOS", "Android", "iOS", "Web"]
        return [system for system in preferred if system in systems] + sorted(systems - set(preferred), key=str.casefold)

    def refresh_dynamic_filters(self):
        for key, choices in (("os", self.available_systems()), ("ide", sorted({i for r in self.recipes.values() for i in r.ide if i.strip()}, key=str.casefold))):
            combo = self.filters[key]
            current = combo.currentData()
            placeholder = combo.itemText(0)
            blocked = combo.blockSignals(True)
            combo.clear()
            combo.addItem(placeholder, "")
            for choice in choices:
                combo.addItem(choice, choice)
            combo.setCurrentIndex(max(0, combo.findData(current)))
            combo.blockSignals(blocked)

    def layout_filters(self):
        columns = 1 if self.width() < 1100 else 2
        if self.filter_columns == columns:
            return
        self.filter_columns = columns
        for number, combo in enumerate(self.filters.values()):
            self.filter_grid.removeWidget(combo)
            self.filter_grid.addWidget(combo, number // columns, number % columns)
        self.filter_grid.removeWidget(self.reset_filters_button)
        self.filter_grid.addWidget(self.reset_filters_button, (len(self.filters) + columns - 1) // columns, 0, 1, columns)

    def saved_searches(self, strict=False):
        try:
            # The raw preflight distinguishes an absent preference from a damaged
            # JSON row; the standard setting() fallback deliberately hides that.
            with self.store.connect() as db:
                row = db.execute("SELECT value FROM settings WHERE key=?", (SAVED_SEARCH_KEY,)).fetchone()
            value = json.loads(row[0]) if row else {"version": 1, "items": []}
            return validate_saved_searches(value)
        except (ValueError, TypeError, UnicodeError) as error:
            message = "Le ricerche salvate non sono leggibili. I dati originali sono conservati: crea un backup prima di recuperarli."
            if strict:
                raise ValueError(message) from error
            self.show_notice(message)
            return []

    def write_saved_searches(self, items):
        items = validate_saved_searches({"version": 1, "items": items})
        self.store.set_setting(SAVED_SEARCH_KEY, {"version": 1, "items": items})

    def search_snapshot(self, rid, name):
        return {"id": rid, "name": unicodedata.normalize("NFC", name.strip()), "text": self.search_edit.text(),
                "filters": {**{key: combo.currentData() or "" for key, combo in self.filters.items()}, "sort": self.sort_combo.currentData() or "relevance"},
                "navigation": {key: value for key, value in self.selection_filter.items() if key in SAVED_SEARCH_NAVIGATION}}

    def save_current_search(self):
        try:
            items = self.saved_searches(strict=True)
            if len(items) >= MAX_SAVED_SEARCHES:
                raise ValueError(f"Hai raggiunto {MAX_SAVED_SEARCHES} ricerche. Elimina una ricerca prima di aggiungerne un’altra.")
            name, accepted = QInputDialog.getText(self, "Salva ricerca", "Nome della ricerca (massimo 80 caratteri)", text=self.search_edit.text()[:60])
            if not accepted:
                return
            rid = uuid.uuid4().hex
            items.append(self.search_snapshot(rid, name))
            self.write_saved_searches(items)
            self.active_saved_search = rid
            self.rebuild_navigation()
            self.statusBar().showMessage("Ricerca salvata con testo e filtri")
        except Exception as error:
            self.show_error("Impossibile salvare la ricerca", error)

    def update_saved_actions(self):
        active = bool(self.active_saved_search and any(e["id"] == self.active_saved_search for e in self.saved_searches()))
        for action in (self.update_saved_action, self.rename_saved_action, self.delete_saved_action):
            action.setEnabled(active)

    def update_saved_search(self):
        try:
            items = self.saved_searches(strict=True)
            entry = next((e for e in items if e["id"] == self.active_saved_search), None)
            if entry is None:
                return
            self.write_saved_searches([self.search_snapshot(e["id"], e["name"]) if e is entry else e for e in items])
            self.rebuild_navigation()
            self.statusBar().showMessage("Ricerca salvata aggiornata")
        except Exception as error:
            self.show_error("Impossibile aggiornare la ricerca", error)

    def rename_saved_search(self, rid=None):
        rid = rid or self.active_saved_search
        try:
            items = self.saved_searches(strict=True)
            entry = next((e for e in items if e["id"] == rid), None)
            if entry is None:
                return
            name, accepted = QInputDialog.getText(self, "Rinomina ricerca", "Nuovo nome", text=entry["name"])
            if accepted:
                entry["name"] = unicodedata.normalize("NFC", name.strip())
                self.write_saved_searches(items)
                self.rebuild_navigation()
        except Exception as error:
            self.show_error("Impossibile rinominare la ricerca", error)

    def delete_saved_search(self, rid=None):
        rid = rid or self.active_saved_search
        try:
            items = self.saved_searches(strict=True)
            entry = next((e for e in items if e["id"] == rid), None)
            if entry is None:
                return
            if QMessageBox.question(self, "Elimina ricerca salvata", f"Eliminare la ricerca «{entry['name']}»?\nLe schede e le raccolte restano conservate.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
                return
            self.write_saved_searches([e for e in items if e["id"] != rid])
            if self.active_saved_search == rid:
                self.active_saved_search = None
            self.rebuild_navigation()
        except Exception as error:
            self.show_error("Impossibile eliminare la ricerca", error)

    def restore_saved_search(self, rid):
        entry = next((e for e in self.saved_searches() if e["id"] == rid), None)
        if entry is None:
            self.show_notice("La ricerca selezionata non è più disponibile.")
            return
        navigation = dict(entry["navigation"])
        missing = []
        if navigation.get("stack") and navigation["stack"] not in self.catalog.stacks:
            navigation.pop("stack")
            navigation.pop("guided", None)
            missing.append("tecnologia")
        if navigation.get("collection") and navigation["collection"] not in dict(self.store.collections()):
            navigation.pop("collection")
            missing.append("raccolta")
        if navigation.get("section") and navigation["section"] not in SECTIONS:
            navigation.pop("section")
            missing.append("sezione")
        if navigation.get("group") and navigation["group"] not in {s["group"] for s in self.catalog.stacks.values()}:
            navigation.pop("group")
            missing.append("gruppo")
        self.selection_filter = navigation
        self.active_saved_search = rid
        blocked = self.search_edit.blockSignals(True)
        self.search_edit.setText(entry["text"])
        self.search_edit.blockSignals(blocked)
        for key, combo in self.filters.items():
            value = entry["filters"].get(key, "")
            index = combo.findData(value)
            if index < 0:
                missing.append(key)
            blocked = combo.blockSignals(True)
            combo.setCurrentIndex(max(0, index))
            combo.blockSignals(blocked)
        with QSignalBlocker(self.sort_combo):
            self.sort_combo.setCurrentIndex(max(0, self.sort_combo.findData(entry["filters"].get("sort") or "relevance")))
        self.active_label.setText("Ricerca: " + entry["name"])
        self.update_collection_actions()
        self.update_saved_actions()
        if navigation.get("guided"):
            self.mode_combo.setCurrentIndex(1)
            ids, done = self.guided_ids(), self.guided_done()
            if ids:
                self.open_recipe(next((item for item in ids if item not in done), ids[0]))
        self.update_guided_navigation()
        if missing:
            self.show_notice("Ricerca ripristinata senza riferimenti non più disponibili: " + ", ".join(dict.fromkeys(missing)) + ".")
        self.schedule_search()

    def navigation_item(self, data):
        def visit(item):
            if item.data(0, Qt.ItemDataRole.UserRole) == data:
                return item
            for index in range(item.childCount()):
                result = visit(item.child(index))
                if result is not None:
                    return result
            return None
        for index in range(self.tree.topLevelItemCount()):
            result = visit(self.tree.topLevelItem(index))
            if result is not None:
                return result
        return None

    def focus_search(self):
        self.search_edit.setFocus()
        self.search_edit.selectAll()

    def toggle_sidebar(self):
        if self.focus_mode:
            self.toggle_focus_mode(False)
            self.sidebar.show()
            self._sidebar_was_auto_hidden = False
            return
        self._sidebar_was_auto_hidden = False
        self.sidebar.setVisible(not self.sidebar.isVisible())

    def show_notice(self, text):
        if text not in self.notice_messages:
            self.notice_messages.append(text)
        self.notice_label.setText("\n".join(self.notice_messages))
        self.notice_frame.show()

    def notice_personal_errors(self):
        errors = getattr(self.catalog, "personal_errors", [])
        if errors:
            logging.warning("Schede personali non caricate: %s", errors)
            self.show_notice(f"{len(errors)} schede personali non sono state caricate perché non valide. "
                "I dati originali sono conservati nel profilo; i dettagli sono nel registro locale.")

    def update_collection_actions(self):
        enabled = bool(self.selection_filter.get("collection"))
        self.rename_collection_action.setEnabled(enabled)
        self.delete_collection_action.setEnabled(enabled)

    def guided_ids(self):
        stack = self.selection_filter.get("stack")
        if not self.selection_filter.get("guided"):
            return []
        ordered = []
        for section in SECTIONS:
            rows = sorted((r for r in self.recipes.values() if r.stack == stack and r.section == section and not r.project and not r.personal), key=lambda r: r.title.casefold())
            ordered.extend(r.id for r in rows[:2])
        projects = sorted((r for r in self.recipes.values() if r.stack == stack and r.project and not r.personal), key=lambda r: r.title.casefold())
        ordered.extend(r.id for r in projects[:2])
        return ordered

    def guided_done(self):
        progress = self.store.setting("guided_progress", {})
        if not isinstance(progress, dict):
            return set()
        values = progress.get(self.selection_filter.get("stack"), [])
        return {rid for rid in values if isinstance(rid, str)} if isinstance(values, list) else set()

    def update_guided_navigation(self):
        ids = self.guided_ids()
        rid = self.current_recipe.id if self.current_recipe else None
        visible = rid in ids
        self.guided_toolbar.setVisible(visible)
        if not visible:
            return
        position = ids.index(rid)
        done = self.guided_done()
        self.guided_label.setText(f"Passo {position + 1} di {len(ids)} · {len(done.intersection(ids))} completati")
        self.guided_previous.setEnabled(position > 0)
        self.guided_next.setEnabled(position + 1 < len(ids))
        self.guided_completed.setChecked(rid in done)
        self.guided_completed.setText("✓ Completato" if rid in done else "Segna completato")

    def guided_navigate(self, delta):
        ids = self.guided_ids()
        if self.current_recipe and self.current_recipe.id in ids:
            position = ids.index(self.current_recipe.id) + delta
            if 0 <= position < len(ids):
                self.open_recipe(ids[position])

    def toggle_guided_completed(self):
        if not self.current_recipe or self.current_recipe.id not in self.guided_ids():
            return
        done = self.guided_done()
        rid = self.current_recipe.id
        done.discard(rid) if rid in done else done.add(rid)
        progress = self.store.setting("guided_progress", {})
        if not isinstance(progress, dict):
            progress = {}
        progress[self.selection_filter["stack"]] = sorted(done)
        try:
            self.store.set_setting("guided_progress", progress)
        except Exception as error:
            self.show_error("Impossibile salvare l’avanzamento", error)
        self.update_guided_navigation()

    def select_navigation(self, item, previous=None):
        if item is None:
            return
        data = item.data(0, Qt.ItemDataRole.UserRole) or {}
        if data.get("saved_search"):
            self.restore_saved_search(data["saved_search"])
            return
        self.active_saved_search = None
        self.selection_filter = data
        if self.selection_filter.get("guided"):
            self.mode_combo.setCurrentIndex(1)
            self.search_edit.clear()
            for combo in self.filters.values():
                combo.setCurrentIndex(0)
            ids = self.guided_ids()
            done = self.guided_done()
            if ids:
                self.open_recipe(next((rid for rid in ids if rid not in done), ids[0]))
        self.active_label.setText(item.text(0))
        self.update_collection_actions()
        self.update_saved_actions()
        self.update_guided_navigation()
        self.schedule_search()

    def query(self):
        data = {key: combo.currentData() or "" for key, combo in self.filters.items()}
        data["sort"] = self.sort_combo.currentData() or "relevance"
        if data["sort"] == "recent":
            data["recent_ids"] = self.store.history()
        selected = self.selection_filter
        data.update({key: selected[key] for key in ("stack", "group", "section", "only_projects") if key in selected})
        if selected.get("special") == "favorites":
            data["ids"] = self.store.favorites()
        elif selected.get("special") == "history":
            data["ids"] = self.store.history()
        elif selected.get("special") == "personal":
            data["ids"] = [r.id for r in self.recipes.values() if r.personal]
        elif selected.get("collection"):
            data["ids"] = self.store.collection_ids(selected["collection"])
        elif selected.get("guided"):
            data["ids"] = self.guided_ids()
        return SearchQuery(text=self.search_edit.text(), **data)

    def schedule_search(self, *args):
        if hasattr(self, "debounce"):
            self.refresh_active_filters()
            # Invalidate immediately, before the debounce, so old requests cannot flash stale rows.
            self.request += 1
            if self.index_ready:
                self.debounce.start()

    def queue_index(self, force=False):
        """Coalesce edits while one worker owns the index; never wait in the UI."""
        self.request += 1
        self.debounce.stop()
        self.index_generation += 1
        self.index_ready = False
        self.index_status.show()
        self.index_progress.show()
        self.index_status_label.setText("Preparazione della ricerca locale… Puoi continuare a leggere e modificare le schede.")
        self.count_label.setText("Preparazione ricerca…")
        self.results_list.setEnabled(False)
        self.more_button.setEnabled(False)
        self.export_collection_action.setEnabled(False)
        self.set_results_state("loading", "Prepariamo la ricerca", "Puoi continuare a leggere e modificare le schede mentre l’indice viene aggiornato.", "Guida rapida", self.show_help)
        if self.pending_index:
            force = force or self.pending_index[-1]
        self.pending_index = (self.index_generation, dict(self.recipes), self.catalog.fingerprint, force)
        if self.index_job is None:
            self.start_index_job()

    def start_index_job(self):
        generation, recipes, fingerprint, force = self.pending_index
        self.pending_index = None
        worker = IndexWorker(self.index, recipes, fingerprint, generation, force)
        worker.signals.completed.connect(self.index_finished)
        self.index_job = worker
        self.index_threadpool.start(worker)

    def index_finished(self, generation, error):
        self.index_job = None
        if self.pending_index is not None:
            self.start_index_job()
            return
        if generation != self.index_generation:
            return
        self.index_progress.hide()
        if error:
            self.index_status_label.setText("Ricerca non disponibile. Riprova con File → Ricostruisci indice di ricerca.")
            self.count_label.setText("Ricerca non disponibile")
            self.index_notice = "Impossibile aggiornare l’indice locale. Schede e dati personali sono conservati. Dettaglio: " + error
            self.show_notice(self.index_notice)
            self.set_results_state("error", "Ricerca non disponibile", "Il catalogo e i dati personali restano conservati. Riprova a ricostruire l’indice locale.", "Ricostruisci indice", self.rebuild_index)
            logging.error("Indicizzazione non riuscita: %s", error)
            return
        self.index_ready = True
        if self.index_notice in self.notice_messages:
            self.notice_messages.remove(self.index_notice)
            self.notice_label.setText("\n".join(self.notice_messages))
            self.notice_frame.setVisible(bool(self.notice_messages))
        self.index_notice = ""
        self.index_status.hide()
        self.results_list.setEnabled(True)
        self.export_collection_action.setEnabled(True)
        self.count_label.setText("Ricerca…")
        self.statusBar().showMessage("Catalogo pronto · ricerca in preparazione")
        self.schedule_search()

    def run_search(self, append=False):
        if not self.index_ready:
            return
        self.request += 1
        request = self.request
        query = self.query()
        if append:
            query.offset = len(self.model.ids)
        self.count_label.setText("Ricerca…" if not append else self.count_label.text())
        if not append:
            self.set_results_state("loading", "Cerchiamo nella biblioteca", "Stiamo selezionando le ricette che rispondono alla tua ricerca.")
            self.statusBar().showMessage("Ricerca locale in corso…")
        self.more_button.setEnabled(False)
        worker = SearchWorker(self.index, query, request, append)
        worker.signals.completed.connect(self.search_finished)
        self.workers[request] = worker
        self.threadpool.start(worker)

    def search_finished(self, request, result, error, append):
        self.workers.pop(request, None)
        if request != self.request:
            return
        self.last_search_request = request
        self.last_search_text = self.search_edit.text()
        self.last_search_result = result
        self.last_search_error = error
        self.more_button.setEnabled(True)
        if error:
            self.count_label.setText("Ricerca non disponibile")
            self.statusBar().showMessage(error)
            self.open_intent = None
            self.set_results_state("error", "Non riusciamo a cercare", "Riprova la ricerca. Se il problema continua, ricostruisci l’indice dal menu File.", "Riprova", self.run_search)
            return
        ids = result.ids
        if self.selection_filter.get("guided") and not self.search_edit.text().strip():
            order = {rid: position for position, rid in enumerate(self.guided_ids())}
            ids = sorted(ids, key=lambda rid: order.get(rid, len(order)))
        self.model.set_ids(ids, append)
        self.count_label.setText(f"{result.total:,} risultati".replace(",", "."))
        self.has_more_results = len(self.model.ids) < result.total
        if result.total:
            self.set_results_state("results")
        else:
            self.set_results_state("empty", "Nessuna ricetta trovata", "Prova una parola diversa oppure rimuovi un filtro attivo.", "Azzera ricerca e filtri", self.reset_filters)
        self.suggestion_button.setVisible(bool(result.suggestions))
        if result.suggestions:
            self.suggestion_button.setText("Forse cercavi: " + result.suggestions[0])
            self.suggestion_button.setProperty("query", result.suggestions[0])
        self.statusBar().showMessage(f"Ricerca locale · {result.elapsed_ms:.0f} ms · {len(self.model.ids)} risultati caricati")
        if self.open_intent is not None:
            intent = self.open_intent
            self.open_intent = None
            if intent == self.criteria_signature():
                self.select_first_current_result()

    def reset_filters(self):
        self.active_saved_search = None
        self.selection_filter = {}
        self.search_edit.clear()
        for combo in self.filters.values():
            combo.setCurrentIndex(0)
        self.sort_combo.setCurrentIndex(0)
        self.active_label.setText("Tutte le tecnologie")
        self.tree.setCurrentItem(self.tree.topLevelItem(0))
        self.update_saved_actions()
        self.schedule_search()

    def select_result(self, index, previous=None):
        if index.isValid() and index.row() < len(self.model.ids):
            self.open_recipe(self.model.ids[index.row()])

    def open_recipe(self, rid, record=True):
        recipe = self.recipes.get(rid)
        if recipe is None:
            return
        if self.current_recipe is not None:
            self.parameter_cache[self.current_recipe.id] = dict(self.current_parameters)
        self.parameter_timer.stop()
        self.current_recipe = recipe
        cached = self.parameter_cache.get(rid, {})
        self.current_parameters = {p["name"]: cached.get(p["name"], str(p.get("default", ""))) for p in recipe.parameters}
        self.store.visit(rid)
        if record:
            self.history = self.history[:self.history_position + 1]
            if not self.history or self.history[-1] != rid:
                self.history.append(rid)
            self.history_position = len(self.history) - 1
        self.render_current()
        self.update_guided_navigation()
        self.reader_scroll.verticalScrollBar().setValue(0)

    def navigate(self, delta):
        position = self.history_position + delta
        if 0 <= position < len(self.history):
            self.history_position = position
            self.open_recipe(self.history[position], record=False)

    def install_reader(self, body):
        old = self.reader_scroll.takeWidget()
        self.reader_scroll.setWidget(body)
        if old:
            old.deleteLater()

    def show_welcome(self):
        if self.focus_mode:
            self.toggle_focus_mode(False)
        self.current_recipe = None
        self.code_blocks = []
        self.guided_toolbar.hide()
        body = QWidget()
        body.setObjectName("reader")
        layout = QVBoxLayout(body)
        layout.setContentsMargins(32, 30, 32, 32)
        layout.setSpacing(18)
        layout.addWidget(label("LA TUA BIBLIOTECA OPERATIVA", "eyebrow"))
        layout.addWidget(label("Il codice giusto,\nquando ti serve.", "heroTitle"))
        layout.addWidget(label("Esempi, passaggi e comandi per trasformare un’idea in un progetto. Cerca un obiettivo o scegli da dove iniziare.", "muted"))
        stats = QHBoxLayout()
        stats.setSpacing(12)
        for value, caption in ((f"{len(self.catalog.recipes):,}".replace(",", "."), "ricette"),
            (str(len(self.catalog.stacks)), "tecnologie"), (str(sum(r.project for r in self.catalog.recipes.values())), "progetti completi")):
            panel = QFrame()
            panel.setObjectName("statCard")
            pv = QVBoxLayout(panel)
            pv.setContentsMargins(16, 13, 16, 13)
            pv.setSpacing(2)
            pv.addWidget(label(value, "recipeTitle"))
            pv.addWidget(label(caption, "muted"))
            stats.addWidget(panel)
        layout.addLayout(stats)
        layout.addWidget(label("Scegli il prossimo passo", "sectionTitle"))
        quick = ResponsivePanel()
        grid = QGridLayout(quick)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(12)
        examples = [("Creare un’API", "FastAPI · rotte, dati e test", "fastapi", "web"),
                    ("Costruire un’interfaccia", "React · componenti e interazioni", "react", "web"),
                    ("Aprire una finestra desktop", "PySide6 · widget e finestre", "pyside6", "desktop"),
                    ("Lavorare con i dati", "PostgreSQL · query e database", "postgresql", "database")]
        examples = [row for row in examples if row[2] in self.catalog.stacks]
        if not examples:
            examples = [(spec["label"], "Esplora le ricette", sid, "library") for sid, spec in list(self.catalog.stacks.items())[:4]]
        buttons = []
        for title, caption, stack, symbol in examples:
            button = LibraryLink(title, caption, symbol)
            button.clicked.connect(lambda checked=False, value=stack: self.select_stack(value))
            buttons.append(button)
        columns = [0]
        def arrange():
            value = 2 if quick.width() >= 620 else 1
            if columns[0] == value:
                return
            columns[0] = value
            for number, button in enumerate(buttons):
                grid.removeWidget(button)
                grid.addWidget(button, number // value, number % value)
        quick.resized.connect(arrange)
        arrange()
        layout.addWidget(quick)
        layout.addWidget(label("Richiama azioni, tecnologie e ricette recenti con Ctrl+P. Tutto resta disponibile offline.", "muted"))
        layout.addStretch()
        self.install_reader(body)
        self.set_reader_enabled(False)

    def select_stack(self, stack):
        self.active_saved_search = None
        self.selection_filter = {"stack": stack}
        self.active_label.setText(self.catalog.stacks[stack]["label"])
        self.search_edit.clear()
        item = self.navigation_item({"stack": stack})
        if item is not None:
            self.tree.setCurrentItem(item)
        self.update_collection_actions()
        self.update_saved_actions()
        self.update_guided_navigation()
        self.schedule_search()

    def set_reader_enabled(self, enabled):
        for widget in (self.favorite_button, self.recipe_menu_button, self.export_button, self.mode_combo):
            widget.setEnabled(enabled)
        self.back_button.setEnabled(self.history_position > 0)
        self.forward_button.setEnabled(0 <= self.history_position < len(self.history) - 1)
        self.focus_button.setEnabled(enabled)
        self.focus_action.setEnabled(enabled)

    def render_current(self, *args):
        if not self.current_recipe:
            return
        recipe = self.current_recipe
        self.code_blocks = []
        self.set_reader_enabled(True)
        self.store.set_setting("reader_mode", self.mode_combo.currentIndex())
        self.favorite_button.setText("★" if self.store.annotation(recipe.id)[0] else "☆")
        guided = self.mode_combo.currentIndex() == 1
        body = QWidget()
        body.setObjectName("reader")
        layout = QVBoxLayout(body)
        layout.setContentsMargins(28, 20, 28, 32)
        layout.setSpacing(16)
        technology = self.catalog.stacks.get(recipe.stack, {}).get("label", recipe.stack)
        layout.addWidget(label(f"{technology.upper()}   /   {recipe.section.upper()}", "eyebrow"))
        layout.addWidget(label(recipe.title, "recipeTitle"))
        self.summary_label = label(recipe.summary, "muted")
        layout.addWidget(self.summary_label)
        row = QHBoxLayout()
        for value in [recipe.difficulty, " · ".join(recipe.os), STATUSES.get(recipe.verification.get("status"), "Revisionato")] + (["Progetto completo"] if recipe.project else []):
            row.addWidget(label(value, "badge"))
        row.addStretch()
        layout.addLayout(row)
        verification = recipe.verification
        self.verification_toggle = QPushButton("Dettagli della verifica ▾")
        self.verification_toggle.setCheckable(True)
        self.verification_toggle.setAccessibleName("Mostra dettagli della verifica")
        layout.addWidget(self.verification_toggle)
        self.verification_details = label(f"{STATUSES.get(verification.get('status'), 'Revisionato')} · "
            f"{verification.get('date', recipe.reviewed)}\n{verification.get('details', 'Esecuzione non attestata.')}", "muted")
        self.verification_details.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard)
        self.verification_details.hide()
        self.verification_toggle.toggled.connect(self.verification_details.setVisible)
        layout.addWidget(self.verification_details)
        if recipe.parameters:
            layout.addWidget(label("Personalizza l’esempio", "sectionTitle"))
            form = QFormLayout()
            self.parameter_edits = {}
            for parameter in recipe.parameters:
                edit = QLineEdit(self.current_parameters.get(parameter["name"], str(parameter.get("default", ""))))
                edit.setAccessibleName(parameter.get("label", parameter["name"]))
                hints = {"identifier": "Lettere ASCII, cifre e underscore; inizia con una lettera.", "namespace": "Parti separate da punti, per esempio Azienda.Progetto.",
                         "port": "Numero intero da 1 a 65535.", "path": "Percorso senza risalire alle cartelle superiori.", "string": "Testo dell’esempio."}
                edit.setToolTip(hints.get(parameter.get("type", "string"), hints["string"]))
                edit.textChanged.connect(lambda value, key=parameter["name"]: self.parameter_changed(key, value))
                self.parameter_edits[parameter["name"]] = edit
                form.addRow(parameter.get("label", parameter["name"]) + (" *" if parameter.get("required", True) else ""), edit)
            layout.addLayout(form)
            self.parameter_error = label("", "muted")
            self.parameter_error.hide()
            layout.addWidget(self.parameter_error)
        else:
            self.parameter_edits = {}
        layout.addWidget(label("Prerequisiti", "sectionTitle"))
        self.prerequisites_label = label(recipe.prerequisites)
        layout.addWidget(self.prerequisites_label)
        layout.addWidget(label("Versioni di riferimento: " + recipe.versions, "muted"))
        self.guide_browser = None
        if guided:
            layout.addWidget(label("Procedura guidata", "sectionTitle"))
            guide = OfflineBrowser(recipe.guide)
            guide.setMinimumHeight(220)
            guide.setMaximumHeight(420)
            guide.anchorClicked.connect(self.open_link)
            self.guide_browser = guide
            layout.addWidget(guide)
        self.preview_container = QWidget()
        self.preview_layout = QVBoxLayout(self.preview_container)
        self.preview_layout.setContentsMargins(0, 0, 0, 0)
        self.preview_layout.setSpacing(16)
        layout.addWidget(self.preview_container)
        self.expected_label = label(recipe.expected)
        layout.addWidget(label("Risultato atteso", "sectionTitle"))
        layout.addWidget(self.expected_label)
        if guided and recipe.errors:
            layout.addWidget(label("Errori frequenti e soluzioni", "sectionTitle"))
            for error in recipe.errors:
                layout.addWidget(label("• " + error))
        if guided:
            layout.addWidget(label("Verifica e fonti", "sectionTitle"))
            verification = recipe.verification
            layout.addWidget(label(f"{STATUSES.get(verification.get('status'), 'Revisionato')} · {verification.get('date', recipe.reviewed)}\n{verification.get('details', '')}", "muted"))
            for source in recipe.sources:
                button = QPushButton("Fonte: " + (QUrl(source).host() or "documentazione"))
                button.setToolTip(source + "\nApri nel browser (richiede connessione)")
                button.setAccessibleName("Apri fonte " + source)
                button.clicked.connect(lambda checked=False, url=source: self.open_link(QUrl(url)))
                layout.addWidget(button)
            if recipe.variants:
                layout.addWidget(label("Varianti di ambiente", "sectionTitle"))
                for variant in recipe.variants:
                    layout.addWidget(label(str(variant.get("title", variant.get("os", "Variante"))) + ": " + str(variant.get("description", variant.get("notes", "")))))
            if recipe.related:
                layout.addWidget(label("Continua con", "sectionTitle"))
                for rid in recipe.related:
                    related = self.recipes.get(rid)
                    if related:
                        button = QPushButton(related.title + " →")
                        button.clicked.connect(lambda checked=False, value=rid: self.open_recipe(value))
                        layout.addWidget(button)
        note = self.store.annotation(recipe.id)[1]
        if note:
            layout.addWidget(label("Le tue note", "sectionTitle"))
            layout.addWidget(label(note))
        layout.addWidget(label("Catalogo offline · Toolchain e dipendenze dell’esempio vanno predisposte separatamente.", "muted"))
        layout.addStretch()
        self.install_reader(body)
        self.refresh_parameter_preview()

    def parameter_changed(self, key, value):
        self.current_parameters[key] = value
        self.export_button.setEnabled(False)
        for block in self.code_blocks:
            block.copy_button.setEnabled(False)
            block.editor.setEnabled(False)
        self.export_button.setToolTip("Attendi la verifica dei parametri prima di esportare.")
        self.parameter_timer.start()

    def refresh_parameter_preview(self):
        if not self.current_recipe or not hasattr(self, "preview_layout"):
            return
        try:
            rendered = render_recipe(self.current_recipe.to_dict(), self.current_parameters)
            if self.parameter_edits:
                self.parameter_error.hide()
            self.export_button.setEnabled(True)
            self.export_button.setToolTip("Esporta i file con i parametri visualizzati.")
        except ValueError as error:
            if self.parameter_edits:
                self.parameter_error.setText(str(error))
                self.parameter_error.show()
            self.export_button.setEnabled(False)
            # Prevent copying a stale preview after an invalid parameter edit.
            for block in self.code_blocks:
                block.copy_button.setEnabled(False)
                block.editor.setEnabled(False)
            return
        while self.preview_layout.count():
            item = self.preview_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.code_blocks = []
        files = [a for a in rendered["assets"] if a.get("role") != "command"]
        commands = [a for a in rendered["assets"] if a.get("role") == "command"]
        if files:
            self.preview_layout.addWidget(label("File e codice", "sectionTitle"))
        for asset in files + commands:
            if commands and asset is commands[0]:
                self.preview_layout.addWidget(label("Comandi da eseguire", "sectionTitle"))
            block = CodeBlock(asset)
            if self.zoom:
                block.editor.zoomIn(self.zoom)
            self.code_blocks.append(block)
            self.preview_layout.addWidget(block)
        self.expected_label.setText(rendered.get("expected", ""))
        self.summary_label.setText(rendered.get("summary", ""))
        self.prerequisites_label.setText(rendered.get("prerequisites", ""))
        if self.guide_browser is not None:
            scroll = self.guide_browser.verticalScrollBar().value()
            self.guide_browser.setMarkdown(rendered.get("guide", ""))
            self.guide_browser.verticalScrollBar().setValue(scroll)

    def toggle_favorite(self):
        if not self.current_recipe:
            return
        favorite = not self.store.annotation(self.current_recipe.id)[0]
        try:
            self.store.annotate(self.current_recipe.id, favorite=favorite)
        except Exception as error:
            self.show_error("Impossibile aggiornare i preferiti", error)
            return
        self.favorite_button.setText("★" if favorite else "☆")
        if self.selection_filter.get("special") == "favorites":
            self.schedule_search()

    def edit_note(self):
        if not self.current_recipe:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Note personali")
        dialog.resize(580, 380)
        layout = QVBoxLayout(dialog)
        edit = QTextEdit()
        edit.setAcceptRichText(False)
        edit.setPlainText(self.store.annotation(self.current_recipe.id)[1])
        layout.addWidget(edit)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        try:
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.store.annotate(self.current_recipe.id, note=edit.toPlainText())
                self.render_current()
        finally:
            dialog.deleteLater()

    def edit_recipe(self, recipe):
        editor = RecipeEditor(self.catalog.stacks, recipe.to_dict() if isinstance(recipe, Recipe) else recipe, self)
        try:
            if editor.exec() == QDialog.DialogCode.Accepted:
                rid = self.store.save_recipe(editor.result_recipe)
                self.reload_personal()
                self.open_recipe(rid)
                self.statusBar().showMessage("Scheda personale salvata")
        finally:
            editor.deleteLater()

    def compare_current(self):
        if not self.current_recipe:
            return
        from devatlas.codewidgets import ComparisonDialog
        dialog = ComparisonDialog(self.recipes, self.catalog.stacks, left_id=self.current_recipe.id,
            left_parameters=self.current_parameters, zoom=self.zoom, parent=self)
        try:
            dialog.exec()
        finally:
            dialog.deleteLater()

    def reload_personal(self):
        self.request += 1
        self.recipes = self.catalog.merged(self.store.list_recipes())
        self.model.recipes = self.recipes
        self.refresh_dynamic_filters()
        self.model.set_ids([rid for rid in self.model.ids if rid in self.recipes])
        self.rebuild_navigation()
        self.notice_personal_errors()
        self.queue_index()

    def delete_personal(self):
        if not self.current_recipe or not self.current_recipe.personal:
            QMessageBox.information(self, "Catalogo incluso", "Per modificare questa scheda crea una copia personale.")
            return
        if QMessageBox.question(self, "Elimina scheda personale", "Eliminare questa scheda e le sue annotazioni?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        self.store.delete_recipe(self.current_recipe.id)
        self.current_recipe = None
        self.reload_personal()
        self.show_welcome()

    def create_collection(self):
        name, accepted = QInputDialog.getText(self, "Nuova raccolta", "Nome della raccolta")
        if accepted and name.strip():
            try:
                cid = self.store.create_collection(name)
                self.selection_filter = {"collection": cid}
                self.rebuild_navigation()
                self.update_guided_navigation()
                self.schedule_search()
            except Exception as error:
                self.show_error("Impossibile creare la raccolta", error)

    def collection_context_menu(self, position):
        item = self.tree.itemAt(position)
        data = item.data(0, Qt.ItemDataRole.UserRole) if item is not None else {}
        saved_id = (data or {}).get("saved_search")
        if saved_id:
            self.active_saved_search = saved_id
            self.update_saved_actions()
            menu = QMenu(self.tree)
            menu.addAction("Rinomina ricerca…", lambda: self.rename_saved_search(saved_id))
            menu.addAction("Elimina ricerca…", lambda: self.delete_saved_search(saved_id))
            try:
                menu.exec(self.tree.viewport().mapToGlobal(position))
            finally:
                menu.deleteLater()
            return
        cid = (data or {}).get("collection")
        if not cid:
            return
        self.tree.setCurrentItem(item)
        menu = QMenu(self.tree)
        menu.addAction("Rinomina raccolta…", lambda: self.rename_collection(cid))
        menu.addAction("Elimina raccolta…", lambda: self.delete_collection(cid))
        try:
            menu.exec(self.tree.viewport().mapToGlobal(position))
        finally:
            menu.deleteLater()

    def rename_collection(self, cid=None):
        cid = cid or self.selection_filter.get("collection")
        names = dict(self.store.collections())
        if cid not in names:
            return
        name, accepted = QInputDialog.getText(self, "Rinomina raccolta", "Nuovo nome", text=names[cid])
        if accepted:
            try:
                self.store.rename_collection(cid, name)
                self.rebuild_navigation()
                self.statusBar().showMessage("Raccolta rinominata")
            except Exception as error:
                self.show_error("Impossibile rinominare la raccolta", error)

    def delete_collection(self, cid=None):
        cid = cid or self.selection_filter.get("collection")
        names = dict(self.store.collections())
        if cid not in names:
            return
        if QMessageBox.question(self, "Elimina raccolta", f"Eliminare la raccolta «{names[cid]}»?\nLe schede, i preferiti e le note vengono conservati.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        try:
            self.store.delete_collection(cid)
            if self.selection_filter.get("collection") == cid:
                self.selection_filter = {}
            self.rebuild_navigation()
            self.update_guided_navigation()
            self.schedule_search()
            self.statusBar().showMessage("Raccolta eliminata; schede e annotazioni conservate")
        except Exception as error:
            self.show_error("Impossibile eliminare la raccolta", error)

    def add_to_collection(self):
        if not self.current_recipe:
            return
        collections = self.store.collections()
        if not collections:
            self.create_collection()
            collections = self.store.collections()
        if not collections:
            return
        name, accepted = QInputDialog.getItem(self, "Aggiungi alla raccolta", "Raccolta", [c[1] for c in collections], 0, False)
        if accepted:
            cid = next(c[0] for c in collections if c[1] == name)
            try:
                self.store.add_to_collection(cid, self.current_recipe.id)
            except Exception as error:
                self.show_error("Impossibile aggiungere la scheda", error)
                return
            self.statusBar().showMessage("Scheda aggiunta a " + name)
            self.schedule_search()

    def remove_from_collection(self):
        cid = self.selection_filter.get("collection")
        if cid and self.current_recipe:
            self.store.remove_from_collection(cid, self.current_recipe.id)
            self.schedule_search()
        else:
            self.statusBar().showMessage("Seleziona prima una raccolta nella navigazione.")

    def export_current(self, zipped):
        if not self.current_recipe:
            return
        if zipped:
            filename, _ = QFileDialog.getSaveFileName(self, "Esporta progetto ZIP", self.current_recipe.id + ".zip", "Archivio ZIP (*.zip)")
        else:
            parent = QFileDialog.getExistingDirectory(self, "Scegli la cartella in cui creare l’esempio")
            filename = str(Path(parent) / self.current_recipe.id) if parent else ""
        if not filename:
            return
        try:
            count = export_project(self.current_recipe.to_dict(), Path(filename), parameters=self.current_parameters, zipped=zipped)
            self.statusBar().showMessage(f"Esportati {count} file in {filename}", 15000)
            self.show_export_destination(Path(filename).parent if zipped else Path(filename))
        except Exception as error:
            self.show_error("Esportazione non riuscita", error)

    def export_recipe_bundle(self):
        if not self.current_recipe:
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Esporta scheda modificabile", self.current_recipe.id + ".devatlas.zip", "Pacchetto DevAtlas (*.devatlas.zip)")
        if filename:
            try:
                save_bundle(Path(filename), [self.current_recipe.to_dict()])
                self.statusBar().showMessage("Scheda esportata")
            except Exception as error:
                self.show_error("Esportazione non riuscita", error)

    def export_collection(self):
        if not self.index_ready:
            self.statusBar().showMessage("Attendi il completamento dell’indice prima di esportare la raccolta.")
            return
        query = self.query()
        ids = []
        while True:
            result = self.index.search(replace(query, offset=len(ids), limit=200))
            ids.extend(result.ids)
            if len(ids) >= result.total:
                break
        if not ids:
            self.statusBar().showMessage("La raccolta corrente non contiene schede.")
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Esporta raccolta corrente", "raccolta.devatlas.zip", "Pacchetto DevAtlas (*.devatlas.zip)")
        if filename:
            try:
                save_bundle(Path(filename), [self.recipes[rid].to_dict() for rid in ids])
                self.statusBar().showMessage(f"Esportate {len(ids)} schede")
            except Exception as error:
                self.show_error("Esportazione non riuscita", error)

    def backup_personal(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Crea backup personale", f"devatlas-backup-{date.today()}.devatlas.zip", "Pacchetto DevAtlas (*.devatlas.zip)")
        if filename:
            try:
                data = self.store.backup_data()
                save_bundle(Path(filename), data["recipes"], personal=data)
                self.statusBar().showMessage("Backup personale creato")
                if data.get("settings_recovery"):
                    self.show_notice("Il backup contiene anche le preferenze non leggibili per il recupero manuale. "
                        "Schede, note e raccolte valide sono state salvate normalmente.")
            except Exception as error:
                self.show_error("Backup non riuscito", error)

    def import_bundle(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Importa schede o backup", "", "Pacchetto DevAtlas (*.zip)")
        if not filename:
            return
        try:
            payload = load_bundle(Path(filename))
            recipes = payload["recipes"]
            personal = payload.get("personal")
            collisions = sum(r["id"] in self.recipes for r in recipes)
            detail = f"{len(recipes)} schede nel pacchetto; {collisions} identificatori già presenti.\n"
            detail += "Le schede vengono importate come contenuti personali. I conflitti vengono conservati in copie separate."
            if personal:
                detail += f"\nIl backup include {len(personal.get('annotations', []))} annotazioni e {len(personal.get('collections', []))} raccolte."
            if QMessageBox.question(self, "Riepilogo importazione", detail, QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Cancel) != QMessageBox.StandardButton.Ok:
                return
            if personal is not None:
                self.store.restore_data(personal, duplicate=True)
            else:
                self.store.import_recipes(recipes)
            self.reload_personal()
            self.statusBar().showMessage("Importazione completata")
        except Exception as error:
            self.show_error("Importazione non riuscita", error)

    def update_catalog(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Aggiorna catalogo da pacchetto locale", "", "Pacchetto DevAtlas (*.zip)")
        if not filename:
            return
        try:
            payload = load_bundle(Path(filename))
            recipes = payload["recipes"]
            if not recipes or any(r["id"].startswith("personal-") for r in recipes):
                raise ValueError("Seleziona un pacchetto del catalogo incluso, senza schede personali.")
            if any(r["stack"] not in self.catalog.stacks for r in recipes):
                raise ValueError("Il pacchetto contiene tecnologie sconosciute a questa versione dell’app.")
            if QMessageBox.question(self, "Aggiorna catalogo", f"Aggiornare o aggiungere {len(recipes)} schede?\nPreferiti, note e raccolte restano conservati.", QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Cancel) != QMessageBox.StandardButton.Ok:
                return
            combined = {rid: r.to_dict() for rid, r in self.catalog.recipes.items()}
            combined.update({r["id"]: r for r in recipes})
            data = {"format": "RecipeBundle", "version": 1, "stacks": self.catalog.stacks, "recipes": list(combined.values())}
            target = self.directory / "catalogo-locale.json"
            temp = target.with_suffix(".tmp")
            temp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            Catalog(temp)  # Validate before replacing the existing local catalog.
            temp.replace(target)
            self.catalog = Catalog(target)
            self.reload_personal()
            self.show_welcome()
            self.statusBar().showMessage("Catalogo aggiornato")
        except Exception as error:
            self.show_error("Aggiornamento non riuscito", error)

    def rebuild_index(self):
        self.queue_index(force=True)

    def copy_guide(self):
        if self.current_recipe:
            try:
                QApplication.clipboard().setText(readme(render_recipe(self.current_recipe.to_dict(), self.current_parameters)))
                self.statusBar().showMessage("Guida Markdown copiata")
            except ValueError as error:
                self.show_error("Parametri non validi", error)

    def find_in_recipe(self):
        if not self.current_recipe:
            return
        focused = QApplication.focusWidget()
        for block in self.code_blocks:
            if focused is block.editor or focused is not None and block.editor.isAncestorOf(focused):
                if hasattr(block, "show_find"):
                    block.show_find()
                    self.reader_scroll.ensureWidgetVisible(block)
                    return
        text, ok = QInputDialog.getText(self, "Cerca nel codice", "Testo da cercare")
        if ok and text:
            for block in self.code_blocks:
                block.editor.moveCursor(block.editor.textCursor().MoveOperation.Start)
                if block.editor.find(text):
                    self.reader_scroll.ensureWidgetVisible(block)
                    block.editor.setFocus()
                    return
            self.statusBar().showMessage("Testo non trovato nei blocchi di codice.")

    def open_link(self, url):
        if url.scheme() in ("http", "https"):
            QDesktopServices.openUrl(url)
        elif url.scheme() == "recipe":
            self.open_recipe(url.host() or url.path().lstrip("/"))

    def change_theme(self):
        self.store.set_setting("theme", self.theme_combo.currentData())
        apply_theme(QApplication.instance(), self.theme_combo.currentData(), self.zoom)
        if self.current_recipe:
            self.render_current()
        self.refresh_visuals()
        self.results_list.doItemsLayout()
        self.results_list.viewport().update()

    def system_theme_changed(self, *args):
        if self.theme_combo.currentData() == "system":
            self.change_theme()

    def adjust_zoom(self, amount):
        self.zoom = min(5, max(-2, self.zoom + amount))
        self.adapt_header()
        self.store.set_setting("zoom", self.zoom)
        apply_theme(QApplication.instance(), self.theme_combo.currentData(), self.zoom)
        self.render_current()
        self.refresh_visuals()
        self.results_list.doItemsLayout()

    def show_help(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Guida a DevAtlas")
        dialog.resize(750, 680)
        layout = QVBoxLayout(dialog)
        guide = OfflineBrowser((PACKAGE / "data" / "guida.md").read_text(encoding="utf-8"))
        layout.addWidget(guide)
        close = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close.rejected.connect(dialog.reject)
        layout.addWidget(close)
        try:
            dialog.exec()
        finally:
            dialog.deleteLater()

    def about(self):
        QMessageBox.information(self, "DevAtlas", f"DevAtlas {__version__}\nAtlante del Codice\n\n{len(self.catalog.recipes)} schede · {len(self.catalog.stacks)} percorsi\nPython 3.13 · PySide6 6.12 · SQLite FTS5\n\nContenuti originali, fonti ufficiali e stato delle verifiche nelle singole schede.\nLibrerie e relative licenze sono incluse nella distribuzione.")

    def show_error(self, title, error):
        logging.error("%s: %s", title, error)
        QMessageBox.warning(self, title, str(error))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "new_button"):
            self.adapt_header()
            if hasattr(self, "filter_grid"):
                self.layout_filters()
                self.resize_active_chips()
                self.sync_results_presentation()
            compact = self.width() < 1200
            self.new_button.setText("+ Nuova" if compact else "+ Nuova scheda")
            self.export_button.setText("Esporta ▾" if compact else "Esporta progetto ▾")
            if not self.focus_mode and self.width() < 1000 and self.sidebar.isVisible():
                self._sidebar_was_auto_hidden = True
                self.sidebar.hide()
            elif not self.focus_mode and self.width() >= 1200 and self._sidebar_was_auto_hidden:
                self.sidebar.show()
                self._sidebar_was_auto_hidden = False

    def closeEvent(self, event):
        self.debounce.stop()
        self.parameter_timer.stop()
        self.request += 1
        self.index_generation += 1
        self.pending_index = None
        self.index_threadpool.waitForDone()
        self.threadpool.waitForDone()
        try:
            self.store.set_setting("geometry", bytes(self.saveGeometry().toBase64()).decode())
            sizes = self.focus_restore["sizes"] if self.focus_mode and self.focus_restore else self.splitter.sizes()
            sizes = [size if size > 0 else fallback for size, fallback in zip(sizes, [248, 380, 900])]
            self.store.set_setting("splitter", sizes)
            visible = self.focus_restore if self.focus_mode and self.focus_restore else {
                "sidebar": self.sidebar.isVisible() or self._sidebar_was_auto_hidden,
                "results": self.splitter.widget(1).isVisible()}
            self.store.set_setting("panels_visibility", {key: bool(visible[key]) for key in ("sidebar", "results")})
        except Exception as error:
            logging.warning("Impossibile salvare la disposizione della finestra: %s", error)
        super().closeEvent(event)


def main(argv=None):
    parser = argparse.ArgumentParser(description="DevAtlas — Atlante del Codice offline")
    parser.add_argument("--data-dir", type=Path, help="Cartella dati personali (predefinita: LocalAppData/DevAtlas)")
    parser.add_argument("--catalog", type=Path, help="Catalogo locale alternativo")
    parser.add_argument("--smoke-test", action="store_true", help="Avvia, esegui una ricerca e chiudi")
    arguments = parser.parse_args(argv)
    if arguments.data_dir:
        os.environ["DEVATLAS_DATA_DIR"] = str(arguments.data_dir)
    configure_qt_plugins()
    app = QApplication.instance() or QApplication(sys.argv[:1])
    app.setApplicationName("DevAtlas")
    app.setOrganizationName("DevAtlas")
    app.setApplicationVersion(__version__)
    app.setStyle("Fusion")
    directory = None
    guard = None
    def report(kind, value, tb):
        logging.error("Errore non gestito", exc_info=(kind, value, tb))
        QMessageBox.critical(None, "DevAtlas", f"Si è verificato un errore. I dettagli sono nel registro locale.\n\n{value}")
    sys.excepthook = report
    try:
        directory = user_directory()
        logging.basicConfig(filename=directory / "devatlas.log", encoding="utf-8", level=logging.WARNING)
        guard = ProfileInstance(directory, app)
        if not guard.acquire():
            return 0
        catalog, notice = startup_catalog(directory, arguments.catalog)
        window = MainWindow(catalog, directory)
        def activate_window():
            if window.isMinimized():
                window.showNormal()
            else:
                window.show()
            window.raise_()
            window.activateWindow()
        guard.activated.connect(activate_window)
        if notice:
            window.show_notice(notice)
        window.show()
        if arguments.smoke_test:
            smoke_state = {"started": False, "finished": False, "exit_code": 1}
            started_at = time.monotonic()
            smoke_timer = QTimer(window)
            smoke_timer.setInterval(50)
            def finish_smoke(success, reason):
                if smoke_state["finished"]:
                    return
                smoke_state["finished"] = True
                smoke_state["exit_code"] = 0 if success else 1
                smoke_timer.stop()
                result = window.last_search_result
                data = {"status": "passed" if success else "failed", "reason": reason, "query": "python json",
                        "index_ready": window.index_ready, "results": result.total if result else 0,
                        "recipe": window.current_recipe.id if success and window.current_recipe else None,
                        "code_blocks": len(window.code_blocks) if success else 0,
                        "elapsed_ms": round((time.monotonic() - started_at) * 1000), "version": __version__}
                try:
                    (directory / "smoke-test.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                except OSError as error:
                    logging.error("Rapporto smoke non salvato: %s", error)
                    smoke_state["exit_code"] = 1
                window.close()
            def smoke():
                if time.monotonic() - started_at >= 20:
                    finish_smoke(False, "Timeout: il flusso di ricerca non è stato completato entro 20 secondi.")
                elif not window.index_ready:
                    if window.index_job is None and window.pending_index is None:
                        finish_smoke(False, "Preparazione dell’indice non riuscita.")
                elif not smoke_state["started"]:
                    smoke_state["started"] = True
                    window.search_edit.setText("python json")
                    window.debounce.stop()
                    window.run_search()
                elif window.last_search_request == window.request and window.last_search_text == "python json":
                    if window.last_search_error:
                        finish_smoke(False, "Errore durante la ricerca: " + window.last_search_error)
                    elif not window.model.ids:
                        finish_smoke(False, "La ricerca non ha restituito risultati.")
                    else:
                        window.results_list.setCurrentIndex(window.model.index(0))
                        success = window.current_recipe is not None and bool(window.code_blocks)
                        finish_smoke(success, "Indice, ricerca e lettore verificati." if success else "Il lettore non mostra i blocchi di codice.")
            smoke_timer.timeout.connect(smoke)
            smoke_timer.start()
        result = app.exec()
        return smoke_state["exit_code"] if arguments.smoke_test else result
    except Exception as error:
        logging.exception("Avvio non riuscito")
        location = directory or arguments.data_dir or os.environ.get("DEVATLAS_DATA_DIR", "profilo predefinito")
        if arguments.smoke_test:
            if directory is not None:
                try:
                    (directory / "smoke-test.json").write_text(json.dumps({"status": "failed", "reason": str(error)}), encoding="utf-8")
                except OSError:
                    pass
        else:
            QMessageBox.critical(None, "DevAtlas — Avvio non riuscito", f"{error}\n\nCartella dati richiesta:\n{location}\n\nVerifica i permessi della cartella. I dati esistenti vengono conservati.")
        return 1
    finally:
        if guard is not None:
            guard.close()


if __name__ == "__main__":
    raise SystemExit(main())

