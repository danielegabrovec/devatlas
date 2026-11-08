"""CMake and Docker recipes. No builds or containers are started by this builder."""
import json
from catalog_support import Book, slug
from desktop_tools_common import save_book

CMAKE_HEAD='''cmake_minimum_required(VERSION 3.24)
project(RecipeBuild VERSION 1.2.0 LANGUAGES CXX)
add_executable(recipe main.cpp)
'''
MAIN='#include <iostream>\nint main(){std::cout << "Build pronto\\n";return 0;}\n'
CMAKE = [
("Inizializzare un eseguibile CMake","Separare configurazione e build usando una directory esterna ai sorgenti.","",{}),
("Richiedere uno standard C++ sul target","Esprimere la feature cxx_std_20 senza modificare tutti i target globalmente.","target_compile_features(recipe PRIVATE cxx_std_20)",{}),
("Attivare warning portabili per compilatore","Scegliere opzioni MSVC e GCC/Clang con una condizione CMake.",'if(MSVC)\n target_compile_options(recipe PRIVATE /W4)\nelse()\n target_compile_options(recipe PRIVATE -Wall -Wextra -Wpedantic)\nendif()',{}),
("Trattare warning come errori per un target","Usare COMPILE_WARNING_AS_ERROR senza concatenare flag manuali.",'set_property(TARGET recipe PROPERTY COMPILE_WARNING_AS_ERROR ON)',{}),
("Passare una macro di compilazione al sorgente","Usare target_compile_definitions per un valore limitato al target.",'target_compile_definitions(recipe PRIVATE RECIPE_MODE=1)',{"main.cpp":'#include <iostream>\nint main(){std::cout<<RECIPE_MODE<<"\\n";}\n'}),
("Aggiungere include privati a un target","Dichiarare la directory degli header senza include_directories globale.",'target_include_directories(recipe PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/include")',{"include/config.hpp":"#pragma once\nconstexpr int answer=42;\n","main.cpp":'#include "config.hpp"\n#include <iostream>\nint main(){std::cout<<answer<<"\\n";}\n'}),
("Offrire un'opzione configurabile di compilazione","Esporre una scelta ON/OFF nella cache CMake.",'option(RECIPE_VERBOSE "Enable verbose output" OFF)\nif(RECIPE_VERBOSE)\n target_compile_definitions(recipe PRIVATE RECIPE_VERBOSE=1)\nendif()',{}),
("Conservare un parametro stringa nella cache","Usare CACHE STRING per una configurazione mostrata durante configure.",'set(RECIPE_CHANNEL "local" CACHE STRING "Release channel")\nset_property(CACHE RECIPE_CHANNEL PROPERTY STRINGS local beta stable)\nmessage(STATUS "Recipe channel: ${RECIPE_CHANNEL}")',{}),
("Generare un header con configure_file","Inserire la versione del progetto senza editare manualmente il sorgente.",'configure_file(version.hpp.in "${CMAKE_CURRENT_BINARY_DIR}/version.hpp" @ONLY)\ntarget_include_directories(recipe PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")',{"version.hpp.in":'#pragma once\n#define RECIPE_VERSION "@PROJECT_VERSION@"\n',"main.cpp":'#include "version.hpp"\n#include <iostream>\nint main(){std::cout<<RECIPE_VERSION<<"\\n";}\n'}),
("Separare una libreria statica dall'eseguibile","Collegare una libreria tramite nome target e propagare i suoi include.",'add_library(mathlib STATIC math.cpp)\ntarget_include_directories(mathlib PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/include")\ntarget_link_libraries(recipe PRIVATE mathlib)',{"math.cpp":'#include "math.hpp"\nint square(int n){return n*n;}\n',"include/math.hpp":"#pragma once\nint square(int n);\n","main.cpp":'#include "math.hpp"\n#include <iostream>\nint main(){std::cout<<square(7)<<"\\n";}\n'}),
("Modellare una libreria header-only con INTERFACE","Propagare include e feature senza compilare un archivio vuoto.",'add_library(recipe_headers INTERFACE)\ntarget_include_directories(recipe_headers INTERFACE "${CMAKE_CURRENT_SOURCE_DIR}/include")\ntarget_compile_features(recipe_headers INTERFACE cxx_std_17)\ntarget_link_libraries(recipe PRIVATE recipe_headers)',{"include/value.hpp":"#pragma once\ninline constexpr int value=42;\n"}),
("Riutilizzare file oggetto con OBJECT library","Compilare una unità condivisa senza produrre una libreria separata.",'add_library(recipe_objects OBJECT helper.cpp)\ntarget_link_libraries(recipe PRIVATE recipe_objects)',{"helper.cpp":"int helper_value(){return 42;}\n"}),
("Registrare un test eseguibile con CTest","Far fallire il test quando l'eseguibile restituisce uno stato non zero.",'include(CTest)\nif(BUILD_TESTING)\n add_test(NAME recipe_runs COMMAND recipe)\nendif()',{}),
("Impostare timeout e risultato atteso di un test","Combinare TIMEOUT e PASS_REGULAR_EXPRESSION in CTest.",'include(CTest)\nadd_test(NAME recipe_output COMMAND recipe)\nset_tests_properties(recipe_output PROPERTIES TIMEOUT 5 PASS_REGULAR_EXPRESSION "Build pronto")',{}),
("Installare un eseguibile in una directory staging","Dichiarare install TARGETS evitando copie manuali del binario.",'install(TARGETS recipe RUNTIME DESTINATION bin)',{}),
("Usare le directory di installazione convenzionali","Applicare GNUInstallDirs per rispettare layout e override del sistema.",'include(GNUInstallDirs)\ninstall(TARGETS recipe RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}")',{}),
("Creare un pacchetto ZIP con CPack","Usare i file installabili come contenuto del pacchetto.",'install(TARGETS recipe RUNTIME DESTINATION bin)\nset(CPACK_GENERATOR ZIP)\nset(CPACK_PACKAGE_VERSION "${PROJECT_VERSION}")\ninclude(CPack)',{}),
("Condividere preset di configurazione e build","Dichiarare Ninja Debug in CMakePresets invece di ricordare i flag.","",{"CMakePresets.json":json.dumps({"version":3,"configurePresets":[{"name":"debug","generator":"Ninja","binaryDir":"${sourceDir}/build/debug","cacheVariables":{"CMAKE_BUILD_TYPE":"Debug"}}],"buildPresets":[{"name":"debug","configurePreset":"debug"}]},indent=2)}),
("Aggiungere una macro soltanto alle build Debug","Usare una generator expression dipendente dalla configurazione.",'target_compile_definitions(recipe PRIVATE "$<$<CONFIG:Debug>:RECIPE_DEBUG=1>")',{}),
("Abilitare AddressSanitizer solo su GCC e Clang","Applicare insieme opzioni di compilazione e linking.",'if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")\n target_compile_options(recipe PRIVATE -fsanitize=address -fno-omit-frame-pointer)\n target_link_options(recipe PRIVATE -fsanitize=address)\nelse()\n message(STATUS "ASan demo not enabled for this compiler")\nendif()',{}),
("Controllare supporto a ottimizzazione interprocedurale","Interrogare CheckIPOSupported prima di attivare IPO.",'include(CheckIPOSupported)\ncheck_ipo_supported(RESULT recipe_ipo OUTPUT recipe_ipo_error)\nif(recipe_ipo)\n set_property(TARGET recipe PROPERTY INTERPROCEDURAL_OPTIMIZATION TRUE)\nelse()\n message(STATUS "IPO unavailable: ${recipe_ipo_error}")\nendif()',{}),
("Esportare compile_commands per strumenti di analisi","Attivare il compilation database con generatori Makefile o Ninja.",'set(CMAKE_EXPORT_COMPILE_COMMANDS ON)',{}),
("Dichiarare un header generato come dipendenza","Usare OUTPUT e DEPENDS per rigenerare soltanto quando cambia l'input.",'add_custom_command(OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/generated.hpp" COMMAND "${CMAKE_COMMAND}" -E copy_if_different "${CMAKE_CURRENT_SOURCE_DIR}/template.hpp" "${CMAKE_CURRENT_BINARY_DIR}/generated.hpp" DEPENDS template.hpp VERBATIM)\ntarget_sources(recipe PRIVATE "${CMAKE_CURRENT_BINARY_DIR}/generated.hpp")\ntarget_include_directories(recipe PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")',{"template.hpp":"#pragma once\nconstexpr int generated_value=42;\n"}),
("Copiare risorse dopo il linking","Usare TARGET_FILE_DIR per supportare generatori multiconfigurazione.",'add_custom_command(TARGET recipe POST_BUILD COMMAND "${CMAKE_COMMAND}" -E copy_if_different "${CMAKE_CURRENT_SOURCE_DIR}/message.txt" "$<TARGET_FILE_DIR:recipe>/message.txt" VERBATIM)',{"message.txt":"Risorsa locale della ricetta\n"}),
]

DOCKERFILE='''FROM python:3.13-slim
WORKDIR /app
COPY app.py .
EXPOSE 8000
CMD ["python", "app.py"]
'''
APP='''from http.server import BaseHTTPRequestHandler, HTTPServer
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        data=b"Servizio locale pronto\\n"
        self.send_response(200)
        self.send_header("Content-Type","text/plain; charset=utf-8")
        self.send_header("Content-Length",str(len(data)))
        self.end_headers()
        self.wfile.write(data)
if __name__=="__main__":HTTPServer(("0.0.0.0",8000),Handler).serve_forever()
'''
COMPOSE_BASE='''services:
  web:
    build: .
    ports:
      - "127.0.0.1:8089:8000"
'''
DOCKER_COMPOSE = [
("Avviare un servizio locale con Compose","Pubblicare il servizio soltanto sull'interfaccia localhost.","",{}),
("Attendere il superamento dell'healthcheck","Definire un controllo HTTP e avviare con compose up --wait.",'    healthcheck:\n      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen(\'http://127.0.0.1:8000/\', timeout=2)"]\n      interval: 5s\n      timeout: 3s\n      retries: 5\n',{}),
("Impostare variabili d'ambiente nel servizio","Dichiarare PYTHONUNBUFFERED per rendere immediati i log.",'    environment:\n      PYTHONUNBUFFERED: "1"\n',{}),
("Caricare configurazione da un file env","Separare la configurazione locale dal file Compose.",'    env_file:\n      - local.env\n',{"local.env":"RECIPE_MODE=development\nPYTHONUNBUFFERED=1\n"}),
("Montare sorgenti in sola lettura per sviluppo","Usare un bind mount circoscritto al file applicativo.",'    volumes:\n      - ./app.py:/app/app.py:ro\n',{}),
("Conservare dati su un volume nominato","Distinguere i dati persistenti dal filesystem effimero del container.",'    volumes:\n      - recipe-data:/data\nvolumes:\n  recipe-data:\n',{}),
("Usare un filesystem container in sola lettura","Consentire scrittura temporanea soltanto nel tmpfs dichiarato.",'    read_only: true\n    tmpfs:\n      - /tmp\n',{}),
("Rimuovere capability Linux non necessarie","Applicare cap_drop ALL a un server senza porte privilegiate.",'    cap_drop:\n      - ALL\n',{}),
("Impedire acquisizione di privilegi aggiuntivi","Usare no-new-privileges come opzione del container.",'    security_opt:\n      - no-new-privileges:true\n',{}),
("Limitare la memoria del servizio locale","Impostare mem_limit nella configurazione Compose.",'    mem_limit: 128m\n',{}),
("Limitare il consumo CPU del container","Assegnare una quota CPU anziché presumere tutte le CPU host.",'    cpus: 0.50\n',{}),
("Configurare riavvio su errore","Applicare una politica di restart con massimo numero di tentativi.",'    restart: on-failure:3\n',{}),
("Aggiungere un processo init minimo","Delegare reaping dei processi figli al runtime.",'    init: true\n',{}),
("Controllare la dimensione dei log container","Ruotare log json-file con limiti espliciti.",'    logging:\n      driver: json-file\n      options:\n        max-size: "2m"\n        max-file: "2"\n',{}),
("Concedere un tempo di arresto controllato","Dare al processo un intervallo prima dell'arresto forzato.",'    stop_grace_period: 10s\n',{}),
("Definire un profilo di sviluppo opzionale","Avviare un servizio soltanto abilitando il profilo debug.",'    profiles: [debug]\n',{}),
("Eseguire il container come utente non privilegiato","Impostare UID e GID numerici per un'app che non scrive nei sorgenti.",'    user: "10001:10001"\n',{}),
("Sovrascrivere il comando del servizio","Usare una lista di argomenti evitando interpretazione implicita della shell.",'    command: ["python", "-u", "app.py"]\n',{}),
("Assegnare etichette al servizio","Aggiungere metadati applicativi elaborabili dai tool di inventario.",'    labels:\n      it.ricettario.component: "web"\n      it.ricettario.environment: "local"\n',{}),
("Dichiarare una rete dedicata al progetto","Isolare il servizio in una rete bridge gestita da Compose.",'    networks: [recipe-net]\nnetworks:\n  recipe-net:\n    driver: bridge\n',{}),
]
DOCKER_BUILDS = [
("Escludere file inutili dal build context","Usare dockerignore per tenere ambienti virtuali e repository fuori dall'immagine.",DOCKERFILE,{".dockerignore":".git\n.venv\n__pycache__\n*.pyc\n.env\n"}),
("Inserire metadati OCI nell'immagine","Descrivere titolo, versione e licenza senza contenuti sensibili.",DOCKERFILE.replace("WORKDIR /app",'LABEL org.opencontainers.image.title="Recipe local server"\nLABEL org.opencontainers.image.version="1.0.0"\nLABEL org.opencontainers.image.licenses="MIT"\nWORKDIR /app'),{}),
("Parametrizzare la versione base di Python","Usare ARG prima di FROM per una base selezionabile alla build.",DOCKERFILE.replace("FROM python:3.13-slim","ARG PYTHON_VERSION=3.13\nFROM python:${PYTHON_VERSION}-slim"),{}),
("Copiare sorgenti assegnando proprietà all'utente","Usare COPY --chown e USER su un'immagine Linux.",DOCKERFILE.replace("COPY app.py .","RUN groupadd -g 10001 recipe && useradd -u 10001 -g recipe -M recipe\nCOPY --chown=10001:10001 app.py .\nUSER 10001:10001"),{}),
("Disabilitare bytecode e buffering di Python nel container","Impostare variabili runtime che evitano pycache e log ritardati.",DOCKERFILE.replace("WORKDIR /app","ENV PYTHONDONTWRITEBYTECODE=1\nENV PYTHONUNBUFFERED=1\nWORKDIR /app"),{}),
("Separare ENTRYPOINT e argomenti CMD","Permettere un override degli argomenti mantenendo Python come eseguibile.",DOCKERFILE.replace('CMD ["python", "app.py"]','ENTRYPOINT ["python"]\nCMD ["app.py"]'),{}),
("Usare una build multistadio per preparare risorse","Copiare soltanto gli output dichiarati dallo stadio di preparazione.",'''FROM python:3.13-slim AS prepare
WORKDIR /build
COPY app.py .
RUN python -m py_compile app.py
FROM python:3.13-slim
WORKDIR /app
COPY --from=prepare /build/app.py .
EXPOSE 8000
CMD ["python","app.py"]
''',{}),
("Aggiungere un healthcheck nell'immagine","Fare verificare la risposta HTTP al runtime Docker.",DOCKERFILE.replace('EXPOSE 8000','EXPOSE 8000\nHEALTHCHECK --interval=5s --timeout=3s --retries=5 CMD python -c "import urllib.request; urllib.request.urlopen(\'http://127.0.0.1:8000/\', timeout=2)"'),{}),
]
DOCKER_CLI = [
("Leggere i log del servizio Compose","Mostrare le ultime righe senza collegarsi a un terminale interno.","docker compose logs --tail 50 web"),
("Ispezionare la configurazione Compose risolta","Validare YAML e interpolazioni prima di avviare servizi.","docker compose config --quiet\ndocker compose config"),
("Eseguire un comando diagnostico nel servizio","Interrogare l'interprete del container già avviato.","docker compose exec -T web python --version"),
("Misurare risorse di un container in una sola lettura","Usare stats --no-stream per ottenere un campione finito.","$container=docker compose ps -q web\ndocker stats --no-stream $container"),
("Ricostruire ignorando la cache di build","Usare build --no-cache quando si vuole ricalcolare gli strati.","docker compose build --no-cache web"),
("Fermare il progetto conservando volumi nominati","Usare compose down senza -v per preservare i dati dichiarati.","docker compose down"),
]

def build_all():
    assert len(CMAKE)==24,len(CMAKE)
    cmake=Book("cmake","CMake 3.24+; C++17/20",["https://cmake.org/cmake/help/latest/guide/tutorial/index.html","https://cmake.org/cmake/help/latest/manual/cmake-buildsystem.7.html"],"CMake 3.24+, compilatore C++ installato. Su Windows usare Developer PowerShell MSVC o una toolchain già configurata.",os=["Windows","Linux","macOS"],ide=["VS Code","Visual Studio","CLion"])
    for title,description,config,extra in CMAKE:
        files={"main.cpp":MAIN,"CMakeLists.txt":CMAKE_HEAD+config+"\n",**extra}
        commands="cmake -S . -B build\ncmake --build build --config Debug"
        if "CTest" in description or "test" in title.lower():commands+="\nctest --test-dir build -C Debug --output-on-failure"
        if "install" in title.lower():commands+="\ncmake --install build --config Debug --prefix stage"
        if "CPack" in title:commands+="\ncpack --config build/CPackConfig.cmake -C Debug"
        if "preset" in title:commands="cmake --preset debug\ncmake --build --preset debug"
        if "compile_commands" in title:commands="cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Debug\ncmake --build build"
        cmake.add(slug(title),title,description,files,section="Compilazione e build",commands=commands,explanation=f"## Obiettivo\n{description}\n\n## Avvio\nSalva main.cpp, CMakeLists.txt e gli eventuali file aggiuntivi rispettando le directory. Esegui i comandi dalla cartella sorgente; build è separata dai sorgenti. Il risultato è il target recipe, mentre la proprietà specifica è dichiarata soltanto sul target interessato.\n\n## Controllo\nLeggi il log di configurazione e build. CMake interrompe configure se il compilatore richiesto non è disponibile. I comandi Windows sono esempi PowerShell; configurazioni su Linux e macOS non sono dichiarate eseguite.\n\n## Dettaglio\n{description}",expected=description,tags=["CMake","build",slug(title)],errors=["Ninja non trovato: installarlo se si usa il preset o il compilation database.","Compilatore non trovato: aprire il terminale di sviluppo della toolchain."])
    cmake.add("progetto-libreria-test","Progetto completo: libreria C++ con test e installazione","Separare una libreria riusabile, un eseguibile di test e uno staging di installazione.",{"CMakeLists.txt":'''cmake_minimum_required(VERSION 3.24)
project(RecipeLibrary VERSION 1.0.0 LANGUAGES CXX)
add_library(calc STATIC src/calc.cpp)
target_compile_features(calc PUBLIC cxx_std_17)
target_include_directories(calc PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include> $<INSTALL_INTERFACE:include>)
add_executable(calc_test tests/calc_test.cpp)
target_link_libraries(calc_test PRIVATE calc)
include(CTest)
add_test(NAME square_values COMMAND calc_test)
install(TARGETS calc ARCHIVE DESTINATION lib)
install(DIRECTORY include/ DESTINATION include)
''',"include/calc.hpp":"#pragma once\nint square(int value);\n","src/calc.cpp":'#include "calc.hpp"\nint square(int value){return value*value;}\n',"tests/calc_test.cpp":'#include "calc.hpp"\nint main(){return square(0)==0 && square(7)==49 && square(-3)==9 ? 0 : 1;}\n',"README.md":"# Calc\nConfigura, compila, esegui CTest e installa in stage. I controlli non usano assert, quindi restano attivi anche in Release.\n"},project=True,section="Progetti completi",commands="cmake -S . -B build\ncmake --build build --config Debug\nctest --test-dir build -C Debug --output-on-failure\ncmake --install build --config Debug --prefix stage",explanation="## Progetto\nLa libreria calc espone un header pubblico e implementa square. Il target calc_test verifica zero, positivo e negativo e restituisce un codice di uscita controllabile da CTest. L'installazione copia libreria e header sotto stage, senza modificare directory di sistema.\n\n## Prova\nEsegui i quattro comandi in ordine. CTest deve completare square_values; stage/include contiene calc.hpp. Nessuna build su piattaforme non presenti è attestata.",expected="CTest registra square_values e lo staging contiene libreria e header.",tags=["project","CMake","CTest","library"],errors=["Toolchain C++ non installata o non configurata."])
    assert len(cmake.recipes)==25
    save_book(cmake)
    assert len(DOCKER_COMPOSE)+len(DOCKER_BUILDS)+len(DOCKER_CLI)==34
    book=Book("docker","Docker Engine 27+; Compose 2.29+; Linux containers",["https://docs.docker.com/compose/","https://docs.docker.com/reference/dockerfile/","https://docs.docker.com/compose/how-tos/startup-order/"],"Docker Desktop configurato per container Linux su Windows, oppure Docker Engine Linux. Porta locale 8089 libera. Internet necessario per scaricare l'immagine Python; i file sono esempi, nessun container viene avviato dal catalogo.",os=["Windows","Linux"],ide=["VS Code"])
    def add(title,description,dockerfile,compose,extra,commands):
        book.add(slug(title),title,description,{"Dockerfile":dockerfile,"app.py":APP,"compose.yaml":compose,**extra},commands=commands,section="Container e ambienti",explanation=f"## Obiettivo\n{description}\n\n## Cartella di lavoro\nSalva Dockerfile, app.py, compose.yaml e gli eventuali file aggiuntivi nella stessa cartella. Avvia i comandi da quella cartella. Il servizio ascolta sulla porta 8000 interna; soltanto 127.0.0.1:8089 viene pubblicata sull'host.\n\n## Controllo\nApri http://127.0.0.1:8089 dopo l'avvio e leggi i log in caso di errore. {description}\n\n## Arresto\nUsa docker compose down dalla stessa cartella. I volumi nominati sono conservati; nessun comando di questa ricetta esegue prune globale. Esecuzione container e compatibilità macOS non attestate.",expected=description,tags=["Docker","Compose",slug(title)],errors=["Cannot connect to Docker daemon: avviare Docker Desktop o il servizio Engine.","Porta 8089 occupata: scegliere una porta locale libera nella mappatura."])
    for title,description,suffix,extra in DOCKER_COMPOSE:
        command="docker compose up --build -d"
        if "healthcheck" in title:command="docker compose up --build --wait"
        if "profilo" in title:command="docker compose --profile debug up --build -d"
        add(title,description,DOCKERFILE,COMPOSE_BASE+suffix,extra,command)
    for title,description,dockerfile,extra in DOCKER_BUILDS:
        add(title,description,dockerfile,COMPOSE_BASE,extra,"docker compose build\ndocker compose up -d")
    for title,description,command in DOCKER_CLI:
        prefix="docker compose up --build -d\n" if "configurazione" not in title else ""
        add(title,description,DOCKERFILE,COMPOSE_BASE,{},prefix+command)
    compose='''services:
  web:
    build: .
    ports: ["127.0.0.1:8089:8000"]
    environment:
      REDIS_HOST: redis
    depends_on:
      redis:
        condition: service_healthy
  redis:
    image: redis:7.4-alpine
    command: ["redis-server", "--appendonly", "yes"]
    volumes: ["visits:/data"]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 3s
      timeout: 2s
      retries: 10
volumes:
  visits:
'''
    app='''import os, socket
from http.server import BaseHTTPRequestHandler, HTTPServer
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            with socket.create_connection((os.environ.get("REDIS_HOST","redis"),6379),timeout=2) as client:
                client.sendall(b"*2\\r\\n$4\\r\\nINCR\\r\\n$6\\r\\nvisits\\r\\n")
                with client.makefile("rb") as reader:reply=reader.readline(100)
            if not reply.startswith(b":"):raise ValueError("Redis response not integer")
            body=f"Visite: {int(reply[1:])}\\n".encode()
            status=200
        except (OSError,ValueError):body=b"Archivio temporaneamente non disponibile\\n";status=503
        self.send_response(status);self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body)
if __name__=="__main__":HTTPServer(("0.0.0.0",8000),Handler).serve_forever()
'''
    book.add("progetto-contatore-redis","Progetto completo: servizio HTTP e contatore persistente Redis","Coordinare due servizi locali con healthcheck, rete interna e volume nominato.",{"Dockerfile":DOCKERFILE,"app.py":app,"compose.yaml":compose,"README.md":"# Contatore locale\nAvvia con Compose e apri localhost:8089. Redis non espone porte host. Il volume visits conserva il conteggio dopo compose down.\n"},project=True,section="Progetti completi",commands="docker compose up --build --wait\nInvoke-WebRequest http://127.0.0.1:8089/ | Select-Object -ExpandProperty Content\ndocker compose down",explanation="## Progetto\nUn server HTTP Python usa il protocollo RESP minimo per INCR visits su Redis. La rete Compose risolve redis come hostname; Redis non pubblica porte sull'host. L'healthcheck evita di avviare il web prima della disponibilità iniziale di Redis. Il server gestisce un'indisponibilità successiva con HTTP 503.\n\n## Prova\nVisita due volte localhost:8089: il numero cresce. Esegui down e up dalla medesima cartella: il volume nominato mantiene il contatore. Non utilizzare down -v se vuoi conservare i dati. Questo esempio è locale e documentato, non distribuito online.",expected="Il numero di visite cresce e resta disponibile dopo ricreazione dei container.",tags=["project","Docker","Redis","healthcheck","persistence"],errors=["Redis non healthy: controllare docker compose logs redis.","HTTP 503: Redis non raggiungibile dopo l'avvio."])
    assert len(book.recipes)==35
    save_book(book)

if __name__=="__main__":build_all()
