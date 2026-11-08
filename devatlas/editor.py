from __future__ import annotations
from copy import deepcopy
from datetime import date
import uuid
import csv
import io
import hashlib
from pathlib import PurePosixPath
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout,
    QInputDialog, QLabel, QLineEdit, QListWidget, QMenu, QMessageBox, QPlainTextEdit, QPushButton,
    QScrollArea, QSplitter, QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)
from devatlas.bundles import validate_recipe
from devatlas.codewidgets import CodeEditor, CodeFindBar, OfflineBrowser
from devatlas.models import SECTIONS
from devatlas.templating import safe_relative


LANGUAGES = {'.py':'python','.cpp':'cpp','.hpp':'cpp','.h':'cpp','.c':'c','.cs':'csharp',
    '.js':'javascript','.mjs':'javascript','.cjs':'javascript','.ts':'typescript','.tsx':'tsx',
    '.jsx':'jsx','.rs':'rust','.go':'go','.java':'java','.sql':'sql','.json':'json','.ps1':'powershell',
    '.sh':'bash','.bat':'text','.cmd':'text','.html':'html','.css':'css','.yml':'yaml','.yaml':'yaml',
    '.xml':'xml','.xaml':'xml','.csproj':'xml','.toml':'toml','.md':'markdown','.dart':'dart',
    '.vue':'vue','.svelte':'svelte','.kt':'kotlin','.kts':'kotlin','.swift':'swift','.php':'php','.rb':'ruby'}
FILE_TEMPLATES = {
    'python':'def main():\n    print("Ciao")\n\nif __name__ == "__main__":\n    main()\n',
    'cpp':'#include <iostream>\n\nint main() {\n    std::cout << "Ciao\\n";\n    return 0;\n}\n',
    'c':'#include <stdio.h>\n\nint main(void) {\n    puts("Ciao");\n    return 0;\n}\n',
    'csharp':'Console.WriteLine("Ciao");\n',
    'javascript':'export function greet(name) {\n    return `Ciao ${name}`;\n}\n',
    'typescript':'export function greet(name: string): string {\n    return `Ciao ${name}`;\n}\n',
    'sql':'SELECT 1 AS risultato;\n','json':'{\n}\n','yaml':'name: esempio\n',
    'toml':'[app]\nname = "esempio"\n','powershell':"$ErrorActionPreference = 'Stop'\nWrite-Output 'Ciao'\n",
    'bash':"#!/usr/bin/env bash\nset -euo pipefail\nprintf 'Ciao\\n'\n",
    'rust':'fn main() {\n    println!("Ciao");\n}\n',
    'go':'package main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Ciao")\n}\n',
    'java':'class Main {\n    public static void main(String[] args) {\n        System.out.println("Ciao");\n    }\n}\n',
    'dart':"void main() {\n  print('Ciao');\n}\n",
    'html':'<!doctype html>\n<html lang="it">\n<head><meta charset="utf-8"><title>Esempio</title></head>\n<body><h1>Ciao</h1></body>\n</html>\n',
    'css':'body {\n    font-family: system-ui, sans-serif;\n}\n',
    'vue':'<script setup>\nimport { ref } from "vue";\nconst message = ref("Ciao");\n</script>\n<template><p>{{ message }}</p></template>\n',
    'svelte':'<script>\nlet message = $state("Ciao");\n</script>\n<p>{message}</p>\n',
    'markdown':'# Titolo\n\nDescrivi obiettivo, prerequisiti e risultato atteso.\n',
    'cmake':'cmake_minimum_required(VERSION 3.24)\nproject(Esempio LANGUAGES CXX)\nadd_executable(esempio main.cpp)\n',
    'dockerfile':'FROM python:3.13-slim\nWORKDIR /app\nCOPY main.py .\nCMD ["python", "main.py"]\n',
}


def language_for_path(path):
    name = PurePosixPath(path.replace('\\', '/')).name
    if name == 'CMakeLists.txt':return 'cmake'
    if name == 'Dockerfile':return 'dockerfile'
    return LANGUAGES.get(PurePosixPath(name).suffix.lower(), 'text')


def csv_text(values):
    output = io.StringIO()
    csv.writer(output, lineterminator='').writerow(values)
    return output.getvalue()


def csv_values(edit):
    try:
        return [value.strip() for value in next(csv.reader([edit.text()], skipinitialspace=True, strict=True)) if value.strip()]
    except csv.Error as error:
        raise ValueError("Chiudi le virgolette dei valori separati da virgole.") from error


def set_combo_text(combo, text):
    if combo.findText(text) < 0:
        combo.addItem(text)
    combo.setCurrentText(text)


class RecipeEditor(QDialog):
    def __init__(self, stacks: dict, recipe=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modifica scheda personale" if recipe and recipe.get("personal") else "Nuova scheda personale")
        available = self.screen().availableGeometry()
        self.resize(min(1050, available.width() - 40), min(780, available.height() - 55))
        self.setMinimumSize(680, 420)
        self.result_recipe = None
        self.original = deepcopy(recipe or {})
        self.assets = deepcopy(self.original.get("assets", [{"id": "file-0", "path": "esempio.py", "language": "python", "role": "file", "content": "print('Ciao da DevAtlas')\n"}]))
        self.active_asset = -1
        self.loading_asset = False
        self._loaded_asset_text = ""
        self._last_asset_path = ""
        self.dirty = False
        layout = QVBoxLayout(self)
        intro = QLabel("Le tue ricette restano separate dal catalogo incluso. Codice, comandi e istruzioni vengono esportati insieme.")
        intro.setWordWrap(True)
        intro.setObjectName("muted")
        layout.addWidget(intro)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, 1)
        general = QWidget()
        form = QFormLayout(general)
        self.title_edit = QLineEdit(self.original.get("title", ""))
        self.title_edit.setAccessibleName("Titolo della scheda")
        self.summary_edit = QPlainTextEdit(self.original.get("summary", ""))
        self.summary_edit.setMaximumHeight(80)
        self.stack_edit = QComboBox()
        for sid, spec in stacks.items():
            self.stack_edit.addItem(spec["label"], sid)
        current = self.stack_edit.findData(self.original.get("stack", "python"))
        self.stack_edit.setCurrentIndex(max(0, current))
        self.section_edit = QComboBox()
        self.section_edit.addItems(SECTIONS)
        set_combo_text(self.section_edit, self.original.get("section", "Codice applicativo"))
        self.difficulty_edit = QComboBox()
        self.difficulty_edit.addItems(["Base", "Intermedio", "Avanzato"])
        set_combo_text(self.difficulty_edit, self.original.get("difficulty", "Base"))
        self.project_edit = QCheckBox("Contiene un progetto completo")
        self.project_edit.setChecked(bool(self.original.get("project")))
        self.project_edit.toggled.connect(self.mark_dirty)
        self.version_edit = QLineEdit(self.original.get("versions", ""))
        self.prerequisites_edit = QPlainTextEdit(self.original.get("prerequisites", ""))
        self.prerequisites_edit.setMaximumHeight(65)
        self.expected_edit = QPlainTextEdit(self.original.get("expected", ""))
        self.expected_edit.setMaximumHeight(65)
        self.tags_edit = QLineEdit(csv_text(self.original.get("tags", [])))
        self.os_edit = QLineEdit(csv_text(self.original.get("os", ["Windows"])))
        self.ide_edit = QLineEdit(csv_text(self.original.get("ide", ["VS Code"])))
        self.sources_edit = QLineEdit(csv_text(self.original.get("sources", [])))
        for edit in (self.tags_edit, self.os_edit, self.ide_edit, self.sources_edit):
            edit.setToolTip('Separa con virgole; racchiudi fra virgolette i valori che contengono una virgola.')
        for label, widget in (("Titolo *", self.title_edit), ("Obiettivo *", self.summary_edit),
            ("Tecnologia", self.stack_edit), ("Sezione", self.section_edit), ("Difficoltà", self.difficulty_edit), ("Progetto", self.project_edit),
            ("Versioni", self.version_edit), ("Prerequisiti", self.prerequisites_edit), ("Risultato atteso", self.expected_edit),
            ("Tag, separati da virgole", self.tags_edit), ("Sistemi", self.os_edit), ("IDE", self.ide_edit), ("Fonti (URL)", self.sources_edit)):
            form.addRow(label, widget)
        def scrollable(page):
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(page)
            return scroll
        self.tabs.addTab(scrollable(general), "Ricetta")
        files = QWidget()
        files_layout = QVBoxLayout(files)
        split = QSplitter()
        self.asset_list = QListWidget()
        self.asset_list.setAccessibleName("File e blocchi della scheda")
        self.asset_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.asset_list.customContextMenuRequested.connect(self.asset_context_menu)
        self.asset_list.setMaximumWidth(260)
        split.addWidget(self.asset_list)
        source = QWidget()
        source_layout = QVBoxLayout(source)
        info = QFormLayout()
        self.asset_form = info
        self.path_edit = QLineEdit()
        self.role_edit = QComboBox()
        for label, key in (("File completo", "file"), ("Frammento da inserire", "snippet"), ("Comandi", "command")):
            self.role_edit.addItem(label, key)
        self.language_edit = QComboBox()
        self.language_edit.setEditable(True)
        self.language_edit.addItems(list(dict.fromkeys(["python", "cpp", "csharp", "javascript", "typescript", "tsx", "jsx", *LANGUAGES.values(), "cmake", "dockerfile", "text"])))
        self.shell_edit = QComboBox()
        self.shell_edit.addItems(["PowerShell", "Bash", "CMD"])
        self.cwd_edit = QLineEdit(".")
        self.command_os = QComboBox()
        self.command_os.addItems(["Windows", "Linux", "macOS", "Tutti"])
        for label, widget in (("Percorso o etichetta", self.path_edit), ("Tipo", self.role_edit),
            ("Linguaggio", self.language_edit), ("Shell dei comandi", self.shell_edit),
            ("Sistema dei comandi", self.command_os), ("Directory dei comandi", self.cwd_edit)):
            info.addRow(label, widget)
        source_layout.addLayout(info)
        self.code_edit = CodeEditor(readonly=False)
        self.code_edit.setAccessibleName("Codice modificabile")
        self.code_edit.setMinimumHeight(180)
        code_tools = QHBoxLayout()
        find = QPushButton("Trova nel codice")
        find.clicked.connect(self.show_code_find)
        self.wrap_edit = QCheckBox("A capo")
        self.wrap_edit.toggled.connect(lambda enabled: self.code_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth if enabled else QPlainTextEdit.LineWrapMode.NoWrap))
        self.template_button = QPushButton("Inserisci modello")
        self.template_button.setToolTip("Inserisce un modello soltanto in un blocco vuoto; non esegue codice")
        self.template_button.clicked.connect(self.insert_template)
        for widget in (find, self.wrap_edit, self.template_button):code_tools.addWidget(widget)
        code_tools.addStretch()
        source_layout.addLayout(code_tools)
        self.code_find = CodeFindBar(self.code_edit, self)
        source_layout.addWidget(self.code_find)
        source_layout.addWidget(self.code_edit, 1)
        split.addWidget(source)
        split.setStretchFactor(1, 1)
        files_layout.addWidget(split, 1)
        row = QHBoxLayout()
        for label, callback in (("Aggiungi file", self.add_file), ("Aggiungi comandi", self.add_command), ("Rimuovi blocco", self.remove_asset)):
            button = QPushButton(label)
            button.clicked.connect(callback)
            row.addWidget(button)
        row.addStretch()
        files_layout.addLayout(row)
        self.tabs.addTab(scrollable(files), "Codice e comandi")
        self.guide_edit = QPlainTextEdit(self.original.get("guide", ""))
        self.guide_edit.setPlaceholderText("Spiega i passaggi in Markdown. Per i frammenti indica il file e il punto esatto in cui inserirli.")
        self.tabs.addTab(self.guide_edit, "Guida")
        self.preview = OfflineBrowser()
        self.tabs.addTab(self.preview, "Anteprima guida")
        parameter_page = QWidget()
        pv = QVBoxLayout(parameter_page)
        hint = QLabel("Inserisci {{nome}} nei file e nei comandi. Per stringhe usa {{nome|json}}, per argomenti {{nome|powershell}} o {{nome|bash}}.")
        hint.setWordWrap(True)
        pv.addWidget(hint)
        self.parameter_table = QTableWidget(0, 5)
        self.parameter_table.setHorizontalHeaderLabels(["Nome", "Etichetta", "Tipo", "Valore iniziale", "Obbligatorio"])
        self.parameter_table.horizontalHeader().setStretchLastSection(True)
        for p in self.original.get("parameters", []):
            self.add_parameter(p)
        pv.addWidget(self.parameter_table)
        pr = QHBoxLayout()
        plus = QPushButton("Aggiungi parametro")
        plus.clicked.connect(lambda: self.add_parameter())
        minus = QPushButton("Rimuovi parametro")
        minus.clicked.connect(self.remove_parameter)
        pr.addWidget(plus)
        pr.addWidget(minus)
        pr.addStretch()
        pv.addLayout(pr)
        self.tabs.addTab(scrollable(parameter_page), "Parametri")
        self.errors_edit = QPlainTextEdit("\n".join(self.original.get("errors", [])))
        self.errors_edit.setPlaceholderText("Un errore frequente e la sua soluzione per riga.")
        self.tabs.addTab(self.errors_edit, "Errori frequenti")
        self.validation_label = QLabel()
        self.validation_label.setTextFormat(Qt.TextFormat.PlainText)
        self.validation_label.setWordWrap(True)
        self.validation_label.setObjectName("validationMessage")
        self.validation_label.hide()
        self._invalid_widget = None
        layout.addWidget(self.validation_label)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Salva scheda")
        buttons.button(QDialogButtonBox.StandardButton.Save).setObjectName("primary")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Annulla")
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.asset_list.currentRowChanged.connect(self.select_asset)
        self.tabs.currentChanged.connect(lambda: self.preview.setMarkdown(self.guide_edit.toPlainText()))
        self.refresh_assets()
        self.asset_list.setCurrentRow(0)
        for edit in self.findChildren(QLineEdit):
            if not edit.property("transientUi"):
                edit.textChanged.connect(self.mark_dirty)
        for edit in self.findChildren(QPlainTextEdit):
            edit.document().contentsChange.connect(lambda position, removed, added: self.mark_dirty() if removed or added else None)
        for combo in self.findChildren(QComboBox):
            combo.currentTextChanged.connect(self.mark_dirty)
        self.path_edit.textChanged.connect(self.update_asset_title)
        self.path_edit.textChanged.connect(self.infer_language)
        self.language_edit.currentTextChanged.connect(self.code_edit.set_language)
        self.language_edit.currentTextChanged.connect(self.update_template_button)
        self.code_edit.textChanged.connect(self.update_template_button)
        self.shell_edit.currentTextChanged.connect(self.sync_command_language)
        self.role_edit.currentIndexChanged.connect(self.update_command_fields)
        self.parameter_table.itemChanged.connect(self.mark_dirty)
        self.save_shortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        self.save_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.save_shortcut.activated.connect(self.save)
        self.file_shortcut = QShortcut(QKeySequence("Ctrl+Shift+N"), self)
        self.file_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.file_shortcut.activated.connect(self.add_file)
        self.remove_shortcut = QShortcut(QKeySequence("Delete"), self.asset_list)
        self.remove_shortcut.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.remove_shortcut.activated.connect(self.remove_asset)
        self.update_command_fields()
        self.update_template_button()
        self.dirty = False

    def mark_dirty(self, *args):
        if not self.loading_asset:
            self.dirty = True
            if hasattr(self, "validation_label"):
                self.validation_label.hide()
                if self._invalid_widget is not None:
                    self._invalid_widget.setProperty("invalid", False)
                    self._invalid_widget.style().unpolish(self._invalid_widget)
                    self._invalid_widget.style().polish(self._invalid_widget)
                    self._invalid_widget = None

    def show_code_find(self):
        self.tabs.setCurrentIndex(1)
        self.code_edit.show_find()
        self.tabs.widget(1).ensureWidgetVisible(self.code_find)

    def asset_context_menu(self, point):
        item = self.asset_list.itemAt(point)
        if item is not None:
            self.asset_list.setCurrentItem(item)
        menu = QMenu(self)
        menu.addAction("Trova nel codice…", self.show_code_find)
        menu.addSeparator()
        menu.addAction("Aggiungi file…", self.add_file)
        menu.addAction("Aggiungi comandi", self.add_command)
        remove = menu.addAction("Rimuovi blocco", self.remove_asset)
        remove.setEnabled(len(self.assets) > 1)
        try:
            menu.exec(self.asset_list.viewport().mapToGlobal(point))
        finally:
            menu.deleteLater()

    def infer_language(self, path):
        if self.loading_asset:return
        old_language = language_for_path(self._last_asset_path)
        if self.role_edit.currentData() != "command" and self.language_edit.currentText() in (old_language, "text"):
            self.language_edit.setCurrentText(language_for_path(path))
        self._last_asset_path = path

    def update_template_button(self, *args):
        if hasattr(self, "template_button"):
            self.template_button.setEnabled(not self.code_edit.toPlainText() and self.language_edit.currentText() in FILE_TEMPLATES)

    def insert_template(self):
        if self.code_edit.toPlainText():return
        text = FILE_TEMPLATES.get(self.language_edit.currentText())
        if text is not None:
            self.code_edit.setPlainText(text)
            self.code_edit.setFocus()

    def update_command_fields(self, *args):
        command = self.role_edit.currentData() == "command"
        for widget in (self.shell_edit, self.command_os, self.cwd_edit):
            self.asset_form.setRowVisible(widget, command)
        self.update_template_button()

    def show_validation(self, message, widget=None, tab=None):
        self.validation_label.setText("Controlla la scheda: " + message)
        self.validation_label.setAccessibleName("Errore di validazione: " + message)
        self.validation_label.show()
        if widget is not None:
            self._invalid_widget = widget
            widget.setProperty("invalid", True)
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            if tab is not None:
                self.tabs.setCurrentIndex(tab)
                scroll = self.tabs.widget(tab)
                if isinstance(scroll, QScrollArea):scroll.ensureWidgetVisible(widget)
            widget.setFocus()

    def add_parameter(self, parameter=None):
        parameter = parameter or {"name": "project_name", "label": "Nome progetto", "type": "identifier", "default": "MioProgetto"}
        row = self.parameter_table.rowCount()
        self.parameter_table.insertRow(row)
        for column, key in ((0, "name"), (1, "label"), (3, "default")):
            self.parameter_table.setItem(row, column, QTableWidgetItem(str(parameter.get(key, ""))))
        self.parameter_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, deepcopy(parameter))
        combo = QComboBox()
        combo.addItems(["identifier", "namespace", "port", "path", "string"])
        combo.setCurrentText(parameter.get("type", "string"))
        combo.currentTextChanged.connect(self.mark_dirty)
        self.parameter_table.setCellWidget(row, 2, combo)
        required = QTableWidgetItem()
        required.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable)
        required.setCheckState(Qt.CheckState.Checked if parameter.get("required", True) else Qt.CheckState.Unchecked)
        self.parameter_table.setItem(row, 4, required)
        self.dirty = True

    def remove_parameter(self):
        row = self.parameter_table.currentRow()
        if row >= 0:
            self.parameter_table.removeRow(row)
            self.dirty = True

    def update_asset_title(self, text):
        if not self.loading_asset and 0 <= self.active_asset < self.asset_list.count():
            self.asset_list.item(self.active_asset).setText(text)

    def sync_command_language(self, shell):
        if not self.loading_asset and self.role_edit.currentData() == "command":
            self.language_edit.setCurrentText({"PowerShell": "powershell", "Bash": "bash", "CMD": "text"}.get(shell, "text"))

    def refresh_assets(self):
        self.asset_list.blockSignals(True)
        self.asset_list.clear()
        self.asset_list.addItems([asset.get("path", "Codice") for asset in self.assets])
        self.asset_list.blockSignals(False)

    def save_active_asset(self):
        if 0 <= self.active_asset < len(self.assets):
            asset = self.assets[self.active_asset]
            current = self.code_edit.toPlainText()
            if current != self._loaded_asset_text:
                asset["content"] = current
                if "sha256" in asset:asset["sha256"] = hashlib.sha256(current.encode()).hexdigest()
            asset.update(path=self.path_edit.text(), role=self.role_edit.currentData(), language=self.language_edit.currentText())
            if self.role_edit.currentData() == "command":
                asset.update(shell=self.shell_edit.currentText(), os=self.command_os.currentText(), cwd=self.cwd_edit.text())
            self._loaded_asset_text = current

    def select_asset(self, index):
        self.save_active_asset()
        self.active_asset = index
        if index < 0:
            return
        asset = self.assets[index]
        self.loading_asset = True
        self.path_edit.setText(asset.get("path", ""))
        self.role_edit.setCurrentIndex(max(0, self.role_edit.findData(asset.get("role", "file"))))
        self.language_edit.setCurrentText(asset.get("language", "text"))
        set_combo_text(self.shell_edit, asset.get("shell", "PowerShell"))
        set_combo_text(self.command_os, asset.get("os", "Windows"))
        self.cwd_edit.setText(asset.get("cwd", "."))
        self.code_edit.setPlainText(asset.get("content", ""))
        self.code_edit.set_language(asset.get("language", "text"))
        self._loaded_asset_text = self.code_edit.toPlainText()
        self._last_asset_path = asset.get("path", "")
        self.loading_asset = False
        self.update_command_fields()
        self.update_template_button()

    def add_file(self):
        name, accepted = QInputDialog.getText(self, "Nuovo file", "Percorso relativo (esempio: src/main.py)")
        if not accepted:
            return
        try:
            safe_relative(name)
        except ValueError as error:
            QMessageBox.warning(self, "Percorso non valido", str(error))
            return
        self.save_active_asset()
        self.assets.append({"id": uuid.uuid4().hex, "path": name, "role": "file", "language": language_for_path(name), "content": ""})
        self.active_asset = -1
        self.refresh_assets()
        self.asset_list.setCurrentRow(len(self.assets) - 1)
        self.dirty = True

    def add_command(self):
        self.save_active_asset()
        self.assets.append({"id": uuid.uuid4().hex, "path": "Comandi", "role": "command", "language": "powershell", "content": "", "shell": "PowerShell", "os": "Windows", "cwd": "."})
        self.active_asset = -1
        self.refresh_assets()
        self.asset_list.setCurrentRow(len(self.assets) - 1)
        self.dirty = True

    def remove_asset(self):
        if len(self.assets) <= 1:
            QMessageBox.information(self, "Blocco necessario", "Mantieni almeno un file, frammento o blocco di comandi.")
            return
        index = self.asset_list.currentRow()
        if index >= 0:
            self.assets.pop(index)
            self.active_asset = -1
            self.refresh_assets()
            self.asset_list.setCurrentRow(min(index, len(self.assets) - 1))
            self.dirty = True

    def save(self):
        if not self.title_edit.text().strip():
            self.show_validation("Inserisci il titolo.", self.title_edit, 0)
            return
        if not self.summary_edit.toPlainText().strip():
            self.show_validation("Descrivi l’obiettivo della scheda.", self.summary_edit, 0)
            return
        self.save_active_asset()
        parameters = []
        try:
            metadata = {}
            for key, edit, caption in (("tags", self.tags_edit, "Tag"), ("os", self.os_edit, "Sistemi"),
                                       ("ide", self.ide_edit, "IDE"), ("sources", self.sources_edit, "Fonti")):
                try:
                    metadata[key] = csv_values(edit)
                except ValueError as error:
                    self.show_validation(caption + ": " + str(error), edit, 0)
                    return
            for row in range(self.parameter_table.rowCount()):
                def text(column):
                    item = self.parameter_table.item(row, column)
                    return item.text() if item else ""
                name = text(0)
                import re
                if not re.fullmatch(r"[A-Za-z_]\w*", name) or any(p["name"] == name for p in parameters):
                    self.parameter_table.setCurrentCell(row, 0)
                    self.show_validation("I nomi dei parametri devono essere identificatori univoci.", self.parameter_table, 4)
                    return
                required = self.parameter_table.item(row, 4)
                parameter = deepcopy(self.parameter_table.item(row, 0).data(Qt.ItemDataRole.UserRole) or {})
                default = parameter.get("default") if "default" in parameter and str(parameter["default"]) == text(3) else text(3)
                parameter.update(name=name, type=self.parameter_table.cellWidget(row, 2).currentText(), default=default, required=required is None or required.checkState() == Qt.CheckState.Checked)
                if text(1) or "label" in parameter:
                    parameter["label"] = text(1) or name
                from devatlas.templating import validate_parameter
                try:
                    validate_parameter(parameter, str(default))
                except ValueError as error:
                    self.parameter_table.setCurrentCell(row, 3)
                    self.show_validation(str(error), self.parameter_table, 4)
                    return
                parameters.append(parameter)
            for number, asset in enumerate(self.assets):
                try:
                    if not asset.get("path", "").strip():raise ValueError("Inserisci il percorso o l’etichetta del blocco.")
                    if asset.get("role") != "command":safe_relative(asset["path"])
                    elif not asset.get("cwd", ".").strip():raise ValueError("Inserisci la directory dei comandi, per esempio un punto.")
                except ValueError as error:
                    self.asset_list.setCurrentRow(number)
                    self.show_validation(str(error), self.cwd_edit if asset.get("role") == "command" else self.path_edit, 1)
                    return
            data = deepcopy(self.original)
            data.update(id=self.original.get("id", "") if self.original.get("personal") else "personal-" + uuid.uuid4().hex,
                title=self.title_edit.text().strip(), summary=self.summary_edit.toPlainText().strip(), stack=self.stack_edit.currentData(),
                group="Personali", section=self.section_edit.currentText(), difficulty=self.difficulty_edit.currentText(), project=self.project_edit.isChecked(),
                versions=self.version_edit.text(), prerequisites=self.prerequisites_edit.toPlainText(), expected=self.expected_edit.toPlainText(),
                tags=metadata["tags"], os=metadata["os"], ide=metadata["ide"], sources=metadata["sources"],
                guide=self.guide_edit.toPlainText(), assets=self.assets, parameters=parameters,
                errors=[s.strip() for s in self.errors_edit.toPlainText().splitlines() if s.strip()], reviewed=date.today().isoformat(),
                verification={"status": "documentato", "details": "Scheda personale: esecuzione non attestata.", "date": date.today().isoformat()}, personal=True)
            validate_recipe(data)
            self.result_recipe = data
            self.dirty = False
            self.accept()
        except (ValueError, TypeError, KeyError) as error:
            self.show_validation(str(error))

    def reject(self):
        if self.dirty:
            answer = QMessageBox.question(self, "Modifiche non salvate", "Vuoi chiudere senza salvare le modifiche?", QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Cancel)
            if answer != QMessageBox.StandardButton.Discard:
                return
        super().reject()

