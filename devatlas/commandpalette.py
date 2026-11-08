"""Bounded, keyboard-first selector for existing UI actions and destinations.

The owner supplies callbacks and decides which recent recipes to include. This
module does not read the catalog, execute commands, or change application theme.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import islice
import re
import unicodedata
from typing import Callable, Iterable

from PySide6.QtCore import QAbstractListModel, QEvent, QModelIndex, QRect, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel, QLineEdit, QListView,
                              QStyle, QStyledItemDelegate, QToolButton, QVBoxLayout)

from devatlas.theme import THEMES


MAX_COMMANDS = 256
COMMAND_ROLE = int(Qt.ItemDataRole.UserRole) + 1
_STOP_WORDS = frozenset("a al alla alle con da del della di e gli i il in la le lo per un una uno".split())
_SYNONYMS = (
    ("open", "apri", "aprire", "mostra", "mostrare", "show", "vai"),
    ("search", "cerca", "cercare", "ricerca", "trova", "trovare", "find"),
    ("save", "salva", "salvare", "salvataggio"),
    ("export", "esporta", "esportare", "esportazione"),
    ("import", "importa", "importare", "importazione"),
    ("favorite", "favorites", "favourite", "favourites", "preferiti", "preferito", "preferite", "preferita"),
    ("recent", "recenti", "recente", "history", "cronologia"),
    ("recipe", "recipes", "ricetta", "ricette", "scheda", "schede", "snippet", "snippets"),
    ("collection", "collections", "raccolta", "raccolte", "collezione", "collezioni"),
    ("settings", "impostazioni", "impostazione", "preferenze", "opzioni"),
    ("theme", "tema", "aspetto"),
    ("dark", "scuro", "scura"),
    ("light", "chiaro", "chiara"),
    ("new", "nuovo", "nuova", "nuove", "crea", "creare"),
    ("technology", "technologies", "tecnologia", "tecnologie", "linguaggio", "linguaggi", "framework", "language"),
    ("javascript", "js"), ("typescript", "ts"), ("python", "python3"),
    ("nodejs", "node"), ("nextjs", "next"), ("pyside6", "pyside"), ("pyqt6", "pyqt"),
)
_CANONICAL = {word: group[0] for group in _SYNONYMS for word in group}


def _words(value: str) -> tuple[str, ...]:
    value = value.casefold()
    for source, target in ((r"(?<!\w)c\+\+(?!\w)", " cpp "), (r"(?<!\w)c#(?!\w)", " csharp "),
                           (r"(?<!\w)asp\.net(?!\w)", " aspnet "), (r"(?<!\w)\.net(?!\w)", " dotnet "),
                           (r"(?<!\w)node\.js(?!\w)", " nodejs "), (r"(?<!\w)next\.js(?!\w)", " nextjs ")):
        value = re.sub(source, target, value)
    value = "".join(letter for letter in unicodedata.normalize("NFKD", value) if not unicodedata.combining(letter))
    return tuple(word for word in re.findall(r"\w+", value) if word not in _STOP_WORDS)


def _indexed_words(value: str) -> frozenset[str]:
    original = _words(value)
    return frozenset((*original, *(_CANONICAL.get(word, word) for word in original)))


@dataclass(frozen=True)
class Command:
    id: str
    title: str
    category: str
    callback: Callable[[], None] | None
    description: str = ""
    shortcut: str = ""
    enabled: bool = True
    keywords: tuple[str, ...] = ()

    @property
    def available(self) -> bool:
        return bool(self.enabled and callable(self.callback))


class CommandModel(QAbstractListModel):
    """Only materializes the bounded list supplied by the UI owner."""

    def __init__(self, commands: Iterable[Command], parent=None):
        super().__init__(parent)
        selected = tuple(islice(commands, MAX_COMMANDS + 1))
        self.truncated = len(selected) > MAX_COMMANDS
        unique = {}
        for command in selected[:MAX_COMMANDS]:
            if not isinstance(command, Command):
                raise TypeError("La palette richiede oggetti Command.")
            if not command.id or not command.title:
                raise ValueError("Ogni comando richiede ID e titolo.")
            unique.setdefault(command.id, command)
        self.commands = tuple(unique.values())
        self._fields = tuple((_indexed_words(command.title), _indexed_words(command.category),
                              _indexed_words(" ".join(command.keywords)), _indexed_words(command.description))
                             for command in self.commands)
        self._visible = tuple(range(len(self.commands)))

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._visible)

    def command(self, index: QModelIndex) -> Command | None:
        if not index.isValid() or index.model() is not self or not 0 <= index.row() < len(self._visible):
            return None
        return self.commands[self._visible[index.row()]]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        command = self.command(index)
        if command is None:
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            return command.title
        if role == COMMAND_ROLE:
            return command
        if role == Qt.ItemDataRole.ToolTipRole:
            return command.description + ("\nNon disponibile in questo momento." if not command.available else "")
        if role == Qt.ItemDataRole.AccessibleTextRole:
            return f"{command.title}, {command.category}" + (", non disponibile" if not command.available else "")
        if role == Qt.ItemDataRole.AccessibleDescriptionRole:
            return command.description
        return None

    def flags(self, index):
        command = self.command(index)
        if command is None or not command.available:
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

    def set_query(self, value: str):
        query = tuple(dict.fromkeys(_CANONICAL.get(word, word) for word in _words(value)))
        if not query:
            visible = tuple(range(len(self.commands)))
        else:
            matches = []
            for number, fields in enumerate(self._fields):
                score = 0
                for needle in query:
                    best = 0
                    for terms, weight in zip(fields, (10, 3, 7, 2)):
                        if needle in terms:
                            best = max(best, weight + 3)
                        elif len(needle) > 1 and any(term.startswith(needle) for term in terms):
                            best = max(best, weight)
                    if not best:
                        break
                    score += best
                else:
                    matches.append((-score, number))
            visible = tuple(number for _, number in sorted(matches))
        self.beginResetModel()
        self._visible = visible
        self.endResetModel()


class CommandDelegate(QStyledItemDelegate):
    """Paints text with semantic application colors; no global styling changes."""

    def sizeHint(self, option, index):
        metrics = QFontMetrics(option.font)
        return QSize(320, max(68, metrics.height() * 3 + 22))

    def paint(self, painter: QPainter, option, index):
        command = index.data(COMMAND_ROLE)
        if command is None:
            return
        app = QApplication.instance()
        name = app.property("devatlasTheme") if app else "light"
        theme = THEMES.get(name, THEMES["light"])
        selected = bool(option.state & QStyle.StateFlag.State_Selected) and command.available
        painter.save()
        painter.fillRect(option.rect, QColor(theme["selection"] if selected else theme["surface"]))
        if selected:
            painter.fillRect(QRect(option.rect.left(), option.rect.top() + 8, 3, option.rect.height() - 16), QColor(theme["accent"]))
        base = QFont(option.font)
        base_size = base.pointSizeF() if base.pointSizeF() > 0 else 10
        category_font = QFont(base)
        category_font.setPointSizeF(max(8, base_size - 1))
        category_font.setBold(True)
        title_font = QFont(base)
        title_font.setBold(True)
        description_font = QFont(base)
        description_font.setPointSizeF(max(8, base_size - .5))
        content = option.rect.adjusted(14, 8, -14, -8)
        category_metrics = QFontMetrics(category_font)
        title_metrics = QFontMetrics(title_font)
        description_metrics = QFontMetrics(description_font)
        category_rect = QRect(content.left(), content.top(), content.width(), category_metrics.height())
        title_rect = QRect(content.left(), category_rect.bottom() + 2, content.width(), title_metrics.height())
        description_rect = QRect(content.left(), title_rect.bottom() + 3, content.width(), description_metrics.height())
        painter.setFont(category_font)
        painter.setPen(QColor(theme["accent"] if selected else theme["muted"]))
        painter.drawText(category_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         category_metrics.elidedText(command.category.upper(), Qt.TextElideMode.ElideRight, max(1, category_rect.width())))
        if command.shortcut:
            shortcut_width = min(content.width() // 3, title_metrics.horizontalAdvance(command.shortcut) + 12)
            shortcut_rect = QRect(content.right() - shortcut_width, title_rect.top(), shortcut_width, title_rect.height())
            painter.setFont(description_font)
            painter.setPen(QColor(theme["muted"]))
            painter.drawText(shortcut_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                             description_metrics.elidedText(command.shortcut, Qt.TextElideMode.ElideRight, shortcut_width))
            title_rect.setRight(shortcut_rect.left() - 8)
        painter.setFont(title_font)
        painter.setPen(QColor(theme["text"] if command.available else theme["muted"]))
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         title_metrics.elidedText(command.title, Qt.TextElideMode.ElideRight, max(1, title_rect.width())))
        painter.setFont(description_font)
        painter.setPen(QColor(theme["muted"]))
        description = command.description or ("Non disponibile in questo momento" if not command.available else "")
        painter.drawText(description_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         description_metrics.elidedText(description, Qt.TextElideMode.ElideRight, max(1, description_rect.width())))
        painter.setPen(QColor(theme["border"]))
        painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
        painter.restore()


class CommandPalette(QDialog):
    """Ctrl+P is registered by the owner; this dialog handles local navigation."""

    commandTriggered = Signal(str)

    def __init__(self, commands: Iterable[Command], parent=None):
        super().__init__(parent)
        self.setObjectName("commandPalette")
        self.setWindowTitle("Azioni rapide")
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setModal(True)
        self._dispatching = False
        self.selectedCommand: Command | None = None
        self.model = CommandModel(commands, self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 14)
        layout.setSpacing(10)
        heading = QHBoxLayout()
        title = QLabel("Azioni rapide")
        title.setObjectName("sectionTitle")
        heading.addWidget(title)
        heading.addStretch()
        shortcut = QLabel("Ctrl+P")
        shortcut.setObjectName("badge")
        heading.addWidget(shortcut)
        close = QToolButton()
        close.setText("×")
        close.setAccessibleName("Chiudi azioni rapide")
        close.setToolTip("Chiudi · Esc")
        close.setFixedSize(32, 32)
        close.clicked.connect(self.reject)
        heading.addWidget(close)
        layout.addLayout(heading)
        subtitle = QLabel("Cerca un’azione, una tecnologia o una ricetta recente.")
        subtitle.setObjectName("muted")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        self.searchEdit = QLineEdit()
        self.searchEdit.setObjectName("search")
        self.searchEdit.setPlaceholderText("Scrivi cosa vuoi fare…")
        self.searchEdit.setAccessibleName("Cerca azioni e destinazioni")
        self.searchEdit.setClearButtonEnabled(True)
        self.searchEdit.installEventFilter(self)
        layout.addWidget(self.searchEdit)
        self.listView = QListView()
        self.listView.setObjectName("commandPaletteList")
        self.listView.setAccessibleName("Comandi disponibili")
        self.listView.setModel(self.model)
        self.listView.setItemDelegate(CommandDelegate(self.listView))
        self.listView.setUniformItemSizes(True)
        self.listView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.listView.setSelectionMode(QListView.SelectionMode.SingleSelection)
        self.listView.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        self.listView.installEventFilter(self)
        self.listView.clicked.connect(self._activate_index)
        layout.addWidget(self.listView, 1)
        self.emptyLabel = QLabel()
        self.emptyLabel.setObjectName("muted")
        self.emptyLabel.setAccessibleName("Stato dei risultati della palette")
        self.emptyLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.emptyLabel.setWordWrap(True)
        layout.addWidget(self.emptyLabel, 1)
        self.countLabel = QLabel()
        self.countLabel.setObjectName("muted")
        self.countLabel.setWordWrap(True)
        layout.addWidget(self.countLabel)
        help_label = QLabel("↑↓ sposta  ·  Invio esegue  ·  Esc chiude")
        help_label.setObjectName("muted")
        help_label.setWordWrap(True)
        layout.addWidget(help_label)
        self.searchEdit.textChanged.connect(self._filter)
        screen = self.screen() or QApplication.primaryScreen()
        available = screen.availableGeometry() if screen else QRect(0, 0, 1024, 768)
        width, height = max(280, available.width() - 32), max(260, available.height() - 32)
        self.setMinimumSize(min(420, width), min(310, height))
        self.resize(min(760, width), min(570, height))
        self.setFocusProxy(self.searchEdit)
        self._filter("")

    def showEvent(self, event):
        super().showEvent(event)
        self.searchEdit.setFocus(Qt.FocusReason.OtherFocusReason)
        self.searchEdit.selectAll()

    def _filter(self, value):
        self.model.set_query(value)
        count = self.model.rowCount()
        self.listView.setVisible(count > 0)
        self.emptyLabel.setVisible(count == 0)
        self.emptyLabel.setText("Nessun comando trovato. Prova con un’altra parola." if value.strip() else "Non ci sono azioni disponibili.")
        available = [row for row in range(count) if self.model.command(self.model.index(row)).available]
        self.listView.setCurrentIndex(self.model.index(available[0]) if available else QModelIndex())
        if count and not available:
            self.countLabel.setText(f"{count} risultati · nessuna azione attivabile in questo momento")
        else:
            suffix = " · elenco limitato alle destinazioni rapide" if self.model.truncated else ""
            self.countLabel.setText(f"{count} {'risultato' if count == 1 else 'risultati'}{suffix}")

    def _move(self, direction):
        rows = [row for row in range(self.model.rowCount()) if self.model.command(self.model.index(row)).available]
        if not rows:
            return
        current = self.listView.currentIndex().row()
        if current in rows:
            destination = rows[(rows.index(current) + direction) % len(rows)]
        else:
            destination = rows[0] if direction > 0 else rows[-1]
        index = self.model.index(destination)
        self.listView.setCurrentIndex(index)
        self.listView.scrollTo(index)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.KeyPress and watched in (self.searchEdit, self.listView):
            key = event.key()
            if key in (Qt.Key.Key_Down, Qt.Key.Key_Up):
                self._move(1 if key == Qt.Key.Key_Down else -1)
                return True
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self._activate_index(self.listView.currentIndex())
                return True
            if key == Qt.Key.Key_Escape:
                self.reject()
                return True
        return super().eventFilter(watched, event)

    def _activate_index(self, index):
        command = self.model.command(index)
        if self._dispatching or command is None or not command.available:
            return
        self._dispatching = True
        self.selectedCommand = command
        callback = command.callback
        context = self.parentWidget() or QApplication.instance()
        self.accept()
        self.commandTriggered.emit(command.id)
        # The callback is attached to the owner/application, never to this
        # short-lived dialog. Other modal actions open after it has closed.
        QTimer.singleShot(0, context, callback)
