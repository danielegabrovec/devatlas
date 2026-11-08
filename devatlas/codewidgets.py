from __future__ import annotations
from bisect import bisect_left
import difflib
import hashlib
from PySide6.QtCore import Qt, QRect, QSize, QTimer, QByteArray, QEvent, QObject, QRunnable, QThreadPool, Signal
from PySide6.QtGui import (QAccessible, QAccessibleAnnouncementEvent, QColor, QFont, QFontDatabase,
    QKeySequence, QPainter, QPalette, QSyntaxHighlighter, QTextCharFormat, QTextCursor, QTextDocument, QTextFormat)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QCompleter, QDialog, QDialogButtonBox,
    QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QPushButton, QScrollArea,
    QSizePolicy, QSplitter, QTextBrowser, QTextEdit, QToolButton, QVBoxLayout, QWidget)
from pygments import lex
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.styles import get_style_by_name


def color_contrast(first, second):
    if first.alpha() < 255:
        alpha = first.alphaF()
        a, b = first.getRgbF(), second.getRgbF()
        first = QColor.fromRgbF(*(a[index] * alpha + b[index] * (1 - alpha) for index in range(3)))
    def luminance(color):
        parts = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in color.getRgbF()[:3]]
        return .2126 * parts[0] + .7152 * parts[1] + .0722 * parts[2]
    a, b = sorted((luminance(first), luminance(second)))
    return (b + .05) / (a + .05)


def readable_token(color, background, text):
    if color.alpha() < 255:
        alpha = color.alphaF()
        a, b = color.getRgbF(), background.getRgbF()
        color = QColor.fromRgbF(*(a[index] * alpha + b[index] * (1 - alpha) for index in range(3)))
    if color_contrast(color, background) >= 4.5:
        return color
    target = text
    if color_contrast(target, background) < 4.5:
        target = max((QColor("black"), QColor("white")), key=lambda c: color_contrast(c, background))
    original, destination = color.getRgbF(), target.getRgbF()
    for step in range(1, 21):
        fraction = step / 20
        candidate = QColor.fromRgbF(*(original[i] * (1 - fraction) + destination[i] * fraction for i in range(3)))
        if color_contrast(candidate, background) >= 4.5:
            return candidate
    return target


class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document, language="text", dark=False):
        super().__init__(document)
        self.language = language
        try:
            self.lexer = get_lexer_by_name(language, stripnl=False, ensurenl=False)
        except Exception:
            self.lexer = TextLexer(stripnl=False, ensurenl=False)
        self.dark = dark
        self.owner = None
        self.spans = []
        self.ends = []
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.refresh)
        document.contentsChange.connect(lambda position, removed, added: self.timer.start() if removed or added else None)
        self.refresh()

    def set_language(self, language):
        if language == self.language:
            return
        self.language = language
        try:
            self.lexer = get_lexer_by_name(language, stripnl=False, ensurenl=False)
        except Exception:
            self.lexer = TextLexer(stripnl=False, ensurenl=False)
        self.refresh()

    def refresh(self):
        if self.owner is not None:
            self.dark = QApplication.instance().property("devatlasTheme") == "dark"
        style = get_style_by_name("native" if self.dark else "friendly")
        self.spans, self.ends = [], []
        colors = {}
        position = 0
        for token, value in lex(self.document().toPlainText(), self.lexer):
            length = len(value.encode("utf-16-le")) // 2
            spec = style.style_for_token(token)
            fmt = QTextCharFormat()
            if spec.get("color"):
                key = spec["color"]
                if key not in colors:
                    color = QColor("#" + key)
                    if self.owner is not None:
                        color = readable_token(color, self.owner.palette().color(QPalette.ColorRole.Base), self.owner.palette().color(QPalette.ColorRole.Text))
                    colors[key] = color
                color = colors[key]
                fmt.setForeground(color)
            if spec.get("bold"):
                fmt.setFontWeight(QFont.Weight.Bold)
            if spec.get("italic"):
                fmt.setFontItalic(True)
            self.spans.append((position, position + length, fmt))
            self.ends.append(position + length)
            position += length
        self.rehighlight()

    def highlightBlock(self, text):
        start = self.currentBlock().position()
        end = start + len(text.encode("utf-16-le")) // 2
        index = bisect_left(self.ends, start + 1)
        for a, b, fmt in self.spans[index:]:
            if a >= end:
                break
            self.setFormat(max(a, start) - start, min(b, end) - max(a, start), fmt)


class LineNumbers(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.number_width(), 0)

    def paintEvent(self, event):
        self.editor.paint_numbers(event)


class CodeEditor(QPlainTextEdit):
    metricsChanged = Signal()
    findRequested = Signal()
    copied = Signal()

    def __init__(self, text="", language="text", *, readonly=True, parent=None):
        super().__init__(parent)
        self.find_bar = None
        self.copy_allowed = lambda: True
        self.selection_source = None
        self.setObjectName("code")
        self.setReadOnly(readonly)
        self.setTabChangesFocus(readonly)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setFont(QFont("Cascadia Code" if "Cascadia Code" in QFontDatabase.families() else "JetBrains Mono", 10))
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * 4)
        self.numbers = LineNumbers(self)
        self.blockCountChanged.connect(self.update_margin)
        self.updateRequest.connect(self.update_numbers)
        self.setPlainText(text)
        self.update_margin()
        self.highlighter = SyntaxHighlighter(self.document(), language, QApplication.instance().property("devatlasTheme") == "dark")
        self.highlighter.owner = self
        self.highlighter.refresh()
        self.setAccessibleName("Codice sorgente")

    def set_language(self, language):
        self.highlighter.set_language(language)

    def show_find(self):
        """Open the local find bar without touching the surrounding reader."""
        self.findRequested.emit()
        return self.find_bar is not None

    def event(self, event):
        if event.type() == QEvent.Type.ShortcutOverride and self.find_bar is not None:
            if event.matches(QKeySequence.StandardKey.Find) or event.key() == Qt.Key.Key_F3:
                event.accept()
                return True
        return super().event(event)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.StandardKey.Find) and self.find_bar is not None:
            self.show_find()
            event.accept()
            return
        if event.key() == Qt.Key.Key_F3 and self.find_bar is not None:
            self.find_bar.find_next(bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier))
            event.accept()
            return
        if event.matches(QKeySequence.StandardKey.Copy):
            self.copy()
            event.accept()
            return
        super().keyPressEvent(event)

    def copy(self):
        if not self.copy_allowed() or not self.textCursor().hasSelection():
            return
        if self.selection_source is None:
            super().copy()
        else:
            QApplication.clipboard().setText(self.selection_source())
        self.copied.emit()

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        for action in menu.actions():
            if action.objectName() == "edit-copy":
                action.triggered.disconnect()
                action.triggered.connect(self.copy)
                action.setEnabled(self.copy_allowed() and self.textCursor().hasSelection())
        if self.find_bar is not None:
            menu.addSeparator()
            menu.addAction("Trova nel blocco…", self.show_find)
        try:
            menu.exec(event.globalPos())
        finally:
            menu.deleteLater()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (QEvent.Type.FontChange, QEvent.Type.ApplicationFontChange) and hasattr(self, "numbers"):
            self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * 4)
            self.update_margin()
            self.numbers.update()
            self.metricsChanged.emit()
        if event.type() in (QEvent.Type.PaletteChange, QEvent.Type.ApplicationPaletteChange) and hasattr(self, "highlighter"):
            self.highlighter.timer.start(0)

    def number_width(self):
        return 17 + self.fontMetrics().horizontalAdvance("9") * max(2, len(str(self.blockCount())))

    def update_margin(self):
        self.setViewportMargins(self.number_width(), 0, 0, 0)
        rect = self.contentsRect()
        self.numbers.setGeometry(QRect(rect.left(), rect.top(), self.number_width(), rect.height()))

    def update_numbers(self, rect, dy):
        if dy:
            self.numbers.scroll(0, dy)
        else:
            self.numbers.update(0, rect.y(), self.numbers.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_margin()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        rect = self.contentsRect()
        self.numbers.setGeometry(QRect(rect.left(), rect.top(), self.number_width(), rect.height()))

    def paint_numbers(self, event):
        painter = QPainter(self.numbers)
        block = self.firstVisibleBlock()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        height = self.fontMetrics().height()
        color = self.palette().color(QPalette.ColorRole.PlaceholderText)
        painter.setPen(readable_token(color, self.palette().color(QPalette.ColorRole.Base), self.palette().color(QPalette.ColorRole.Text)))
        painter.setFont(self.font())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and top + height >= event.rect().top():
                painter.drawText(0, top, self.numbers.width() - 8, height, Qt.AlignmentFlag.AlignRight, str(block.blockNumber() + 1))
            top += round(self.blockBoundingRect(block).height())
            block = block.next()


class CodeFindBar(QWidget):
    """Literal, local search. Native cursor selection leaves diff colors intact."""
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.setObjectName("codeSearchBar")
        self.editor = editor
        editor.find_bar = self
        editor.findRequested.connect(self.show_search)
        self.matches = []
        self.truncated = False
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 3, 0, 3)
        row.setSpacing(4)
        self.search_edit = QLineEdit()
        self.search_edit.setObjectName("codeSearchInput")
        self.search_edit.setProperty("transientUi", True)
        self.search_edit.setPlaceholderText("Cerca nel blocco")
        self.search_edit.setAccessibleName("Testo da cercare nel blocco")
        self.search_edit.setClearButtonEnabled(True)
        row.addWidget(self.search_edit, 1)
        self.previous_button = QToolButton()
        self.previous_button.setText("↑")
        self.previous_button.setAccessibleName("Occorrenza precedente")
        self.next_button = QToolButton()
        self.next_button.setText("↓")
        self.next_button.setAccessibleName("Occorrenza successiva")
        self.case_button = QToolButton()
        self.case_button.setText("Aa")
        self.case_button.setCheckable(True)
        self.case_button.setToolTip("Distingui maiuscole e minuscole")
        self.case_button.setAccessibleName("Distingui maiuscole e minuscole")
        self.count_label = QLabel("0 risultati")
        self.count_label.setObjectName("muted")
        self.count_label.setTextFormat(Qt.TextFormat.PlainText)
        self.close_button = QToolButton()
        self.close_button.setText("×")
        self.close_button.setAccessibleName("Chiudi ricerca nel blocco")
        for widget in (self.previous_button, self.next_button, self.case_button, self.count_label, self.close_button):
            row.addWidget(widget)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(80)
        self.timer.timeout.connect(lambda: self.refresh(select=False))
        self.search_edit.textChanged.connect(lambda _: self.refresh(select=True))
        self.search_edit.returnPressed.connect(self.find_next)
        self.case_button.toggled.connect(lambda _: self.refresh(select=True))
        self.next_button.clicked.connect(lambda: self.find_next(False))
        self.previous_button.clicked.connect(lambda: self.find_next(True))
        self.close_button.clicked.connect(self.close_search)
        self.search_edit.installEventFilter(self)
        editor.document().contentsChange.connect(lambda pos, removed, added: self.timer.start() if (removed or added) and self.isVisible() else None)
        editor.selectionChanged.connect(self.update_count)
        self.hide()

    def show_search(self):
        selection = self.editor.textCursor().selectedText()
        self.show()
        if selection and len(selection) <= 160 and "\u2029" not in selection and "\u2028" not in selection:
            self.search_edit.setText(selection)
        self.search_edit.setFocus()
        self.search_edit.selectAll()
        self.refresh(select=False)

    def close_search(self):
        self.hide()
        self.editor.setFocus()

    def eventFilter(self, watched, event):
        if watched is self.search_edit and event.type() in (QEvent.Type.KeyPress, QEvent.Type.ShortcutOverride):
            if event.key() == Qt.Key.Key_Escape:
                if event.type() == QEvent.Type.KeyPress:
                    self.close_search()
                event.accept()
                return True
            if event.matches(QKeySequence.StandardKey.Find) or event.key() == Qt.Key.Key_F3:
                if event.type() == QEvent.Type.KeyPress:
                    if event.key() == Qt.Key.Key_F3:
                        self.find_next(bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier))
                    else:
                        self.show_search()
                event.accept()
                return True
        return super().eventFilter(watched, event)

    def flags(self, backward=False):
        flags = QTextDocument.FindFlag.FindCaseSensitively if self.case_button.isChecked() else QTextDocument.FindFlag(0)
        return flags | QTextDocument.FindFlag.FindBackward if backward else flags

    def refresh(self, select=False):
        query = self.search_edit.text()
        self.matches, self.truncated = [], False
        if query:
            cursor = self.editor.document().find(query, 0, self.flags())
            while not cursor.isNull():
                self.matches.append((cursor.selectionStart(), cursor.selectionEnd()))
                if len(self.matches) > 1000:
                    self.truncated = True
                    break
                cursor = self.editor.document().find(query, cursor.selectionEnd(), self.flags())
        if select and self.matches:
            cursor = self.editor.textCursor()
            cursor.setPosition(self.matches[0][0])
            cursor.setPosition(self.matches[0][1], QTextCursor.MoveMode.KeepAnchor)
            self.editor.setTextCursor(cursor)
            self.editor.ensureCursorVisible()
        elif select:
            cursor = self.editor.textCursor()
            cursor.clearSelection()
            self.editor.setTextCursor(cursor)
        self.previous_button.setEnabled(bool(self.matches))
        self.next_button.setEnabled(bool(self.matches))
        self.update_count()

    def update_count(self):
        cursor = self.editor.textCursor()
        position = (cursor.selectionStart(), cursor.selectionEnd())
        if not self.search_edit.text():
            text = ""
        elif not self.matches:
            text = "Nessun risultato"
        elif self.truncated:
            text = "1000+ risultati"
        else:
            number = self.matches.index(position) + 1 if position in self.matches else 0
            text = f"{number}/{len(self.matches)}" if number else f"{len(self.matches)} risultati"
        self.count_label.setText(text)
        self.count_label.setAccessibleName(text or "Ricerca vuota")

    def find_next(self, backward=False):
        query = self.search_edit.text()
        if not query:
            self.show_search()
            return
        current = self.editor.textCursor()
        start = current.selectionStart() if backward else current.selectionEnd()
        result = self.editor.document().find(query, start, self.flags(backward))
        if result.isNull():
            start = self.editor.document().characterCount() - 1 if backward else 0
            result = self.editor.document().find(query, start, self.flags(backward))
        if not result.isNull():
            self.editor.setTextCursor(result)
            self.editor.ensureCursorVisible()
        self.update_count()


def source_selection(source, cursor):
    """Map Qt UTF-16 positions back to the untouched source, including CRLF."""
    if cursor.selectionStart() == 0 and cursor.selectionEnd() >= cursor.document().characterCount() - 1:
        return source
    boundaries = [0]
    index = 0
    while index < len(source) and len(boundaries) <= cursor.selectionEnd():
        start = index
        if source[index:index + 2] == "\r\n":
            index += 2
            boundaries.append(index)
        else:
            index += 1
            if ord(source[start]) > 0xFFFF:
                boundaries.append(start)
            boundaries.append(index)
    begin = min(cursor.selectionStart(), len(boundaries) - 1)
    end = min(cursor.selectionEnd(), len(boundaries) - 1)
    return source[boundaries[begin]:boundaries[end]]


class CodeBlock(QFrame):
    def __init__(self, asset, parent=None):
        super().__init__(parent)
        self.asset = asset
        self.expanded = False
        self._layout_pending = False
        self.setObjectName("codeBlock")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        header = QHBoxLayout()
        label = asset.get("path", "Codice")
        if asset.get("role") == "command":
            label = f"{asset.get('shell', 'Terminale')} · {asset.get('os', 'Tutti')} · {asset.get('cwd', '.')}"
        elif asset.get("role") == "snippet":
            label += " · frammento"
        title = QLabel(label)
        title.setTextFormat(Qt.TextFormat.PlainText)
        title.setWordWrap(True)
        title.setObjectName("muted")
        header.addWidget(title, 1)
        self.copy_button = QPushButton("Copia")
        self.copy_name = "Copia " + label
        self.copy_button.setAccessibleName(self.copy_name)
        self.copy_button.setAccessibleDescription("Copia l’intero blocco originale negli appunti")
        self.copy_button.clicked.connect(self.copy)
        self.copy_timer = QTimer(self)
        self.copy_timer.setSingleShot(True)
        self.copy_timer.setInterval(1400)
        self.copy_timer.timeout.connect(self.reset_copy_feedback)
        header.addWidget(self.copy_button)
        layout.addLayout(header)
        tools = QHBoxLayout()
        tools.setSpacing(6)
        self.find_button = QToolButton()
        self.find_button.setText("Trova")
        self.find_button.setAccessibleName("Trova nel blocco, Ctrl+F")
        self.find_button.clicked.connect(self.show_find)
        self.wrap_button = QToolButton()
        self.wrap_button.setText("↵")
        self.wrap_button.setCheckable(True)
        self.wrap_button.setToolTip("A capo automatico, senza modificare il codice")
        self.wrap_button.setAccessibleName("A capo automatico")
        self.expand_button = QToolButton()
        self.expand_button.setText("Espandi")
        self.expand_button.setToolTip("Mostra più righe; il resto rimane scorrevole")
        self.expand_button.setAccessibleName("Espandi blocco di codice")
        self.expand_button.clicked.connect(self.toggle_expanded)
        self.selection_button = QToolButton()
        self.selection_button.setText("Copia selezione")
        self.selection_button.setToolTip("Copia soltanto la selezione, senza numeri di riga")
        self.selection_button.setAccessibleName("Copia selezione")
        self.info_label = QLabel()
        self.info_label.setObjectName("muted")
        for widget in (self.find_button, self.wrap_button, self.expand_button, self.selection_button):
            tools.addWidget(widget)
        tools.addStretch()
        tools.addWidget(self.info_label)
        layout.addLayout(tools)
        self.editor = CodeEditor(asset.get("content", ""), asset.get("language", "text"))
        self.editor.copy_allowed = lambda: self.copy_button.isEnabled()
        self.editor.selection_source = lambda: source_selection(self.asset.get("content", ""), self.editor.textCursor())
        self.editor.copied.connect(lambda: self.copy_feedback("Selezione copiata"))
        self.selection_button.clicked.connect(self.editor.copy)
        self.editor.selectionChanged.connect(self.sync_selection)
        self.copy_button.installEventFilter(self)
        self.find_bar = CodeFindBar(self.editor, self)
        self.find_bar.installEventFilter(self)
        layout.addWidget(self.find_bar)
        self.editor.setMinimumHeight(80)
        layout.addWidget(self.editor)
        self.height_timer = QTimer(self)
        self.height_timer.setSingleShot(True)
        self.height_timer.timeout.connect(self.update_height)
        self.editor.metricsChanged.connect(self.schedule_height)
        self.editor.blockCountChanged.connect(self.schedule_height)
        self.editor.document().documentLayout().documentSizeChanged.connect(self.schedule_height)
        self._wrap_key = str(asset.get("sha256") or hashlib.sha256(asset.get("content", "").encode()).hexdigest()) + "|" + asset.get("path", "")
        wraps = QApplication.instance().property("devatlasCodeWrap") or {}
        self.wrap_button.setChecked(bool(wraps.get(self._wrap_key)))
        self.wrap_button.toggled.connect(self.set_wrap)
        self.set_wrap(self.wrap_button.isChecked())
        self.sync_selection()
        self.update_height()

    def copy(self):
        if not self.copy_button.isEnabled():
            return
        QApplication.clipboard().setText(self.asset.get("content", ""))
        self.copy_feedback("Codice copiato")

    def copy_feedback(self, message):
        self.copy_button.setText("Copiato")
        self.copy_button.setAccessibleName(message)
        self.copy_button.setAccessibleDescription(message + " negli appunti")
        QAccessible.updateAccessibility(QAccessibleAnnouncementEvent(self, message))
        self.copy_timer.start()

    def reset_copy_feedback(self):
        self.copy_button.setText("Copia")
        self.copy_button.setAccessibleName(self.copy_name)
        self.copy_button.setAccessibleDescription("Copia l’intero blocco originale negli appunti")

    def sync_selection(self):
        self.selection_button.setEnabled(self.copy_button.isEnabled() and self.editor.textCursor().hasSelection())

    def eventFilter(self, watched, event):
        if watched is self.copy_button and event.type() == QEvent.Type.EnabledChange and hasattr(self, "editor"):
            self.sync_selection()
        elif watched is getattr(self, "find_bar", None) and event.type() in (QEvent.Type.Show, QEvent.Type.Hide):
            self.schedule_height()
        return super().eventFilter(watched, event)

    def show_find(self):
        self.editor.show_find()
        self.schedule_height()

    def set_wrap(self, enabled):
        self.editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth if enabled else QPlainTextEdit.LineWrapMode.NoWrap)
        wraps = dict(QApplication.instance().property("devatlasCodeWrap") or {})
        wraps[self._wrap_key] = bool(enabled)
        while len(wraps) > 200:
            wraps.pop(next(iter(wraps)))
        QApplication.instance().setProperty("devatlasCodeWrap", wraps)
        self.schedule_height()

    def toggle_expanded(self):
        self.expanded = not self.expanded
        self.expand_button.setText("Riduci" if self.expanded else "Espandi")
        self.expand_button.setAccessibleName("Riduci blocco di codice" if self.expanded else "Espandi blocco di codice")
        self.schedule_height()

    def schedule_height(self, *args):
        if hasattr(self, "height_timer"):
            self.height_timer.start(0)

    def update_height(self):
        lines = self.editor.blockCount()
        visual = 0
        block = self.editor.document().firstBlock()
        while block.isValid() and visual <= 40:
            visual += max(1, block.layout().lineCount())
            block = block.next()
        visual = max(visual, min(lines, 41))
        self.expand_button.setVisible(visual > 14)
        self.info_label.setText(f"{lines} righe")
        limit = 36 if self.expanded else 14
        extra = self.editor.frameWidth() * 2 + 14
        if not self.wrap_button.isChecked():
            extra += self.editor.horizontalScrollBar().sizeHint().height()
        height = min(720, max(92, self.editor.fontMetrics().lineSpacing() * min(visual + 1, limit) + extra))
        if self.editor.height() != height:
            self.editor.setFixedHeight(height)
        self.layout().invalidate()
        preferred = self.layout().totalHeightForWidth(max(1, self.width()))
        self.setMinimumHeight(max(self.layout().minimumSize().height(), preferred))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "selection_button"):
            self.selection_button.setText("Selezione" if self.width() < 480 else "Copia selezione")
        self.schedule_height()


class OfflineBrowser(QTextBrowser):
    """Local text renderer: no automatic local/remote document or image fetches."""
    def __init__(self, markdown="", parent=None):
        super().__init__(parent)
        self.setOpenLinks(False)
        self.setOpenExternalLinks(False)
        self.setMarkdown(markdown)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setMinimumHeight(100)

    def loadResource(self, resource_type, url):
        return QByteArray()


MAX_COMPARE_BYTES = 2 * 1024 * 1024
MAX_COMPARE_LINES = 20000


def compare_preflight(text):
    if not isinstance(text, str) or len(text) > MAX_COMPARE_BYTES:
        raise ValueError("Il confronto supporta fino a 2 MiB per blocco. Puoi esportare il file dalla scheda.")
    try:
        if len(text.encode("utf-8")) > MAX_COMPARE_BYTES:
            raise ValueError("Il blocco supera 2 MiB di testo UTF-8.")
    except UnicodeError as error:
        raise ValueError("Il blocco contiene testo Unicode non valido.") from error
    lines = text.splitlines(keepends=True)
    if len(lines) > MAX_COMPARE_LINES:
        raise ValueError("Il confronto supporta fino a 20.000 righe per blocco. Puoi esportare il file dalla scheda.")
    return lines


def line_differences(left, right):
    """Line ranges refer to the original texts, including newline differences."""
    a, b = compare_preflight(left), compare_preflight(right)
    result = {"left": [], "right": [], "added": 0, "removed": 0, "changed": 0, "identical": left == right}
    if left == right:
        return result
    matcher = difflib.SequenceMatcher(None, a, b, autojunk=len(a) + len(b) > 4000)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "insert":
            result["right"].append((j1, j2, "added"))
            result["added"] += j2 - j1
        elif tag == "delete":
            result["left"].append((i1, i2, "removed"))
            result["removed"] += i2 - i1
        elif tag == "replace":
            result["left"].append((i1, i2, "changed"))
            result["right"].append((j1, j2, "changed"))
            result["changed"] += max(i2 - i1, j2 - j1)
    return result


class ComparePane(QWidget):
    changed = Signal()

    def __init__(self, recipes, stacks, title, recipe_id, parameters=None, zoom=0, parent=None):
        super().__init__(parent)
        self.recipes, self.stacks = recipes, stacks
        self.loading = True
        self.valid = False
        self.rendered_asset = None
        self.current_recipe_id = None
        self.values_by_recipe = {recipe_id: dict(parameters or {})}
        self.parameter_edits = {}
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(160)
        self.timer.timeout.connect(self.render_asset)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        heading = QLabel(title)
        heading.setObjectName("sectionTitle")
        layout.addWidget(heading)
        self.recipe_combo = QComboBox()
        self.recipe_combo.setEditable(True)
        self.recipe_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.recipe_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.recipe_combo.setMinimumContentsLength(14)
        self.recipe_combo.setAccessibleName("Scheda " + title.lower())
        for rid, recipe in sorted(recipes.items(), key=lambda pair: (stacks.get(pair[1].stack, {}).get("label", pair[1].stack).casefold(), pair[1].title.casefold())):
            technology = stacks.get(recipe.stack, {}).get("label", recipe.stack)
            suffix = " · personale" if recipe.personal else ""
            self.recipe_combo.addItem(technology + " · " + recipe.title + suffix, rid)
        self.recipe_combo.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.recipe_combo.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.recipe_combo.completer().setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.recipe_combo.setCurrentIndex(max(0, self.recipe_combo.findData(recipe_id)))
        layout.addWidget(self.recipe_combo)
        self.asset_combo = QComboBox()
        self.asset_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.asset_combo.setMinimumContentsLength(14)
        self.asset_combo.setAccessibleName("Blocco " + title.lower())
        layout.addWidget(self.asset_combo)
        self.parameter_scroll = QScrollArea()
        self.parameter_scroll.setWidgetResizable(True)
        self.parameter_scroll.setMaximumHeight(145)
        self.parameter_widget = QWidget()
        self.parameter_form = QFormLayout(self.parameter_widget)
        self.parameter_form.setContentsMargins(4, 4, 4, 4)
        self.parameter_scroll.setWidget(self.parameter_widget)
        layout.addWidget(self.parameter_scroll)
        self.error_label = QLabel()
        self.error_label.setTextFormat(Qt.TextFormat.PlainText)
        self.error_label.setWordWrap(True)
        self.error_label.setObjectName("muted")
        self.error_label.hide()
        layout.addWidget(self.error_label)
        self.editor = CodeEditor(readonly=True)
        self.editor.setAccessibleName("Codice " + title.lower())
        self.editor.setMinimumHeight(120)
        if zoom:
            self.editor.zoomIn(zoom)
        tools = QHBoxLayout()
        find = QToolButton()
        find.setText("Trova")
        find.setAccessibleName("Trova nel codice " + title.lower())
        find.clicked.connect(self.editor.show_find)
        wrap = QCheckBox("A capo")
        wrap.setAccessibleName("A capo nel codice " + title.lower())
        wrap.toggled.connect(lambda enabled: self.editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth if enabled else QPlainTextEdit.LineWrapMode.NoWrap))
        tools.addWidget(find)
        tools.addWidget(wrap)
        tools.addStretch()
        layout.addLayout(tools)
        self.find_bar = CodeFindBar(self.editor, self)
        layout.addWidget(self.find_bar)
        layout.addWidget(self.editor, 1)
        copy_row = QHBoxLayout()
        self.info_label = QLabel()
        self.info_label.setTextFormat(Qt.TextFormat.PlainText)
        self.info_label.setWordWrap(True)
        self.info_label.setObjectName("muted")
        copy_row.addWidget(self.info_label, 1)
        self.copy_button = QPushButton("Copia")
        self.copy_button.setAccessibleName("Copia codice " + title.lower())
        self.copy_button.clicked.connect(self.copy)
        self.editor.copy_allowed = lambda: self.valid and self.copy_button.isEnabled()
        self.editor.selection_source = lambda: source_selection(self.rendered_asset["content"], self.editor.textCursor()) if self.valid and self.rendered_asset is not None else ""
        copy_row.addWidget(self.copy_button)
        layout.addLayout(copy_row)
        self.recipe_combo.currentTextChanged.connect(self.select_recipe)
        self.asset_combo.currentIndexChanged.connect(self.render_asset)
        self.loading = False
        self.select_recipe()

    def invalidate(self, message=""):
        self.valid = False
        self.rendered_asset = None
        self.copy_button.setEnabled(False)
        self.editor.setEnabled(False)
        self.editor.setExtraSelections([])
        self.error_label.setText(message)
        self.error_label.setVisible(bool(message))
        self.changed.emit()

    def select_recipe(self, *args):
        if self.loading:
            return
        index = self.recipe_combo.currentIndex()
        if index < 0 or self.recipe_combo.currentText() != self.recipe_combo.itemText(index):
            self.invalidate("Scegli una scheda dai suggerimenti della ricerca.")
            return
        rid = self.recipe_combo.currentData()
        recipe = self.recipes.get(rid)
        if recipe is None:
            self.invalidate("La scheda non è più disponibile.")
            return
        if len(recipe.parameters) > 64 or len(recipe.assets) > 1000:
            self.invalidate("La scheda contiene troppi parametri o blocchi per il confronto. Esportala dalla biblioteca.")
            return
        self.loading = True
        self.current_recipe_id = rid
        self.asset_combo.clear()
        for number, asset in enumerate(recipe.assets):
            name = asset.get("path", "Codice")
            if asset.get("role") == "command":
                name = f"{asset.get('shell', 'Comandi')} · {name}"
            self.asset_combo.addItem(name, number)
        while self.parameter_form.rowCount():
            self.parameter_form.removeRow(0)
        self.parameter_edits = {}
        values = self.values_by_recipe.setdefault(rid, {})
        for parameter in recipe.parameters:
            name = parameter["name"]
            value = str(values.get(name, parameter.get("default", "")))
            values[name] = value
            edit = QLineEdit(value)
            edit.setAccessibleName(parameter.get("label", name))
            edit.textChanged.connect(lambda text, r=rid, n=name: self.parameter_changed(r, n, text))
            caption = QLabel(parameter.get("label", name))
            caption.setTextFormat(Qt.TextFormat.PlainText)
            caption.setWordWrap(True)
            caption.setMaximumWidth(170)
            self.parameter_form.addRow(caption, edit)
            self.parameter_edits[name] = edit
        self.parameter_scroll.setVisible(bool(recipe.parameters))
        self.loading = False
        self.render_asset()

    def parameter_changed(self, rid, name, value):
        self.values_by_recipe.setdefault(rid, {})[name] = value
        if rid == self.current_recipe_id:
            self.invalidate("Aggiornamento dei parametri…")
            self.timer.start()

    def render_asset(self, *args):
        if self.loading:
            return
        self.timer.stop()
        try:
            index = self.recipe_combo.currentIndex()
            if index < 0 or self.recipe_combo.currentText() != self.recipe_combo.itemText(index):
                raise ValueError("Scegli una scheda dai suggerimenti della ricerca.")
            recipe = self.recipes[self.current_recipe_id]
            number = self.asset_combo.currentData()
            if number is None or not 0 <= number < len(recipe.assets):
                raise ValueError("Seleziona un file o un blocco di comandi.")
            asset = recipe.assets[number]
            compare_preflight(asset["content"])
            values = self.values_by_recipe.get(recipe.id, {})
            from devatlas.templating import PLACEHOLDER, render_recipe
            # Bound expansion before allocating a large rendered string. Unknown
            # framework placeholders remain literal, just as in the main reader.
            estimate = len(asset["content"].encode("utf-8"))
            for match in PLACEHOLDER.finditer(asset["content"]):
                if match.group(1) in values:
                    estimate += max(0, len(values[match.group(1)].encode("utf-8")) * 6 + 4 - len(match.group(0)))
                    if estimate > MAX_COMPARE_BYTES:
                        raise ValueError("Il contenuto parametrizzato può superare 2 MiB. Riduci i valori o esporta il file.")
            rendered = render_recipe({"assets": [asset], "parameters": recipe.parameters}, values)
            result = rendered["assets"][0]
            lines = compare_preflight(result["content"])
            self.rendered_asset = result
            self.valid = True
            self.editor.setEnabled(True)
            self.editor.setPlainText(result["content"])
            simplified = len(result["content"]) > 200000 or len(lines) > 2000
            self.editor.set_language("text" if simplified else result.get("language", "text"))
            self.copy_button.setEnabled(True)
            self.error_label.hide()
            path = result.get("path", "Codice")
            short_path = path if len(path) <= 55 else path[:26] + "…" + path[-26:]
            self.info_label.setText(short_path + " · " + f"{len(lines):,} righe".replace(",", ".") + (" · colori semplificati" if simplified else ""))
            self.changed.emit()
        except (ValueError, TypeError, KeyError, UnicodeError) as error:
            self.invalidate(str(error))

    def copy(self):
        if self.valid and self.rendered_asset is not None:
            QApplication.clipboard().setText(self.rendered_asset["content"])
            self.info_label.setText("Codice copiato")


class DifferenceSignals(QObject):
    completed = Signal(int, object, str)


class DifferenceWorker(QRunnable):
    def __init__(self, generation, left, right):
        super().__init__()
        self.generation, self.left, self.right = generation, left, right
        self.signals = DifferenceSignals()

    def run(self):
        try:
            self.signals.completed.emit(self.generation, line_differences(self.left, self.right), "")
        except Exception as error:
            self.signals.completed.emit(self.generation, None, str(error))


class ComparisonDialog(QDialog):
    def __init__(self, recipes, stacks, left_id=None, right_id=None, left_parameters=None, zoom=0, parent=None):
        super().__init__(parent)
        self._closed = False
        self.generation = 0
        self.pending_diff = None
        self.job = None
        self.diff_result = None
        self.syncing = False
        self.threadpool = QThreadPool(self)
        self.threadpool.setMaxThreadCount(1)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(120)
        self.timer.timeout.connect(self.start_pending)
        self.setWindowTitle("Confronta codice — DevAtlas")
        available = self.screen().availableGeometry()
        self.resize(min(1280, available.width() - 40), min(820, available.height() - 55))
        self.setMinimumSize(760, 520)
        if not recipes:
            raise ValueError("Non ci sono schede da confrontare.")
        left_id = left_id if left_id in recipes else next(iter(recipes))
        if right_id not in recipes:
            right_id = next((rid for rid, r in recipes.items() if rid != left_id and r.stack == recipes[left_id].stack),
                            next((rid for rid in recipes if rid != left_id), left_id))
        layout = QVBoxLayout(self)
        hint = QLabel("Scegli due schede e i blocchi da affiancare. Ogni lato ha parametri e copia indipendenti.")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        self.summary_label = QLabel("Confronto per righe, in sola lettura.")
        self.summary_label.setTextFormat(Qt.TextFormat.PlainText)
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.left = ComparePane(recipes, stacks, "Sinistra", left_id, left_parameters, zoom)
        self.right = ComparePane(recipes, stacks, "Destra", right_id, zoom=zoom)
        for pane in (self.left, self.right):
            self.splitter.addWidget(pane)
            pane.changed.connect(self.schedule_diff)
        self.splitter.setSizes([600, 600])
        layout.addWidget(self.splitter, 1)
        self.sync_scroll = QCheckBox("Sincronizza scorrimento")
        self.sync_scroll.setChecked(True)
        layout.addWidget(self.sync_scroll)
        self.left.editor.verticalScrollBar().valueChanged.connect(lambda value: self.synchronize(self.right, value))
        self.right.editor.verticalScrollBar().valueChanged.connect(lambda value: self.synchronize(self.left, value))
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.schedule_diff()

    def synchronize(self, target, value):
        if not self.sync_scroll.isChecked() or self.syncing or not (self.left.valid and self.right.valid):
            return
        self.syncing = True
        target.editor.verticalScrollBar().setValue(value)
        self.syncing = False

    def schedule_diff(self):
        if self._closed:
            return
        self.generation += 1
        self.diff_result = None
        for pane in (self.left, self.right):
            pane.editor.setExtraSelections([])
        if not self.left.valid or not self.right.valid:
            self.pending_diff = None
            self.timer.stop()
            self.summary_label.setText("Completa la selezione e correggi i parametri indicati per confrontare i due lati.")
            return
        self.pending_diff = (self.generation, self.left.rendered_asset["content"], self.right.rendered_asset["content"])
        self.summary_label.setText("Calcolo delle differenze…")
        self.timer.start()

    def start_pending(self):
        if self._closed or self.job is not None or self.pending_diff is None:
            return
        self.timer.stop()
        job = DifferenceWorker(*self.pending_diff)
        self.pending_diff = None
        self.job = job
        job.signals.completed.connect(self.diff_finished)
        self.threadpool.start(job)

    def diff_finished(self, generation, result, error):
        self.job = None
        if self._closed:
            return
        if generation == self.generation:
            if error:
                self.summary_label.setText("Confronto non disponibile: " + error)
            else:
                self.diff_result = result
                self.apply_differences(result)
        if self.pending_diff is not None:
            self.start_pending()

    def apply_differences(self, result):
        dark = QApplication.instance().property("devatlasTheme") == "dark"
        colors = {"added": "#164e39" if dark else "#dcfce7", "removed": "#6b2636" if dark else "#fee2e2", "changed": "#594713" if dark else "#fef3c7"}
        for pane, key in ((self.left, "left"), (self.right, "right")):
            selections = []
            for begin, end, kind in result[key]:
                for number in range(begin, end):
                    block = pane.editor.document().findBlockByNumber(number)
                    if not block.isValid():
                        continue
                    selection = QTextEdit.ExtraSelection()
                    selection.cursor = QTextCursor(block)
                    selection.format.setBackground(QColor(colors[kind]))
                    selection.format.setForeground(readable_token(pane.editor.palette().color(QPalette.ColorRole.Text), QColor(colors[kind]), pane.editor.palette().color(QPalette.ColorRole.Text)))
                    selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
                    selections.append(selection)
            pane.editor.setExtraSelections(selections)
        self.summary_label.setText("Testi identici." if result["identical"] else
            f"Righe aggiunte: +{result['added']} · rimosse: −{result['removed']} · modificate: {result['changed']}\nVerde: aggiunte · rosso: rimosse · ambra: modifiche")

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (QEvent.Type.PaletteChange, QEvent.Type.ApplicationPaletteChange) and getattr(self, "diff_result", None) is not None:
            self.apply_differences(self.diff_result)

    def done(self, result):
        self._closed = True
        self.generation += 1
        self.pending_diff = None
        self.timer.stop()
        for pane in (self.left, self.right):
            pane.timer.stop()
        self.threadpool.waitForDone()
        super().done(result)

