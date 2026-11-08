"""Behavioral retrieval, isolation and concurrency contracts on independent data."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import threading

import pytest

from devatlas.models import Recipe, SearchQuery
from devatlas.search import SearchIndex


def recipe(rid,stack,title,*,summary="",code="",tags=(),**changes):
    data={"id":rid,"stack":stack,"title":title,"summary":summary,"guide":summary,"tags":list(tags),
          "group":"Linguaggi","section":"Codice applicativo","difficulty":"Base","os":["Windows","Linux"],
          "ide":["VS Code"],"verification":{"status":"statico"},"project":False,
          "assets":[{"id":"code","path":"example.txt","role":"file","language":"text","content":code},
                    {"id":"command","path":"Comandi","role":"command","shell":"PowerShell","os":"Windows","content":"example"}]}
    data.update(changes)
    return Recipe(data)


@pytest.fixture
def index(tmp_path):
    rows=[
        recipe("c-build","c","Compilare una libreria C",tags=["build"]),
        recipe("cpp-build","cpp","Compilare una libreria C++",tags=["build"]),
        recipe("cs-build","csharp","Compilare una libreria C#",tags=["build"]),
        recipe("qt-settings","qt-cpp","Conservare le preferenze",code='QSettings settings("Example", "App");'),
        recipe("pyqt-settings","pyqt6","Conservare una preferenza",code='QSettings("Example", "App").setValue("enabled", True)'),
        recipe("pyside-settings","pyside6","Conservare una preferenza",code='QSettings("Example", "App").setValue("enabled", True)'),
        recipe("pyqt-generic","pyqt6","Aprire una finestra con opzioni",summary="Opzioni, apertura e finestra con elenco selezionabile.",code="QComboBox()"),
        recipe("py-json","python","Leggere configurazione JSON",summary="Aprire e decodificare un documento JSON.",tags=["read","json"],code="json.loads(text)"),
        recipe("py-memory","python","Confrontare allocazioni",summary="Misurare memoria con tracemalloc.",code="tracemalloc.start()"),
        recipe("promise-status","javascript","Raccogliere tutti gli esiti asincroni",code="await Promise.allSettled(tasks)",tags=["promise"]),
        recipe("promise-wait","javascript","Attendere una sequenza di lavori",code="await Promise.all(tasks)",tags=["promise"]),
        recipe("cpp-span","cpp","Leggere array senza copiare",code="std::span<const int> view(items);"),
        recipe("pkg-other","packaging","Leggere dati JSON per un installer",code="json.loads(text)",tags=["json"]),
    ]
    engine=SearchIndex(tmp_path/"search.sqlite")
    engine.rebuild({item.id:item for item in rows},"independent-fixture")
    return engine


@pytest.mark.parametrize(("text","expected"),[
    ("C compilare","c-build"),("C17 compilare","c-build"),("C++ compilare","cpp-build"),("C++20 compilare","cpp-build"),
    ("c# compilare","cs-build"),("C#12 compilare","cs-build"),(".NET compilare","cs-build"),(".NET8.0 compilare","cs-build"),("csharp build","cs-build"),
    ("Qt C++ QSettings","qt-settings"),("Qt6 C++ QSettings","qt-settings"),("Qt 6 C++ QSettings","qt-settings"),
    ("PyQt QSettings","pyqt-settings"),("PySide6 QSettings","pyside-settings"),
    ("JavaScript Promise.allSettled","promise-status"),("cpp std::span<const int>","cpp-span"),
    ("python aprire json","py-json"),
])
def test_symbolic_languages_and_qualified_api_names(index,text,expected):
    assert index.search(SearchQuery(text,limit=1)).ids==[expected]


def test_generic_qt_covers_bindings_but_not_plain_cpp(index):
    result=index.search(SearchQuery("Qt6 QSettings",limit=20))
    assert {"qt-settings","pyqt-settings","pyside-settings"}<=set(result.ids)
    assert "cpp-build" not in result.ids


def test_api_evidence_outranks_unrelated_natural_language(index):
    result=index.search(SearchQuery("PyQt opzioni apertura QSettings",limit=1))
    assert result.ids==["pyqt-settings"]


@pytest.mark.parametrize("text",["pythno JSON","PYTHNO JSON","pythno aprire json"])
def test_language_typo_has_visible_suggestion_and_scoped_results(index,text):
    result=index.search(SearchQuery(text))
    assert result.ids==["py-json"]
    assert result.suggestions and "python" in result.suggestions[0]


def test_api_typo_is_suggested_without_silently_changing_identifier(index):
    result=index.search(SearchQuery("PyQt QSetings"))
    assert not result.ids
    assert result.suggestions and "qsettings" in result.suggestions[0]


def test_partial_api_name_remains_searchable(index):
    assert index.search(SearchQuery("PyQt QSet",limit=1)).ids==["pyqt-settings"]


@pytest.mark.parametrize("text",['" OR * NOT )',"'; DROP TABLE recipes; --",'NEAR(json,read)',"😀",'"',"[std::span<T>]"])
def test_ordinary_user_punctuation_never_becomes_fts_or_sql_syntax(index,text):
    index.search(SearchQuery(text))
    assert index.search(SearchQuery("python JSON")).ids==["py-json"]


def test_explicit_filters_override_inferred_stack_and_combine(index):
    result=index.search(SearchQuery("JSON",stack="python",section="Codice applicativo",difficulty="Base",
                                   os="Windows",shell="PowerShell",ide="VS Code",status="statico",group="Linguaggi"))
    assert result.ids==["py-json"]
    assert not index.search(SearchQuery("JSON",stack="python",os="macOS")).ids
    assert not index.search(SearchQuery("JSON",stack="python",status="eseguito")).ids
    assert not index.search(SearchQuery("JSON",stack="python",shell="Bash")).ids
    assert not index.search(SearchQuery("JSON",stack="python",group="Altre")).ids


def test_filter_wildcards_are_literal_not_sql_patterns(tmp_path):
    row=recipe("literal","python","Config JSON",code="json.loads(text)",ide=["Editor_100%"],os=["Win_dows%"])
    engine=SearchIndex(tmp_path/"literal.sqlite");engine.rebuild({row.id:row},"literal")
    assert engine.search(SearchQuery("JSON",ide="Editor_100%",os="Win_dows%")).ids==[row.id]
    assert not engine.search(SearchQuery("JSON",ide="Editor%" )).ids
    assert not engine.search(SearchQuery("JSON",os="Win%" )).ids


def test_ids_none_empty_membership_and_saved_order_are_distinct(index):
    assert index.search(SearchQuery("JSON",ids=None)).total>=1
    assert index.search(SearchQuery("JSON",ids=[])).total==0
    assert index.search(SearchQuery("JSON",ids=["py-memory"])).total==0
    ordered=["py-memory","py-json","missing","py-memory"]
    assert index.search(SearchQuery(ids=ordered)).ids==["py-memory","py-json"]


def test_natural_language_scope_does_not_leak_unrelated_packaging(index):
    assert index.search(SearchQuery("python leggere JSON")).ids==["py-json"]
    assert "pkg-other" in index.search(SearchQuery("python build JSON")).ids


def test_paging_is_stable_and_total_does_not_depend_on_page(tmp_path):
    rows=[recipe(f"task-{n}","python",f"Elaborare campione {n:03d}",summary="Operazione locale campione") for n in range(37)]
    engine=SearchIndex(tmp_path/"paging.sqlite");engine.rebuild({row.id:row for row in rows},"paging")
    full=engine.search(SearchQuery("python campione",limit=200))
    pages=[engine.search(SearchQuery("python campione",limit=7,offset=start)) for start in range(0,42,7)]
    assert [rid for page in pages for rid in page.ids]==full.ids
    assert all(page.total==37 for page in pages)
    assert not engine.search(SearchQuery("python campione",offset=100)).ids
    assert engine.search(SearchQuery("python campione",offset=-10,limit=0)).ids==full.ids[:1]


def test_cached_results_are_independent_and_all_filters_partition_cache(index):
    first=index.search(SearchQuery("JSON"));first.ids.clear();first.suggestions.append("modified")
    second=index.search(SearchQuery("JSON"))
    assert second.ids and "modified" not in second.suggestions
    assert index.search(SearchQuery("JSON",stack="javascript")).ids==[]
    assert index.search(SearchQuery("JSON",ids=["py-json"])).ids==["py-json"]


def test_project_filter_and_textless_sorting(tmp_path):
    normal=recipe("normal","python","A normale")
    project=recipe("project","python","Z progetto",project=True)
    engine=SearchIndex(tmp_path/"project.sqlite");engine.rebuild({r.id:r for r in (normal,project)},"project")
    assert engine.search(SearchQuery()).ids==["project","normal"]
    assert engine.search(SearchQuery(only_projects=True)).ids==["project"]


def test_rebuild_invalidates_cached_results_and_personal_signature(tmp_path):
    old=recipe("personal","python","Appunti ceramica",personal=True)
    engine=SearchIndex(tmp_path/"personal.sqlite");engine.rebuild({old.id:old},"catalog-unchanged")
    assert engine.search(SearchQuery("ceramica")).ids==[old.id]
    generation=engine.generation
    updated=recipe("personal","python","Appunti fotografia",personal=True)
    engine.rebuild({updated.id:updated},"catalog-unchanged")
    assert engine.generation==generation+1
    assert engine.search(SearchQuery("fotografia")).ids==[old.id]
    assert not engine.search(SearchQuery("ceramica")).ids


def test_failed_rebuild_preserves_last_committed_generation(index):
    before=index.search(SearchQuery("python JSON"))
    generation=index.generation
    malformed=recipe("broken","python","Rotto");malformed.data["summary"]=None
    with pytest.raises(TypeError):index.rebuild({malformed.id:malformed},"invalid")
    assert index.generation==generation
    assert index.search(SearchQuery("python JSON")).ids==before.ids
    assert index.search(SearchQuery("C++ build")).ids==["cpp-build"]


def test_force_rebuild_repairs_derived_index_without_deleting_active_database(tmp_path):
    row=recipe("source","python","Configurazione JSON")
    engine=SearchIndex(tmp_path/"force.sqlite");engine.rebuild({row.id:row},"source-v1")
    with engine.connect() as db:db.execute("DELETE FROM search")
    assert not engine.search(SearchQuery("JSON")).ids
    engine.rebuild({row.id:row},"source-v1",force=True)
    assert engine.search(SearchQuery("JSON")).ids==[row.id]


def test_searches_from_many_threads_share_no_connections_or_mutable_results(index):
    queries=[("python JSON","py-json"),("C++ build","cpp-build"),("PyQt QSettings","pyqt-settings"),
             ("JavaScript Promise.allSettled","promise-status")]*20
    def work(pair):
        text,expected=pair
        result=index.search(SearchQuery(text,limit=1))
        assert result.ids==[expected]
        result.ids.clear()
    with ThreadPoolExecutor(max_workers=8) as pool:list(pool.map(work,queries))
    assert index.search(SearchQuery("python JSON")).ids==["py-json"]


def test_concurrent_rebuild_and_search_observe_whole_snapshots(tmp_path):
    engine=SearchIndex(tmp_path/"concurrent.sqlite")
    batches=[{f"{label}-{n}":recipe(f"{label}-{n}","python",f"JSON {label} {n}") for n in range(7)} for label in ("alpha","beta")]
    engine.rebuild(batches[0],"alpha")
    allowed={frozenset(batch) for batch in batches}
    barrier=threading.Barrier(6)
    def reader():
        barrier.wait()
        for _ in range(20):
            result=engine.search(SearchQuery("python JSON",limit=50))
            assert result.total==7 and frozenset(result.ids) in allowed
    def writer(seed):
        barrier.wait()
        for n in range(6):engine.rebuild(batches[(n+seed)%2],f"{seed}-{n}",force=True)
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures=[pool.submit(reader) for _ in range(4)]+[pool.submit(writer,seed) for seed in range(2)]
        for future in futures:future.result(timeout=15)
    assert engine.generation==13
    assert not list(tmp_path.glob("*.building"))


def test_two_index_instances_can_rebuild_the_same_cache_path(tmp_path):
    path=tmp_path/"shared.sqlite"
    rows={f"record-{n}":recipe(f"record-{n}","python",f"JSON record {n}") for n in range(50)}
    engines=[SearchIndex(path),SearchIndex(path)]
    barrier=threading.Barrier(2)
    def build(engine):
        barrier.wait()
        engine.rebuild(rows,"same-source",force=True)
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(build,engines))
    for engine in engines:assert engine.search(SearchQuery("python JSON",limit=100)).total==50
