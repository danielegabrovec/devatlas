"""Three layers: primitive palette, semantic themes, native component tokens."""
from __future__ import annotations
from PySide6.QtGui import QColor, QFont, QFontDatabase, QPalette
from PySide6.QtCore import Qt
from devatlas.paths import PACKAGE

PRIMITIVES = {
    "indigo600": "#4f46e5", "indigo700": "#4338ca", "indigo100": "#e8eaff",
    "indigo200": "#c7d2fe", "slate950": "#0c1220", "slate900": "#151e2e",
    "slate800": "#202c40", "slate700": "#34445d", "slate600": "#526078",
    "slate300": "#b0bdd2", "slate100": "#edf2fa", "white": "#ffffff",
    "blue700": "#1d4ed8", "teal800": "#115e59", "violet700": "#6d28d9",
    "amber800": "#92400e", "green800": "#166534",
}
COMPONENTS = {"card_radius": 12, "space_xs": 4, "space_sm": 8, "space_md": 16,
              "space_lg": 24, "space_xl": 32, "focus_width": 2}
THEMES = {
    "light": {"background": "#edf1f8", "surface": "#ffffff", "raised": "#f5f7fc",
              "sidebar": "#f7f9fe", "reader": "#fbfcff", "text": "#18243a", "muted": "#526078",
              "border": "#d8e0ee", "accent": PRIMITIVES["indigo600"], "accent_hover": PRIMITIVES["indigo700"],
              "accent_text": "#3730a3", "selection": "#e9ecff", "card_hover": "#f5f6ff",
              "code": "#f3f6fc", "success": "#166534", "warning": "#854d0e", "danger": "#b42318", "scroll_thumb": "#6b7891"},
    "dark": {"background": PRIMITIVES["slate950"], "surface": PRIMITIVES["slate900"], "raised": "#1d293d",
             "sidebar": "#10192a", "reader": "#111b2b", "text": "#edf2fb", "muted": "#b0bdd2",
             "border": "#34445d", "accent": "#b9bcff", "accent_hover": "#d2d4ff",
             "accent_text": "#d9ddff", "selection": "#29385c", "card_hover": "#1d2b43",
             "code": "#0d1626", "success": "#86efac", "warning": "#fcd34d", "danger": "#fda4af", "scroll_thumb": "#7b8eae"},
}

def technology_tone(group, theme="light"):
    dark = theme == "dark"
    tones = {
        "Linguaggi": (("#1e40af", "#e5edff"), ("#b8d0ff", "#233b60")),
        "Desktop e GUI": (("#5b21b6", "#efe7ff"), ("#d4bfff", "#3a2857")),
        "Web e backend": (("#115e59", "#dff5ef"), ("#9de7d1", "#173d38")),
        "Database": (("#92400e", "#fff0d6"), ("#fbd38d", "#49331d")),
        "Strumenti": (("#334155", "#e9eef6"), ("#d0dced", "#2b3a50")),
    }
    return tones.get(group, tones["Strumenti"])[1 if dark else 0]

def status_tone(status, theme="light"):
    palette = THEMES.get(theme, THEMES["light"])
    return palette["success"] if status == "eseguito" else palette["accent"] if status == "compilato" else palette["muted"]

def apply_theme(app, name="system", zoom=0):
    if app.style().objectName().lower() != "fusion":
        app.setStyle("Fusion")
    if name == "system":
        name = "dark" if app.styleHints().colorScheme() == Qt.ColorScheme.Dark else "light"
    if name not in THEMES:
        name = "light"
    theme = THEMES[name]
    app.setProperty("devatlasTheme", name)
    app.setProperty("devatlasZoom", zoom)
    palette = QPalette()
    for role, key in ((QPalette.Window, "background"), (QPalette.WindowText, "text"),
                      (QPalette.Base, "surface"), (QPalette.AlternateBase, "raised"),
                      (QPalette.Text, "text"), (QPalette.Button, "surface"), (QPalette.ButtonText, "text"),
                      (QPalette.Highlight, "selection"), (QPalette.HighlightedText, "text"),
                      (QPalette.ToolTipBase, "surface"), (QPalette.ToolTipText, "text"), (QPalette.PlaceholderText, "muted")):
        palette.setColor(role, QColor(theme[key]))
    app.setPalette(palette)
    family = "Inter" if "Inter" in QFontDatabase.families() else "Segoe UI"
    font = QFont(family)
    font.setPointSizeF(10 + zoom)
    app.setFont(font)
    compact = app.property("devatlasDensity") == "compact"
    tokens = {**theme, "font_small": max(8, 9 + zoom), "font_body": 10 + zoom, "font_section": 12 + zoom,
              "font_title": 21 + zoom, "font_hero": 26 + zoom, "font_brand": 17 + zoom,
              "chevron": (PACKAGE / "assets" / ("ui-chevron-" + name + ".svg")).as_posix(),
              "button_y": 5 if compact else 7, "tree_y": 4 if compact else 6}
    app.setStyleSheet("""
      QWidget { color: %(text)s; }
      QMainWindow, QDialog { background: %(background)s; }
      QWidget#header { background: %(surface)s; border-bottom: 1px solid %(border)s; }
      QWidget#sidebar { background: %(sidebar)s; border-right: 1px solid %(border)s; }
      QWidget#reader { background: %(reader)s; }
      QWidget#resultsPanel { background: %(background)s; }
      QFrame#notice { background: %(raised)s; border: 1px solid %(warning)s; border-radius: 7px; }
      QFrame#destinationNotice { background: %(raised)s; border: 1px solid %(border)s; border-radius: 7px; }
      QLabel#brand { font-size: %(font_brand)spt; font-weight: 700; }
      QLabel#muted, QLabel#eyebrow { color: %(muted)s; }
      QLabel#eyebrow { font-size: %(font_small)spt; font-weight: 600; }
      QLabel#recipeTitle { font-size: %(font_title)spt; font-weight: 700; }
      QLabel#heroTitle { font-size: %(font_hero)spt; font-weight: 700; }
      QLabel#sectionTitle, QLabel#stateTitle { font-size: %(font_section)spt; font-weight: 600; }
      QLabel#badge { background: %(selection)s; color: %(accent_text)s; border-radius: 5px; padding: 4px 8px; font-size: %(font_small)spt; }
      QFrame#statCard { background: %(surface)s; border: 1px solid %(border)s; border-radius: 10px; }
      QLineEdit, QComboBox, QSpinBox, QPlainTextEdit, QTextEdit, QTextBrowser {
        background: %(surface)s; border: 1px solid %(border)s; border-radius: 7px; padding: 7px;
        placeholder-text-color: %(muted)s;
        selection-background-color: %(selection)s; selection-color: %(text)s; }
      QLineEdit#search { font-size: %(font_section)spt; padding: 10px 14px; border: 1px solid %(border)s; border-radius: 10px; background: %(raised)s; }
      QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus, QTextEdit:focus { border: 2px solid %(accent)s; padding: 6px; }
      QLineEdit#search:focus { padding: 9px 13px; }
      QComboBox { min-height: 23px; padding-right: 22px; }
      QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 22px; border: none; background: transparent; }
      QComboBox::down-arrow { image: url("%(chevron)s"); width: 12px; height: 8px; }
      QComboBox QAbstractItemView { background: %(surface)s; border: 1px solid %(border)s; selection-background-color: %(selection)s; }
      QPushButton, QToolButton { background: %(surface)s; border: 1px solid %(border)s; border-radius: 7px; padding: %(button_y)spx 12px; }
      QPushButton:hover, QToolButton:hover { background: %(selection)s; border-color: %(accent)s; }
      QPushButton:pressed, QToolButton:pressed { background: %(selection)s; }
      QPushButton:focus, QToolButton:focus { border: 2px solid %(accent)s; }
      QPushButton:disabled, QToolButton:disabled { color: %(muted)s; background: %(raised)s; }
      QPushButton#primary { background: %(accent)s; color: %(surface)s; border: 1px solid %(accent)s; font-weight: 600; }
      QPushButton#primary:hover { background: %(accent_hover)s; }
      QPushButton#iconButton, QToolButton#iconButton { padding: 5px; }
      QPushButton#filterChip { background: %(selection)s; border: 1px solid %(selection)s; color: %(accent_text)s; padding: 4px 9px; border-radius: 12px; font-size: %(font_small)spt; }
      QPushButton#filterChip:hover { border-color: %(accent)s; }
      QTreeWidget { background: %(sidebar)s; border: none; outline: 0; }
      QTreeWidget::item { padding: %(tree_y)spx 4px; margin: 1px 3px; border-radius: 6px; min-height: 19px; }
      QTreeWidget::item:selected { background: %(selection)s; color: %(accent_text)s; }
      QTreeWidget::item:hover { background: %(raised)s; }
      QListView { background: transparent; border: none; outline: 0; }
      QFrame#codeBlock { background: %(code)s; border: 1px solid %(border)s; border-radius: 9px; }
      QPlainTextEdit#code { background: %(code)s; border: none; border-radius: 0px; padding: 5px; }
      QTabWidget::pane { border: 1px solid %(border)s; background: %(surface)s; border-radius: 7px; }
      QTabBar::tab { padding: 9px 14px; color: %(muted)s; border-bottom: 2px solid transparent; }
      QTabBar::tab:selected { color: %(accent)s; border-bottom-color: %(accent)s; }
      QScrollArea { border: none; background: transparent; }
      QSplitter::handle { background: %(border)s; width: 1px; height: 1px; }
      QSplitter::handle:hover { background: %(accent)s; }
      QStatusBar { background: %(surface)s; border-top: 1px solid %(border)s; color: %(muted)s; font-size: %(font_small)spt; }
      QMenu { background: %(surface)s; border: 1px solid %(border)s; padding: 5px; }
      QMenu::item { padding: 8px 25px 8px 12px; border-radius: 4px; }
      QMenu::item:selected { background: %(selection)s; }
      QToolTip { background: %(surface)s; color: %(text)s; border: 1px solid %(border)s; padding: 5px; }
      QScrollBar:vertical { background: %(raised)s; width: 10px; margin: 0; }
      QScrollBar::handle:vertical { background: %(scroll_thumb)s; border-radius: 5px; min-height: 30px; }
      QScrollBar::handle:vertical:hover { background: %(accent)s; }
      QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
    """ % tokens)
    return theme
