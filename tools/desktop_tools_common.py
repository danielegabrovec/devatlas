"""Catalog authoring conventions for the desktop/tools collection only."""
SECTION_MAP={
    "Layout e grafica":"Codice applicativo", "File e persistenza":"Codice applicativo",
    "Ricerca e dati":"Codice applicativo", "Debug e diagnostica":"Debug",
    "Concorrenza":"Codice applicativo", "Progetti completi":"Inizializzazione",
    "Compilazione e build":"Compilazione", "Container e ambienti":"Configurazione",
    "CI/CD":"Test", "Distribuzione e packaging":"Distribuzione",
}

def save_book(book):
    for recipe in book.recipes:
        recipe["section"]=SECTION_MAP.get(recipe["section"],recipe["section"])
        for asset in recipe["assets"]:
            path=asset["path"]
            if path=="CMakeLists.txt":asset["language"]="cmake"
            elif path=="Dockerfile":asset["language"]="dockerfile"
            elif path.endswith((".csproj",".xaml")):asset["language"]="xml"
            elif path.endswith(".iss"):asset["language"]="ini"
    book.save()
