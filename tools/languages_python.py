"""120 Python tasks, authored as a concrete inventory, without combinatorial expansion."""
from catalog_support import Book
from languages_common import program, require_count


def build_all():
    b = Book("python", "Python 3.11–3.13; esempi con libreria standard", ["https://docs.python.org/3.13/library/", "https://docs.python.org/3.13/tutorial/"], "CPython 3.11 o successivo nel PATH. Nessun pacchetto esterno; sqlite3 deve essere incluso nella distribuzione.")
    def add(title, desc, code, expected, tags, section="Codice applicativo"):
        program(b, title, desc, code, expected=expected, tags=tags.split(), section=section)
    # Text: 13 independent transformations and parsers.
    add("Dividere una riga con un massimo di separatori", "Conserva il testo del messaggio anche quando contiene altri due punti.", '''line = "INFO:utente:accesso:riuscito"
level, user, message = line.split(":", 2)
print(level, user, message, sep=" | ")''', "INFO | utente | accesso:riuscito", "string split parser")
    add("Ripulire spazi e righe vuote", "Normalizza un testo acquisito da un modulo conservando soltanto righe significative.", '''raw = "  prima riga  \\n\\n seconda   riga \\n"
lines = [" ".join(line.split()) for line in raw.splitlines() if line.strip()]
print("\\n".join(lines))''', "Due righe: prima riga e seconda riga, senza spazi ripetuti.", "string whitespace normalize")
    add("Confrontare testo senza distinguere maiuscole", "Usa casefold per confrontare testo Unicode invece del solo lower.", '''left, right = "Straße", "STRASSE"
print(left.casefold() == right.casefold())''', "True: il confronto gestisce anche la espansione Unicode di ß.", "unicode casefold compare")
    add("Normalizzare accenti Unicode", "Rende equivalenti le forme composta e scomposta di una lettera accentata.", '''import unicodedata
a, b = "café", "cafe\\u0301"
print(a == b)
print(unicodedata.normalize("NFC", a) == unicodedata.normalize("NFC", b))''', "False, poi True dopo la normalizzazione NFC.", "unicode nfc normalization")
    add("Creare uno slug leggibile", "Trasforma un titolo in una chiave ASCII con separatori stabili.", '''import re
import unicodedata
title = "Caffè e Python: primi passi!"
ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
print(re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-"))''', "caffe-e-python-primi-passi", "slug regex transliteration")
    add("Sostituire variabili in un modello testuale", "Genera un messaggio con Template senza eseguire espressioni nel modello.", '''from string import Template
template = Template("Ciao $nome, hai $numero messaggi.")
print(template.substitute(nome="Ada", numero=3))''', "Ciao Ada, hai 3 messaggi.", "template substitution")
    add("Validare un codice con espressione regolare", "Accetta soltanto due lettere maiuscole seguite da quattro cifre.", '''import re
pattern = re.compile(r"[A-Z]{2}\\d{4}")
for value in ["AB1234", "AB1234x", "ab1234"]:
    print(value, bool(pattern.fullmatch(value)))''', "Solo AB1234 risulta valido; fullmatch impedisce suffissi inattesi.", "regex validation fullmatch")
    add("Estrarre gruppi con nome da un log", "Legge livello e durata da un log senza dipendere da indici numerici.", '''import re
match = re.fullmatch(r"(?P<level>INFO|WARN) durata=(?P<ms>\\d+)ms", "INFO durata=42ms")
if match:
    print(match.group("level"), int(match.group("ms")))''', "INFO 42", "regex named groups log")
    add("Mascherare cifre con una sostituzione regex", "Conserva le ultime quattro cifre e nasconde le precedenti.", '''import re
number = "1234 5678 9012 3456"
digits = re.sub(r"\\D", "", number)
masked = "*" * max(0, len(digits) - 4) + digits[-4:]
print(masked)''', "Dodici asterischi seguiti da 3456.", "regex masking string")
    add("Mandare a capo un paragrafo", "Formatta un testo in righe di larghezza limitata per report su terminale.", '''import textwrap
text = "Un esempio di paragrafo italiano che deve entrare in una colonna stretta."
print(textwrap.fill(text, width=28))''', "Paragrafo suddiviso senza spezzare normalmente le parole.", "textwrap terminal formatting")
    add("Analizzare campi CSV con virgole tra virgolette", "Legge una riga CSV rispettando il quoting, dove split non sarebbe corretto.", '''import csv
row = next(csv.reader(['"Rossi, Ada",42,"Roma"']))
print(row)''', "Tre campi; Rossi, Ada resta un campo unico.", "csv quoting parser")
    add("Formattare colonne numeriche", "Allinea etichette, interi e importi con specificatori espliciti.", '''rows = [("pane", 2, 1.35), ("latte", 10, 1.8)]
for name, quantity, price in rows:
    print(f"{name:<8} {quantity:>3d} {price:>7.2f}")''', "Due righe con quantità a destra e prezzi a due decimali; separatore decimale punto.", "format fstring alignment")
    add("Codificare e decodificare UTF-8", "Converte testo in byte e mostra come segnalare input UTF-8 non valido.", '''text = "Città"
payload = text.encode("utf-8")
print(payload.decode("utf-8"))
try:
    b"\\xff".decode("utf-8", errors="strict")
except UnicodeDecodeError:
    print("Byte non valido")''', "Città e poi Byte non valido.", "utf8 bytes encoding errors")
    # Collections: 20 tasks.
    add("Eliminare duplicati mantenendo l'ordine", "Deduplica elementi hashable rispettando la prima occorrenza.", '''values = [3, 1, 3, 2, 1]
unique = list(dict.fromkeys(values))
print(unique)''', "[3, 1, 2]", "list deduplicate order")
    add("Ordinare senza modificare la lista originale", "Ottiene una nuova lista ordinata e conserva la sequenza sorgente.", '''original = [9, 2, 5]
ordered = sorted(original)
print(original, ordered)''', "[9, 2, 5] e [2, 5, 9].", "list sorting immutable")
    add("Ordinare record su più campi", "Ordina per cognome e, in caso di parità, per nome.", '''people = [{"name": "Luca", "surname": "Rossi"}, {"name": "Ada", "surname": "Rossi"}]
print(sorted(people, key=lambda p: (p["surname"], p["name"])))''', "Ada precede Luca perché la seconda chiave risolve il pareggio.", "sorting key records")
    add("Raggruppare record per categoria", "Costruisce gruppi indipendenti senza perdere gli elementi del medesimo gruppo.", '''from collections import defaultdict
groups = defaultdict(list)
for category, amount in [("A", 10), ("B", 5), ("A", 7)]:
    groups[category].append(amount)
print(dict(groups))''', "A contiene [10, 7], B contiene [5].", "groupby defaultdict aggregation")
    add("Contare frequenze con Counter", "Conta le parole e recupera le due più frequenti.", '''from collections import Counter
counts = Counter("rosso blu rosso verde blu rosso".split())
print(counts.most_common(2))''', "rosso:3 e blu:2.", "counter frequency histogram")
    add("Unire dizionari con precedenza esplicita", "Sovrascrive le impostazioni di base soltanto con quelle definite dall'utente.", '''defaults = {"theme": "light", "size": 12}
user = {"size": 16}
merged = defaults | user
print(merged)
print(defaults)''', "size è 16 nel risultato e 12 nel dizionario originale.", "dict merge configuration")
    add("Appiattire una sequenza di liste", "Concatena un solo livello di annidamento senza ricorsione implicita.", '''rows = [[1, 2], [], [3, 4]]
flat = [value for row in rows for value in row]
print(flat)''', "[1, 2, 3, 4]", "list flatten comprehension")
    add("Dividere una lista in blocchi", "Produce lotti conservando anche l'ultimo blocco incompleto.", '''def chunks(values, size):
    if size <= 0:
        raise ValueError("La dimensione deve essere positiva")
    for start in range(0, len(values), size):
        yield values[start:start + size]
print(list(chunks(list(range(7)), 3)))''', "[[0, 1, 2], [3, 4, 5], [6]]", "batch chunk generator")
    add("Trasporre una matrice rettangolare", "Scambia righe e colonne rilevando righe con lunghezze differenti.", '''matrix = [[1, 2, 3], [4, 5, 6]]
transposed = [list(column) for column in zip(*matrix, strict=True)]
print(transposed)''', "[[1, 4], [2, 5], [3, 6]]; strict richiede Python 3.10+.", "matrix transpose zip")
    add("Abbinare sequenze controllando la lunghezza", "Evita la perdita silenziosa degli elementi eccedenti durante zip.", '''names, ages = ["Ada", "Luca"], [36]
try:
    print(list(zip(names, ages, strict=True)))
except ValueError as error:
    print(type(error).__name__)''', "ValueError perché le sequenze non hanno la stessa lunghezza.", "zip strict validation")
    add("Gestire una coda limitata", "Mantiene soltanto gli ultimi eventi usando una deque con capacità.", '''from collections import deque
recent = deque(maxlen=3)
recent.extend(["a", "b", "c", "d"])
print(list(recent))
print(recent.popleft())''', "Restano b,c,d; l'estrazione FIFO restituisce b.", "deque queue bounded")
    add("Estrarre attività per priorità", "Usa un min-heap con contatore per risolvere pareggi senza confrontare gli oggetti.", '''import heapq
queue = []
for index, (priority, name) in enumerate([(3, "report"), (1, "backup"), (1, "mail")]):
    heapq.heappush(queue, (priority, index, name))
while queue:
    print(heapq.heappop(queue)[2])''', "backup, mail, report: numero più piccolo significa priorità maggiore.", "heap priority queue")
    add("Trovare i maggiori valori senza ordinare tutto", "Recupera i primi tre valori più grandi con heapq.nlargest.", '''import heapq
scores = [4, 90, 3, 20, 88, 41]
print(heapq.nlargest(3, scores))''', "[90, 88, 41]", "heap topk nlargest")
    add("Inserire mantenendo l'ordinamento", "Trova un punto di inserimento e aggiorna una lista ordinata.", '''import bisect
values = [10, 20, 40]
bisect.insort(values, 30)
print(values, bisect.bisect_left(values, 20))''', "[10, 20, 30, 40] e indice 1.", "bisect sorted insertion")
    add("Calcolare differenze tra insiemi", "Individua aggiunte, rimozioni e valori invariati tra due snapshot.", '''before, after = {"a", "b"}, {"b", "c"}
print("aggiunti", sorted(after - before))
print("rimossi", sorted(before - after))
print("comuni", sorted(before & after))''', "Aggiunto c, rimosso a, comune b.", "set difference intersection")
    add("Leggere configurazioni a più livelli", "Cerca prima nelle opzioni locali poi nei valori predefiniti usando ChainMap.", '''from collections import ChainMap
defaults = {"size": 12, "theme": "light"}
local = {"size": 16}
config = ChainMap(local, defaults)
print(config["size"], config["theme"])
config["theme"] = "dark"
print(local)''', "16 light; la scrittura modifica il primo mapping.", "chainmap config precedence")
    add("Accumulare importi per chiave", "Calcola totali senza inizializzare manualmente ogni chiave numerica.", '''from collections import defaultdict
totals = defaultdict(int)
for name, amount in [("A", 2), ("B", 4), ("A", 3)]:
    totals[name] += amount
print(dict(totals))''', "A:5 e B:4.", "defaultdict sum aggregation")
    add("Enumerare a partire da uno", "Associa numeri di riga leggibili senza alterare gli indici della lista.", '''for number, line in enumerate(["rosso", "blu"], start=1):
    print(f"{number}: {line}")''', "1: rosso e 2: blu.", "enumerate index iteration")
    add("Confrontare elementi consecutivi", "Calcola differenze tra campioni adiacenti con pairwise.", '''from itertools import pairwise
samples = [10, 13, 12, 20]
print([right - left for left, right in pairwise(samples)])''', "[3, -1, 8]", "pairwise delta iterator")
    add("Generare un prodotto cartesiano", "Elenca combinazioni di due insiemi indipendenti senza cicli annidati manuali.", '''from itertools import product
print(list(product(["S", "M"], ["rosso", "blu"])))''', "Quattro coppie taglia-colore.", "itertools product combinations")
    # Numeric: 9.
    add("Arrotondare importi con Decimal", "Usa aritmetica decimale e una politica di arrotondamento dichiarata.", '''from decimal import Decimal, ROUND_HALF_UP
total = Decimal("1.005").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
print(total)''', "1.01: la modalità è half-up, non il default half-even.", "decimal money rounding")
    add("Calcolare con frazioni esatte", "Mantiene numeratore e denominatore senza errore binario in somme razionali.", '''from fractions import Fraction
value = Fraction(1, 3) + Fraction(1, 6)
print(value, value.numerator, value.denominator)''', "1/2 1 2", "fraction rational arithmetic")
    add("Calcolare media e deviazione standard", "Distingue la deviazione della popolazione da quella di un campione.", '''from statistics import mean, pstdev, stdev
values = [2, 4, 4, 4, 5, 5, 7, 9]
print(mean(values), round(pstdev(values), 3), round(stdev(values), 3))''', "5, deviazione popolazione 2, deviazione campione circa 2.138.", "statistics mean deviation")
    add("Trovare mediana e moda", "Descrive il centro e il valore più frequente senza confondere media e mediana.", '''from statistics import median, multimode
values = [1, 2, 2, 9, 20]
print(median(values), multimode(values))''', "Mediana 2 e moda [2].", "statistics median mode")
    add("Calcolare quartili con metodo esplicito", "Divide una distribuzione ordinata con il metodo inclusivo.", '''from statistics import quantiles
values = [1, 2, 3, 4, 5, 6, 7, 8, 9]
print(quantiles(values, n=4, method="inclusive"))''', "[3.0, 5.0, 7.0]", "statistics quantiles quartile")
    add("Semplificare rapporti con MCD", "Riduce un rapporto intero usando il massimo comune divisore.", '''from math import gcd
a, b = 42, 56
divisor = gcd(a, b)
print(a // divisor, b // divisor)''', "3 4", "gcd ratio integers")
    add("Trovare un periodo comune", "Determina dopo quanti minuti due intervalli regolari si riallineano.", '''from math import lcm
print(lcm(12, 18))''', "36 minuti.", "lcm schedule period")
    add("Campionare dati in modo riproducibile", "Isola il generatore pseudo-casuale per ottenere test deterministici.", '''import random
rng = random.Random(42)
print(rng.sample(list(range(10)), 3))''', "[1, 0, 4] con il generatore indicato; non usare random per segreti.", "random seed sampling")
    add("Generare un token casuale per identificazione", "Genera byte casuali adatti a un token invece del generatore per simulazioni.", '''import secrets
token = secrets.token_urlsafe(24)
print(token)
print(len(token))''', "Token URL-safe casuale di 32 caratteri; l'output varia.", "secrets token random")
    # Dates: 8.
    add("Analizzare e formattare una data", "Legge un formato italiano esplicito senza dipendere dalla locale di sistema.", '''from datetime import datetime
value = datetime.strptime("29/10/2026", "%d/%m/%Y")
print(value.strftime("%Y-%m-%d"))''', "2026-10-29", "date parse strptime format")
    add("Produrre un timestamp UTC consapevole", "Crea un datetime con fuso orario e rappresentazione ISO 8601.", '''from datetime import datetime, timezone
now = datetime.now(timezone.utc)
print(now.isoformat(timespec="seconds"))
print(now.utcoffset().total_seconds())''', "Timestamp corrente con +00:00 e offset 0.", "datetime utc timezone")
    add("Calcolare giorni tra due date", "Sottrae date civili senza introdurre effetti dell'ora legale.", '''from datetime import date
print((date(2026, 11, 5) - date(2026, 10, 29)).days)''', "7", "date difference duration")
    add("Trovare l'ultimo giorno del mese", "Gestisce mesi di lunghezza diversa e anni bisestili con calendar.", '''import calendar
from datetime import date
year, month = 2028, 2
last = calendar.monthrange(year, month)[1]
print(date(year, month, last))''', "2028-02-29", "calendar month leap")
    add("Convertire orari con offset fisso", "Converte un istante UTC in un offset dichiarato; un offset fisso non sostituisce le regole DST.", '''from datetime import datetime, timezone, timedelta
instant = datetime(2026, 1, 10, 12, tzinfo=timezone.utc)
fixed = timezone(timedelta(hours=1))
print(instant.astimezone(fixed).isoformat())''', "2026-01-10T13:00:00+01:00", "timezone offset conversion")
    add("Sommare durate senza manipolare stringhe", "Aggiunge ore e minuti attraversando automaticamente il cambio giorno.", '''from datetime import datetime, timedelta
start = datetime(2026, 10, 29, 23, 40)
print(start + timedelta(minutes=45))''', "2026-10-30 00:25:00", "timedelta arithmetic")
    add("Misurare una durata con un orologio monotono", "Misura tempo trascorso senza dipendere dalle correzioni dell'orologio civile.", '''from time import perf_counter
start = perf_counter()
result = sum(i * i for i in range(10000))
print(result, perf_counter() - start)''', "Somma 333283335000 e durata non negativa variabile.", "benchmark monotonic perf_counter")
    add("Leggere una data ISO con offset", "Preserva l'offset di un timestamp durante il parsing.", '''from datetime import datetime
value = datetime.fromisoformat("2026-10-29T10:15:00+02:00")
print(value.utcoffset().total_seconds())''', "7200.0 secondi.", "iso8601 datetime offset")
    # Files: 15; temporary directories isolate their side effects.
    add("Leggere e scrivere testo con pathlib", "Effettua un round-trip UTF-8 in una directory temporanea.", '''from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    path = Path(folder) / "note.txt"
    path.write_text("Città\\n", encoding="utf-8")
    print(path.read_text(encoding="utf-8"), end="")''', "Città; la cartella temporanea viene rimossa all'uscita.", "pathlib text file utf8")
    add("Leggere un file riga per riga", "Processa un file come iteratore senza caricarne tutto il contenuto.", '''from tempfile import TemporaryFile
with TemporaryFile(mode="w+", encoding="utf-8") as stream:
    stream.write("uno\\ndue\\n")
    stream.seek(0)
    for number, line in enumerate(stream, 1):
        print(number, line.rstrip("\\n"))''', "Righe numerate 1 uno e 2 due.", "file streaming lines")
    add("Scrivere byte e verificarne la lunghezza", "Usa modalità binaria per payload che non sono testo.", '''from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    path = Path(folder) / "packet.bin"
    path.write_bytes(bytes([0, 127, 255]))
    print(path.stat().st_size, list(path.read_bytes()))''', "3 [0, 127, 255]", "binary bytes file")
    add("Cercare file con glob", "Seleziona soltanto file con una determinata estensione.", '''from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    root = Path(folder)
    for name in ["a.py", "b.txt", "c.py"]:
        (root / name).touch()
    print(sorted(path.name for path in root.glob("*.py")))''', "['a.py', 'c.py']", "glob files filter")
    add("Creare cartelle annidate in modo idempotente", "Crea tutti i genitori e accetta una directory già esistente.", '''from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    path = Path(folder) / "reports" / "2026"
    path.mkdir(parents=True, exist_ok=True)
    path.mkdir(parents=True, exist_ok=True)
    print(path.is_dir())''', "True anche dopo il secondo tentativo.", "mkdir directory idempotent")
    add("Copiare un file conservando i metadati", "Duplica un file di esempio con copy2 e confronta i contenuti.", '''from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
with TemporaryDirectory() as folder:
    root = Path(folder)
    source, target = root / "a.txt", root / "b.txt"
    source.write_text("dato", encoding="utf-8")
    shutil.copy2(source, target)
    print(target.read_text(encoding="utf-8"))''', "dato; il comportamento preciso dei metadati dipende dal filesystem.", "shutil copy metadata")
    add("Sostituire atomicamente un file nella stessa directory", "Scrive prima un file provvisorio e poi sostituisce il destinatario con os.replace.", '''from pathlib import Path
from tempfile import TemporaryDirectory
import os
with TemporaryDirectory() as folder:
    target = Path(folder) / "config.json"
    pending = target.with_suffix(".tmp")
    pending.write_text('{"enabled": true}', encoding="utf-8")
    os.replace(pending, target)
    print(target.exists(), pending.exists())''', "True False; non è una garanzia di persistenza dopo perdita di alimentazione.", "atomic replace file")
    add("Calcolare SHA-256 leggendo a blocchi", "Ottiene un digest senza caricare in RAM un file intero.", '''import hashlib
import io
stream = io.BytesIO(b"abc")
digest = hashlib.sha256()
while block := stream.read(65536):
    digest.update(block)
print(digest.hexdigest())''', "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad", "sha256 hash streaming")
    add("Creare e leggere un archivio ZIP", "Produce uno ZIP di testo e ne legge un membro senza estrarre percorsi esterni.", '''import io
import zipfile
buffer = io.BytesIO()
with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
    archive.writestr("notes/readme.txt", "esempio")
with zipfile.ZipFile(io.BytesIO(buffer.getvalue())) as archive:
    print(archive.read("notes/readme.txt").decode())''', "esempio", "zip archive compression")
    add("Comprimere e decomprimere con gzip", "Comprime un payload UTF-8 mantenendo separati byte e testo.", '''import gzip
data = "ripetizione " * 20
packed = gzip.compress(data.encode("utf-8"), mtime=0)
print(gzip.decompress(packed).decode("utf-8") == data)''', "True dopo il round-trip.", "gzip compression bytes")
    add("Controllare che un percorso rimanga nella radice", "Rifiuta una destinazione con traversal dopo aver risolto il percorso.", '''from pathlib import Path
root = Path.cwd().resolve()
for relative in ["reports/output.txt", "../outside.txt"]:
    candidate = (root / relative).resolve()
    print(relative, candidate.is_relative_to(root))''', "True per reports/output.txt e False per ../outside.txt.", "path traversal resolve containment")
    add("Leggere un tratto binario con seek", "Accede a un intervallo di un flusso senza scorrere tutti i byte.", '''import io
stream = io.BytesIO(b"HEADERpayload")
stream.seek(6)
print(stream.read(7))''', "b'payload'", "seek binary offset")
    add("Usare un file temporaneo nominato", "Chiude il file prima di riaprirlo, per essere compatibile con Windows.", '''from pathlib import Path
from tempfile import NamedTemporaryFile
with NamedTemporaryFile(delete=False, suffix=".txt") as stream:
    stream.write(b"temporary")
    path = Path(stream.name)
try:
    print(path.read_text(encoding="utf-8"))
finally:
    path.unlink()''', "temporary; la rimozione avviene anche se la lettura fallisce.", "tempfile windows cleanup")
    add("Confrontare due file per contenuto", "Evita il confronto superficiale basato soltanto su dimensione e timestamp.", '''from pathlib import Path
from tempfile import TemporaryDirectory
import filecmp
with TemporaryDirectory() as folder:
    a, b = Path(folder) / "a", Path(folder) / "b"
    a.write_bytes(b"abc")
    b.write_bytes(b"abd")
    print(filecmp.cmp(a, b, shallow=False))''', "False anche se le dimensioni sono uguali.", "filecmp compare content")
    add("Leggere un file con BOM UTF-8", "Decodifica un eventuale BOM senza conservarlo nel testo applicativo.", '''payload = b"\\xef\\xbb\\xbfNome;Eta\\nAda;36"
text = payload.decode("utf-8-sig")
print(text.splitlines()[0])''', "Nome;Eta senza carattere BOM iniziale.", "bom utf8 encoding csv")
    # Serialization: 10.
    add("Serializzare JSON leggibile con Unicode", "Mantiene lettere accentate e ordina le chiavi per rendere leggibili i diff.", '''import json
data = {"nome": "Città", "valori": [1, 2]}
text = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
print(text)
print(json.loads(text) == data)''', "JSON con Città leggibile e True al round-trip.", "json serialization unicode")
    add("Segnalare la posizione di un errore JSON", "Restituisce riga e colonna di un documento non valido.", '''import json
try:
    json.loads('{"a":}')
except json.JSONDecodeError as error:
    print(error.lineno, error.colno, error.msg)''', "Riga 1, colonna 6 e messaggio del parser.", "json parse error diagnostics")
    add("Leggere e scrivere CSV con intestazioni", "Converte un dizionario in CSV e lo rilegge con DictReader.", '''import csv
import io
buffer = io.StringIO(newline="")
writer = csv.DictWriter(buffer, fieldnames=["nome", "eta"])
writer.writeheader()
writer.writerow({"nome": "Ada, Rossi", "eta": 36})
buffer.seek(0)
print(list(csv.DictReader(buffer)))''', "Un record; eta viene letta come stringa e il nome conserva la virgola.", "csv dictwriter dictreader")
    add("Leggere configurazioni TOML", "Analizza un documento TOML usando tomllib incluso in Python 3.11.", '''import tomllib
config = tomllib.loads('[app]\\nname="Catalogo"\\nport=8080\\n')
print(config["app"]["name"], config["app"]["port"])''', "Catalogo 8080", "toml config tomllib")
    add("Leggere opzioni INI tipizzate", "Ottiene booleani e interi da una configurazione testuale.", '''from configparser import ConfigParser
config = ConfigParser()
config.read_string("[app]\\nenabled=yes\\nport=8080\\n")
print(config.getboolean("app", "enabled"), config.getint("app", "port"))''', "True 8080", "ini configparser settings")
    add("Estrarre elementi da XML", "Legge attributi e testo con ElementTree senza dipendenze aggiuntive.", '''from xml.etree import ElementTree as ET
root = ET.fromstring('<items><item id="7">Ada</item></items>')
for item in root.findall("item"):
    print(item.attrib["id"], item.text)''', "7 Ada; usare per XML fidato e di dimensioni limitate.", "xml elementtree parse")
    add("Convertire byte in Base64", "Codifica dati binari per un canale testuale e valida la decodifica.", '''import base64
encoded = base64.b64encode(b"\\x00\\xff").decode("ascii")
print(encoded)
print(base64.b64decode(encoded, validate=True))''', "AP8= e b'\\x00\\xff'.", "base64 binary serialization")
    add("Serializzare una dataclass in JSON", "Trasforma un oggetto dati in un dizionario prima della codifica JSON.", '''from dataclasses import dataclass, asdict
import json
@dataclass
class Item:
    name: str
    quantity: int
print(json.dumps(asdict(Item("pane", 2)), ensure_ascii=False))''', '{"name": "pane", "quantity": 2}', "dataclass json asdict")
    add("Impacchettare numeri in un protocollo binario", "Definisce ordine dei byte e dimensioni dei campi con struct.", '''import struct
packet = struct.pack(">HI", 7, 1000)
print(packet.hex())
print(struct.unpack(">HI", packet))''', "0007000003e8 e (7, 1000).", "struct binary endian protocol")
    add("Creare query string da parametri", "Codifica spazi e caratteri riservati correttamente in un URL.", '''from urllib.parse import urlencode, parse_qs
query = urlencode({"q": "C++ e Qt", "page": 2})
print(query)
print(parse_qs(query))''', "La query codifica + come %2B; la lettura ripristina C++ e Qt.", "url query encode parameters")
    # Functions and objects: 15.
    add("Usare argomenti solo per parola chiave", "Impedisce di scambiare accidentalmente opzioni booleane posizionali.", '''def render(text, *, uppercase=False):
    return text.upper() if uppercase else text
print(render("ciao", uppercase=True))''', "CIAO; render('ciao', True) sarebbe TypeError.", "function keyword arguments")
    add("Evitare un valore predefinito mutabile", "Alloca una nuova lista quando il chiamante non ne fornisce una.", '''def append_value(value, values=None):
    if values is None:
        values = []
    values.append(value)
    return values
print(append_value(1), append_value(2))''', "[1] [2]: le invocazioni non condividono la lista.", "function default mutable")
    add("Restituire più risultati con una tupla", "Restituisce conteggio e totale con un contratto semplice.", '''def summarize(values):
    return len(values), sum(values)
count, total = summarize([2, 3, 5])
print(count, total)''', "3 10", "function tuple unpacking")
    add("Creare una chiusura con stato", "Mantiene un contatore locale senza variabili globali.", '''def make_counter():
    value = 0
    def next_value():
        nonlocal value
        value += 1
        return value
    return next_value
counter = make_counter()
print(counter(), counter())''', "1 2", "closure nonlocal state")
    add("Decorare una funzione conservandone i metadati", "Aggiunge un log mantenendo nome e docstring con functools.wraps.", '''from functools import wraps
def traced(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        print("chiamata", function.__name__)
        return function(*args, **kwargs)
    return wrapper
@traced
def square(value):
    return value * value
print(square(4), square.__name__)''', "chiamata square e 16 square.", "decorator wraps metadata")
    add("Memorizzare risultati puri con cache", "Evita di ricalcolare gli stessi sottoproblemi di una funzione ricorsiva.", '''from functools import cache
@cache
def fibonacci(n):
    if n < 0:
        raise ValueError("n deve essere non negativo")
    return n if n < 2 else fibonacci(n - 1) + fibonacci(n - 2)
print(fibonacci(20), fibonacci.cache_info().hits > 0)''', "6765 True", "memoization cache recursion")
    add("Fissare argomenti con partial", "Costruisce una funzione specializzata senza scrivere un wrapper ripetitivo.", '''from functools import partial
def add_tax(amount, rate):
    return amount * (1 + rate)
vat22 = partial(add_tax, rate=0.22)
print(round(vat22(100), 2))''', "122.0", "partial function binding")
    add("Definire un record immutabile", "Usa dataclass frozen per un oggetto valore con uguaglianza strutturale.", '''from dataclasses import dataclass, FrozenInstanceError
@dataclass(frozen=True)
class Point:
    x: int
    y: int
p = Point(2, 3)
print(p == Point(2, 3))
try:
    p.x = 8
except FrozenInstanceError:
    print("immutabile")''', "True e immutabile.", "dataclass frozen equality")
    add("Validare una proprietà di classe", "Protegge un'invariante usando un setter con controllo dell'input.", '''class Account:
    def __init__(self, balance):
        self.balance = balance
    @property
    def balance(self):
        return self._balance
    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError("Saldo negativo")
        self._balance = value
print(Account(20).balance)''', "20; i saldi negativi sollevano ValueError.", "property validation class")
    add("Definire stati con Enum", "Distingue stati simbolici da normali stringhe.", '''from enum import Enum
class Status(Enum):
    READY = "ready"
    BUSY = "busy"
current = Status("ready")
print(current is Status.READY, current.value)''', "True ready", "enum states identity")
    add("Gestire una risorsa con contextmanager", "Esegue sempre la fase di rilascio di una risorsa simulata.", '''from contextlib import contextmanager
@contextmanager
def resource():
    print("apertura")
    try:
        yield "risorsa"
    finally:
        print("chiusura")
with resource() as value:
    print(value)''', "apertura, risorsa, chiusura.", "contextmanager resource finally")
    add("Creare un iteratore personalizzato", "Espone un intervallo tramite protocollo iter e next.", '''class Countdown:
    def __init__(self, start):
        self.value = start
    def __iter__(self):
        return self
    def __next__(self):
        if self.value <= 0:
            raise StopIteration
        self.value -= 1
        return self.value + 1
print(list(Countdown(3)))''', "[3, 2, 1]", "iterator protocol next")
    add("Gestire errori di dominio con eccezioni dedicate", "Distingue un errore applicativo dai problemi generici del runtime.", '''class InsufficientStock(Exception):
    pass
def reserve(available, requested):
    if requested > available:
        raise InsufficientStock(f"Disponibili {available}, richiesti {requested}")
    return available - requested
try:
    reserve(2, 3)
except InsufficientStock as error:
    print(error)''', "Disponibili 2, richiesti 3.", "exception domain errors")
    add("Selezionare comportamenti con match", "Analizza tuple evento con pattern e guardia evitando indici ripetuti.", '''def describe(event):
    match event:
        case ("move", x, y) if x >= 0 and y >= 0:
            return f"posizione {x},{y}"
        case ("quit",):
            return "uscita"
        case _:
            return "evento non supportato"
print(describe(("move", 2, 3)))''', "posizione 2,3", "pattern match guard")
    add("Descrivere un'interfaccia con Protocol", "Tipizza strutturalmente un oggetto senza richiedere ereditarietà comune.", '''from typing import Protocol
class Named(Protocol):
    name: str
class User:
    def __init__(self, name):
        self.name = name
def greeting(value: Named) -> str:
    return f"Ciao {value.name}"
print(greeting(User("Ada")))''', "Ciao Ada; il controllo del protocollo è principalmente statico.", "typing protocol structural")
    # Concurrency: 8.
    add("Eseguire coroutine concorrenti con gather", "Avvia due attese asincrone e conserva l'ordine dei risultati.", '''import asyncio
async def task(value):
    await asyncio.sleep(0.01)
    return value * 2
async def main():
    print(await asyncio.gather(task(2), task(3)))
asyncio.run(main())''', "[4, 6]", "asyncio gather concurrency")
    add("Applicare un timeout asincrono", "Interrompe un'attesa che supera il tempo massimo gestendo TimeoutError.", '''import asyncio
async def main():
    try:
        await asyncio.wait_for(asyncio.sleep(1), timeout=0.01)
    except TimeoutError:
        print("tempo scaduto")
asyncio.run(main())''', "tempo scaduto", "asyncio timeout cancellation")
    add("Limitare la concorrenza con Semaphore", "Impedisce l'esecuzione contemporanea di più di due sezioni protette.", '''import asyncio
async def main():
    semaphore = asyncio.Semaphore(2)
    async def work(value):
        async with semaphore:
            await asyncio.sleep(0.01)
            return value
    print(await asyncio.gather(*(work(i) for i in range(5))))
asyncio.run(main())''', "[0, 1, 2, 3, 4]; al massimo due attese sono attive nella sezione.", "asyncio semaphore rate concurrency")
    add("Spostare lavoro bloccante in un thread", "Usa asyncio.to_thread per non bloccare l'event loop durante una funzione sincrona.", '''import asyncio
import time
def blocking():
    time.sleep(0.01)
    return "completato"
async def main():
    print(await asyncio.to_thread(blocking))
asyncio.run(main())''', "completato", "asyncio thread blocking")
    add("Distribuire operazioni con ThreadPoolExecutor", "Applica una funzione in un pool mantenendo l'ordine dei risultati con map.", '''from concurrent.futures import ThreadPoolExecutor
def square(value):
    return value * value
with ThreadPoolExecutor(max_workers=2) as pool:
    print(list(pool.map(square, [2, 3, 4])))''', "[4, 9, 16]; per CPU puro i thread CPython non garantiscono parallelismo.", "thread executor pool")
    add("Distribuire calcoli in processi separati", "Protegge il punto d'ingresso per supportare lo spawn di Windows.", '''from concurrent.futures import ProcessPoolExecutor
def square(value):
    return value * value
if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=2) as pool:
        print(list(pool.map(square, [2, 3, 4])))''', "[4, 9, 16]; eseguire come file, non incollare in una console interattiva.", "multiprocessing executor spawn")
    add("Passare dati con Queue tra thread", "Trasferisce elementi con un sentinella di chiusura e attende l'elaborazione.", '''from queue import Queue
from threading import Thread
queue = Queue()
def consume():
    while True:
        item = queue.get()
        try:
            if item is None:
                return
            print(item * 2)
        finally:
            queue.task_done()
worker = Thread(target=consume)
worker.start()
queue.put(3)
queue.put(None)
queue.join()
worker.join()''', "6 e terminazione del worker senza attese permanenti.", "thread queue sentinel producer consumer")
    add("Proteggere uno stato condiviso con Lock", "Rende atomico l'aggiornamento di un contatore rispetto ai thread dell'applicazione.", '''from threading import Lock, Thread
lock = Lock()
counter = 0
def increment():
    global counter
    for _ in range(1000):
        with lock:
            counter += 1
threads = [Thread(target=increment) for _ in range(2)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
print(counter)''', "2000", "thread lock shared state")
    # System, diagnostics and tests: 11.
    add("Analizzare argomenti CLI con argparse", "Definisce un argomento numerico e un flag con guida automatica.", '''import argparse
parser = argparse.ArgumentParser(description="Somma ripetuta")
parser.add_argument("--count", type=int, default=3)
parser.add_argument("--verbose", action="store_true")
args = parser.parse_args()
print(sum(range(args.count)))
if args.verbose:
    print("conteggio", args.count)''', "Senza argomenti stampa 3; --help mostra il contratto CLI.", "argparse cli arguments", "Inizializzazione")
    add("Leggere una variabile di ambiente con default", "Configura il programma senza inserire segreti o percorsi nel sorgente.", '''import os
raw = os.environ.get("APP_PORT", "8080")
port = int(raw)
if not 1 <= port <= 65535:
    raise ValueError("Porta fuori intervallo")
print(port)''', "8080 se APP_PORT non è impostata; valore invalido produce un errore chiaro.", "environment config port")
    add("Eseguire un processo senza shell", "Passa una lista di argomenti e verifica il codice di uscita del processo figlio.", '''import subprocess
import sys
result = subprocess.run([sys.executable, "-c", "print(6 * 7)"], capture_output=True, text=True, check=True, timeout=5)
print(result.stdout.strip())''', "42; nessuna interpolazione attraverso una shell.", "subprocess process arguments")
    add("Configurare log con livelli", "Emette messaggi selezionati da una soglia di severità.", '''import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("catalogo")
logger.debug("nascosto")
logger.info("avvio completato")''', "INFO avvio completato sul flusso stderr.", "logging diagnostics level", "Debug")
    add("Stampare uno stack trace gestito", "Conserva il dettaglio dell'eccezione senza interrompere subito l'applicazione.", '''import traceback
try:
    int("non numero")
except ValueError:
    print(traceback.format_exc().strip())''', "Traceback con ValueError e riga della conversione.", "traceback exception debug", "Debug")
    add("Scrivere un test unitario con unittest", "Verifica risultato e gestione di un input non valido con assertRaises.", '''import unittest
def divide(a, b):
    return a / b
class DivideTest(unittest.TestCase):
    def test_result(self):
        self.assertEqual(divide(6, 3), 2)
    def test_zero(self):
        with self.assertRaises(ZeroDivisionError):
            divide(1, 0)
if __name__ == "__main__":
    unittest.main()''', "Due test passano se la funzione mantiene il contratto.", "unittest testing assert", "Test")
    add("Sostituire un collaboratore con mock", "Controlla un risultato e verifica l'interazione senza chiamare servizi esterni.", '''from unittest.mock import Mock
repository = Mock()
repository.get_name.return_value = "Ada"
message = "Ciao " + repository.get_name(7)
assert message == "Ciao Ada"
repository.get_name.assert_called_once_with(7)
print(message)''', "Ciao Ada; l'asserzione controlla anche l'argomento 7.", "mock unittest dependency", "Test")
    add("Profilare una funzione con cProfile", "Identifica chiamate e tempi cumulativi su un carico locale.", '''import cProfile
def workload():
    return sum(i * i for i in range(10000))
cProfile.run("workload()", sort="cumulative")''', "Tabella con numero chiamate e tempi; i tempi variano tra esecuzioni.", "profile cprofile performance", "Debug")
    add("Misurare allocazioni con tracemalloc", "Legge memoria corrente e picco delle allocazioni tracciate da Python.", '''import tracemalloc
tracemalloc.start()
values = [str(i) for i in range(10000)]
current, peak = tracemalloc.get_traced_memory()
print(current > 0, peak >= current, len(values))
tracemalloc.stop()''', "True True 10000; non misura tutta la memoria nativa del processo.", "memory tracemalloc profiling", "Debug")
    add("Confrontare due versioni di testo", "Produce un diff unificato con intestazioni leggibili.", '''from difflib import unified_diff
before = ["uno\\n", "due\\n"]
after = ["uno\\n", "tre\\n"]
print("".join(unified_diff(before, after, fromfile="prima", tofile="dopo")), end="")''', "Il diff rimuove due e aggiunge tre.", "difflib diff text")
    add("Individuare un eseguibile nel PATH", "Controlla la disponibilità di una toolchain prima di avviare un comando.", '''import shutil
import sys
from pathlib import Path
name = Path(sys.executable).name
print(shutil.which(name) is not None)''', "True se l'eseguibile Python corrente è raggiungibile con lo stesso nome dal PATH.", "path executable discovery")
    # Python's SQLite adapter: 10 distinct API contracts.
    add("Eseguire query SQLite parametrizzate da Python", "Associa i valori tramite placeholder invece di concatenare testo SQL.", '''import sqlite3
with sqlite3.connect(":memory:") as db:
    db.execute("CREATE TABLE items(name TEXT)")
    db.execute("INSERT INTO items VALUES (?)", ("L'acqua",))
    print(db.execute("SELECT name FROM items WHERE name=?", ("L'acqua",)).fetchone()[0])''', "L'acqua senza problemi di quoting.", "sqlite parameter sql binding")
    add("Inserire più righe SQLite con executemany", "Invia una sequenza di parametri con un solo contratto di query.", '''import sqlite3
with sqlite3.connect(":memory:") as db:
    db.execute("CREATE TABLE items(value INTEGER)")
    db.executemany("INSERT INTO items VALUES (?)", [(2,), (3,), (5,)])
    print(db.execute("SELECT SUM(value) FROM items").fetchone()[0])''', "10", "sqlite executemany batch")
    add("Leggere righe SQLite per nome colonna", "Configura row_factory per ridurre gli indici numerici nel codice di accesso.", '''import sqlite3
db = sqlite3.connect(":memory:")
try:
    db.row_factory = sqlite3.Row
    row = db.execute("SELECT 7 AS id, 'Ada' AS name").fetchone()
    print(row["id"], row["name"])
finally:
    db.close()''', "7 Ada", "sqlite row_factory records")
    add("Annullare una transazione SQLite", "Dimostra il rollback automatico del context manager dopo un vincolo violato.", '''import sqlite3
db = sqlite3.connect(":memory:")
try:
    db.execute("CREATE TABLE items(id INTEGER PRIMARY KEY)")
    try:
        with db:
            db.execute("INSERT INTO items VALUES (1)")
            db.execute("INSERT INTO items VALUES (1)")
    except sqlite3.IntegrityError:
        print("rollback")
    print(db.execute("SELECT COUNT(*) FROM items").fetchone()[0])
finally:
    db.close()''', "rollback e 0 righe: anche il primo inserimento viene annullato.", "sqlite transaction rollback")
    add("Leggere SQLite a blocchi con fetchmany", "Processa un cursore per lotti invece di richiedere tutte le righe insieme.", '''import sqlite3
with sqlite3.connect(":memory:") as db:
    cursor = db.execute("SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3")
    while batch := cursor.fetchmany(2):
        print([row[0] for row in batch])''', "[1, 2] e [3].", "sqlite cursor fetchmany streaming")
    add("Registrare una funzione Python in SQLite", "Espone una trasformazione deterministica alle query del collegamento corrente.", '''import sqlite3
with sqlite3.connect(":memory:") as db:
    db.create_function("double_value", 1, lambda value: value * 2, deterministic=True)
    print(db.execute("SELECT double_value(?)", (21,)).fetchone()[0])''', "42; la funzione è registrata sul singolo collegamento.", "sqlite udf create_function")
    add("Adattare Decimal per SQLite esplicitamente", "Mantiene la rappresentazione decimale in una colonna TEXT senza adattatori impliciti.", '''from decimal import Decimal
import sqlite3
with sqlite3.connect(":memory:") as db:
    db.execute("CREATE TABLE amounts(value TEXT)")
    db.execute("INSERT INTO amounts VALUES (?)", (str(Decimal("12.30")),))
    amount = Decimal(db.execute("SELECT value FROM amounts").fetchone()[0])
    print(amount)''', "12.30; l'aritmetica precisa avviene in Python, non con REAL SQL.", "sqlite decimal adapter")
    add("Duplicare un database SQLite con backup", "Copia un database aperto usando l'API backup anziché copiare file attivi.", '''import sqlite3
source, target = sqlite3.connect(":memory:"), sqlite3.connect(":memory:")
try:
    source.execute("CREATE TABLE items(id INTEGER)")
    source.execute("INSERT INTO items VALUES (7)")
    source.commit()
    source.backup(target)
    print(target.execute("SELECT id FROM items").fetchone()[0])
finally:
    source.close()
    target.close()''', "7 nel database di destinazione.", "sqlite backup connection")
    add("Ottenere l'identificativo SQLite appena inserito", "Legge lastrowid dal cursore dell'inserimento pertinente.", '''import sqlite3
with sqlite3.connect(":memory:") as db:
    db.execute("CREATE TABLE items(id INTEGER PRIMARY KEY, name TEXT)")
    cursor = db.execute("INSERT INTO items(name) VALUES (?)", ("Ada",))
    print(cursor.lastrowid)''', "1 nel database appena creato.", "sqlite lastrowid insert identity")
    add("Esportare SQL da un collegamento Python", "Produce istruzioni di ricostruzione mediante iterdump su dati sintetici.", '''import sqlite3
with sqlite3.connect(":memory:") as db:
    db.execute("CREATE TABLE demo(value TEXT)")
    db.execute("INSERT INTO demo VALUES ('esempio')")
    print("\\n".join(db.iterdump()))''', "Script con BEGIN, CREATE TABLE, INSERT e COMMIT.", "sqlite dump export sql")
    program(b, "Progetto completo CLI inventario JSON", "Realizza una CLI con persistenza JSON, validazione e test separati; i file vengono scritti soltanto nel percorso passato dall'utente.", '''import argparse
from inventory import Inventory
def main():
    parser = argparse.ArgumentParser(description="Inventario locale")
    parser.add_argument("--file", default="inventory.json")
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add")
    add.add_argument("name")
    add.add_argument("quantity", type=int)
    commands.add_parser("list")
    args = parser.parse_args()
    inventory = Inventory(args.file)
    if args.command == "add":
        inventory.add(args.name, args.quantity)
    for name, quantity in inventory.items():
        print(f"{name}: {quantity}")
if __name__ == "__main__":
    main()''', filename="main.py", files={
        "inventory.py": '''import json
from pathlib import Path
class Inventory:
    def __init__(self, path):
        self.path = Path(path)
        self.data = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else {}
        if not isinstance(self.data, dict) or any(not isinstance(k, str) or type(v) is not int or v < 0 for k, v in self.data.items()):
            raise ValueError("Inventario non valido")
    def add(self, name, quantity):
        if not name.strip() or quantity <= 0:
            raise ValueError("Nome non vuoto e quantità positiva richiesti")
        self.data[name] = self.data.get(name, 0) + quantity
        pending = self.path.with_suffix(self.path.suffix + ".tmp")
        pending.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
        pending.replace(self.path)
    def items(self):
        return sorted(self.data.items())''',
        "test_inventory.py": '''import tempfile
import unittest
from pathlib import Path
from inventory import Inventory
class InventoryTests(unittest.TestCase):
    def test_persistence(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "items.json"
            Inventory(path).add("viti", 3)
            self.assertEqual(Inventory(path).items(), [("viti", 3)])
    def test_validation(self):
        with self.assertRaises(ValueError):
            Inventory("nonexistent-inventory-demo.json").add("", 0)
if __name__ == "__main__":
    unittest.main()''',
        "README.md": "# Inventario Python\n\nRichiede Python 3.11+. Nessuna dipendenza esterna.\n\nEseguire `python -m unittest -v`, quindi `python main.py add viti 3` e `python main.py list`. Il JSON viene salvato nella cartella corrente; `--file percorso.json` sceglie il file. Esecuzioni successive sommano le quantità. Il file provvisorio viene sostituito nella stessa directory; non sono gestite scritture simultanee da processi diversi.\n"}, command="python -m unittest -v\npython main.py add viti 3\npython main.py list", expected="Due test passano. Alla prima esecuzione la CLI stampa viti: 3; i dati rimangono nel JSON per l'avvio successivo.", tags=("project", "cli", "json", "unittest", "persistence"), section="Progetti completi", project=True)
    require_count(b, 120)


if __name__ == "__main__":
    build_all()
