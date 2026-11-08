"""Authoring helpers; the generated catalog remains editable JSON/Markdown/source."""
from __future__ import annotations

import hashlib
import ast
import json
import re
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog"
DATE = "2026-10-29"
SECTION_ALIASES = {
    "Progetti completi": "Inizializzazione", "CI/CD": "Distribuzione", "Compilazione e build": "Compilazione",
    "Container e ambienti": "Configurazione", "Query e operazioni SQL": "Database",
    "Distribuzione e packaging": "Distribuzione", "Ricerca e dati": "Codice applicativo",
    "Layout e grafica": "Codice applicativo", "File e persistenza": "Codice applicativo",
    "Debug e diagnostica": "Debug", "Concorrenza": "Codice applicativo",
    "Build, test e distribuzione": "Compilazione", "Compilazione, test e debug": "Debug",
}

STACKS = {
    "python": ("Python", "Linguaggi", 120), "cpp": ("C++", "Linguaggi", 80),
    "csharp": ("C# / .NET", "Linguaggi", 70), "javascript": ("JavaScript", "Linguaggi", 55),
    "typescript": ("TypeScript", "Linguaggi", 55), "rust": ("Rust", "Linguaggi", 35),
    "go": ("Go", "Linguaggi", 30), "java": ("Java", "Linguaggi", 30), "c": ("C", "Linguaggi", 25),
    "pyside6": ("PySide6", "Desktop e GUI", 100), "pyqt6": ("PyQt6", "Desktop e GUI", 60),
    "qt-cpp": ("Qt6 C++", "Desktop e GUI", 60), "electron": ("Electron", "Desktop e GUI", 40),
    "avalonia": ("Avalonia", "Desktop e GUI", 35), "maui": (".NET MAUI", "Desktop e GUI", 30),
    "winui": ("WinUI 3", "Desktop e GUI", 25), "nodejs": ("Node.js", "Web e backend", 90),
    "react": ("React", "Web e backend", 100), "nextjs": ("Next.js", "Web e backend", 100),
    "aspnet": ("ASP.NET Core", "Web e backend", 65), "fastapi": ("FastAPI", "Web e backend", 65),
    "html-css": ("HTML / CSS", "Web e backend", 45), "django": ("Django", "Web e backend", 35),
    "sql": ("SQL", "Database", 50), "sqlite": ("SQLite", "Database", 65),
    "postgresql": ("PostgreSQL", "Database", 75), "mysql": ("MySQL / MariaDB", "Database", 60),
    "powershell": ("PowerShell", "Strumenti", 30), "bash": ("Bash", "Strumenti", 20),
    "git": ("Git", "Strumenti", 40), "cmake": ("CMake", "Strumenti", 25),
    "docker": ("Docker", "Strumenti", 35), "cicd": ("CI/CD", "Strumenti", 30),
    "packaging": ("Packaging e rilascio", "Strumenti", 20),
    "kotlin": ("Kotlin", "Linguaggi", 30), "swift": ("Swift", "Linguaggi", 25),
    "php": ("PHP", "Linguaggi", 30), "dart": ("Dart", "Linguaggi", 25),
    "vue": ("Vue", "Web e backend", 35), "svelte": ("Svelte", "Web e backend", 30),
    "angular": ("Angular", "Web e backend", 30), "spring": ("Spring Boot", "Web e backend", 30),
    "flutter": ("Flutter", "Desktop e GUI", 30), "tauri": ("Tauri", "Desktop e GUI", 25),
    "mongodb": ("MongoDB", "Database", 25), "redis": ("Redis", "Database", 25),
}
PROJECT_TARGETS = {stack: 1 for stack in STACKS}
PROJECT_TARGETS.update({"pyside6": 2, "nodejs": 3, "react": 3, "nextjs": 3, "aspnet": 2, "fastapi": 2,
    "postgresql": 2, "powershell": 0, "bash": 0, "cicd": 0, "packaging": 0})
EXPECTED_RECIPES = sum(spec[2] for spec in STACKS.values())
EXPECTED_PROJECTS = sum(PROJECT_TARGETS.values())


def slug(text: str) -> str:
    import unicodedata
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def language(path: str) -> str:
    return {".py": "python", ".cpp": "cpp", ".h": "cpp", ".hpp": "cpp", ".c": "c",
            ".cs": "csharp", ".js": "javascript", ".mjs": "javascript", ".jsx": "jsx",
            ".ts": "typescript", ".tsx": "tsx", ".rs": "rust", ".go": "go", ".java": "java",
            ".sql": "sql", ".ps1": "powershell", ".sh": "bash", ".json": "json", ".html": "html",
            ".css": "css", ".yml": "yaml", ".yaml": "yaml", ".xml": "xml", ".xaml": "xml",
            ".toml": "toml", ".md": "markdown", ".txt": "text", ".kt": "kotlin", ".kts": "kotlin",
            ".swift": "swift", ".php": "php", ".dart": "dart", ".vue": "vue", ".svelte": "svelte"}.get(Path(path).suffix, "text")


def enrich_editorial(recipe):
    """Replace scaffold-only abstracts with facts actually present in the code.

    This inspects text/AST only: it does not execute examples or change their code
    or verification records. The same transformation runs in every authoring build.
    """
    generic = ("Il componente completo è in", "Il file main.mjs è un", "Demo.csproj definisce",
               "app.py contiene applicazione", "Apri index.html insieme", "File interessati:",
               "operation.py contiene", "Il progetto completo usa")
    old = recipe.get("summary", "")
    if not old.startswith(generic):
        return False
    files = {a["path"]: a.get("content", "") for a in recipe.get("assets", []) if a.get("role") == "file"}
    stack = recipe["stack"]
    facts = []
    if stack == "fastapi" and "app.py" in files:
        try:
            tree = ast.parse(files["app.py"])
            routes, calls = [], set()
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for deco in node.decorator_list:
                        if isinstance(deco, ast.Call) and isinstance(deco.func, ast.Attribute) and deco.func.attr in {"get", "post", "put", "patch", "delete"} and deco.args and isinstance(deco.args[0], ast.Constant):
                            routes.append(deco.func.attr.upper() + " " + str(deco.args[0].value))
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        calls.add(node.func.id)
            if routes:
                facts.append("Endpoint dell’esempio: " + ", ".join(dict.fromkeys(routes)) + ".")
            used = sorted(calls & {"Query", "Path", "Body", "Header", "Cookie", "Field", "File", "UploadFile", "Form", "Depends", "HTTPException", "ConfigDict", "APIRouter", "JSONResponse", "StreamingResponse", "FileResponse", "RedirectResponse"})
            if used:
                facts.append("Validazione e risposte usano " + ", ".join(used) + ".")
        except SyntaxError:
            return False
    elif stack == "aspnet" and "Program.cs" in files:
        code = files["Program.cs"]
        routes = [verb.upper() + " " + path for verb, path in re.findall(r'\.Map(Get|Post|Put|Patch|Delete)\(\s*"([^"\n]+)"', code)]
        if routes:
            facts.append("Rotte dell’esempio: " + ", ".join(dict.fromkeys(routes)) + ".")
        apis = sorted(set(re.findall(r'\b(?:Results\.[A-Za-z]+|AddRateLimiter|UseRateLimiter|AddProblemDetails|UseExceptionHandler|AddAuthentication|AddAuthorization|UseAuthentication|UseAuthorization|AddCors|UseCors|AddOutputCache|UseOutputCache|ConfigureKestrel)\b', code)))
        if apis:
            facts.append("Il comportamento è configurato con " + ", ".join(apis) + ".")
    elif stack == "react" and "src/App.jsx" in files:
        code = files["src/App.jsx"]
        hooks = sorted(set(re.findall(r'\b(use[A-Z][A-Za-z]+)\s*\(', code)))
        handlers = sorted(set(re.findall(r'\b(on[A-Z][A-Za-z]+)\s*=', code)))
        if hooks:
            facts.append("Lo stato e il ciclo di vita usano " + ", ".join(hooks) + ".")
        if handlers:
            facts.append("Interazioni gestite: " + ", ".join(handlers) + ".")
        if re.search(r'\bnew\s+FormData\(', code):
            facts.append("FormData legge i controlli nominati del form durante l’invio.")
        names = list(dict.fromkeys(re.findall(r'\bname=["\']([^"\']+)["\']', code)))
        if names:
            facts.append("Campi nominati: " + ", ".join(names[:6]) + ".")
    elif stack == "nodejs":
        code = files.get("main.mjs", "")
        modules = sorted(set(re.findall(r'(?:from\s*|import\s*)["\'](node:[^"\']+)["\']', code)))
        if modules:
            facts.append("Moduli standard utilizzati: " + ", ".join(modules) + ".")
        apis = sorted(set(re.findall(r'\b(?:fs|path|os|crypto|process|stream|server|response|request|readline)\.([A-Za-z][A-Za-z0-9]*)\s*\(', code)))
        if apis:
            facts.append("Operazioni richiamate: " + ", ".join(apis[:6]) + ".")
    elif stack == "nextjs":
        paths = [p for p in files if p.startswith("app/") and p not in {"app/layout.js", "app/globals.css"}]
        code = "\n".join(files[p] for p in paths)
        apis = sorted(set(re.findall(r'\b(?:cookies|headers|revalidateTag|revalidatePath|cacheTag|cacheLife|redirect|notFound|useRouter|useSearchParams|usePathname|generateStaticParams|fetch)\s*\(', code)))
        apis = [a.split("(")[0].strip() for a in apis]
        if apis:
            facts.append("API richiamate: " + ", ".join(apis) + ".")
        if paths:
            facts.append("File della funzionalità: " + ", ".join(paths[:4]) + ".")
    elif stack == "html-css":
        css = files.get("style.css", "")
        properties = re.findall(r'\b(display|grid-template-columns|grid-template-rows|gap|flex-direction|flex-wrap|justify-content|align-items|position|overflow|aspect-ratio|container-type|scroll-snap-type|object-fit)\s*:\s*([^;}]+)', css)
        if properties:
            facts.append("Regole CSS dimostrate: " + "; ".join(k + ": " + v.strip()[:90] for k, v in properties[:4]) + ".")
        roles = sorted(set(re.findall(r'\b(?:role|aria-live|aria-expanded)=["\']([^"\']+)["\']', files.get("index.html", ""))))
        if roles:
            facts.append("Semantica accessibile dichiarata: " + ", ".join(roles) + ".")
    elif stack == "django":
        code = files.get("operation.py", "")
        methods = sorted(set(re.findall(r'\.([A-Za-z][A-Za-z_]+)\s*\(', code)) & {"filter", "exclude", "get", "create", "update", "delete", "annotate", "aggregate", "values", "values_list", "order_by", "select_related", "prefetch_related", "bulk_create", "bulk_update", "get_or_create", "update_or_create", "atomic", "count", "exists"})
        if methods:
            facts.append("Operazioni ORM richiamate: " + ", ".join(methods) + ".")
        fields = list(dict.fromkeys(re.findall(r'\bF\(["\']([^"\']+)["\']\)', code)))
        if fields:
            facts.append("Le espressioni F lavorano sui campi " + ", ".join(fields) + " direttamente nel database.")
    if not facts:
        return False
    summary = recipe["title"].rstrip(".") + ". " + " ".join(facts[:2])
    recipe["summary"] = summary
    guide = recipe.get("guide", "").replace(old, " ".join(facts), 1)
    heading = "## Dettagli del codice"
    if heading not in guide:
        guide += "\n\n" + heading + "\n\n" + "\n".join("- " + fact for fact in facts) + "\n"
    recipe["guide"] = guide
    recipe["editorial"] = {"version": 1, "method": "Fatti ricavati staticamente dai file dell’esempio", "facts": facts}
    return True


class Book:
    def __init__(self, stack: str, version: str, sources: list[str], prerequisites: str,
                 *, os: list[str] | None = None, ide: list[str] | None = None):
        self.stack, self.version, self.sources, self.prerequisites = stack, version, sources, prerequisites
        self.os = os or ["Windows", "Linux", "macOS"]
        self.ide = ide or ["VS Code"]
        self.recipes: list[dict] = []

    def add(self, key: str, title: str, summary: str, files: dict[str, str], *,
            section: str = "Codice applicativo", explanation: str = "", expected: str = "",
            commands: list[dict] | str | None = None, tags: list[str] | None = None,
            errors: list[str] | None = None, difficulty: str = "Intermedio", project: bool = False,
            parameters: list[dict] | None = None, related: list[str] | None = None,
            verification: dict | None = None, variants: list[dict] | None = None,
            os: list[str] | None = None, ide: list[str] | None = None, sources: list[str] | None = None,
            file_roles: dict[str, str] | None = None):
        rid = f"{self.stack}-{slug(key)}"
        assert rid not in {r["id"] for r in self.recipes}, rid
        assets = []
        for index, (path, content) in enumerate(files.items()):
            assets.append({"id": f"file-{index}", "path": path, "language": language(path),
                           "role": (file_roles or {}).get(path, "file"), "content": content.rstrip() + "\n"})
        if isinstance(commands, str):
            commands = [{"shell": "PowerShell", "os": "Windows", "cwd": ".", "code": commands}]
        commands = commands or []
        for index, command in enumerate(commands):
            assets.append({"id": f"command-{index}", "path": command.get("label", "Comandi"),
                           "language": "powershell" if command.get("shell") == "PowerShell" else "bash",
                           "role": "command", "content": command.get("code", "").rstrip() + "\n",
                           "shell": command.get("shell", "Bash"), "os": command.get("os", "Tutti"),
                           "cwd": command.get("cwd", ".")})
        recipe = {"id": rid, "title": title, "summary": summary, "stack": self.stack,
                  "group": STACKS[self.stack][1], "section": SECTION_ALIASES.get(section, section), "difficulty": difficulty,
                  "os": os or self.os, "ide": ide or self.ide, "versions": self.version,
                  "prerequisites": self.prerequisites, "tags": tags or [], "project": project,
                  "assets": assets, "parameters": parameters or [], "related": related or [],
                  "expected": expected or summary, "errors": errors or [], "sources": sources or self.sources,
                  "reviewed": DATE, "verification": verification or {"status": "documentato",
                  "details": "Esempio originale revisionato nel catalogo; esecuzione non attestata.", "date": DATE},
                  "variants": variants or [], "guide": explanation}
        enrich_editorial(recipe)
        self.recipes.append(recipe)
        return recipe

    def save(self):
        directory = CATALOG / self.stack
        directory.mkdir(parents=True, exist_ok=True)
        for recipe in self.recipes:
            directory_recipe = directory / recipe["id"]
            directory_recipe.mkdir(exist_ok=True)
            data = deepcopy(recipe)
            data["guide_path"] = "guide.md"
            (directory_recipe / "guide.md").write_text(recipe["guide"], encoding="utf-8")
            data.pop("guide", None)
            for asset in data["assets"]:
                asset["source"] = "assets/" + asset["id"] + ".txt"
                asset_path = directory_recipe / asset["source"]
                asset_path.parent.mkdir(exist_ok=True)
                asset_path.write_text(asset["content"], encoding="utf-8")
                asset["sha256"] = hashlib.sha256(asset["content"].encode()).hexdigest()
                asset.pop("content", None)
            (directory_recipe / "recipe.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{self.stack}: {len(self.recipes)}/{STACKS[self.stack][2]}")

