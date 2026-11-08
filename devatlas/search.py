from __future__ import annotations
import json
import re
import sqlite3
import time
import unicodedata
import math
import threading
import os
import weakref
from contextlib import contextmanager, closing
from collections import Counter, OrderedDict, defaultdict
from difflib import get_close_matches
from functools import lru_cache
from snowballstemmer.italian_stemmer import ItalianStemmer
from snowballstemmer.english_stemmer import EnglishStemmer
from pathlib import Path
from types import MappingProxyType
from devatlas.models import Recipe, SearchQuery, SearchResult

ALIASES = {
    "python": ["python", "python3"], "javascript": ["javascript", "js"], "typescript": ["typescript", "ts"],
    "react": ["react", "reactjs"], "rust": ["rust", "cargo"], "go": ["golang", "go"], "java": ["java"],
    "sqlite": ["sqlite", "sqlite3"], "fastapi": ["fastapi"], "django": ["django"], "electron": ["electron"],
    "avalonia": ["avalonia"], "maui": ["maui"], "winui": ["winui", "winui3"],
    "powershell": ["powershell", "pwsh"], "bash": ["bash"], "git": ["git"], "cmake": ["cmake"], "docker": ["docker", "docker compose"],
    "cpp": ["c++", "cpp", "cplusplus"], "csharp": ["c#", "csharp", ".net", "dotnet"],
    "pyside6": ["pyside6", "pyside"], "pyqt6": ["pyqt6", "pyqt"],
    "qt-cpp": ["qt6 c++", "qt c++", "qt6 cpp"], "nodejs": ["node.js", "nodejs", "node"],
    "nextjs": ["next.js", "nextjs", "next"], "postgresql": ["postgresql", "postgres", "psql"],
    "mysql": ["mysql", "mariadb"], "c": ["c"], "aspnet": ["asp.net", "aspnet"],
    "html-css": ["html", "css"], "cicd": ["ci/cd", "cicd", "github actions"], "sql": ["sql"],
    "kotlin": ["kotlin"], "swift": ["swift", "swiftui"], "php": ["php"], "dart": ["dart"],
    "vue": ["vue", "vuejs", "vue.js"], "svelte": ["svelte", "sveltekit"], "angular": ["angular"],
    "spring": ["spring", "spring boot", "springboot"], "flutter": ["flutter"], "tauri": ["tauri"],
    "mongodb": ["mongodb", "mongo", "mongosh"], "redis": ["redis"],
}
SYNONYMS = [
    "inizializzare inizializzazione creare avviare bootstrap scaffold init new progetto project setup",
    "installare installazione install pip npm dipendenze dependencies requirements",
    "compilare compilazione compile build cmake eseguibile executable",
    "debug debuggare debugare debugger breakpoint debugpy pdb gdb lldb",
    "errore error eccezione exception traceback risolvere troubleshooting",
    "leggere lettura aprire read open load caricare",
    "scrivere scrittura salvare write save persist",
    "file files cartella directory path percorso filesystem",
    "finestra window mainwindow widget gui interfaccia",
    "richiesta request fetch http chiamata api endpoint",
    "form modulo moduloform formulario",
    "validazione validare validate validation input",
    "autenticazione authentication login accesso auth",
    "test testing pytest unittest mock verificare",
    "distribuire distribuzione deployment deploy pubblicare release packaging pacchetto",
    "database db query sql dati tabella table",
    "asincrono async await asynchronous",
    "ordinare ordine sort sorting orderby",
    "filtrare filtro filter where",
    "cercare ricerca search find fts",
    "ambiente environment env venv virtuale",
    "eliminare rimuovere cancellare delete remove unlink",
    "aggiornare aggiornamento update updating",
    "inserire inserimento insert insertion",
    "conflitto conflitti conflict conflicts",
    "upsert insert_or_update",
    "riga righe line lines streaming stream iterare",
    "deduplicare deduplicazione duplicati ripetizioni ripetuti univoci unique distinct deduplicate",
    "numero numeri intero interi integer number numeric int",
    "contare conteggio contatore contatori counter count counting frequenze",
    "concorrente concorrenti concorrenza concurrency concurrent thread safe race sincronizzare mutex lock",
    "cancellazione annullare annullamento cancel cancellation cancellare",
    "proprieta ownership esclusiva exclusive trasferire transfer move",
    "copie copia copiare copy clone cloning",
    "fallire fallimento fallimenti falliscono fail failure rejected reject",
    "chiudere chiusura rilasciare rilascio dispose close cleanup risorse resources",
    "sconosciuto sconosciuti esterno unknown external",
    "contesto context contesti",
    "esaustivita esaustivo exhaustive esaustiva union discriminated never casi",
    "finanziario importi importo decimal bigdecimal money floating point precisione",
    "contemporanei contemporaneamente simultanei parallelismo parallel concurrent concorrenza concurrency pool workers worker",
    "sovrapposti sovrapposte sovrapposta overlap overlapping",
    "minuto minuti minute minutes",
    "limite limitare limitazione massimo limit limits throttle rate quota",
    "inviare invio submit submission",
    "campo campi field fields",
    "trasformare espandere convertire expand flatten unnest json_table",
    "cumulativa cumulativo progressivo progressiva running cumulative",
    "sum somma sommare totale total",
    "recente recent latest ultimo ultima last newest",
    "acquisti acquisto ordini ordine orders purchase",
    "salute healthy health healthcheck readiness",
    "pausa debounce smetto digitazione timer singleshot",
    "ramo rami branch worktree working checkout",
    "bottone pulsante button click clicked",
    "tabella table grid datagrid qtableview",
    "lista list elenco array collection",
    "json serializzare serializzazione serialize deserialize deserializzare",
    "preferenza preferenze impostazione impostazioni settings preferences ricordare remember conservare persist",
    "includere incluso inclusa inclusi incorporare incorporato embedded embed include included",
    "autonoma autonomo standalone selfcontained",
    "dimensione dimensioni dimension size sizes bytes byte kilobyte megabyte filesize",
    "caricare caricamento upload uploaded uploading",
    "coda code queue lavoro lavori job jobs task tasks worker workers",
    "blocco bloccato bloccate bloccati locked locking lock",
    "saltare saltando skip evitare avoid",
    "atomico atomica atomiche atomicamente atomic atomically race",
    "incrementare incremento increment incrementing incrementa",
    "colonna colonne column columns griglia grid",
    "adattiva adattive adattivo responsive adaptive automatic automatico automatica",
    "ottenere recuperare retrieve get leggere read",
    "oltre eccedere supera superare exceed exceeding limite limitare",
]
STOP = set("come cosa fare una un uno i il lo la le gli l di da del della dei delle e ed con per in su a the how to an of and using nel nella nello sul dal al alla voglio posso dentro tutto tutti tramite anche se dell dello dagli dalla senza".split())
SYN_MAP = {}
for group in SYNONYMS:
    for word in group.split():
        SYN_MAP.setdefault(word, set()).update(group.split())
_IT, _EN = ItalianStemmer(), EnglishStemmer()
_STEM_LOCK = threading.Lock()
_PATH_STATES_GUARD = threading.Lock()
_PATH_STATES = weakref.WeakValueDictionary()


class _SharedIndexState:
    def __init__(self):
        self.lock = threading.RLock()
        # Publishing one tuple keeps lock-free generation reads on a committed
        # snapshot. The registry does not retain closed engine instances.
        self.committed = (0, None)


@lru_cache(maxsize=100000)
def stems(token):
    if len(token) < 4 or not token.isalpha():
        return (token,)
    with _STEM_LOCK:
        return tuple(sorted({token, _IT.stemWord(token), _EN.stemWord(token)}))


_SYN_STEMS = defaultdict(set)
for _word, _alternatives in SYN_MAP.items():
    for _stem in stems(_word):
        _SYN_STEMS[_stem].update(_alternatives)


@lru_cache(maxsize=10000)
def synonyms(token):
    return frozenset(word for stem in stems(token) for word in _SYN_STEMS.get(stem, ()))


def index_text(value):
    split = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", value)
    split = re.sub(r"([a-z\d])([A-Z])", r"\1 \2", split).replace("_", " ")
    text = normalize(value + " " + split)
    return text + " " + " ".join(dict.fromkeys(s for word in text.split() for s in stems(word) if s != word))


def normalize(value: str) -> str:
    value = value.lower()
    for source, target in ((r"(?<!\w)c\+\+(\d+)?(?!\w)", "cpp"), (r"(?<!\w)c#(\d+)?(?!\w)", "csharp"),
                           (r"(?<!\w)asp\.net(\d+(?:\.\d+)*)?(?!\w)", "aspnet"), (r"(?<!\w)\.net(\d+(?:\.\d+)*)?(?!\w)", "dotnet"),
                           (r"(?<!\w)node\.js(\d+(?:\.\d+)*)?(?!\w)", "nodejs"), (r"(?<!\w)next\.js(\d+(?:\.\d+)*)?(?!\w)", "nextjs"),
                           (r"(?<!\w)vue\.js(\d+(?:\.\d+)*)?(?!\w)", "vuejs"),
                           (r"(?<!\w)c(89|90|99|11|17|23)(?!\w)", "c")):
        value = re.sub(source,lambda match:" "+target+" "+(match.group(1) or "").replace("."," ")+" ",value)
    value = "".join(c for c in unicodedata.normalize("NFKD", value) if not unicodedata.combining(c))
    return " ".join(re.findall(r"[\w]+", value, re.UNICODE))


def words(value):
    return [s for s in normalize(value).split() if s not in STOP]


class SearchIndex:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.vocabulary = ()
        self.features = {}
        self.document_frequency = {}
        self.field_frequency = {}
        self.stack_sizes = {}
        self.recipe_stacks = {}
        self.sort_info = {}
        # Engine objects sharing a cache path also share its committed snapshot.
        key=os.path.normcase(str(self.path.resolve()))
        with _PATH_STATES_GUARD:
            self._state = _PATH_STATES.get(key)
            if self._state is None:
                self._state = _SharedIndexState()
                _PATH_STATES[key] = self._state
        self._lock = self._state.lock
        self._cache = OrderedDict()
        self._suggestions = {}
        self._vocabulary_set = set()
        self._vocabulary_by_length = {}
        self._generation = -1

    @property
    def generation(self):
        """Committed snapshot counter; reading it never waits for a rebuild."""
        return self._state.committed[0]

    def _adopt_snapshot(self):
        generation, snapshot = self._state.committed
        if generation == self._generation:
            return
        if snapshot is not None:
            for name, value in snapshot.items():
                setattr(self, name, value)
        self._cache = OrderedDict()
        self._suggestions = {}
        self._generation = generation

    def _freeze_snapshot(self):
        return MappingProxyType({
            "features": MappingProxyType({rid: tuple(frozenset(field) for field in fields) for rid, fields in self.features.items()}),
            "document_frequency": MappingProxyType(dict(self.document_frequency)),
            "field_frequency": MappingProxyType({key: MappingProxyType(dict(value)) for key, value in self.field_frequency.items()}),
            "stack_sizes": MappingProxyType(dict(self.stack_sizes)),
            "recipe_stacks": MappingProxyType(dict(self.recipe_stacks)),
            "sort_info": MappingProxyType(dict(self.sort_info)),
            "vocabulary": tuple(self.vocabulary),
            "_vocabulary_set": frozenset(self._vocabulary_set),
            "_vocabulary_by_length": MappingProxyType({key: tuple(value) for key, value in self._vocabulary_by_length.items()}),
        })

    def prepare_features(self, recipes):
        frequencies = Counter()
        field_frequencies = defaultdict(Counter)
        stack_sizes = Counter()
        self.features = {}
        self.recipe_stacks = {}
        self.sort_info = {}
        for rid, recipe in recipes.items():
            fields = [recipe.title, recipe.summary, " ".join(recipe.tags), recipe.guide + " " + " ".join(recipe.errors),
                      " ".join(a["content"] for a in recipe.assets)]
            feature = tuple(frozenset(index_text(f).split()) for f in fields)
            self.features[rid] = feature
            self.recipe_stacks[rid] = recipe.stack
            self.sort_info[rid] = (normalize(recipe.title), {"Base": 0, "Intermedio": 1, "Avanzato": 2}.get(recipe.difficulty, 3))
            stack_sizes[recipe.stack] += 1
            frequencies.update(frozenset().union(*feature))
            for number, terms in enumerate(feature):
                field_frequencies[(recipe.stack, number)].update(terms)
        self.document_frequency = dict(frequencies)
        self.field_frequency = dict(field_frequencies)
        self.stack_sizes = dict(stack_sizes)

    @contextmanager
    def connect(self):
        with self._lock:
            db = sqlite3.connect(self.path, timeout=20)
            try:
                with db:
                    yield db
            finally:
                db.close()

    def rebuild(self, recipes: dict[str, Recipe], fingerprint: str, *, force: bool = False):
        with self._lock:
            self._adopt_snapshot()
            attributes=("features","document_frequency","field_frequency","stack_sizes","recipe_stacks","sort_info",
                        "vocabulary","_vocabulary_set","_vocabulary_by_length","_cache","_suggestions")
            previous={name:getattr(self,name) for name in attributes}
            self._cache=OrderedDict()
            self._suggestions={}
            try:
                snapshot = self._rebuild(recipes, fingerprint, force=force)
            except Exception:
                for name,value in previous.items():
                    setattr(self,name,value)
                raise
            self._state.committed = (self.generation + 1, snapshot)
            self._adopt_snapshot()

    def _rebuild(self, recipes: dict[str, Recipe], fingerprint: str, *, force: bool = False):
        import hashlib
        self.prepare_features(recipes)
        signature = "engine-v6:" + fingerprint + hashlib.sha256(json.dumps([r.data for r in recipes.values() if r.personal], sort_keys=True).encode()).hexdigest()
        if self.path.exists() and not force:
            try:
                with self.connect() as db:
                    previous = db.execute("SELECT value FROM metadata WHERE key='signature'").fetchone()
                if previous and previous[0] == signature:
                    self._vocab()
                    return self._freeze_snapshot()
            except sqlite3.DatabaseError:
                pass
        temporary = self.path.with_suffix(".building")
        if temporary.exists():
            temporary.unlink()
        with closing(sqlite3.connect(temporary)) as db, db:
            db.executescript("""
                CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT);
                CREATE TABLE recipes(id TEXT PRIMARY KEY,stack TEXT,section TEXT,os TEXT,shell TEXT,ide TEXT,difficulty TEXT,status TEXT,grp TEXT,project INTEGER,title TEXT);
                CREATE VIRTUAL TABLE search USING fts5(id UNINDEXED,title,summary,aliases,tags,body,code,tokenize='unicode61 remove_diacritics 2',prefix='2 3 4');
                CREATE INDEX recipe_stack ON recipes(stack);
                CREATE VIRTUAL TABLE vocabulary USING fts5vocab(search,'row');
            """)
            for recipe in recipes.values():
                shell = "|" + "|".join(sorted({a.get("shell", "") for a in recipe.assets if a.get("shell")})) + "|"
                db.execute("INSERT INTO recipes VALUES (?,?,?,?,?,?,?,?,?,?,?)", (
                    recipe.id, recipe.stack, recipe.section, "|" + "|".join(recipe.os) + "|", shell,
                    "|" + "|".join(recipe.ide) + "|", recipe.difficulty, recipe.verification.get("status", "documentato"),
                    recipe.group, int(recipe.project), recipe.title))
                aliases = " ".join([recipe.stack] + ALIASES.get(recipe.stack, []) + [recipe.section])
                db.execute("INSERT INTO search VALUES (?,?,?,?,?,?,?)", (recipe.id, index_text(recipe.title),
                    index_text(recipe.summary), index_text(aliases), index_text(" ".join(recipe.tags)),
                    index_text(recipe.guide + " " + recipe.prerequisites + " " + " ".join(recipe.errors)),
                    index_text(" ".join(a.get("content", "") for a in recipe.assets))))
            db.execute("INSERT INTO metadata VALUES ('signature',?)", (signature,))
            db.execute("INSERT INTO search(search) VALUES ('optimize')")
        # Load all fallible derived data before publishing the new database.
        # Readers keep the previous committed snapshot if this step fails.
        try:
            self._vocab(temporary)
            snapshot = self._freeze_snapshot()
            temporary.replace(self.path)
        except Exception:
            temporary.unlink(missing_ok=True)
            raise
        return snapshot

    def _vocab(self, path=None):
        if path is None:
            with self.connect() as db:
                self.vocabulary = tuple(r[0] for r in db.execute("SELECT term FROM vocabulary WHERE length(term)>2 AND doc>=1"))
        else:
            with closing(sqlite3.connect(path)) as db:
                self.vocabulary = tuple(r[0] for r in db.execute("SELECT term FROM vocabulary WHERE length(term)>2 AND doc>=1"))
        self._vocabulary_set = set(self.vocabulary)
        lengths = defaultdict(list)
        for term in self.vocabulary:
            lengths[len(term)].append(term)
        self._vocabulary_by_length = dict(lengths)

    def _correct(self, token, alias_words):
        if token in self._suggestions:
            return self._suggestions[token]
        candidates = get_close_matches(token, alias_words, n=1, cutoff=.78)
        if not candidates:
            nearby = [word for size in range(max(3, len(token)-2), len(token)+3)
                      for word in self._vocabulary_by_length.get(size, ())
                      if word[0] == token[0]]
            candidates = get_close_matches(token, nearby, n=1, cutoff=.86)
        value = candidates[0] if candidates else token
        if len(self._suggestions) < 2048:
            self._suggestions[token] = value
        return value

    @staticmethod
    def _technologies(text):
        source = normalize(text).split()
        occurrences = []
        for stack, aliases in ALIASES.items():
            for alias in aliases:
                parts = normalize(alias).split()
                for start in range(len(source)-len(parts)+1):
                    if source[start:start+len(parts)] == parts:
                        occurrences.append((len(parts),start,start+len(parts),stack))
        # Composite names own their span: Qt C++ does not also mean core C++.
        selected = []
        for length,start,end,stack in sorted(occurrences,reverse=True):
            if not any(start>=a and end<=b and length<b-a for a,b,_ in selected):
                selected.append((start,end,stack))
        detected = {stack for _,_,stack in selected}
        if "qt-cpp" in detected:
            detected.discard("cpp")
        if "sql" in detected and detected & {"sqlite","postgresql","mysql"}:
            detected.discard("sql")
        for framework,parent in (("pyside6","python"),("pyqt6","python"),("fastapi","python"),("django","python"),
                                 ("aspnet","csharp"),("avalonia","csharp"),("maui","csharp"),("winui","csharp"),
                                 ("react","javascript"),("nextjs","javascript"),("nodejs","javascript"),
                                 ("vue","javascript"),("svelte","javascript"),("angular","typescript"),
                                 ("flutter","dart"),("spring","java")):
            if framework in detected:
                detected.discard(parent)
        if not detected and any(word in {"qt","qt6"} for word in source):
            detected.update(("qt-cpp","pyside6","pyqt6"))
        if "cpp" in detected and any(word in {"qt","qt6"} for word in source):
            detected = (detected - {"cpp"}) | {"qt-cpp"}
        return detected

    def search(self, query: SearchQuery) -> SearchResult:
        # A query sees one coherent generation, including features and SQL data.
        # Connections remain local to the calling thread and close before replace.
        with self._lock:
            self._adopt_snapshot()
            return self._search(query)

    def _search(self, query: SearchQuery) -> SearchResult:
        start = time.perf_counter()
        if query.sort not in ("", "relevance", "title", "difficulty", "recent"):
            raise ValueError("Ordinamento di ricerca non valido.")
        if query.ids == []:
            return SearchResult()
        if query.scope not in ("", "all", "code", "title"):
            raise ValueError("Ambito di ricerca non valido.")
        tokens = list(dict.fromkeys(words(query.text)))[:24]
        cache_key = (query.text,query.stack,query.section,query.difficulty,query.status,query.group,
                     query.os,query.shell,query.ide,query.only_projects,None if query.ids is None else tuple(query.ids),query.scope,
                     query.sort,tuple(query.recent_ids or ()) if query.sort == "recent" else None)
        if tokens and cache_key in self._cache:
            ranked,total,suggestions = self._cache[cache_key]
            self._cache.move_to_end(cache_key)
            offset=max(0,query.offset)
            return SearchResult(list(ranked[offset:offset+max(1,min(query.limit,200))]),total,list(suggestions),(time.perf_counter()-start)*1000)
        # Preserve exact API spellings. Ordinary unknown words can be corrected,
        # with an explicit suggestion returned alongside the retrieval results.
        api_tokens=set()
        for raw in re.findall(r"[A-Za-z_]\w*(?:(?:::|->|[.:-])[A-Za-z_]\w*)*",query.text):
            if ("_" in raw or "." in raw or ":" in raw or
                sum(letter.isupper() for letter in raw)>=2 or re.search(r"[a-z][A-Z]",raw)):
                api_tokens.update(normalize(raw).split())
        alias_words=sorted({word for aliases in ALIASES.values() for alias in aliases for word in normalize(alias).split()})
        corrected=[]
        suggested=[]
        for token in tokens:
            if len(token)>=4 and token not in SYN_MAP and not any(s in self._vocabulary_set for s in stems(token)):
                candidate=self._correct(token,alias_words)
                suggested.append(candidate)
                corrected.append(candidate if token not in api_tokens or candidate in alias_words else token)
            else:
                corrected.append(token)
                suggested.append(token)
        suggestions=[" ".join(suggested)] if suggested!=tokens else []
        tokens=corrected
        clauses, values = [], []
        for field in ("stack", "section", "difficulty", "status"):
            value = getattr(query, field)
            if value:
                clauses.append("r." + field + "=?")
                values.append(value)
        if query.group:
            clauses.append("r.grp=?")
            values.append(query.group)
        for field in ("os", "shell", "ide"):
            value = getattr(query, field)
            if value:
                clauses.append("r." + field + " LIKE ? ESCAPE '\\'")
                values.append("%|" + value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "|%")
        if query.only_projects:
            clauses.append("r.project=1")
        if query.ids is not None:
            clauses.append("r.id IN (" + ",".join("?" for _ in query.ids) + ")")
            values.extend(query.ids)
        # Explicit symbolic language names are filters, so C++ can never collapse to C or C#.
        detected = {query.stack} if query.stack else self._technologies(" ".join(tokens))
        if not query.stack:
            if detected:
                packaging_intent={"build","compile","compilare","compilazione","publish","pubblicare","distribuire",
                                  "distribuzione","deploy","deployment","release","rilascio","packaging","package",
                                  "pacchetto","installer","eseguibile","executable","wheel","sdist","tarball","zip"}
                allowed = sorted(detected | ({"packaging"} if set(tokens)&packaging_intent else set()))
                if detected=={"csharp"} and not re.search(r"c#|csharp",query.text,re.IGNORECASE):
                    allowed += ["aspnet", "avalonia", "maui", "winui"]
                clauses.append("r.stack IN (" + ",".join("?" for _ in allowed) + ")")
                values.extend(allowed)
        where = " AND ".join(clauses) or "1=1"

        def match_for(ts, operator="AND"):
            groups = []
            for token in ts:
                expanded = sorted({s for t in [token, *synonyms(token)] for s in stems(t) if len(s)>1 or len(token)==1})
                # These tokens are constructed, never interpreted as user-supplied FTS syntax.
                groups.append("(" + " OR ".join('"' + term.replace('"', '""') + '"*' for term in expanded) + ")")
            expression = (" " + operator + " ").join(groups)
            return f"{query.scope}:({expression})" if query.scope in ("code", "title") else expression

        with self.connect() as db:
            if tokens:
                statement = "SELECT r.id FROM search s JOIN recipes r ON r.id=s.id WHERE search MATCH ? AND " + where
                # Retrieval is intentionally soft for natural language. Ranking
                # rewards independent concept coverage, exact names and API tokens.
                technology_terms = {t for stack in detected for a in ALIASES.get(stack,()) for t in normalize(a).split()}
                meaningful = [t for t in tokens if t not in technology_terms] or tokens
                params = [match_for(meaningful, "OR")] + values
                total = db.execute("SELECT count(*) FROM (" + statement + ")", params).fetchone()[0]
                if not total:
                    # Natural-language questions contain optional details. Retry
                    # with meaningful matching terms, preserving explicit filters.
                    # Misspelled identifiers are never silently substituted.
                    meaningful = list(tokens)
                    technology_terms = {t for stack in detected for a in ALIASES.get(stack,()) for t in normalize(a).split()}
                    meaningful = [t for t in meaningful if t not in technology_terms] or meaningful
                    if meaningful:
                        params = [match_for(meaningful, "OR")] + values
                        total = db.execute("SELECT count(*) FROM (" + statement + ")", params).fetchone()[0]
                statement += " ORDER BY bm25(search,0,12,6,9,7,1,0.5),r.title COLLATE NOCASE,r.id"
                candidates = [r[0] for r in db.execute(statement, params)]
                # Compute expansion and corpus weights once per query, not once
                # per candidate. Synonyms cannot borrow IDF from their rarest term.
                plans=[]
                population=max(1,len(self.features))
                for token in meaningful:
                    exact=frozenset(stems(token))
                    expanded=frozenset(s for term in synonyms(token) for s in stems(term))-exact
                    known=[self.document_frequency.get(term,0) for term in exact]
                    frequency=max(known,default=0)
                    if not frequency:
                        frequency=max((self.document_frequency.get(term,0) for term in expanded),default=population)
                    idf=min(5.0,1+math.log((population+1)/(frequency+1)))
                    plans.append((token,exact,expanded,idf))
                def score(rid):
                    feature = self.features.get(rid, [])
                    result = 0.0
                    hits = 0
                    stack=self.recipe_stacks.get(rid,"")
                    size=self.stack_sizes.get(stack,1)
                    for token,exact,expanded,idf in plans:
                        best = 0
                        for field_number, (values_set, weight) in enumerate(zip(feature, (8.0,5.0,4.0,1.2,4.0))):
                            if query.scope == "code" and field_number != 4 or query.scope == "title" and field_number != 0:
                                continue
                            matches=exact & values_set
                            quality=1.0
                            if not matches:
                                matches=expanded & values_set
                                quality=.65
                            if matches:
                                frequency=max(self.field_frequency[(stack,field_number)].get(term,0) for term in matches)
                                # Repeated fixture/import text is weak evidence.
                                # Do not award positive rarity per stack: it makes
                                # an incidental term in a small stack outrank a
                                # directly relevant description in another stack.
                                specificity=(.12 if frequency/size>=.65 else 1.0) if field_number>=3 else 1.0
                                # A deliberately named API is stronger intent
                                # than incidental prose around it (e.g. an
                                # options window versus a QSettings recipe).
                                api_boost=6.0 if token in api_tokens and quality==1 else 1
                                best=max(best,weight*quality*specificity*api_boost)
                        if best:
                            hits += 1
                        result += best * idf
                    return result + hits * hits * 2.0
                if query.sort in ("", "relevance"):
                    ranked = sorted(enumerate(candidates), key=lambda pair: (-score(pair[1]), pair[0]))
                    ranked_ids=tuple(rid for _,rid in ranked)
                else:
                    ranked_ids=tuple(self._sort_ids(candidates, query))
                self._cache[cache_key]=(ranked_ids,total,tuple(suggestions))
                if len(self._cache)>192:
                    self._cache.popitem(last=False)
                ids = list(ranked_ids[max(0, query.offset):max(0, query.offset) + max(1, min(query.limit, 200))])
            else:
                total = db.execute("SELECT count(*) FROM recipes r WHERE " + where, values).fetchone()[0]
                order = "r.project DESC,r.title COLLATE NOCASE,r.id"
                ordering_values = []
                if query.ids:
                    order = "CASE r.id " + " ".join("WHEN ? THEN " + str(n) for n, rid in enumerate(query.ids)) + " END,r.title"
                    ordering_values = list(query.ids)
                if query.sort in ("", "relevance"):
                    ids = [r[0] for r in db.execute("SELECT r.id FROM recipes r WHERE " + where +
                           " ORDER BY " + order + " LIMIT ? OFFSET ?",
                           values + ordering_values + [max(1, min(query.limit, 200)), max(0, query.offset)])]
                else:
                    candidates = [r[0] for r in db.execute("SELECT r.id FROM recipes r WHERE " + where, values)]
                    ids = self._sort_ids(candidates, query)[max(0,query.offset):max(0,query.offset)+max(1,min(query.limit,200))]
        return SearchResult(ids, total, suggestions, (time.perf_counter() - start) * 1000)

    def _sort_ids(self, ids, query):
        recent = {rid: number for number, rid in reversed(list(enumerate(query.recent_ids or ())))}
        unvisited = max(recent.values(), default=-1) + 1
        def key(rid):
            title, difficulty = self.sort_info.get(rid, (rid, 3))
            if query.sort == "difficulty":
                return difficulty, title, rid
            if query.sort == "recent":
                return recent.get(rid, unvisited), title, rid
            return title, rid
        return sorted(ids, key=key)

