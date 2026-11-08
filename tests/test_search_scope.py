import pytest
from devatlas.models import Recipe, SearchQuery
from devatlas.search import SearchIndex
from test_core import sample


@pytest.fixture
def index(tmp_path):
    title = sample("python-title", title="Segnale speciale")
    title.update(summary="Solo nel titolo", guide="Guida", prerequisites="Python", tags=[])
    title["assets"][0]["content"] = "print('normale')\n"
    code = sample("python-code", title="Altro esempio")
    code.update(summary="Solo nel sorgente", guide="Guida", prerequisites="Python", tags=[])
    code["assets"][0]["content"] = "print('segnale speciale')\n"
    engine = SearchIndex(tmp_path / "index.sqlite")
    engine.rebuild({r["id"]: Recipe(r) for r in (title, code)}, "scope-test")
    return engine


def test_scope_distinguishes_code_and_title_even_after_cached_queries(index):
    assert set(index.search(SearchQuery("segnale")).ids) == {"python-title", "python-code"}
    assert index.search(SearchQuery("segnale", scope="code")).ids == ["python-code"]
    assert index.search(SearchQuery("segnale", scope="title")).ids == ["python-title"]
    assert index.search(SearchQuery("segnale", scope="code")).ids == ["python-code"]


def test_scope_is_validated_instead_of_interpolating_arbitrary_fts_columns(index):
    with pytest.raises(ValueError, match="Ambito"):
        index.search(SearchQuery("segnale", scope="code) OR *"))


def test_new_scope_preserves_previous_positional_query_arguments():
    query = SearchQuery("json", "python", "", "", "", "", "", "", "", True, None, 20, 10)
    assert query.only_projects is True and query.limit == 20 and query.offset == 10 and query.scope == ""


@pytest.mark.parametrize("text,expected", [("Vue.js form", {"vue"}), ("Spring Boot Java", {"spring"}),
    ("Flutter Dart", {"flutter"}), ("SwiftUI", {"swift"}), ("mongosh query", {"mongodb"}), ("Redis TTL", {"redis"})])
def test_added_technology_aliases_do_not_collide_with_parent_languages(text, expected):
    assert SearchIndex._technologies(text) == expected

