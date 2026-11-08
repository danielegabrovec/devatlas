"""JavaScript core recipes: each entry solves a separate language task."""
from catalog_support import Book
from languages_common import program, require_count


def build_all():
    b = Book("javascript", "ECMAScript 2022+; Node.js 22+ per eseguire i file .mjs", ["https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference"], "Node.js 22+ nel PATH. Gli esempi riguardano il linguaggio e le API standard; nessun pacchetto npm.")
    def add(title, desc, code, expected, tags, files=None):
        program(b, title, desc, code, filename="main.mjs", files=files, command="node main.mjs", expected=expected, tags=tags.split())
    add("Convertire numeri senza accettare suffissi", "Distingue Number da parseInt e controlla NaN per validare un campo numerico.", '''for (const text of ["42", "42px", ""]) {
  const value = text.trim() === "" ? NaN : Number(text);
  console.log(text, Number.isFinite(value));
}''', "42 è valido, 42px e la stringa vuota non lo sono.", "number parse finite validation")
    add("Confrontare valori senza coercizione", "Mostra la differenza tra uguaglianza stretta e conversione implicita.", '''console.log(0 === false);
console.log(0 == false);
console.log(Object.is(NaN, NaN));''', "false, true, true: scegliere il confronto secondo il contratto.", "equality coercion strict")
    add("Usare un default solo per valori nulli", "Mantiene zero e stringa vuota con nullish coalescing.", '''const values = [0, "", null, undefined];
for (const value of values) console.log(value ?? "default");''', "0, riga vuota, default, default.", "nullish coalescing default")
    add("Accedere a proprietà annidate opzionali", "Legge un valore mancante senza generare TypeError.", '''const account = { profile: null };
console.log(account.profile?.address?.city ?? "non indicata");''', "non indicata", "optional chaining null")
    add("Destrutturare oggetti con rinomina e default", "Separa il nome pubblico della proprietà dalla variabile locale.", '''const payload = { user_name: "Ada" };
const { user_name: name, active = true } = payload;
console.log(name, active);''', "Ada true; il default interviene su undefined.", "destructuring rename default")
    add("Copiare un array senza condividere la struttura", "Crea un nuovo array con spread; gli oggetti interni restano riferimenti condivisi.", '''const source = [1, 2];
const copy = [...source, 3];
console.log(source, copy);''', "source contiene due elementi, copy ne contiene tre.", "spread array copy")
    add("Calcolare con interi oltre la precisione Number", "Usa BigInt e converte esplicitamente quando serve mescolare i domini numerici.", '''const value = 9007199254740993n;
console.log((value + 2n).toString());''', "9007199254740995; non si sommano direttamente BigInt e Number.", "bigint integer precision")
    add("Verificare multipli con resto non negativo", "Normalizza il resto per ottenere una posizione ciclica anche per indici negativi.", '''const mod = (value, size) => ((value % size) + size) % size;
console.log(mod(-1, 5), mod(6, 5));''', "4 1; size deve essere positivo.", "modulo remainder cyclic")
    add("Scambiare variabili senza un temporaneo", "Usa assegnazione destrutturante mantenendo entrambi i valori.", '''let left = 3, right = 8;
[left, right] = [right, left];
console.log(left, right);''', "8 3", "destructuring swap assignment")
    add("Esprimere condizioni con uno switch esaustivo a runtime", "Rifiuta comandi sconosciuti invece di restituire implicitamente undefined.", '''function execute(command) {
  switch (command) {
    case "start": return "avviato";
    case "stop": return "fermato";
    default: throw new RangeError(`Comando sconosciuto: ${command}`);
  }
}
console.log(execute("start"));''', "avviato; altri comandi generano RangeError.", "switch validation control flow")
    add("Conservare il valore con un'espressione condizionale", "Sceglie una descrizione con un'espressione che restituisce sempre una stringa.", '''const count = 1;
const label = count === 1 ? "elemento" : "elementi";
console.log(`${count} ${label}`);''', "1 elemento", "ternary expression formatting")
    add("Distinguere proprietà assente da valore undefined", "Usa Object.hasOwn quando la presenza della chiave ha un significato proprio.", '''const data = { supplied: undefined };
console.log(Object.hasOwn(data, "supplied"));
console.log(Object.hasOwn(data, "missing"));''', "true e false.", "object hasown undefined property")
    # Arrays and keyed collections: 12.
    add("Trasformare elementi con map", "Deriva un array senza modificare i valori originali.", '''const prices = [10, 20, 30];
console.log(prices.map(price => Math.round(price * 1.22 * 100) / 100));''', "[12.2, 24.4, 36.6]", "array map transform")
    add("Filtrare record per condizione", "Seleziona record attivi senza cancellare quelli della sorgente.", '''const rows = [{ id: 1, active: true }, { id: 2, active: false }];
console.log(rows.filter(row => row.active).map(row => row.id));''', "[1]", "array filter predicate")
    add("Accumulare un totale con reduce", "Definisce il valore iniziale per gestire anche un array vuoto.", '''const total = values => values.reduce((sum, value) => sum + value, 0);
console.log(total([2, 3, 5]), total([]));''', "10 0", "array reduce sum")
    add("Trovare un record e gestire l'assenza", "Usa find con optional chaining quando non esiste una corrispondenza.", '''const rows = [{ id: 1, name: "Ada" }];
console.log(rows.find(row => row.id === 9)?.name ?? "assente");''', "assente", "array find optional")
    add("Deduplicare un array con Set", "Mantiene la prima occorrenza di ciascun valore primitivo.", '''console.log([...new Set([3, 1, 3, 2, 1])]);''', "[3, 1, 2]; gli oggetti si confrontano per identità.", "set deduplicate order")
    add("Usare oggetti come chiavi con Map", "Mantiene chiavi per identità senza convertirle in stringhe.", '''const user = { id: 7 };
const sessions = new Map([[user, "attiva"]]);
console.log(sessions.get(user), sessions.get({ id: 7 }));''', "attiva undefined: due oggetti con gli stessi campi non sono la stessa chiave.", "map object identity keys")
    add("Ordinare numeri senza ordinamento lessicografico", "Fornisce un comparatore numerico e conserva l'array originale.", '''const values = [2, 10, 1];
console.log([...values].sort((a, b) => a - b));''', "[1, 2, 10]", "array sort comparator")
    add("Raggruppare record con un accumulatore Map", "Raccoglie record per categoria evitando collisioni con nomi del prototipo.", '''const groups = new Map();
for (const row of [{ category: "A", value: 1 }, { category: "A", value: 2 }, { category: "B", value: 3 }]) {
  if (!groups.has(row.category)) groups.set(row.category, []);
  groups.get(row.category).push(row.value);
}
console.log([...groups]);''', "A contiene [1,2] e B contiene [3].", "group map aggregation")
    add("Espandere e filtrare con flatMap", "Converte ogni riga in zero o più elementi in un unico passaggio.", '''const rows = ["a,b", "", "c"];
console.log(rows.flatMap(row => row === "" ? [] : row.split(",")));''', "['a', 'b', 'c']", "flatmap flatten filter")
    add("Controllare tutti o almeno un elemento", "Distingue quantificazione universale da esistenziale negli array.", '''const values = [2, 4, 7];
console.log(values.every(n => n > 0), values.some(n => n % 2 !== 0));''', "true true; every su array vuoto è true.", "every some predicate")
    add("Dividere un array in lotti", "Conserva l'ultimo lotto incompleto con una dimensione validata.", '''function chunks(values, size) {
  if (!Number.isInteger(size) || size <= 0) throw new RangeError("Dimensione positiva richiesta");
  const result = [];
  for (let i = 0; i < values.length; i += size) result.push(values.slice(i, i + size));
  return result;
}
console.log(chunks([1, 2, 3, 4, 5], 2));''', "[[1,2],[3,4],[5]]", "array chunk batch")
    add("Costruire un dizionario da coppie", "Converte una sequenza chiave-valore in un oggetto serializzabile.", '''const pairs = [["theme", "dark"], ["size", 14]];
console.log(Object.fromEntries(pairs));''', "Oggetto con theme dark e size 14; l'ultima coppia con la stessa chiave prevale.", "object fromentries entries")
    # Functions and objects: 12.
    add("Creare un contatore con closure", "Conserva stato privato dentro una funzione senza esporlo globalmente.", '''function createCounter() {
  let value = 0;
  return () => ++value;
}
const next = createCounter();
console.log(next(), next());''', "1 2", "closure private state")
    add("Ricevere un numero variabile di argomenti", "Usa rest parameters per implementare un'aggregazione.", '''function sum(...values) { return values.reduce((a, b) => a + b, 0); }
console.log(sum(1, 2, 3));''', "6", "rest parameters function")
    add("Fissare this con bind", "Conserva il ricevitore quando un metodo viene passato come callback.", '''const user = { name: "Ada", greet() { return `Ciao ${this.name}`; } };
const callback = user.greet.bind(user);
console.log(callback());''', "Ciao Ada", "this bind callback")
    add("Incapsulare uno stato con campi privati", "Protegge un saldo attraverso metodi e un campo privato della classe.", '''class Wallet {
  #balance = 0;
  deposit(amount) {
    if (!Number.isFinite(amount) || amount <= 0) throw new RangeError("Importo positivo richiesto");
    this.#balance += amount;
  }
  get balance() { return this.#balance; }
}
const wallet = new Wallet(); wallet.deposit(12);
console.log(wallet.balance);''', "12; #balance non è accessibile dall'esterno della classe.", "class private getter validation")
    add("Comporre comportamenti tramite oggetti", "Passa un collaboratore esplicito senza usare ereditarietà.", '''function createService(repository) {
  return { greeting: id => `Ciao ${repository.get(id).name}` };
}
const service = createService({ get: id => ({ id, name: "Ada" }) });
console.log(service.greeting(7));''', "Ciao Ada", "composition dependency injection")
    add("Copiare dati annidati con structuredClone", "Crea una copia indipendente di una struttura di dati clonabile.", '''const source = { points: [1, 2], created: new Date("2026-01-01T00:00:00Z") };
const copy = structuredClone(source);
copy.points.push(3);
console.log(source.points.length, copy.created instanceof Date);''', "2 true; le funzioni non sono clonabili.", "structuredclone deep copy date")
    add("Congelare la struttura superficiale di un oggetto", "Impedisce modifiche alle proprietà dirette; i riferimenti annidati restano mutabili.", '''const config = Object.freeze({ port: 8080, nested: { enabled: true } });
try { config.port = 9000; } catch (error) { console.log(error.name); }
config.nested.enabled = false;
console.log(config.port, config.nested.enabled);''', "TypeError in modulo strict, poi 8080 false.", "freeze immutable shallow")
    add("Creare un generatore lazy", "Produce una sequenza su richiesta evitando un array intermedio.", '''function* range(start, end) {
  for (let value = start; value < end; value++) yield value;
}
console.log([...range(2, 5)]);''', "[2, 3, 4]", "generator iterator yield")
    add("Rendere iterabile un oggetto", "Implementa Symbol.iterator per usare for-of e spread.", '''const interval = {
  start: 2, end: 4,
  *[Symbol.iterator]() { for (let n = this.start; n <= this.end; n++) yield n; }
};
console.log([...interval]);''', "[2, 3, 4]", "symbol iterator iterable")
    add("Intercettare assegnazioni con Proxy", "Valida un campo durante l'assegnazione prima di inoltrarla all'oggetto.", '''const user = new Proxy({ age: 0 }, {
  set(target, key, value) {
    if (key === "age" && (!Number.isInteger(value) || value < 0)) throw new RangeError("Età non valida");
    return Reflect.set(target, key, value);
  }
});
user.age = 36;
console.log(user.age);''', "36; un'età negativa genera RangeError.", "proxy reflect validation")
    add("Nascondere metadati con WeakMap", "Associa informazioni a un oggetto senza aggiungere proprietà pubbliche.", '''const metadata = new WeakMap();
const item = { id: 7 };
metadata.set(item, { visited: true });
console.log(metadata.get(item).visited, Object.keys(item));''', "true e ['id']; WeakMap non è enumerabile.", "weakmap metadata identity")
    add("Esportare e importare funzioni ESM", "Separa la logica riutilizzabile dal punto d'ingresso con moduli espliciti.", '''import { area } from "./math.mjs";
console.log(area(3, 4));''', "12; esportare anche math.mjs dalla scheda.", "esm module import export", files={"math.mjs":"export const area = (width, height) => width * height;"})
    # Async: 6.
    add("Attendere un valore asincrono", "Espone un contratto Promise anche quando il lavoro dimostrativo è locale.", '''async function loadName() { return "Ada"; }
console.log(await loadName());''', "Ada", "async await promise")
    add("Attendere Promise in parallelo con ordine stabile", "Raccoglie risultati con Promise.all; un rifiuto interrompe l'aggregazione.", '''const delayed = (value, ms) => new Promise(resolve => setTimeout(() => resolve(value), ms));
console.log(await Promise.all([delayed("primo", 10), delayed("secondo", 1)]));''', "['primo','secondo'] nonostante il secondo completi prima.", "promise all parallel")
    add("Raccogliere successi e fallimenti asincroni", "Usa allSettled per ottenere un risultato per ogni operazione.", '''const results = await Promise.allSettled([Promise.resolve(7), Promise.reject(new Error("fallita"))]);
console.log(results.map(result => result.status));''', "['fulfilled','rejected']", "promise allsettled errors")
    add("Applicare un timeout a una Promise", "Compete con un timer e lo rilascia nel finally dopo il completamento.", '''async function withTimeout(promise, ms) {
  let timer;
  try {
    return await Promise.race([promise, new Promise((_, reject) => {
      timer = setTimeout(() => reject(new Error("timeout")), ms);
    })]);
  } finally { clearTimeout(timer); }
}
console.log(await withTimeout(Promise.resolve("ok"), 100));''', "ok; il timeout non cancella automaticamente il lavoro sottostante.", "promise race timeout finally")
    add("Consumare un generatore asincrono", "Elabora una sequenza asincrona con for-await senza accumularla tutta.", '''async function* values() {
  yield await Promise.resolve(2);
  yield await Promise.resolve(3);
}
for await (const value of values()) console.log(value);''', "2 e 3.", "async generator iterator forawait")
    add("Eseguire tentativi asincroni limitati", "Ritenta una funzione fallibile e propaga l'ultimo errore al limite.", '''async function retry(action, attempts) {
  if (attempts < 1) throw new RangeError("Tentativi positivi richiesti");
  for (let i = 0; i < attempts; i++) {
    try { return await action(); } catch (error) { if (i + 1 === attempts) throw error; }
  }
}
let calls = 0;
console.log(await retry(async () => { if (++calls < 2) throw new Error("temporaneo"); return "ok"; }, 3));''', "ok dopo due invocazioni; ritentare soltanto operazioni con semantica adeguata.", "retry async error")
    # Text/locale/date/JSON: 8.
    add("Normalizzare Unicode prima del confronto", "Confronta una vocale composta con una sequenza di base e accento.", '''const a = "café", b = "cafe\\u0301";
console.log(a === b, a.normalize("NFC") === b.normalize("NFC"));''', "false true", "unicode normalize nfc")
    add("Estrarre tutte le corrispondenze regex", "Usa matchAll per ottenere valori e indici di più occorrenze.", '''const text = "id=12 id=7";
console.log([...text.matchAll(/id=(\\d+)/g)].map(match => Number(match[1])));''', "[12, 7]; matchAll richiede il flag globale per la RegExp passata.", "regex matchall capture")
    add("Sostituire con una funzione callback", "Trasforma separatori e iniziali senza costruire dinamicamente codice.", '''const source = "first_name";
console.log(source.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase()));''', "firstName", "regex replace callback camelcase")
    add("Formattare valuta con una locale", "Usa Intl.NumberFormat per separatori e posizione del simbolo.", '''const format = new Intl.NumberFormat("it-IT", { style: "currency", currency: "EUR" });
console.log(format.format(1234.5));''', "Importo in euro con separatori italiani; gli spazi possono essere non interrompibili.", "intl currency localization")
    add("Ordinare testo con regole locali", "Applica un confronto case-insensitive con collazione italiana.", '''const collator = new Intl.Collator("it", { sensitivity: "base", numeric: true });
console.log(["file10", "file2", "File1"].sort(collator.compare));''', "File1, file2, file10.", "intl collator natural sorting")
    add("Formattare una data senza dipendere dal fuso locale", "Imposta UTC nel formatter per ottenere una data civile stabile.", '''const date = new Date("2026-10-29T23:00:00Z");
console.log(new Intl.DateTimeFormat("it-IT", { timeZone: "UTC", dateStyle: "short" }).format(date));''', "29/10/26 nel formato breve italiano.", "intl date timezone utc")
    add("Rileggere date da JSON con reviver", "Ripristina soltanto il campo previsto anziché convertire ogni stringa simile a una data.", '''const data = JSON.parse('{"created":"2026-10-29T00:00:00Z","name":"Ada"}', (key, value) => key === "created" ? new Date(value) : value);
console.log(data.created instanceof Date, data.name);''', "true Ada", "json reviver date parse")
    add("Codificare componenti di un URL", "Protegge caratteri riservati nei parametri di ricerca.", '''const params = new URLSearchParams({ q: "C++ e Qt", page: "2" });
console.log(params.toString());
console.log(params.get("q"));''', "La query conserva il significato dei più; get ripristina C++ e Qt.", "urlsearchparams encoding query")
    # Errors and debugging: 4.
    add("Creare un errore applicativo con causa", "Mantiene l'errore originale quando viene aggiunto contesto al livello superiore.", '''try {
  try { JSON.parse("{"); } catch (cause) { throw new Error("Configurazione non valida", { cause }); }
} catch (error) {
  console.log(error.message, error.cause.name);
}''', "Configurazione non valida SyntaxError.", "error cause exception diagnostics")
    add("Rilasciare sempre una risorsa con finally", "Esegue il rilascio anche quando il lavoro fallisce.", '''let released = false;
try { throw new Error("operazione fallita"); }
catch (error) { console.log(error.message); }
finally { released = true; }
console.log(released);''', "operazione fallita e true.", "try finally cleanup")
    add("Verificare un contratto con assert", "Ferma il programma con un errore se un'invariante viene violata.", '''import assert from "node:assert/strict";
const average = values => values.reduce((a, b) => a + b, 0) / values.length;
assert.equal(average([2, 4]), 3);
assert.throws(() => { throw new RangeError("input"); }, RangeError);
console.log("contratti verificati");''', "contratti verificati", "assert test contract")
    add("Diagnosticare un valore non finito", "Distingue NaN e infinito prima di serializzare risultati numerici.", '''for (const value of [0 / 0, 1 / 0, 42]) {
  console.log({ value, nan: Number.isNaN(value), finite: Number.isFinite(value) });
}''', "NaN e Infinity risultano non finiti; 42 è finito.", "nan infinity diagnostics number")
    program(b, "Progetto completo analizzatore spese JSON", "Separa validazione, aggregazione e test di un report di spese; nessun servizio e nessuna dipendenza npm.", '''import { summarize } from "./expenses.mjs";
import rows from "./data.mjs";
console.log(JSON.stringify(summarize(rows), null, 2));''', filename="main.mjs", files={
      "expenses.mjs": '''export function summarize(rows) {
  const totals = new Map();
  for (const row of rows) {
    if (typeof row.category !== "string" || !Number.isSafeInteger(row.cents) || row.cents < 0) throw new TypeError("Spesa non valida");
    totals.set(row.category, (totals.get(row.category) ?? 0) + row.cents);
  }
  return Object.fromEntries([...totals].sort(([a], [b]) => a.localeCompare(b)));
}''',
      "data.mjs": '''export default [{ category: "casa", cents: 1250 }, { category: "libri", cents: 2000 }, { category: "casa", cents: 750 }];''',
      "expenses.test.mjs": '''import { test } from "node:test";
import assert from "node:assert/strict";
import { summarize } from "./expenses.mjs";
test("somma centesimi per categoria", () => assert.deepEqual(summarize([{category:"A",cents:12},{category:"A",cents:3}]), {A:15}));
test("rifiuta frazioni di centesimo", () => assert.throws(() => summarize([{category:"A",cents:1.5}]), TypeError));''',
      "README.md": "# Report spese JavaScript\n\nNode.js 22+, nessuna dipendenza. `node --test expenses.test.mjs` verifica aggregazione e validazione; `node main.mjs` stampa il report dei dati sintetici. Gli importi sono interi in centesimi per evitare l'aritmetica decimale binaria. I dati sono nel modulo data.mjs; non caricare moduli di provenienza ignota perché gli import eseguono JavaScript.\n"}, command="node --test expenses.test.mjs\nnode main.mjs", expected="Due test superati; report con casa 2000 e libri 2000 centesimi.", tags=("project", "module", "map", "test", "money"), project=True, section="Progetti completi")
    require_count(b, 55)


if __name__ == "__main__":
    build_all()
