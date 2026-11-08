"""Type-level and runtime TypeScript contracts, all as complete small projects."""
import json
from catalog_support import Book
from languages_common import program, require_count

PACKAGE = json.dumps({"name":"typescript-example","private":True,"type":"module","scripts":{"build":"tsc -p tsconfig.json","start":"node dist/main.js"},"devDependencies":{"typescript":"6.0.3"}}, indent=2)
CONFIG = json.dumps({"compilerOptions":{"target":"ES2022","module":"NodeNext","moduleResolution":"NodeNext","strict":True,"outDir":"dist","rootDir":".","noEmitOnError":True,"lib":["ES2022","DOM"]},"include":["*.ts"]}, indent=2)


def build_all():
    b = Book("typescript", "TypeScript 6.0.3, strict; Node.js 22+ per esecuzione", ["https://www.typescriptlang.org/docs/handbook/intro.html", "https://www.typescriptlang.org/docs/handbook/utility-types.html"], "Node.js 22+ e npm. Il progetto dichiara TypeScript 6.0.3: npm install richiede accesso iniziale al registry o cache già disponibile. Consultazione ed export sono offline.")
    def add(title, desc, code, expected, tags, extra=None):
        files = {"package.json": PACKAGE, "tsconfig.json": CONFIG}
        files.update(extra or {})
        program(b, title, desc, code + "\nexport {};", filename="main.ts", files=files,
                command="npm install --ignore-scripts\nnpm run build\nnpm start", expected=expected,
                tags=tags.split(), error="Se tsc segnala un errore, non ignorarlo: noEmitOnError impedisce la generazione del JavaScript; conservare strict e le versioni dichiarate.")
    add("Annotare parametri e valore restituito", "Definisce un contratto numerico esplicito senza ricorrere ad any.", '''function area(width: number, height: number): number { return width * height; }
console.log(area(3, 4));''', "12; passare stringhe viene rifiutato dal compilatore.", "annotation function types")
    add("Restringere una union con typeof", "Distingue input testuali e numerici prima di applicare metodi specifici.", '''function normalize(value: string | number): string {
  return typeof value === "number" ? value.toFixed(2) : value.trim();
}
console.log(normalize(12), normalize(" Ada "));''', "12.00 Ada", "union narrowing typeof")
    add("Modellare stati con union discriminata", "Impedisce l'accesso ai dati finché lo stato non è ready.", '''type State = { kind: "loading" } | { kind: "ready"; value: number };
function describe(state: State): string {
  return state.kind === "ready" ? `valore ${state.value}` : "attesa";
}
console.log(describe({ kind: "ready", value: 7 }));''', "valore 7", "discriminated union state")
    add("Controllare l'esaustività con never", "Fa emergere a compilazione una nuova variante non gestita nello switch.", '''type Action = { type: "add"; value: number } | { type: "clear" };
function unreachable(value: never): never { throw new Error(`Variante inattesa: ${String(value)}`); }
function apply(action: Action): number {
  switch (action.type) {
    case "add": return action.value;
    case "clear": return 0;
    default: return unreachable(action);
  }
}
console.log(apply({ type: "add", value: 3 }));''', "3; aggiungere un nuovo membro ad Action obbliga ad aggiornare apply.", "never exhaustive switch")
    add("Gestire proprietà opzionali", "Distingue una proprietà assente da una stringa sempre presente.", '''interface Person { name: string; nickname?: string }
const label = (person: Person): string => person.nickname ?? person.name;
console.log(label({ name: "Ada" }));''', "Ada", "optional interface nullish")
    add("Proteggere proprietà con readonly", "Descrive un record la cui identità non può essere riassegnata dal chiamante.", '''interface Item { readonly id: number; name: string }
const item: Item = { id: 7, name: "prima" };
item.name = "dopo";
console.log(item.id, item.name);''', "7 dopo; readonly opera staticamente, non congela il runtime.", "readonly property immutability")
    add("Descrivere una tupla con elementi nominati", "Rappresenta una posizione con numero fisso di campi ordinati.", '''type Point = [x: number, y: number];
function distance([x, y]: Point): number { return Math.hypot(x, y); }
console.log(distance([3, 4]));''', "5; una tupla di tre elementi non rispetta Point.", "tuple named destructuring")
    add("Usare un enum con valori stringa", "Espone nomi simbolici con valori serializzabili leggibili.", '''enum Status { Ready = "ready", Busy = "busy" }
const current: Status = Status.Ready;
console.log(current);''', "ready; l'enum produce anche un oggetto JavaScript.", "enum string state")
    add("Limitare opzioni con tipi letterali", "Ammette soltanto dimensioni nominate nel contratto di una funzione.", '''type Size = "small" | "medium" | "large";
function pixels(size: Size): number { return {small: 12, medium: 16, large: 24}[size]; }
console.log(pixels("medium"));''', "16; una stringa arbitraria non viene accettata.", "literal union options")
    add("Verificare una configurazione con satisfies", "Controlla la forma mantenendo l'inferenza specifica dei valori.", '''const routes = { home: "/", settings: "/settings" } satisfies Record<string, string>;
console.log(routes.home.toUpperCase());''', "/; un valore numerico in routes genera errore statico.", "satisfies inference config")
    add("Conservare letterali con as const", "Deriva una union dai valori di un array readonly.", '''const levels = ["info", "warn", "error"] as const;
type Level = typeof levels[number];
const current: Level = "warn";
console.log(current);''', "warn; Level ammette soltanto i tre livelli dichiarati.", "const assertion literal inference")
    add("Validare unknown prima di leggerlo", "Impedisce l'accesso a proprietà non controllate provenienti da dati esterni.", '''function readName(value: unknown): string {
  if (typeof value !== "object" || value === null || !("name" in value) || typeof value.name !== "string") throw new TypeError("Nome assente");
  return value.name;
}
console.log(readName({ name: "Ada" }));''', "Ada; input non conformi generano TypeError.", "unknown runtime validation")
    add("Creare una guardia di tipo riutilizzabile", "Filtra una union con un predicato che informa anche il compilatore.", '''function isString(value: unknown): value is string { return typeof value === "string"; }
const values: unknown[] = ["Ada", 42, "Luca"];
const names = values.filter(isString);
console.log(names.map(name => name.toUpperCase()));''', "['ADA','LUCA']; names è string[].", "type guard predicate filter")
    add("Definire una funzione di asserzione", "Un controllo runtime restringe il tipo nel codice successivo.", '''function assertString(value: unknown): asserts value is string {
  if (typeof value !== "string") throw new TypeError("Stringa richiesta");
}
const value: unknown = "ciao";
assertString(value);
console.log(value.toUpperCase());''', "CIAO", "asserts assertion narrowing")
    add("Restringere null con una funzione dedicata", "Restituisce un valore non nullo soltanto dopo una verifica runtime.", '''function requireValue<T>(value: T | null | undefined): T {
  if (value === null || value === undefined) throw new Error("Valore mancante");
  return value;
}
console.log(requireValue<string>("Ada").length);''', "3; non usa l'asserzione non-null per aggirare il controllo.", "nullable generic guard")
    add("Mantenere il tipo con una funzione generica", "Conserva il legame fra tipo in ingresso e tipo restituito.", '''function identity<T>(value: T): T { return value; }
const value = identity({ id: 7 });
console.log(value.id);''', "7; il risultato conserva la proprietà id tipizzata.", "generic identity inference")
    add("Vincolare un parametro generico", "Richiede una proprietà length senza imporre un tipo concreto.", '''function lengthOf<T extends { length: number }>(value: T): number { return value.length; }
console.log(lengthOf("Ada"), lengthOf([1, 2]));''', "3 2", "generic constraint extends")
    add("Leggere proprietà con keyof", "Collega il nome della chiave al tipo restituito, evitando indici arbitrari.", '''function get<T, K extends keyof T>(value: T, key: K): T[K] { return value[key]; }
const user = { id: 7, name: "Ada" };
console.log(get(user, "name").toUpperCase());''', "ADA; una chiave inesistente è rifiutata.", "keyof indexed generic")
    add("Derivare un tipo da una proprietà", "Riutilizza il contratto di un campo senza duplicarne la definizione.", '''interface Order { id: number; customer: { name: string; email: string } }
type Customer = Order["customer"];
const customer: Customer = { name: "Ada", email: "ada@example.test" };
console.log(customer.name);''', "Ada", "indexed access type")
    add("Derivare un tipo da un valore esistente", "Usa typeof a livello di tipo per mantenere allineate configurazione e parametri.", '''const defaults = { retries: 3, enabled: true };
type Options = typeof defaults;
const custom: Options = { retries: 5, enabled: false };
console.log(custom.retries);''', "5", "typeof type derivation")
    add("Trasformare proprietà con un mapped type", "Costruisce un contratto di flag a partire dalle chiavi di un altro tipo.", '''type Flags<T> = { [K in keyof T]: boolean };
type Features = { search: string; export: number };
const flags: Flags<Features> = { search: true, export: false };
console.log(flags);''', "Oggetto di due booleani con chiavi search ed export.", "mapped type keys")
    add("Scegliere un tipo con conditional types", "Deriva un'etichetta statica dalla natura del tipo ricevuto.", '''type Kind<T> = T extends string ? "text" : "other";
const textKind: Kind<string> = "text";
const numberKind: Kind<number> = "other";
console.log(textKind, numberKind);''', "text other", "conditional type extends")
    add("Estrarre un elemento di array con infer", "Deducendo il parametro interno di un tipo si evita un duplicato manuale.", '''type ElementOf<T> = T extends readonly (infer U)[] ? U : never;
const value: ElementOf<readonly number[]> = 7;
console.log(value);''', "7; ElementOf<string> sarebbe never.", "infer conditional array element")
    add("Generare nomi validi con template literal types", "Compone una union di nomi evento consentiti senza usare stringhe libere.", '''type Entity = "user" | "order";
type EventName = `${Entity}:created`;
const event: EventName = "user:created";
console.log(event);''', "user:created", "template literal type event")
    add("Applicare aggiornamenti parziali con Partial", "Descrive un patch che può contenere soltanto alcuni campi dell'entità.", '''interface User { name: string; active: boolean }
function patch(user: User, changes: Partial<User>): User { return {...user, ...changes}; }
console.log(patch({name:"Ada",active:false}, {active:true}));''', "Nome preservato e active true; campi sconosciuti nel literal sono rifiutati.", "partial patch utility")
    add("Rendere obbligatoria una configurazione con Required", "Descrive la configurazione normalizzata dopo l'applicazione dei default.", '''interface Options { port?: number; host?: string }
function normalize(options: Options): Required<Options> {
  return {port: options.port ?? 8080, host: options.host ?? "localhost"};
}
console.log(normalize({}).port);''', "8080; il risultato ha entrambi i campi obbligatori.", "required defaults config")
    add("Proiettare un contratto con Pick", "Espone soltanto i campi pubblici desiderati di un record.", '''interface User { id: number; name: string; secret: string }
type PublicUser = Pick<User, "id" | "name">;
const user: PublicUser = {id:7,name:"Ada"};
console.log(user);''', "Record con id e name; la proiezione runtime va comunque implementata se i dati originali contengono segreti.", "pick projection public")
    add("Escludere un campo con Omit", "Definisce i dati di creazione senza l'identificativo generato dal sistema.", '''interface Item { id: number; name: string }
type NewItem = Omit<Item, "id">;
function create(data: NewItem): Item { return {id:1,...data}; }
console.log(create({name:"libro"}));''', "{id:1,name:'libro'}", "omit create dto")
    add("Richiedere una mappa completa con Record", "Obbliga a fornire un valore per ogni elemento di una union di chiavi.", '''type Locale = "it" | "en";
const greetings: Record<Locale, string> = {it:"Ciao",en:"Hello"};
console.log(greetings.it);''', "Ciao; rimuovere en produce errore a compilazione.", "record complete map")
    add("Esporre una vista readonly di un oggetto", "Impedisce modifiche attraverso una API di lettura senza copiare il record.", '''type Settings = { theme: string; size: number };
function show(settings: Readonly<Settings>): string { return `${settings.theme}:${settings.size}`; }
console.log(show({theme:"dark",size:14}));''', "dark:14; la protezione è superficiale e statica.", "readonly utility view")
    add("Estrarre membri compatibili da una union", "Seleziona una sotto-union con Extract.", '''type Value = string | number | boolean;
type Numeric = Extract<Value, number | bigint>;
const value: Numeric = 12;
console.log(value);''', "12; Numeric è number.", "extract utility union")
    add("Escludere membri da una union", "Rimuove gli stati non operativi da un contratto.", '''type State = "idle" | "running" | "done";
type ActiveState = Exclude<State, "idle">;
const state: ActiveState = "running";
console.log(state);''', "running", "exclude utility union")
    add("Rimuovere null e undefined da un tipo", "Definisce il tipo restituito dopo una validazione di presenza.", '''type Input = string | null | undefined;
type Present = NonNullable<Input>;
const value: Present = "disponibile";
console.log(value);''', "disponibile; NonNullable non esegue alcun controllo runtime.", "nonnullable utility null")
    add("Derivare il tipo restituito con ReturnType", "Mantiene un contratto dipendente da una factory senza duplicare l'interfaccia.", '''function createUser() { return {id:7,name:"Ada"}; }
type User = ReturnType<typeof createUser>;
const user: User = createUser();
console.log(user.name);''', "Ada", "returntype factory utility")
    add("Riutilizzare i parametri con Parameters", "Trasferisce la tupla degli argomenti a un wrapper.", '''function sum(a: number, b: number): number { return a+b; }
function logged(...args: Parameters<typeof sum>): number {
  console.log("argomenti", args);
  return sum(...args);
}
console.log(logged(2,3));''', "Argomenti [2,3], poi 5.", "parameters tuple wrapper")
    add("Estrarre il risultato asincrono con Awaited", "Descrive il dato ottenuto dopo await di una funzione.", '''async function load() { return {count:3}; }
type Loaded = Awaited<ReturnType<typeof load>>;
const data: Loaded = await load();
console.log(data.count);''', "3", "awaited async utility")
    add("Definire un contenitore generico", "Riutilizza una struttura senza perdere il tipo del payload.", '''interface Box<T> { value: T; updated: boolean }
const box: Box<number> = {value:42,updated:false};
console.log(box.value.toFixed(1));''', "42.0", "generic interface container")
    add("Implementare un'interfaccia con una classe", "Rende esplicito il comportamento richiesto a implementazioni intercambiabili.", '''interface Formatter { format(value: number): string }
class FixedFormatter implements Formatter {
  format(value: number): string { return value.toFixed(2); }
}
console.log(new FixedFormatter().format(3));''', "3.00", "implements interface class")
    add("Richiedere un metodo con una classe astratta", "Condivide una parte dell'algoritmo lasciando un'operazione alle sottoclassi.", '''abstract class Shape {
  abstract area(): number;
  describe(): string { return `area ${this.area()}`; }
}
class Square extends Shape {
  constructor(private readonly side: number) { super(); }
  area(): number { return this.side*this.side; }
}
console.log(new Square(4).describe());''', "area 16", "abstract class inheritance")
    add("Validare un setter tipizzato", "Protegge una proprietà numerica con controllo runtime e getter pubblico.", '''class Quantity {
  private current = 0;
  get value(): number { return this.current; }
  set value(next: number) { if(!Number.isInteger(next)||next<0) throw new RangeError("Quantità non valida"); this.current=next; }
}
const quantity = new Quantity(); quantity.value=7;
console.log(quantity.value);''', "7; un tipo number da solo non garantisce interi positivi.", "getter setter validation")
    add("Nascondere un costruttore con factory statica", "Controlla l'unico punto di creazione di un oggetto valore.", '''class Email {
  private constructor(readonly value: string) {}
  static parse(value: string): Email {
    if (!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(value)) throw new TypeError("Email non valida");
    return new Email(value);
  }
}
console.log(Email.parse("ada@example.test").value);''', "ada@example.test; il controllo è sintattico, non verifica l'esistenza della casella.", "factory private constructor")
    add("Descrivere firme di overload", "Collega tipi in ingresso a tipi in uscita con una implementazione comune.", '''function duplicate(value: string): string;
function duplicate(value: number): number;
function duplicate(value: string | number): string | number {
  return typeof value === "number" ? value*2 : value+value;
}
console.log(duplicate("a"), duplicate(3));''', "aa 6", "overload signatures function")
    add("Tipizzare parametri opzionali e default", "Permette l'omissione di un'opzione mantenendo un valore interno sempre definito.", '''function greet(name: string, prefix = "Ciao", suffix?: string): string {
  return `${prefix} ${name}${suffix ?? ""}`;
}
console.log(greet("Ada"));''', "Ciao Ada", "optional parameter default")
    add("Tipizzare una lista rest come tupla", "Ammette una firma variabile controllata con argomento obbligatorio iniziale.", '''function message(...args: [level: "info" | "error", ...parts: string[]]): string {
  const [level,...parts] = args;
  return `${level}: ${parts.join(" ")}`;
}
console.log(message("info","avvio","riuscito"));''', "info: avvio riuscito", "rest tuple variadic")
    add("Separare import di tipi e valori", "Usa import type per evitare dipendenze runtime superflue.", '''import type { Item } from "./contracts.js";
import { label } from "./contracts.js";
const item: Item = {id:7};
console.log(label(item));''', "elemento 7; il percorso .js è coerente con il JavaScript emesso da NodeNext.", "module import type esm", {"contracts.ts": "export interface Item { id: number }\nexport const label = (item: Item): string => `elemento ${item.id}`;"})
    add("Separare identificativi con un branded type", "Evita lo scambio statico fra stringhe che rappresentano entità diverse.", '''declare const userBrand: unique symbol;
type UserId = string & { readonly [userBrand]: true };
function parseUserId(value: string): UserId {
  if (!/^user-\\d+$/.test(value)) throw new TypeError("ID non valido");
  return value as UserId;
}
console.log(parseUserId("user-7"));''', "user-7; il cast è confinato dopo il controllo runtime.", "brand nominal identifier")
    add("Assegnare callback con parametri compatibili", "Usa una funzione che accetta un tipo più ampio dove viene richiesta una specializzazione.", '''type Animal = { name: string };
type Dog = Animal & { bark(): void };
const describeAnimal = (animal: Animal): void => console.log(animal.name);
const handleDog: (dog: Dog) => void = describeAnimal;
handleDog({name:"Fido",bark(){}});''', "Fido; strictFunctionTypes controlla la direzione dell'assegnazione.", "variance callback strictfunctiontypes")
    add("Collegare nomi evento e payload", "Una mappa di eventi rende il payload dipendente dalla chiave scelta.", '''type Events = { saved: {id:number}; failed: {message:string} };
function emit<K extends keyof Events>(name: K, payload: Events[K]): void { console.log(name,payload); }
emit("saved", {id:7});''', "saved con id 7; un payload message non rispetterebbe saved.", "event map generic payload")
    add("Restituire errori come Result generico", "Obbliga il chiamante a distinguere successo e fallimento senza catturare eccezioni.", '''type Result<T> = {ok:true;value:T}|{ok:false;error:string};
function parsePositive(text:string):Result<number> {
  const value=Number(text);
  return text.trim()!==""&&Number.isFinite(value)&&value>0 ? {ok:true,value} : {ok:false,error:"Numero positivo richiesto"};
}
const result=parsePositive("12");
console.log(result.ok ? result.value : result.error);''', "12", "result discriminated error handling")
    add("Validare un oggetto JSON sconosciuto", "Un parser JSON restituisce unknown e controlla ogni campo necessario prima di creare il dominio.", '''type Product = {name:string;price:number};
function parseProduct(text:string):Product {
  const value:unknown=JSON.parse(text);
  if(typeof value!=="object"||value===null||!("name" in value)||typeof value.name!=="string"||!("price" in value)||typeof value.price!=="number"||!Number.isFinite(value.price)) throw new TypeError("Prodotto non valido");
  return {name:value.name,price:value.price};
}
console.log(parseProduct('{"name":"libro","price":12}'));''', "Prodotto con name libro e price 12; nessun cast presume la validità dei dati.", "json unknown validation parser")
    add("Tipizzare una mappa di oggetti", "Dichiara chiavi e valori di Map e gestisce il possibile undefined di get.", '''const users = new Map<number,{name:string}>([[7,{name:"Ada"}]]);
console.log(users.get(7)?.name ?? "assente");''', "Ada", "map generic optional")
    add("Esporre un insieme senza operazioni di modifica", "Restituisce ReadonlySet per limitare il contratto pubblico del chiamante.", '''function available(): ReadonlySet<string> { return new Set(["it","en"]); }
const languages=available();
console.log(languages.has("it"));''', "true; il tipo non congela l'insieme a runtime.", "readonlyset collection interface")
    add("Tipizzare i valori prodotti da un generatore", "Distingue il tipo dei valori yield da quello finale di return.", '''function* count(): Generator<number, string, void> { yield 1; yield 2; return "fine"; }
const iterator=count();
console.log(iterator.next(),iterator.next(),iterator.next());''', "Due risultati done false con 1 e 2, poi done true con fine.", "generator iterator yield return")
    add("Preservare il tipo in un wrapper asincrono", "Un helper generico mantiene il tipo del risultato durante il tracciamento di una Promise.", '''async function traced<T>(action:()=>Promise<T>):Promise<T> {
  console.log("inizio");
  try { return await action(); } finally { console.log("fine"); }
}
const result=await traced(async()=>({id:7}));
console.log(result.id);''', "inizio, fine, 7; il risultato resta tipizzato con id numerico.", "async generic wrapper promise")
    project_files = {"package.json": PACKAGE, "tsconfig.json": CONFIG,
      "board.ts": '''export type Task = Readonly<{id:number;title:string;done:boolean}>;
export class Board {
  private tasks:Task[]=[];
  add(title:string):Task {
    if(!title.trim()) throw new TypeError("Titolo vuoto");
    const task={id:this.tasks.length+1,title:title.trim(),done:false};
    this.tasks=[...this.tasks,task];
    return task;
  }
  complete(id:number):void {
    if(!this.tasks.some(task=>task.id===id)) throw new RangeError("Task assente");
    this.tasks=this.tasks.map(task=>task.id===id?{...task,done:true}:task);
  }
  list():readonly Task[] { return this.tasks.map(task=>({...task})); }
}''',
      "test.ts": '''import {Board} from "./board.js";
function assert(value:boolean,message:string):void { if(!value) throw new Error(message); }
const board=new Board(); const task=board.add("Studiare TypeScript"); board.complete(task.id);
assert(board.list()[0].done,"Completamento");
try { board.add(" "); throw new Error("Validazione non eseguita"); } catch(error) { assert(error instanceof TypeError,"Tipo errore"); }
console.log("2 contratti verificati");''',
      "README.md": "# Task board TypeScript\n\nNode.js 22+, TypeScript 6.0.3. Eseguire `npm install --ignore-scripts`, `npm run build`, `node dist/test.js`, `npm start`. Il primo download del compilatore richiede Internet o cache npm; il programma emesso usa solo JavaScript standard. Lo stato è in memoria: a ogni avvio viene ricreato. Il contratto readonly è statico; list restituisce copie degli oggetti per non esporre lo stato interno.\n"}
    program(b, "Progetto completo task board tipizzata", "Realizza un dominio in memoria con record readonly, validazione, modifiche controllate, modulo di presentazione e test senza librerie esterne.", '''import {Board} from "./board.js";
const board=new Board();
const task=board.add("Prima attività");
board.complete(task.id);
console.log(board.list());''', filename="main.ts", files=project_files, command="npm install --ignore-scripts\nnpm run build\nnode dist/test.js\nnpm start", expected="Test: 2 contratti verificati; il programma stampa una attività con done true.", tags=("project","domain","readonly","typescript","testing"), project=True, section="Progetti completi")
    require_count(b, 55)


if __name__ == "__main__":
    build_all()
