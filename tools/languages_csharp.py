"""C# and .NET core contracts; no framework-UI or HTTP-backend duplication."""
from catalog_support import Book
from languages_common import program, require_count

CSPROJ = '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable><LangVersion>12</LangVersion></PropertyGroup></Project>'
USINGS = '''using System;
using System.Collections.Generic;
using System.Collections.Concurrent;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Channels;
using System.Threading.Tasks;
using System.Xml.Linq;
'''


def build_all():
    b = Book("csharp", "C# 12, .NET 8; compatibile con SDK successivi che supportano net8.0", ["https://learn.microsoft.com/en-us/dotnet/csharp/", "https://learn.microsoft.com/en-us/dotnet/api/"], "SDK .NET 8+ e targeting pack net8.0; dotnet nel PATH. Nessun pacchetto NuGet esterno. Il primo restore può richiedere i pack della piattaforma.")
    def add(title, desc, body, expected, tags, definitions=""):
        source = USINGS + "\npublic static class Program {\n public static async Task Main(string[] args) {\n" + body + "\n }\n}\n" + definitions
        program(b, title, desc, source, filename="Program.cs", files={"Example.csproj":CSPROJ}, command="dotnet run --project Example.csproj", expected=expected, tags=tags.split(), error="Se manca il targeting pack net8.0, installare il relativo SDK/pack; eventuali warning CS1998 indicano soltanto un Main dimostrativo senza await.")
    add("Convertire un intero senza eccezioni", "Usa TryParse per distinguere un dato valido da un errore dell'utente.", '''foreach (var text in new[] {"42", "abc"}) {
    if (int.TryParse(text, NumberStyles.Integer, CultureInfo.InvariantCulture, out var value)) Console.WriteLine(value);
    else Console.WriteLine("intero non valido");
}''', "42 e intero non valido.", "tryparse integer validation")
    add("Rilevare overflow aritmetico", "Attiva il controllo degli interi in un blocco checked.", '''try { var max = int.MaxValue; Console.WriteLine(checked(max + 1)); }
catch (OverflowException) { Console.WriteLine("overflow rilevato"); }''', "overflow rilevato", "checked overflow arithmetic")
    add("Calcolare importi decimali", "Usa il suffisso m per evitare l'aritmetica binaria double sugli importi.", '''decimal price=12.30m, quantity=3;
Console.WriteLine((price*quantity).ToString("F2",CultureInfo.InvariantCulture));''', "36.90", "decimal money precision")
    add("Limitare un valore con Math.Clamp", "Vincola un parametro all'intervallo ammesso prima dell'utilizzo.", '''int requested = 140;
Console.WriteLine(Math.Clamp(requested, 0, 100));''', "100; i limiti devono essere ordinati.", "clamp range validation")
    add("Arrotondare dichiarando il criterio", "Distingue l'arrotondamento bancario da quello che si allontana da zero.", '''Console.WriteLine(Math.Round(2.5m,0,MidpointRounding.ToEven));
Console.WriteLine(Math.Round(2.5m,0,MidpointRounding.AwayFromZero));''', "2 e 3.", "round midpoint decimal")
    add("Conservare offset con DateTimeOffset", "Rappresenta un istante con offset e lo converte in UTC.", '''var value=DateTimeOffset.Parse("2026-10-29T10:00:00+02:00",CultureInfo.InvariantCulture);
Console.WriteLine(value.ToUniversalTime().ToString("O"));''', "Istante UTC delle 08:00 con offset +00:00.", "datetimeoffset utc iso8601")
    add("Gestire date civili con DateOnly", "Somma giorni senza introdurre ore o fusi orari.", '''var day=DateOnly.ParseExact("29/10/2026","dd/MM/yyyy",CultureInfo.InvariantCulture);
Console.WriteLine(day.AddDays(7).ToString("yyyy-MM-dd"));''', "2026-11-05", "dateonly date arithmetic")
    add("Calcolare una durata con TimeSpan", "Distingue ore totali dalle componenti residue della durata.", '''var duration=TimeSpan.FromHours(27)+TimeSpan.FromMinutes(15);
Console.WriteLine($"totale={duration.TotalHours}; giorni={duration.Days}; ore={duration.Hours}");''', "27.25 ore totali, un giorno e tre ore residue; il separatore dipende dalla cultura.", "timespan duration totalhours")
    add("Analizzare un identificativo Guid", "Rifiuta testo malformato senza interrompere il flusso con un'eccezione.", '''var text="00112233-4455-6677-8899-aabbccddeeff";
Console.WriteLine(Guid.TryParse(text,out var id));
Console.WriteLine(id.ToString("D"));''', "True e GUID nel formato con trattini.", "guid identifier parse")
    add("Generare dati pseudo-casuali riproducibili", "Isola un generatore con seed per simulazioni locali, senza usarlo per segreti.", '''var first=new Random(42); var second=new Random(42);
Console.WriteLine(first.Next(100)==second.Next(100));''', "True per la stessa implementazione e seed; non è un formato persistente di dati casuali.", "random seed deterministic")
    add("Allineare colonne con interpolazione", "Applica larghezza e formato numerico ai valori di un report.", '''var rows=new[]{("pane",2,1.35m),("latte",10,1.80m)};
foreach(var (name,count,price) in rows) Console.WriteLine($"{name,-8} {count,3} {price,7:F2}");''', "Colonne allineate con due decimali secondo la cultura corrente.", "interpolation formatting alignment")
    add("Confrontare stringhe per chiavi tecniche", "Usa OrdinalIgnoreCase per confronti indipendenti dalla cultura utente.", '''Console.WriteLine(string.Equals("CONFIG","config",StringComparison.OrdinalIgnoreCase));''', "True; per ordinamento linguistico usare una cultura esplicita.", "string comparison ordinal case")
    add("Normalizzare testo Unicode in C#", "Rende uguali le rappresentazioni composta e decomposta di un accento.", '''var a="café"; var b="cafe\\u0301";
Console.WriteLine(a==b);
Console.WriteLine(a.Normalize(NormalizationForm.FormC)==b.Normalize(NormalizationForm.FormC));''', "False e True.", "unicode normalization nfc")
    add("Costruire testo con StringBuilder", "Accoda righe senza ricreare una stringa a ogni concatenazione.", '''var builder=new StringBuilder();
for(int i=1;i<=3;i++) builder.Append("Riga ").Append(i).AppendLine();
Console.Write(builder.ToString());''', "Tre righe numerate.", "stringbuilder text performance")
    add("Dividere testo ignorando campi vuoti", "Elimina spazi laterali e segmenti vuoti con opzioni di Split.", '''var values=" a, ,b ,, c ".Split(',',StringSplitOptions.TrimEntries|StringSplitOptions.RemoveEmptyEntries);
Console.WriteLine(string.Join("|",values));''', "a|b|c", "split trimentries removeempty")
    add("Unire etichette senza separatore finale", "Usa string.Join invece di aggiungere manualmente separatori nel ciclo.", '''Console.WriteLine(string.Join(", ",new[]{"Ada","Luca","Marta"}));''', "Ada, Luca, Marta", "join delimiter string")
    add("Estrarre gruppi regex con nome", "Analizza una riga di log con un timeout per il motore regex.", '''var match=Regex.Match("INFO durata=42ms",@"(?<level>INFO|WARN) durata=(?<ms>\\d+)ms",RegexOptions.CultureInvariant,TimeSpan.FromSeconds(1));
if(match.Success) Console.WriteLine($"{match.Groups["level"].Value} {match.Groups["ms"].Value}");''', "INFO 42", "regex named group timeout")
    add("Sostituire regex con MatchEvaluator", "Trasforma uno snake_case in camelCase tramite callback.", '''var result=Regex.Replace("first_name",@"_([a-z])",m=>m.Groups[1].Value.ToUpperInvariant(),RegexOptions.CultureInvariant,TimeSpan.FromSeconds(1));
Console.WriteLine(result);''', "firstName", "regex replace callback")
    add("Analizzare una porzione con ReadOnlySpan", "Legge una parte di stringa senza crearne una sottostringa.", '''var source="id=12345";
Console.WriteLine(int.Parse(source.AsSpan(3),CultureInfo.InvariantCulture));''', "12345", "span parse allocation")
    add("Codificare testo come UTF-8", "Esegue un round-trip esplicito tra stringhe e byte.", '''var bytes=Encoding.UTF8.GetBytes("Città");
Console.WriteLine(bytes.Length);
Console.WriteLine(Encoding.UTF8.GetString(bytes));''', "6 e Città.", "utf8 encoding bytes")
    add("Proiettare dati con Select", "Crea una sequenza derivata mantenendo separata la sorgente.", '''var prices=new[]{10m,20m};
Console.WriteLine(string.Join(",",prices.Select(price=>price*1.22m)));''', "Importi 12.20 e 24.40 con formato della cultura corrente.", "linq select projection")
    add("Filtrare record con Where", "Seleziona elementi con un predicato esplicito.", '''var values=new[]{1,2,3,4};
Console.WriteLine(string.Join(",",values.Where(value=>value%2==0)));''', "2,4", "linq where filter")
    add("Aggregare con un valore iniziale", "Definisce una somma che funziona anche su una sequenza vuota.", '''var values=new[]{2,3,5};
Console.WriteLine(values.Aggregate(0,(sum,value)=>sum+value));''', "10", "linq aggregate fold")
    add("Raggruppare e sommare con GroupBy", "Ottiene totali per categoria senza un ciclo di ricerca manuale.", '''var rows=new[]{(Category:"A",Value:2),(Category:"B",Value:4),(Category:"A",Value:3)};
foreach(var group in rows.GroupBy(row=>row.Category)) Console.WriteLine($"{group.Key}:{group.Sum(row=>row.Value)}");''', "A:5 e B:4.", "linq groupby aggregation")
    add("Ordinare su più chiavi con ThenBy", "Applica una seconda chiave soltanto ai pareggi della prima.", '''var rows=new[]{(Surname:"Rossi",Name:"Luca"),(Surname:"Rossi",Name:"Ada")};
foreach(var row in rows.OrderBy(row=>row.Surname,StringComparer.Ordinal).ThenBy(row=>row.Name,StringComparer.Ordinal)) Console.WriteLine(row.Name);''', "Ada precede Luca.", "linq orderby thenby sorting")
    add("Unire due sequenze per chiave", "Esegue un join interno in memoria tra utenti e ordini.", '''var users=new[]{(Id:1,Name:"Ada"),(Id:2,Name:"Luca")};
var orders=new[]{(UserId:1,Total:12m)};
var rows=users.Join(orders,u=>u.Id,o=>o.UserId,(u,o)=>$"{u.Name}:{o.Total}");
Console.WriteLine(string.Join(",",rows));''', "Un solo abbinamento per Ada.", "linq join relation")
    add("Deduplicare record per una proprietà", "Mantiene il primo elemento per chiave usando DistinctBy.", '''var rows=new[]{(Id:1,Name:"prima"),(Id:1,Name:"seconda"),(Id:2,Name:"terza")};
Console.WriteLine(string.Join(",",rows.DistinctBy(row=>row.Id).Select(row=>row.Name)));''', "prima,terza", "linq distinctby deduplicate")
    add("Suddividere una sequenza con Chunk", "Produce lotti di dimensione massima conservando quello finale incompleto.", '''foreach(var chunk in Enumerable.Range(1,5).Chunk(2)) Console.WriteLine(string.Join(",",chunk));''', "1,2 poi 3,4 poi 5.", "linq chunk batch")
    add("Abbinare elementi con Zip", "Abbina le posizioni delle due sequenze; il risultato termina con la più corta.", '''var pairs=new[]{"Ada","Luca"}.Zip(new[]{36,28});
foreach(var (name,age) in pairs) Console.WriteLine($"{name}:{age}");''', "Ada:36 e Luca:28; validare le lunghezze se devono coincidere.", "linq zip tuple")
    add("Leggere un dizionario senza eccezioni", "Usa TryGetValue per distinguere una chiave assente da un valore presente.", '''var counts=new Dictionary<string,int>{{"A",3}};
if(counts.TryGetValue("A",out var count)) Console.WriteLine(count);
Console.WriteLine(counts.TryGetValue("B",out _));''', "3 e False.", "dictionary trygetvalue lookup")
    add("Calcolare differenze con HashSet", "Individua elementi presenti soltanto nell'insieme iniziale.", '''var before=new HashSet<string>{"a","b"};
before.ExceptWith(new[]{"b","c"});
Console.WriteLine(string.Join(",",before));''', "a", "hashset difference set")
    add("Gestire una coda FIFO", "Inserisce ed estrae record nell'ordine di arrivo.", '''var queue=new Queue<string>(); queue.Enqueue("prima"); queue.Enqueue("seconda");
while(queue.TryDequeue(out var value)) Console.WriteLine(value);''', "prima e seconda.", "queue fifo collection")
    add("Gestire uno stack LIFO", "Modella una cronologia dove l'ultima operazione è la prima a essere estratta.", '''var stack=new Stack<string>(); stack.Push("prima"); stack.Push("seconda");
while(stack.TryPop(out var value)) Console.WriteLine(value);''', "seconda e prima.", "stack lifo undo")
    add("Estrarre attività con PriorityQueue", "Esegue prima l'attività con priorità numerica minore.", '''var queue=new PriorityQueue<string,int>(); queue.Enqueue("report",3); queue.Enqueue("backup",1);
while(queue.TryDequeue(out var task,out var priority)) Console.WriteLine($"{priority}:{task}");''', "1:backup poi 3:report; l'ordine dei pareggi non è garantito.", "priorityqueue heap priority")
    add("Esporre una vista di array in sola lettura", "Limita l'API pubblica con ReadOnlyCollection senza affermare immutabilità profonda.", '''var source=new[]{1,2,3};
var view=Array.AsReadOnly(source);
source[0]=9;
Console.WriteLine(view[0]);''', "9: la vista riflette i cambiamenti dell'array sorgente.", "readonly collection view")
    add("Copiare un record con with", "Deriva un nuovo oggetto valore conservando il record originale.", '''var original=new Person("Ada",36); var changed=original with {Age=37};
Console.WriteLine($"{original.Age} {changed.Age}");''', "36 37", "record with copy", "public record Person(string Name,int Age);")
    add("Distinguere uguaglianza di riferimento e valore", "Confronta due record separati con contenuti equivalenti.", '''var a=new Point(2,3); var b=new Point(2,3);
Console.WriteLine(a==b); Console.WriteLine(ReferenceEquals(a,b));''', "True False", "record equality reference", "public record Point(int X,int Y);")
    add("Proteggere un'invariante tramite proprietà", "Rifiuta valori negativi nel setter di una classe.", '''var item=new Stock(); item.Quantity=7; Console.WriteLine(item.Quantity);''', "7; quantità negative generano ArgumentOutOfRangeException.", "property validation class", '''public class Stock {
private int quantity;
public int Quantity {get=>quantity;set {if(value<0)throw new ArgumentOutOfRangeException(nameof(value));quantity=value;}}
}''')
    add("Scambiare implementazioni tramite interfaccia", "Programma contro un contratto minimo anziché una classe concreta.", '''IFormatter formatter=new HexFormatter(); Console.WriteLine(formatter.Format(255));''', "FF", "interface dependency polymorphism", '''public interface IFormatter {string Format(int value);}
public class HexFormatter:IFormatter {public string Format(int value)=>value.ToString("X");}''')
    add("Condividere un algoritmo con classe astratta", "Richiede una operazione specifica mantenendo il comportamento comune nella base.", '''Shape shape=new Square(4); Console.WriteLine(shape.Describe());''', "area=16", "abstract inheritance template", '''public abstract class Shape {public abstract double Area();public string Describe()=>$"area={Area()}";}
public class Square:Shape {private readonly double side;public Square(double side){this.side=side;}public override double Area()=>side*side;}''')
    add("Riutilizzare un contenitore generico", "Conserva il tipo del dato senza cast da object.", '''var box=new Box<int>(42); Console.WriteLine(box.Value+1);''', "43", "generics container type", "public record Box<T>(T Value);")
    add("Gestire riferimenti nullable", "Dichiara l'assenza possibile e usa un default prima dell'accesso.", '''string? name=null;
Console.WriteLine(name?.Length ?? 0);''', "0; Nullable enable nel progetto attiva l'analisi statica.", "nullable null conditional")
    add("Usare pattern su proprietà", "Seleziona un record combinando verifica del tipo e condizione sui campi.", '''object value=new Customer("Ada",20);
if(value is Customer {Age:>=18} customer) Console.WriteLine(customer.Name);''', "Ada", "property pattern matching", "public record Customer(string Name,int Age);")
    add("Selezionare un risultato con switch expression", "Esprime fasce numeriche con pattern relazionali e caso residuale.", '''int score=82;
var grade=score switch {>=90=>"A",>=75=>"B",>=60=>"C",_=>"D"};
Console.WriteLine(grade);''', "B", "switch expression relational pattern")
    add("Destrutturare un record", "Estrae i componenti nominati tramite il metodo Deconstruct generato.", '''var (name,age)=new Person("Ada",36);Console.WriteLine($"{name}:{age}");''', "Ada:36", "record deconstruction tuple", "public record Person(string Name,int Age);")
    add("Aggiungere un metodo di estensione", "Espone una trasformazione senza modificare il tipo originale.", '''Console.WriteLine("  ciao  ".Clean());''', "ciao", "extension method string", "public static class TextExtensions {public static string Clean(this string value)=>value.Trim();}")
    add("Notificare un cambiamento con event", "Consente sottoscrizione pubblica mantenendo l'emissione dentro la classe.", '''var clock=new Clock();clock.Tick+=(_,_)=>Console.WriteLine("tick");clock.Pulse();''', "tick", "event delegate notification", "public class Clock {public event EventHandler? Tick;public void Pulse()=>Tick?.Invoke(this,EventArgs.Empty);}")
    add("Attendere operazioni con Task.WhenAll", "Ottiene tutti i risultati conservando l'ordine dei task forniti.", '''async Task<int> Work(int value){await Task.Delay(5);return value*2;}
var results=await Task.WhenAll(Work(2),Work(3));Console.WriteLine(string.Join(",",results));''', "4,6", "task whenall async")
    add("Rilevare il primo task completato", "Usa WhenAny per identificare il vincitore e attende anche gli altri per chiudere il lavoro.", '''var slow=Task.Delay(50);var fast=Task.Delay(1);
var first=await Task.WhenAny(slow,fast);Console.WriteLine(ReferenceEquals(first,fast));
await Task.WhenAll(slow,fast);''', "Normalmente True; la temporizzazione non è una garanzia real-time.", "task whenany race")
    add("Cancellare un'attesa con CancellationToken", "Propaga una richiesta di cancellazione a Task.Delay.", '''using var source=new CancellationTokenSource();source.Cancel();
try {await Task.Delay(1000,source.Token);}catch(OperationCanceledException){Console.WriteLine("annullata");}''', "annullata", "cancellationtoken async cancel")
    add("Produrre una sequenza asincrona", "Espone risultati progressivi con IAsyncEnumerable anziché una lista completa.", '''await foreach(var value in Values()) Console.WriteLine(value);
static async IAsyncEnumerable<int> Values(){yield return 1;await Task.Delay(1);yield return 2;}''', "1 e 2.", "iasyncenumerable await foreach generator")
    add("Limitare accessi asincroni con SemaphoreSlim", "Rilascia il permesso nel finally dopo l'operazione protetta.", '''using var semaphore=new SemaphoreSlim(2);
async Task<int> Work(int value){await semaphore.WaitAsync();try{await Task.Delay(1);return value;}finally{semaphore.Release();}}
Console.WriteLine(string.Join(",",await Task.WhenAll(Enumerable.Range(1,4).Select(Work))));''', "1,2,3,4; al massimo due sezioni protette contemporaneamente.", "semaphoreslim concurrency limit")
    add("Parallelizzare un ciclo con Parallel.For", "Distribuisce lavoro indipendente e aggiorna un accumulatore con Interlocked.", '''int total=0;Parallel.For(1,101,value=>Interlocked.Add(ref total,value));Console.WriteLine(total);''', "5050", "parallel for interlocked")
    add("Proteggere uno stato con lock", "Serializza una sezione critica sincrona condivisa da più task.", '''var gate=new object();int count=0;
await Task.WhenAll(Enumerable.Range(0,4).Select(_=>Task.Run(()=>{for(int i=0;i<1000;i++){lock(gate){count++;}}})));
Console.WriteLine(count);''', "4000; non usare await dentro lock.", "lock synchronization shared state")
    add("Collegare produttore e consumatore con Channel", "Completa il writer e consuma tutti gli elementi fino alla chiusura.", '''var channel=Channel.CreateUnbounded<int>();
var producer=Task.Run(async()=>{for(int i=1;i<=3;i++)await channel.Writer.WriteAsync(i);channel.Writer.Complete();});
await foreach(var value in channel.Reader.ReadAllAsync())Console.WriteLine(value);
await producer;''', "1,2,3 e terminazione dopo il completamento del writer.", "channel producer consumer async")
    add("Aggiornare un dizionario concorrente", "Usa AddOrUpdate per contatori condivisi senza una sequenza read-modify-write esterna.", '''var counts=new ConcurrentDictionary<string,int>();
Parallel.For(0,1000,_=>counts.AddOrUpdate("A",1,(_,current)=>current+1));
Console.WriteLine(counts["A"]);''', "1000; la factory può essere invocata più volte e non deve avere effetti collaterali.", "concurrentdictionary addorupdate")
    add("Inizializzare una risorsa soltanto alla prima lettura", "Lazy esegue la factory una sola volta nel caso dimostrato.", '''int calls=0;var value=new Lazy<string>(()=>{calls++;return "pronto";});
Console.WriteLine(calls);Console.WriteLine(value.Value);Console.WriteLine(value.Value);Console.WriteLine(calls);''', "0, pronto, pronto, 1.", "lazy initialization factory")
    add("Leggere e scrivere un file temporaneo UTF-8", "Chiude e rimuove il file temporaneo anche quando il lavoro genera eccezioni.", '''var path=Path.GetTempFileName();
try{await File.WriteAllTextAsync(path,"Città",Encoding.UTF8);Console.WriteLine(await File.ReadAllTextAsync(path,Encoding.UTF8));}
finally{File.Delete(path);}''', "Città; il file temporaneo viene eliminato.", "file async utf8 temporary")
    add("Leggere un flusso binario in memoria", "Usa BinaryWriter e BinaryReader dichiarando la gestione del flusso sottostante.", '''using var stream=new MemoryStream();
using(var writer=new BinaryWriter(stream,Encoding.UTF8,leaveOpen:true)){writer.Write(42);writer.Write("Ada");}
stream.Position=0;using var reader=new BinaryReader(stream,Encoding.UTF8,leaveOpen:true);
Console.WriteLine($"{reader.ReadInt32()}:{reader.ReadString()}");''', "42:Ada; il formato è quello specifico di BinaryWriter.", "stream binary reader writer")
    add("Serializzare e rileggere JSON tipizzato", "Usa System.Text.Json con record e verifica un risultato non nullo.", '''var json=JsonSerializer.Serialize(new Person("Ada",36));
var person=JsonSerializer.Deserialize<Person>(json)??throw new FormatException("JSON nullo");
Console.WriteLine(person.Name);''', "Ada", "json serializer record", "public record Person(string Name,int Age);")
    add("Scrivere campi CSV con quoting corretto", "Raddoppia le virgolette e racchiude i campi che contengono separatori o newline.", '''static string Escape(string value)=>value.IndexOfAny(new[]{',','"','\\r','\\n'})>=0 ? "\\\""+value.Replace("\\\"","\\\"\\\"")+"\\\"" : value;
Console.WriteLine(string.Join(",",new[]{"Rossi, Ada","ha detto \\\"ciao\\\""}.Select(Escape)));''', "Entrambi i campi sono quotati e le virgolette interne vengono raddoppiate.", "csv escaping writer")
    add("Leggere e costruire XML con LINQ to XML", "Seleziona un elemento per attributo e ne legge il contenuto.", '''var root=XElement.Parse("<items><item id='7'>Ada</item></items>");
var item=root.Elements("item").Single(element=>(int?)element.Attribute("id")==7);
Console.WriteLine(item.Value);''', "Ada; usare su XML fidato di dimensioni limitate.", "xml xelement linq")
    add("Creare un archivio ZIP in memoria", "Scrive un membro testuale e riapre l'archivio senza estrarre percorsi sul filesystem.", '''using var buffer=new MemoryStream();
using(var zip=new ZipArchive(buffer,ZipArchiveMode.Create,leaveOpen:true)){using var writer=new StreamWriter(zip.CreateEntry("note.txt").Open());writer.Write("esempio");}
buffer.Position=0;using var readZip=new ZipArchive(buffer,ZipArchiveMode.Read);
using var reader=new StreamReader(readZip.GetEntry("note.txt")!.Open());Console.WriteLine(reader.ReadToEnd());''', "esempio", "zip archive compression memory")
    add("Rilasciare risorse con using e finally", "Mostra l'ordine del rilascio anche quando una operazione fallisce.", '''try{using var resource=new DemoResource();throw new InvalidOperationException("fallita");}
catch(InvalidOperationException error){Console.WriteLine(error.Message);}''', "rilasciata prima di fallita.", "idisposable using cleanup", "public sealed class DemoResource:IDisposable{public void Dispose()=>Console.WriteLine(\"rilasciata\");}")
    add("Aggiungere contesto con una eccezione dedicata", "Conserva la causa originale nella proprietà InnerException.", '''try{try{int.Parse("abc");}catch(FormatException cause){throw new ImportException("Riga non valida",cause);}}
catch(ImportException error){Console.WriteLine($"{error.Message}:{error.InnerException?.GetType().Name}");}''', "Riga non valida:FormatException", "custom exception innerexception", "public class ImportException:Exception{public ImportException(string message,Exception inner):base(message,inner){}}")
    add("Verificare invarianti anche in Release", "Usa un controllo esplicito quando l'asserzione deve rimanere attiva in ogni configurazione.", '''static void Require(bool condition,string message){if(!condition)throw new InvalidOperationException(message);}
Require(2+2==4,"Somma errata");Console.WriteLine("contratto verificato");''', "contratto verificato; Debug.Assert può essere rimosso nelle build senza DEBUG.", "assert invariant release testing")
    add("Misurare un intervallo con Stopwatch", "Usa un timer per durate invece dell'orologio civile.", '''var timer=Stopwatch.StartNew();long sum=0;for(int i=0;i<10000;i++)sum+=i;timer.Stop();
Console.WriteLine($"{sum} {timer.Elapsed.TotalMilliseconds:F3}ms");''', "49995000 e durata variabile non negativa.", "stopwatch benchmark duration")
    add("Analizzare importi con cultura esplicita", "Legge una virgola decimale italiana senza dipendere dalla cultura del processo.", '''var value=decimal.Parse("1.234,50",NumberStyles.Number,CultureInfo.GetCultureInfo("it-IT"));
Console.WriteLine(value.ToString("F2",CultureInfo.InvariantCulture));''', "1234.50", "culture decimal parse globalization")
    add("Validare un valore enum ricevuto come testo", "Combina TryParse e IsDefined per rifiutare valori numerici non previsti.", '''foreach(var text in new[]{"Ready","999"}){bool valid=Enum.TryParse<Status>(text,true,out var status)&&Enum.IsDefined(status);Console.WriteLine(valid);}''', "True False", "enum tryparse isdefined validation", "public enum Status{Ready,Busy}")
    program(b, "Progetto completo registro prestiti C#", "Costruisce un dominio con record, validazione, serializzazione JSON e autotest senza dipendenze NuGet.", '''using System.Text.Json;
var register=new Register();register.Add("Ada","Libro C#");register.Return(1);
Console.WriteLine(JsonSerializer.Serialize(register.List(),new JsonSerializerOptions{WriteIndented=true}));
SelfTests.Run();''', filename="Program.cs", files={
        "Example.csproj":CSPROJ,
        "Register.cs": '''public record Loan(int Id,string Person,string Title,bool Returned);
public sealed class Register{
private readonly List<Loan> loans=new();
public void Add(string person,string title){if(string.IsNullOrWhiteSpace(person)||string.IsNullOrWhiteSpace(title))throw new ArgumentException("Persona e titolo richiesti");loans.Add(new Loan(loans.Count+1,person.Trim(),title.Trim(),false));}
public void Return(int id){var index=loans.FindIndex(loan=>loan.Id==id);if(index<0)throw new KeyNotFoundException("Prestito assente");loans[index]=loans[index] with{Returned=true};}
public IReadOnlyList<Loan> List()=>loans.ToArray();
}''',
        "SelfTests.cs": '''public static class SelfTests{
public static void Run(){var register=new Register();register.Add("Ada","Libro");register.Return(1);if(!register.List()[0].Returned)throw new Exception("Restituzione errata");try{register.Add("","Libro");throw new Exception("Validazione assente");}catch(ArgumentException){}Console.WriteLine("2 contratti verificati");}
}''',
        "README.md": "# Registro prestiti\n\nRichiede SDK .NET 8+ e targeting pack net8.0. `dotnet run --project Example.csproj` esegue il dominio e i due autotest; `dotnet build -c Release` compila. Nessun pacchetto esterno. Il registro è in memoria e viene ricreato a ogni avvio: il JSON stampato è un report, non una persistenza automatica. Gli ID crescono soltanto nel processo corrente.\n"}, command="dotnet build Example.csproj -c Release\ndotnet run --project Example.csproj", expected="JSON con un prestito Returned true e messaggio 2 contratti verificati.", tags=("project","record","domain","json","test"), project=True, section="Progetti completi")
    require_count(b,70)


if __name__=="__main__":
    build_all()
