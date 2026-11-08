"""Command selection contracts: no shell, no catalog dependency, no stale dialog parent."""
from dataclasses import FrozenInstanceError
import pytest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QDialog, QWidget

from devatlas.commandpalette import Command, CommandModel, CommandPalette, MAX_COMMANDS
from devatlas.theme import apply_theme


@pytest.fixture(autouse=True)
def preserve_application_style(qapp):
    palette, font, stylesheet = qapp.palette(), qapp.font(), qapp.styleSheet()
    theme = qapp.property("devatlasTheme")
    yield
    qapp.setPalette(palette)
    qapp.setFont(font)
    qapp.setStyleSheet(stylesheet)
    qapp.setProperty("devatlasTheme", theme)


def commands(events=None):
    events = events if events is not None else []
    def entry(rid,title,category="Azioni",description="",**kwargs):
        return Command(rid,title,category,lambda:events.append(rid),description=description,**kwargs)
    return [
        entry("favorites","Mostra preferiti",description="Apri le schede preferite",shortcut="Alt+F"),
        entry("guided","Modalità guidata",description="Mostra spiegazioni del codice",keywords=("lettore",)),
        entry("export","Esporta progetto",description="Salva i file della ricetta",enabled=False),
        entry("cpp","C++","Tecnologie","Apri il linguaggio C++"),
        entry("csharp","C#","Tecnologie","Apri il linguaggio C#"),
        entry("c","C","Tecnologie","Apri il linguaggio C"),
        entry("javascript","JavaScript","Tecnologie","Apri il linguaggio JavaScript"),
        entry("recent","Regex e validazione","Ricette recenti","Apri la scheda appena consultata"),
    ]


def show_palette(qtbot,items,parent=None):
    palette=CommandPalette(items,parent)
    qtbot.addWidget(palette)
    palette.show()
    qtbot.waitUntil(lambda:palette.isVisible() and palette.searchEdit.hasFocus())
    return palette


def visible_ids(model):
    return [model.command(model.index(row)).id for row in range(model.rowCount())]


def test_command_contract_is_immutable_and_non_callable_is_not_enabled():
    command=Command("x","Titolo","Azioni",None)
    assert not command.available
    with pytest.raises(FrozenInstanceError):command.title="Altro"


@pytest.mark.parametrize(("query","expected"),[
    ("modalita",["guided"]), ("modalità guidata",["guided"]), ("open favourites",["favorites"]),
    ("apri preferite",["favorites"]), ("lettore",["guided"]), ("js",["javascript"]),
    ("C++",["cpp"]), ("C#",["csharp"]), ("C",["c"]),
    ("apri ricetta recente",["recent"]), ("espor",["export"]),
])
def test_filter_handles_accents_simple_synonyms_symbols_and_keywords(query,expected):
    model=CommandModel(commands())
    model.set_query(query)
    assert visible_ids(model)==expected


def test_bounded_input_does_not_materialize_the_catalog():
    consumed=[]
    def source():
        for n in range(2140):
            consumed.append(n)
            yield Command(str(n),f"Ricetta {n}","Recenti",lambda:None)
    model=CommandModel(source())
    assert model.rowCount()==MAX_COMMANDS
    assert len(consumed)==MAX_COMMANDS+1
    assert model.truncated


def test_duplicate_ids_do_not_create_ambiguous_callbacks():
    first=Command("same","Prima","Azioni",lambda:None)
    second=Command("same","Seconda","Azioni",lambda:None)
    model=CommandModel([first,second])
    assert model.rowCount()==1
    assert model.command(model.index(0)) is first


def test_initial_focus_and_navigation_skip_disabled_commands(qtbot):
    events=[]
    items=[Command("first","Prima","Azioni",lambda:events.append("first")),
           Command("disabled","Non disponibile","Azioni",lambda:events.append("disabled"),enabled=False),
           Command("last","Ultima","Azioni",lambda:events.append("last"))]
    palette=show_palette(qtbot,items)
    assert palette.model.command(palette.listView.currentIndex()).id=="first"
    qtbot.keyClick(palette.searchEdit,Qt.Key.Key_Down)
    assert palette.model.command(palette.listView.currentIndex()).id=="last"
    qtbot.keyClick(palette.searchEdit,Qt.Key.Key_Down)
    assert palette.model.command(palette.listView.currentIndex()).id=="first"
    qtbot.keyClick(palette.searchEdit,Qt.Key.Key_Up)
    assert palette.model.command(palette.listView.currentIndex()).id=="last"
    assert palette.searchEdit.hasFocus() and not events


def test_enter_closes_before_the_callback_and_only_dispatches_once(qtbot):
    events=[]
    palette=None
    def action():events.append(("callback",palette.isVisible(),palette.result()))
    palette=show_palette(qtbot,[Command("run","Esegui azione","Azioni",action)])
    palette.accepted.connect(lambda:events.append(("accepted",)))
    qtbot.keyClick(palette.searchEdit,Qt.Key.Key_Return)
    palette._activate_index(palette.model.index(0))
    qtbot.waitUntil(lambda:len(events)==2)
    assert events[0]==("accepted",)
    assert events[1]==("callback",False,int(QDialog.DialogCode.Accepted))


def test_selected_action_can_open_another_modal_with_the_owner_as_parent(qtbot):
    owner=QWidget();qtbot.addWidget(owner);owner.show()
    opened=[]
    palette=None
    def action():
        assert not palette.isVisible()
        dialog=QDialog(owner);dialog.setModal(True);qtbot.addWidget(dialog);dialog.show();opened.append(dialog)
    palette=show_palette(qtbot,[Command("dialog","Apri impostazioni","Azioni",action)],owner)
    qtbot.keyClick(palette.searchEdit,Qt.Key.Key_Enter)
    qtbot.waitUntil(lambda:len(opened)==1)
    assert opened[0].isVisible() and opened[0].parentWidget() is owner
    assert opened[0].parentWidget() is not palette
    opened[0].reject()


def test_modal_exec_can_be_followed_by_another_modal_without_nesting_the_palette(qtbot):
    owner=QWidget();qtbot.addWidget(owner);owner.show()
    events=[]
    palette=None
    def action():
        events.append(QApplication.activeModalWidget() is not palette)
        child=QDialog(owner)
        QTimer.singleShot(0,child.accept)
        events.append(child.exec()==QDialog.DialogCode.Accepted)
    palette=CommandPalette([Command("modal","Apri dialogo","Azioni",action)],owner)
    qtbot.addWidget(palette)
    QTimer.singleShot(0,lambda:qtbot.keyClick(palette.searchEdit,Qt.Key.Key_Return))
    assert palette.exec()==QDialog.DialogCode.Accepted
    qtbot.waitUntil(lambda:len(events)==2)
    assert events==[True,True]


def test_mouse_selection_dispatches_enabled_command(qtbot):
    events=[]
    palette=show_palette(qtbot,[Command("click","Apri","Azioni",lambda:events.append("click"))])
    qtbot.mouseClick(palette.listView.viewport(),Qt.MouseButton.LeftButton,pos=palette.listView.visualRect(palette.model.index(0)).center())
    qtbot.waitUntil(lambda:events==["click"])
    assert not palette.isVisible()


@pytest.mark.parametrize("focus",["searchEdit","listView"])
def test_escape_cancels_without_running_actions(qtbot,focus):
    events=[]
    palette=show_palette(qtbot,commands(events))
    getattr(palette,focus).setFocus()
    qtbot.keyClick(getattr(palette,focus),Qt.Key.Key_Escape)
    assert not palette.isVisible() and not events and palette.selectedCommand is None
    assert palette.result()==QDialog.DialogCode.Rejected


def test_disabled_action_cannot_run_from_enter_or_mouse(qtbot):
    events=[]
    palette=show_palette(qtbot,[Command("disabled","Esporta","Azioni",lambda:events.append("bad"),enabled=False)])
    index=palette.model.index(0)
    assert not (palette.model.flags(index)&Qt.ItemFlag.ItemIsEnabled)
    assert "non disponibile" in palette.model.data(index,Qt.ItemDataRole.AccessibleTextRole)
    palette.listView.setCurrentIndex(index)
    qtbot.keyClick(palette.searchEdit,Qt.Key.Key_Return)
    qtbot.mouseClick(palette.listView.viewport(),Qt.MouseButton.LeftButton,pos=palette.listView.visualRect(index).center())
    qtbot.wait(10)
    assert palette.isVisible() and not events
    assert "nessuna azione attivabile" in palette.countLabel.text()


def test_empty_result_is_explained_and_enter_does_not_accept(qtbot):
    palette=show_palette(qtbot,commands())
    palette.searchEdit.setText("nessuna-corrispondenza")
    assert palette.model.rowCount()==0 and palette.emptyLabel.isVisible()
    assert "Nessun comando trovato" in palette.emptyLabel.text()
    qtbot.keyClick(palette.searchEdit,Qt.Key.Key_Return)
    assert palette.isVisible()
    palette.searchEdit.clear()
    assert palette.model.rowCount()==8 and not palette.emptyLabel.isVisible()


def test_empty_input_list_has_an_accessible_empty_state(qtbot):
    palette=show_palette(qtbot,[])
    assert palette.emptyLabel.isVisible()
    assert palette.emptyLabel.text()=="Non ci sono azioni disponibili."
    assert palette.searchEdit.accessibleName() and palette.listView.accessibleName()


def test_typing_after_arrow_navigation_stays_in_search(qtbot):
    palette=show_palette(qtbot,commands())
    qtbot.keyClick(palette.searchEdit,Qt.Key.Key_Down)
    qtbot.keyClicks(palette.searchEdit,"modalita")
    assert palette.searchEdit.text()=="modalita"
    assert visible_ids(palette.model)==["guided"]


@pytest.mark.parametrize("theme",["light","dark"])
def test_palette_renders_theme_and_zoom_without_changing_global_style(qtbot,qapp,theme):
    apply_theme(qapp,theme,zoom=2)
    before=(qapp.styleSheet(),qapp.palette(),qapp.font())
    items=commands()+[Command("long","Titolo molto lungo "*18,"Ricette recenti",lambda:None,description="Descrizione estesa "*30)]
    palette=show_palette(qtbot,items)
    palette.resize(480,380)
    qtbot.wait(30)
    assert not palette.grab().isNull()
    assert palette.countLabel.geometry().bottom() < palette.height()
    assert palette.searchEdit.geometry().width()>0
    assert (qapp.styleSheet(),qapp.palette(),qapp.font())==before
