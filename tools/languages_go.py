"""Go language tasks, standard library only."""
from catalog_support import Book
from languages_common import program, require_count

GOMOD="module example.test/catalog\n\ngo 1.22\n"


def build_all():
    b=Book("go","Go 1.22+",["https://go.dev/doc/", "https://pkg.go.dev/std"],"Toolchain Go1.22+ nel PATH. Tutti i moduli usano solo la libreria standard e non richiedono download di dipendenze.")
    def add(title,desc,body,expected,tags,imports=(),definitions="",files=None,command=None):
        source='package main\n\nimport (\n"fmt"\n'+''.join(f'"{item}"\n' for item in imports)+')\n\nfunc main(){\n'+body+'\n}\n'+definitions
        assets={"go.mod":GOMOD};assets.update(files or {})
        program(b,title,desc,source,filename="main.go",files=assets,command=command or "go run .",expected=expected,tags=tags.split(),error="Go rifiuta import e variabili inutilizzati: mantenere gli import coerenti con il sorgente; eseguire dalla directory che contiene go.mod.")
    add("Convertire un intero con strconv.Atoi", "Gestisce il valore error restituito dalla conversione senza ignorarlo.",'''value,err:=strconv.Atoi("42");if err!=nil{panic(err)};fmt.Println(value)''',"42", "strconv atoi parse error", ("strconv",))
    add("Formattare numeri senza concatenazioni", "Usa Sprintf per costruire una stringa con precisione e larghezza controllate.",'''label:=fmt.Sprintf("id=%04d prezzo=%.2f",7,12.5);fmt.Println(label)''',"id=0007 prezzo=12.50", "sprintf formatting number")
    add("Dividere e ripulire campi stringa", "Filtra campi vuoti dopo TrimSpace senza confondere questo formato con CSV.",'''var result []string;for _,part:=range strings.Split(" a, ,b ",","){value:=strings.TrimSpace(part);if value!=""{result=append(result,value)}};fmt.Println(result)''',"[a b]", "strings split trim", ("strings",))
    add("Contare rune invece di byte", "Distingue dimensione UTF-8 e numero di code point.",'''value:="Città";fmt.Println(len(value),utf8.RuneCountInString(value))''',"6 5; le rune non sono necessariamente grafemi percepiti dall'utente.", "utf8 rune unicode", ("unicode/utf8",))
    add("Aggiungere elementi a una slice", "Usa il valore restituito da append perché il backing array può cambiare.",'''values:=[]int{1,2};values=append(values,3,4);fmt.Println(values,len(values))''',"[1 2 3 4] 4", "slice append capacity")
    add("Copiare una slice senza condividere i dati", "Alloca un nuovo backing array e verifica che una modifica non tocchi la sorgente.",'''source:=[]int{1,2};target:=make([]int,len(source));copy(target,source);target[0]=9;fmt.Println(source,target)''',"[1 2] [9 2]", "slice copy backing array")
    add("Ordinare una slice con un comparatore", "Ordina record per età attraverso sort.Slice.",'''rows:=[]struct{Name string;Age int}{{"Ada",36},{"Luca",28}};sort.Slice(rows,func(i,j int)bool{return rows[i].Age<rows[j].Age});fmt.Println(rows)''',"Luca precede Ada; per preservare pareggi usare SliceStable.", "sort slice comparator", ("sort",))
    add("Distinguere chiave assente e valore zero", "Usa la seconda restituzione di una lettura map.",'''values:=map[string]int{"A":0};value,ok:=values["A"];fmt.Println(value,ok);_,exists:=values["B"];fmt.Println(exists)''',"0 true e false.", "map comma ok lookup")
    add("Contare frequenze con map", "Sfrutta il valore zero numerico per accumulare conteggi.",'''counts:=make(map[string]int);for _,word:=range []string{"rosso","blu","rosso"}{counts[word]++};fmt.Println(counts["rosso"])''',"2; l'ordine di iterazione della map non è garantito.", "map frequency counter")
    add("Serializzare struct con tag JSON", "Controlla i nomi dei campi e l'omissione delle proprietà vuote.",'''data,err:=json.Marshal(User{Name:"Ada"});if err!=nil{panic(err)};fmt.Println(string(data))''','{"name":"Ada"}', "struct json tags marshal", ("encoding/json",),'''type User struct{Name string `json:"name"`;Nickname string `json:"nickname,omitempty"`}''')
    add("Aggiungere metodi con receiver puntatore", "Modifica lo stato del chiamante invece di lavorare su una copia del record.",'''counter:=Counter{};counter.Increment();fmt.Println(counter.Value)''',"1", "method pointer receiver", definitions='''type Counter struct{Value int}
func(c *Counter)Increment(){c.Value++}''')
    add("Usare un'interfaccia strutturale", "Un tipo soddisfa un'interfaccia implementandone i metodi senza dichiarazioni esplicite.",'''var labeler Labeler=User{Name:"Ada"};fmt.Println(labeler.Label())''',"Utente Ada", "interface structural method", definitions='''type Labeler interface{Label()string}
type User struct{Name string}
func(u User)Label()string{return "Utente "+u.Name}''')
    add("Definire una funzione generica", "Riutilizza un algoritmo su slice con tipo comparabile.",'''fmt.Println(Contains([]int{2,3,5},3),Contains([]string{"a","b"},"c"))''',"true false", "generic comparable constraint", definitions='''func Contains[T comparable](values []T,wanted T)bool{for _,value:=range values{if value==wanted{return true}};return false}''')
    add("Restituire un errore di dominio", "Restituisce un error separato dal risultato valido senza panic per input previsti.",'''value,err:=positive(-1);if err!=nil{fmt.Println(err);return};fmt.Println(value)''',"valore non positivo", "error return validation", ("errors",),'''func positive(value int)(int,error){if value<=0{return 0,errors.New("valore non positivo")};return value,nil}''')
    add("Aggiungere contesto a un errore con wrapping", "Mantiene la causa interrogabile con errors.Is.",'''cause:=errors.New("record assente");wrapped:=fmt.Errorf("lettura utente: %w",cause);fmt.Println(wrapped);fmt.Println(errors.Is(wrapped,cause))''',"lettura utente: record assente e true.", "error wrapping errorsis", ("errors",))
    add("Rilasciare risorse con defer", "Mostra l'ordine LIFO delle funzioni differite al termine di main.",'''defer fmt.Println("rilascio uno");defer fmt.Println("rilascio due");fmt.Println("lavoro")''',"lavoro, rilascio due, rilascio uno.", "defer cleanup lifo")
    add("Contenere un panic nel confine di una funzione", "Recupera un panic attraverso una funzione differita nello stesso goroutine.",'''func(){defer func(){if value:=recover();value!=nil{fmt.Println("recuperato",value)}}();panic("demo")}();fmt.Println("continua")''',"recuperato demo e continua; gli errori previsti vanno restituiti come error.", "panic recover boundary")
    add("Attendere goroutine con WaitGroup", "Registra il lavoro prima di avviarlo e attende tutti i completamenti.",'''var group sync.WaitGroup;for i:=0;i<3;i++{group.Add(1);go func(){defer group.Done()}()};group.Wait();fmt.Println("3 lavori conclusi")''',"3 lavori conclusi", "goroutine waitgroup concurrency", ("sync",))
    add("Chiudere un canale dal produttore", "Consuma con range finché il produttore chiude il canale dopo gli invii.",'''values:=make(chan int);go func(){defer close(values);for i:=1;i<=3;i++{values<-i}}();for value:=range values{fmt.Println(value)}''',"1,2,3 e terminazione senza deadlock.", "channel close range producer")
    add("Applicare un timeout con select", "Compete fra ricezione e scadenza rilasciando il timer.",'''values:=make(chan int);timer:=time.NewTimer(5*time.Millisecond);defer timer.Stop();select{case value:=<-values:fmt.Println(value);case <-timer.C:fmt.Println("tempo scaduto")}''',"tempo scaduto; nessun produttore invia sul canale.", "select timeout timer", ("time",))
    add("Propagare cancellazione con context", "Un worker osserva Done e restituisce quando il chiamante annulla il contesto.",'''ctx,cancel:=context.WithCancel(context.Background());cancel();select{case <-ctx.Done():fmt.Println(ctx.Err());default:fmt.Println("attivo")}''',"context canceled", "context cancellation done", ("context",))
    add("Proteggere aggiornamenti con Mutex", "Evita una race sul contatore condiviso fra goroutine.",'''var gate sync.Mutex;var group sync.WaitGroup;count:=0;for i:=0;i<2;i++{group.Add(1);go func(){defer group.Done();for n:=0;n<1000;n++{gate.Lock();count++;gate.Unlock()}}()};group.Wait();fmt.Println(count)''',"2000; go run -race . richiede una toolchain C e piattaforma supportata.", "mutex race synchronization", ("sync",))
    add("Usare un contatore atomico", "Sincronizza il singolo contatore senza un blocco critico esplicito.",'''var count atomic.Int64;var group sync.WaitGroup;for i:=0;i<2;i++{group.Add(1);go func(){defer group.Done();for n:=0;n<1000;n++{count.Add(1)}}()};group.Wait();fmt.Println(count.Load())''',"2000", "atomic int64 counter", ("sync","sync/atomic"))
    add("Scrivere e leggere un file temporaneo", "Chiude il file prima di rileggerlo per supportare anche Windows.",'''file,err:=os.CreateTemp("","catalog-go-*.txt");if err!=nil{panic(err)};path:=file.Name();defer os.Remove(path);if _,err=file.WriteString("Città");err!=nil{file.Close();panic(err)};if err=file.Close();err!=nil{panic(err)};data,err:=os.ReadFile(path);if err!=nil{panic(err)};fmt.Println(string(data))''',"Città e rimozione automatica al ritorno.", "os tempfile readfile cleanup", ("os",))
    add("Leggere CSV con campi quotati", "Usa encoding/csv per riconoscere le virgole interne a un campo.",'''reader:=csv.NewReader(strings.NewReader("\\\"Rossi, Ada\\\",36\\n"));records,err:=reader.ReadAll();if err!=nil{panic(err)};fmt.Println(records[0][0],len(records[0]))''',"Rossi, Ada 2", "csv quoting reader", ("encoding/csv","strings"))
    add("Rifiutare proprietà JSON sconosciute", "Usa Decoder.DisallowUnknownFields per un contratto di configurazione rigoroso.",'''var config struct{Port int `json:"port"`};decoder:=json.NewDecoder(strings.NewReader(`{"port":8080,"typo":true}`));decoder.DisallowUnknownFields();err:=decoder.Decode(&config);fmt.Println(err!=nil)''',"true; il campo typo viene rifiutato.", "json decoder unknown fields", ("encoding/json","strings"))
    add("Analizzare date usando un layout Go", "Dichiara il formato tramite la data di riferimento specifica di Go.",'''value,err:=time.Parse("02/01/2006","29/10/2026");if err!=nil{panic(err)};fmt.Println(value.Format(time.RFC3339))''',"2026-10-29T00:00:00Z", "time layout parse date", ("time",))
    add("Estrarre sottogruppi con regexp", "Compila un pattern e distingue l'assenza di corrispondenza prima di indicizzare.",'''pattern:=regexp.MustCompile(`^item-(\\d+)$`);matches:=pattern.FindStringSubmatch("item-123");if len(matches)==2{fmt.Println(matches[1])}''',"123; MustCompile è adatto a pattern costanti controllati nello sviluppo.", "regexp submatch capture", ("regexp",))
    add("Eseguire test tabellari con testing", "Espone casi multipli con nomi leggibili e controlli sul contratto.",'''fmt.Println("Eseguire go test . per verificare i casi tabellari")''',"Due sottotest verificano totale e input vuoto.", "testing table tests",definitions='''func Total(values []int)int{sum:=0;for _,value:=range values{sum+=value};return sum}''',files={"main_test.go":'''package main
import "testing"
func TestTotal(t *testing.T){cases:=[]struct{name string;values []int;want int}{{"somma",[]int{2,3},5},{"vuoto",nil,0}};for _,tc:=range cases{t.Run(tc.name,func(t *testing.T){if got:=Total(tc.values);got!=tc.want{t.Fatalf("ottenuto %d, atteso %d",got,tc.want)}})}}'''},command="go test -v .")
    program(b,"Progetto completo inventario in memoria Go", "Organizza dominio, programma e test tabellari in package separati senza servizi o moduli esterni.",'''package main
import("fmt";"example.test/catalog/inventory")
func main(){store:=inventory.New();if err:=store.Add("viti",3);err!=nil{panic(err)};if err:=store.Add("viti",2);err!=nil{panic(err)};fmt.Println(store.Quantity("viti"))}''',filename="main.go",files={
      "go.mod":GOMOD,
      "inventory/store.go":'''package inventory
import("errors";"strings")
type Store struct{values map[string]int}
func New()*Store{return &Store{values:make(map[string]int)}}
func(s *Store)Add(name string,quantity int)error{name=strings.TrimSpace(name);if name==""||quantity<=0{return errors.New("nome non vuoto e quantita positiva richiesti")};s.values[name]+=quantity;return nil}
func(s *Store)Quantity(name string)int{return s.values[name]}''',
      "inventory/store_test.go":'''package inventory
import "testing"
func TestAccumulation(t *testing.T){store:=New();if err:=store.Add("viti",3);err!=nil{t.Fatal(err)};if err:=store.Add("viti",2);err!=nil{t.Fatal(err)};if store.Quantity("viti")!=5{t.Fatal("somma errata")}}
func TestInvalid(t *testing.T){if New().Add("",0)==nil{t.Fatal("validazione assente")}}''',
      "README.md":"# Inventario Go\n\nGo1.22+. `go test ./...` esegue due test; `go run .` stampa5. Nessuna dipendenza esterna. Il dominio è in memoria, privo di accessi concorrenti: aggiungere un mutex o confinare l'istanza a una sola goroutine se usato in concorrenza. La cartella inventory è un package importato usando il modulo dichiarato in go.mod.\n"},command="go test ./...\ngo run .",expected="Due test passano e il programma stampa5.",tags=("project","package","module","testing","map"),project=True,section="Progetti completi")
    require_count(b,30)


if __name__=="__main__":build_all()
