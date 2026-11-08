from dataclasses import replace
import pytest
from devatlas.models import Recipe, SearchQuery
from devatlas.search import SearchIndex
from test_core import sample


@pytest.fixture
def engine(tmp_path):
    records = []
    for rid, title, level in (("python-a", "Àlfa JSON", "Avanzato"), ("python-b", "Beta JSON", "Base"),
                              ("python-c", "Gamma JSON", "Intermedio"), ("python-d", "Delta JSON", "Base")):
        record = sample(rid, title=title)
        record["difficulty"] = level
        records.append(Recipe(record))
    index = SearchIndex(tmp_path / "index.sqlite")
    index.rebuild({r.id: r for r in records}, "sort-test")
    return index


@pytest.mark.parametrize("text", ["", "json"])
def test_order_is_applied_before_pagination_for_all_matching_records(engine, text):
    query = SearchQuery(text, sort="title", limit=2)
    first = engine.search(query)
    second = engine.search(replace(query, offset=2))
    assert first.ids + second.ids == ["python-a", "python-b", "python-d", "python-c"]
    assert first.total == second.total == 4
    assert engine.search(SearchQuery(text, sort="difficulty")).ids == ["python-b", "python-d", "python-c", "python-a"]


def test_recent_order_is_profile_input_and_cache_key_includes_changes(engine):
    query = SearchQuery("json", sort="recent", recent_ids=["missing", "python-c", "python-a"])
    assert engine.search(query).ids[:2] == ["python-c", "python-a"]
    assert engine.search(replace(query, recent_ids=["python-b"])).ids[0] == "python-b"
    assert engine.search(replace(query, sort="title")).ids[0] == "python-a"
    assert engine.search(replace(query, recent_ids=["python-a", "python-a", "python-a", "python-b"])).ids[:2] == ["python-a", "python-b"]


def test_invalid_sort_is_not_interpolated_into_sql(engine):
    with pytest.raises(ValueError, match="Ordinamento"):
        engine.search(SearchQuery("json", sort="title;drop table recipes"))

