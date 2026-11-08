from __future__ import annotations
from dataclasses import dataclass, field
from copy import deepcopy

SECTIONS = ["Installazione", "Inizializzazione", "Configurazione", "Codice applicativo", "Esecuzione",
            "Compilazione", "Debug", "Test", "Database", "Distribuzione", "Risoluzione errori"]
STATUSES = {"documentato": "Revisionato", "statico": "Controllo statico", "compilato": "Compilato", "eseguito": "Eseguito"}


@dataclass
class Recipe:
    data: dict

    def __getattr__(self, key):
        defaults = {"title": "Senza titolo", "summary": "", "guide": "", "assets": [], "tags": [],
                    "parameters": [], "related": [], "errors": [], "sources": [], "os": [], "ide": [],
                    "variants": [], "verification": {"status": "documentato"}, "expected": "",
                    "prerequisites": "", "versions": "", "reviewed": "", "project": False,
                    "section": "Codice applicativo", "difficulty": "Intermedio", "group": "Personali", "personal": False}
        if key in self.data:
            return self.data[key]
        if key in defaults:
            return defaults[key]
        raise AttributeError(key)

    def to_dict(self):
        return deepcopy(self.data)


@dataclass
class SearchQuery:
    text: str = ""
    stack: str = ""
    section: str = ""
    os: str = ""
    shell: str = ""
    ide: str = ""
    difficulty: str = ""
    status: str = ""
    group: str = ""
    only_projects: bool = False
    ids: list[str] | None = None
    limit: int = 50
    offset: int = 0
    scope: str = ""
    sort: str = "relevance"
    recent_ids: list[str] | None = None


@dataclass
class SearchResult:
    ids: list[str] = field(default_factory=list)
    total: int = 0
    suggestions: list[str] = field(default_factory=list)
    elapsed_ms: float = 0

