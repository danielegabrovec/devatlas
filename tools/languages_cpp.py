"""80 independently curated C++20 recipes."""
from catalog_support import Book
from languages_common import program, require_count

HEADERS = '''#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <bitset>
#include <charconv>
#include <cctype>
#include <chrono>
#include <cmath>
#include <complex>
#include <condition_variable>
#include <deque>
#include <filesystem>
#include <fstream>
#include <functional>
#include <future>
#include <iomanip>
#include <iostream>
#include <iterator>
#include <limits>
#include <list>
#include <map>
#include <memory>
#include <mutex>
#include <numeric>
#include <optional>
#include <queue>
#include <random>
#include <ranges>
#include <regex>
#include <set>
#include <span>
#include <sstream>
#include <stack>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <thread>
#include <tuple>
#include <type_traits>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <variant>
#include <vector>
using namespace std;
'''


def build_all():
    b = Book("cpp", "C++20, GCC 13+ oppure Clang 16+/MSVC con libreria C++20", ["https://learn.microsoft.com/en-us/cpp/standard-library/cpp-standard-library-reference", "https://isocpp.org/get-started"], "Compilatore e libreria standard C++20. Comandi pronti per GCC/g++; su Windows usare MSYS2 UCRT64 o una toolchain GCC nel PATH. Nessuna libreria esterna.")
    def add(title, desc, code, expected, tags, definitions=""):
        source = HEADERS + "\n" + definitions + "\nint main(){\n" + code + "\n}\n"
        program(b, title, desc, source, filename="main.cpp", command=[{"shell":"PowerShell","os":"Windows","cwd":".","code":"g++ -std=c++20 -Wall -Wextra -pthread main.cpp -o demo.exe\n.\\demo.exe"},{"shell":"Bash","os":"Linux/macOS","cwd":".","code":"g++ -std=c++20 -Wall -Wextra -pthread main.cpp -o demo\n./demo"}], expected=expected, tags=tags.split(), error="Se un header o simbolo C++20 manca, controllare sia la versione del compilatore sia quella della libreria standard; non rimuovere -std=c++20.")
    # Numerics: 10.
    add("Convertire un intero con from_chars", "Analizza un intero senza eccezioni e rifiuta suffissi non consumati.", '''string text="123";int value=0;auto [end,error]=from_chars(text.data(),text.data()+text.size(),value);
if(error==errc{}&&end==text.data()+text.size())cout<<value<<'\\n';''', "123; il controllo del puntatore finale evita di accettare 123px.", "from_chars parse integer")
    add("Controllare una somma prima dell'overflow", "Verifica il limite superiore prima di sommare due interi non negativi.", '''int a=numeric_limits<int>::max(),b=1;
if(a>=0&&b>=0&&a>numeric_limits<int>::max()-b)cout<<"overflow evitato\\n";
else cout<<a+b<<'\\n';''', "overflow evitato; non viene eseguita la somma con overflow signed.", "overflow numeric_limits checked")
    add("Confrontare double con tolleranza", "Combina tolleranza assoluta e relativa per risultati numerici approssimati.", '''double a=0.1+0.2,b=0.3;
double tolerance=max(1e-12,1e-9*max(abs(a),abs(b)));
cout<<boolalpha<<(abs(a-b)<=tolerance)<<'\\n';''', "true; scegliere le tolleranze in base al problema.", "floating epsilon tolerance")
    add("Arrotondare e stampare con precisione", "Distingue l'arrotondamento numerico dalla sola presentazione decimale.", '''double value=12.345;
cout<<fixed<<setprecision(2)<<value<<'\\n';
cout<<lround(2.5)<<'\\n';''', "Valore a due decimali e 3; lround arrotonda i mezzi lontano da zero.", "round precision formatting")
    add("Semplificare un rapporto con gcd", "Riduce numeratore e denominatore usando la libreria numeric.", '''int a=42,b=56;int divisor=gcd(a,b);cout<<a/divisor<<'/'<<b/divisor<<'\\n';''', "3/4", "gcd ratio numeric")
    add("Calcolare il minimo comune multiplo", "Trova il primo allineamento di due periodi interi.", '''cout<<lcm(12,18)<<'\\n';''', "36; gli input devono evitare overflow del risultato.", "lcm period numeric")
    add("Generare interi uniformi con mt19937", "Separa motore e distribuzione anziché usare rand con il modulo.", '''mt19937 engine(42);uniform_int_distribution<int> dice(1,6);
for(int i=0;i<5;i++)cout<<dice(engine)<<' ';cout<<'\\n';''', "Cinque interi fra 1 e 6; la sequenza della distribuzione può variare tra librerie.", "random mt19937 uniform distribution")
    add("Contare bit attivi con popcount", "Calcola la cardinalità di una maschera unsigned senza un ciclo manuale.", '''unsigned value=0b101101;cout<<popcount(value)<<'\\n';''', "4", "bit popcount mask")
    add("Ruotare bit senza perdere i bit in uscita", "Usa rotl su unsigned per una rotazione circolare del registro.", '''unsigned value=1;cout<<rotl(value,3)<<'\\n';''', "8; rotl è disponibile da C++20.", "bit rotl rotation")
    add("Calcolare modulo e argomento complessi", "Usa complex per rappresentare un numero nel piano e ricavarne il modulo.", '''complex<double> value(3,4);cout<<abs(value)<<' '<<norm(value)<<'\\n';''', "5 25: modulo e modulo quadrato.", "complex abs norm")
    # Strings: 10.
    add("Leggere una vista senza copiare stringhe", "Usa string_view fintanto che la stringa proprietaria rimane viva.", '''string owner="prefix:payload";string_view view(owner);cout<<view.substr(7)<<'\\n';''', "payload; non restituire una vista verso una stringa locale distrutta.", "string_view lifetime substring")
    add("Dividere una riga con stringstream", "Legge campi separati da virgola senza applicare le regole complete di CSV.", '''istringstream input("a,b,c");string field;
while(getline(input,field,','))cout<<field<<'\\n';''', "a, b, c su righe separate; non gestisce quoting CSV.", "split getline delimiter")
    add("Rimuovere spazi laterali da una stringa", "Trova il primo e l'ultimo carattere significativo senza cancellazioni ripetute.", '''string text=" \\tciao \\n";auto first=text.find_first_not_of(" \\t\\r\\n");
auto result=first==string::npos?string{}:text.substr(first,text.find_last_not_of(" \\t\\r\\n")-first+1);
cout<<'['<<result<<"]\\n";''', "[ciao]", "trim whitespace string")
    add("Convertire ASCII in minuscolo senza comportamento indefinito", "Converte i byte tramite unsigned char prima di chiamare tolower.", '''string text="HeLLo";
transform(text.begin(),text.end(),text.begin(),[](unsigned char c){return static_cast<char>(tolower(c));});
cout<<text<<'\\n';''', "hello; non è una normalizzazione Unicode completa.", "tolower ascii unsigned char")
    add("Controllare prefissi e suffissi", "Verifica in modo leggibile il formato esterno di un nome file.", '''string name="report-2026.csv";cout<<boolalpha<<name.starts_with("report-")<<' '<<name.ends_with(".csv")<<'\\n';''', "true true", "starts_with ends_with string")
    add("Cercare e sostituire una sola occorrenza", "Rimpiazza la prima porzione trovata controllando npos.", '''string text="rosso e rosso";auto position=text.find("rosso");
if(position!=string::npos)text.replace(position,5,"blu");cout<<text<<'\\n';''', "blu e rosso", "find replace string npos")
    add("Estrarre gruppi con regex_match", "Verifica l'intera riga ed estrae una parte numerica.", '''string text="item-123";smatch match;
if(regex_match(text,match,regex(R"(item-(\\d+))")))cout<<match[1].str()<<'\\n';''', "123", "regex capture match")
    add("Sostituire pattern con regex_replace", "Compatta sequenze di spazi in un separatore singolo.", '''cout<<regex_replace(string("a   b\\tc"),regex(R"(\\s+)")," ")<<'\\n';''', "a b c", "regex replace whitespace")
    add("Analizzare campi numerici da una riga", "Controlla stream e contenuto residuo prima di accettare il record.", '''istringstream input("7 12.5");int id;double price;
if(input>>id>>price){input>>ws;if(input.eof())cout<<id<<' '<<price<<'\\n';}''', "7 12.5; input con caratteri residui non viene stampato.", "istringstream parser validation")
    add("Costruire una stringa con ostringstream", "Separa la composizione testuale dall'output su terminale.", '''ostringstream output;output<<"id="<<7<<" prezzo="<<fixed<<setprecision(2)<<12.5;cout<<output.str()<<'\\n';''', "id=7 prezzo=12.50", "ostringstream formatting builder")
    # Sequence algorithms: 20.
    add("Ordinare un vector in modo crescente", "Applica sort e stampa il contenitore senza dipendere da un formato custom.", '''vector<int> values{9,2,5};sort(values.begin(),values.end());for(int value:values)cout<<value<<' ';''', "2 5 9", "vector sort algorithm")
    add("Conservare l'ordine dei pareggi con stable_sort", "Ordina record per gruppo mantenendo l'ordine originale all'interno di ogni gruppo.", '''vector<pair<int,string>> rows{{1,"prima"},{0,"altra"},{1,"seconda"}};
stable_sort(rows.begin(),rows.end(),[](const auto&a,const auto&b){return a.first<b.first;});
for(const auto& row:rows)cout<<row.second<<' ';''', "altra prima seconda", "stable_sort records tie")
    add("Selezionare i primi valori con partial_sort", "Ordina soltanto il prefisso che contiene i tre minimi.", '''vector<int> values{9,2,7,1,5};partial_sort(values.begin(),values.begin()+3,values.end());
for(int i=0;i<3;i++)cout<<values[i]<<' ';''', "1 2 5", "partial_sort topk prefix")
    add("Partizionare elementi per predicato", "Raggruppa valori pari e dispari e individua il confine tra i gruppi.", '''vector<int> values{1,2,3,4,5};auto boundary=partition(values.begin(),values.end(),[](int n){return n%2==0;});
cout<<distance(values.begin(),boundary)<<'\\n';''', "2 elementi nel primo gruppo; l'ordine interno non è garantito.", "partition predicate boundary")
    add("Trasformare una sequenza con transform", "Scrive quadrati in un contenitore distinto di dimensione adeguata.", '''vector<int> input{2,3,4},output(input.size());transform(input.begin(),input.end(),output.begin(),[](int n){return n*n;});
for(int value:output)cout<<value<<' ';''', "4 9 16", "transform map vector")
    add("Copiare soltanto elementi selezionati", "Usa back_inserter per non scrivere oltre la capacità logica del destinatario.", '''vector<int> values{1,2,3,4},even;copy_if(values.begin(),values.end(),back_inserter(even),[](int n){return n%2==0;});
for(int value:even)cout<<value<<' ';''', "2 4", "copy_if filter back_inserter")
    add("Sommare valori con accumulate", "Dichiara un accumulatore long long per non usare implicitamente un int.", '''vector<int> values{1000000,2000000,3000000};cout<<accumulate(values.begin(),values.end(),0LL)<<'\\n';''', "6000000", "accumulate sum numeric")
    add("Calcolare un prodotto scalare", "Combina due sequenze della stessa lunghezza con inner_product.", '''vector<int> a{1,2,3},b{4,5,6};cout<<inner_product(a.begin(),a.end(),b.begin(),0)<<'\\n';''', "32; b deve contenere almeno quanti elementi vengono letti da a.", "inner_product dot vector")
    add("Eliminare duplicati adiacenti", "Combina unique con erase per ridurre realmente la lunghezza del vector.", '''vector<int> values{1,1,2,2,3};values.erase(unique(values.begin(),values.end()),values.end());
for(int value:values)cout<<value<<' ';''', "1 2 3; per duplicati non adiacenti ordinare prima se l'ordine può cambiare.", "unique erase deduplicate")
    add("Eliminare valori con erase_if", "Rimuove dal vector gli elementi che soddisfano un predicato in C++20.", '''vector<int> values{1,2,3,4};erase_if(values,[](int n){return n%2==0;});for(int n:values)cout<<n<<' ';''', "1 3", "erase_if vector remove")
    add("Cercare in una sequenza ordinata", "Usa binary_search soltanto dopo aver soddisfatto l'invariante di ordinamento.", '''vector<int> values{2,5,8};cout<<boolalpha<<binary_search(values.begin(),values.end(),5)<<'\\n';''', "true", "binary_search sorted lookup")
    add("Trovare il punto di inserimento con lower_bound", "Ottiene il primo elemento non minore della chiave senza scorrere linearmente.", '''vector<int> values{10,20,40};auto found=lower_bound(values.begin(),values.end(),30);cout<<distance(values.begin(),found)<<'\\n';''', "2", "lower_bound insertion binary")
    add("Trovare il mediano con nth_element", "Posiziona l'elemento centrale senza ordinare completamente il contenitore.", '''vector<int> values{9,1,7,3,5};auto middle=values.begin()+values.size()/2;nth_element(values.begin(),middle,values.end());cout<<*middle<<'\\n';''', "5; l'ordine degli altri elementi resta non specificato.", "nth_element median selection")
    add("Trovare minimo e massimo in un passaggio", "Gestisce una sequenza non vuota con minmax_element.", '''vector<int> values{4,9,1,7};auto [small,large]=minmax_element(values.begin(),values.end());cout<<*small<<' '<<*large<<'\\n';''', "1 9; per una sequenza vuota verificare prima gli iteratori.", "minmax_element extrema")
    add("Invertire una sequenza", "Scambia l'ordine degli elementi sul contenitore esistente.", '''vector<int> values{1,2,3};reverse(values.begin(),values.end());for(int n:values)cout<<n<<' ';''', "3 2 1", "reverse sequence algorithm")
    add("Ruotare una sequenza a sinistra", "Sposta un prefisso in coda senza creare una seconda sequenza.", '''vector<int> values{1,2,3,4};rotate(values.begin(),values.begin()+1,values.end());for(int n:values)cout<<n<<' ';''', "2 3 4 1", "rotate sequence prefix")
    add("Mescolare con un motore casuale esplicito", "Passa il motore a shuffle per isolare la sorgente della casualità.", '''vector<int> values{1,2,3,4,5};mt19937 engine(42);shuffle(values.begin(),values.end(),engine);sort(values.begin(),values.end());cout<<boolalpha<<(values==vector<int>{1,2,3,4,5})<<'\\n';''', "true: shuffle conserva tutti gli elementi, l'ordine prima del sort dipende dalla libreria.", "shuffle random permutation")
    add("Fondere due sequenze ordinate", "Usa merge mantenendo tutte le occorrenze, inclusi eventuali duplicati.", '''vector<int> a{1,3},b{2,4},out;merge(a.begin(),a.end(),b.begin(),b.end(),back_inserter(out));for(int n:out)cout<<n<<' ';''', "1 2 3 4", "merge sorted sequence")
    add("Calcolare differenza tra insiemi ordinati", "Applica set_difference a input ordinati e confrontabili nello stesso modo.", '''vector<int> a{1,2,3},b{2,4},out;set_difference(a.begin(),a.end(),b.begin(),b.end(),back_inserter(out));for(int n:out)cout<<n<<' ';''', "1 3", "set_difference sorted algorithm")
    add("Calcolare somme progressive", "Produce prefissi cumulativi con partial_sum.", '''vector<int> values{2,3,5},prefix(values.size());partial_sum(values.begin(),values.end(),prefix.begin());for(int n:prefix)cout<<n<<' ';''', "2 5 10", "partial_sum prefix scan")
    # Maps and sets: 8.
    add("Contare frequenze con unordered_map", "Incrementa un conteggio per parola senza una scansione di chiavi manuale.", '''unordered_map<string,int> counts;for(const string word:{"rosso","blu","rosso"})++counts[word];cout<<counts.at("rosso")<<'\\n';''', "2; l'ordine di iterazione di unordered_map non è definito.", "unordered_map frequency count")
    add("Leggere map senza inserire una chiave assente", "Usa find al posto di operator[] quando la lettura non deve modificare il contenitore.", '''map<string,int> values{{"A",3}};auto found=values.find("B");cout<<boolalpha<<(found==values.end())<<' '<<values.size()<<'\\n';''', "true 1", "map find lookup noinsert")
    add("Inserire soltanto se la chiave non esiste", "Usa try_emplace per preservare il valore già associato.", '''map<string,int> values;values.try_emplace("A",3);auto [entry,inserted]=values.try_emplace("A",9);cout<<entry->second<<' '<<boolalpha<<inserted<<'\\n';''', "3 false", "try_emplace map insertion")
    add("Aggiornare o inserire con insert_or_assign", "Esplicita la semantica upsert su una mappa.", '''map<string,int> values{{"A",3}};values.insert_or_assign("A",9);cout<<values.at("A")<<'\\n';''', "9", "insert_or_assign map upsert")
    add("Iterare una map con structured binding", "Legge chiavi e valori per riferimento senza copiare ogni coppia.", '''map<string,int> values{{"B",2},{"A",1}};for(const auto& [key,value]:values)cout<<key<<':'<<value<<' ';''', "A:1 B:2 perché map ordina le chiavi.", "map structured binding iteration")
    add("Deduplicare mantenendo l'ordine con un set ausiliario", "Usa il set soltanto per l'appartenenza e conserva un vector per l'ordine.", '''unordered_set<int> seen;vector<int> result;for(int value:{3,1,3,2})if(seen.insert(value).second)result.push_back(value);for(int n:result)cout<<n<<' ';''', "3 1 2", "unordered_set deduplicate stable")
    add("Estrarre elementi da un multiset", "Rimuove una sola occorrenza usando un iteratore anziché la cancellazione per chiave.", '''multiset<int> values{1,1,2};auto found=values.find(1);if(found!=values.end())values.erase(found);cout<<values.count(1)<<'\\n';''', "1", "multiset erase duplicate count")
    add("Interrogare un intervallo di chiavi ordinate", "Usa lower_bound e upper_bound per leggere valori compresi tra due limiti.", '''map<int,string> values{{10,"a"},{20,"b"},{30,"c"}};for(auto it=values.lower_bound(15);it!=values.upper_bound(30);++it)cout<<it->second<<' ';''', "b c", "map range lower_bound upper_bound")
    # Ownership and types: 12.
    add("Gestire proprietà esclusiva con unique_ptr", "Trasferisce un oggetto senza duplicarne la proprietà.", '''auto first=make_unique<string>("Ada");auto second=move(first);cout<<boolalpha<<(first==nullptr)<<' '<<*second<<'\\n';''', "true Ada", "unique_ptr move ownership")
    add("Condividere una risorsa con shared_ptr", "Dimostra conteggio dei proprietari senza ricorrere a delete manuale.", '''auto first=make_shared<int>(7);{auto second=first;cout<<first.use_count()<<' ';}cout<<first.use_count()<<'\\n';''', "2 1; evitare di usare use_count per decisioni concorrenti.", "shared_ptr reference counting")
    add("Osservare una risorsa con weak_ptr", "Controlla la durata di un oggetto senza mantenerlo in vita.", '''weak_ptr<int> observer;{auto owner=make_shared<int>(7);observer=owner;if(auto value=observer.lock())cout<<*value<<' ';}cout<<boolalpha<<observer.expired()<<'\\n';''', "7 true", "weak_ptr lifetime cycles")
    add("Restituire assenza con optional", "Rende esplicito che una ricerca potrebbe non produrre un valore.", '''auto find=[](int id)->optional<string>{if(id==7)return "Ada";return nullopt;};cout<<find(9).value_or("assente")<<'\\n';''', "assente", "optional nullopt result")
    add("Visitare una variant con std::visit", "Esegue un comportamento valido per ogni alternativa tipizzata.", '''variant<int,string> value=string("Ada");visit([](const auto& item){cout<<item<<'\\n';},value);''', "Ada", "variant visit sumtype")
    add("Accedere a una sequenza con span", "Passa una vista contigua a una funzione senza copiare il vector.", '''vector<int> values{2,3,5};span<const int> view(values);cout<<accumulate(view.begin(),view.end(),0)<<'\\n';''', "10; la vista non deve sopravvivere al vector.", "span view lifetime")
    add("Definire uguaglianza di un record C++20", "Lascia al compilatore il confronto strutturale dei membri.", '''cout<<boolalpha<<(Point{2,3}==Point{2,3})<<'\\n';''', "true", "default equality struct", "struct Point{int x;int y;bool operator==(const Point&)const=default;};")
    add("Validare un costruttore mantenendo un'invariante", "Impedisce la creazione di un oggetto con quantità negativa.", '''Stock item(7);cout<<item.quantity()<<'\\n';''', "7; quantità negative generano invalid_argument.", "constructor invariant class", "class Stock{int value;public:explicit Stock(int quantity):value(quantity){if(quantity<0)throw invalid_argument(\"quantita negativa\");}int quantity()const{return value;}};")
    add("Usare polimorfismo con distruttore virtuale", "Distrugge correttamente un oggetto derivato attraverso un puntatore alla base.", '''unique_ptr<Shape> shape=make_unique<Square>(4);cout<<shape->area()<<'\\n';''', "16", "virtual destructor polymorphism", "struct Shape{virtual ~Shape()=default;virtual double area()const=0;};struct Square:Shape{double side;explicit Square(double value):side(value){}double area()const override{return side*side;}};")
    add("Vincolare template con un concept", "Limita un algoritmo a tipi integrali e comunica il requisito al compilatore.", '''cout<<twice(21)<<'\\n';''', "42; twice con una stringa non soddisfa il concept.", "concept template integral", "template<class T> requires is_integral_v<T> T twice(T value){return value+value;}")
    add("Calcolare una costante con constexpr", "Verifica un risultato in fase di compilazione con static_assert.", '''static_assert(square(4)==16);cout<<square(5)<<'\\n';''', "25; la prima verifica avviene durante la compilazione.", "constexpr static_assert compiletime", "constexpr int square(int value){return value*value;}")
    add("Rendere una classe non copiabile", "Usa proprietà esclusiva per esprimere un oggetto trasferibile ma non duplicabile.", '''Session session;Session moved=move(session);cout<<*moved.value<<'\\n';''', "7; il membro unique_ptr disabilita implicitamente la copia.", "moveonly noncopyable ownership", "struct Session{unique_ptr<int> value=make_unique<int>(7);};")
    # I/O: 6.
    add("Scrivere e rileggere un file temporaneo C++", "Usa un nome temporaneo isolato e chiude i flussi prima della rimozione.", '''auto root=filesystem::temp_directory_path()/("cpp-demo-"+to_string(chrono::steady_clock::now().time_since_epoch().count()));filesystem::create_directory(root);auto path=root/"note.txt";
{ofstream out(path);out<<"esempio";if(!out)throw runtime_error("scrittura fallita");}
{ifstream in(path);string value;getline(in,value);cout<<value<<'\\n';}
filesystem::remove_all(root);''', "esempio; la directory temporanea viene eliminata nel percorso di successo.", "fstream filesystem temporary")
    add("Leggere righe da uno stream", "Consuma tutte le righe incluso un ultimo record senza newline finale.", '''istringstream input("uno\\ndue");string line;while(getline(input,line))cout<<'['<<line<<"]\\n";''', "[uno] e [due].", "getline stream lines")
    add("Serializzare un record con std::quoted", "Protegge spazi e virgolette in un formato testuale semplice dichiarato.", '''ostringstream output;output<<7<<' '<<quoted("Ada Rossi");istringstream input(output.str());int id;string name;input>>id>>quoted(name);cout<<id<<':'<<name<<'\\n';''', "7:Ada Rossi; questo formato non è CSV o JSON.", "quoted serialization string")
    add("Leggere byte da un flusso binario", "Usa read e gcount per conoscere i byte realmente ottenuti.", '''istringstream input(string("abc"),ios::in|ios::binary);array<char,8> buffer{};input.read(buffer.data(),buffer.size());cout<<input.gcount()<<' '<<string(buffer.data(),static_cast<size_t>(input.gcount()))<<'\\n';''', "3 abc", "binary read gcount stream")
    add("Comporre percorsi portabili", "Usa filesystem::path invece di concatenare separatori dipendenti dal sistema.", '''filesystem::path path=filesystem::path("reports")/"2026"/"output.csv";cout<<path.filename().string()<<' '<<path.extension().string()<<'\\n';''', "output.csv .csv", "filesystem path extension")
    add("Gestire errori filesystem senza eccezioni", "Passa error_code quando si vuole distinguere fallimento operativo e percorso assente.", '''error_code error;auto type=filesystem::status(filesystem::path("nonexistent-catalog-demo"),error);cout<<boolalpha<<filesystem::exists(type)<<'\\n';''', "false se il percorso dimostrativo non esiste; error contiene un eventuale codice operativo.", "filesystem error_code diagnostics")
    # Concurrency: 6.
    add("Attendere un thread con jthread", "Gestisce il join automaticamente al termine del blocco.", '''{jthread worker([]{cout<<"lavoro concluso\\n";});}''', "lavoro concluso prima dell'uscita dal blocco.", "jthread raii concurrency")
    add("Proteggere un contatore con mutex", "Evita data race su uno stato condiviso fra thread.", '''mutex gate;int count=0;auto work=[&]{for(int i=0;i<1000;i++){lock_guard<mutex> lock(gate);++count;}};
{jthread first(work),second(work);}cout<<count<<'\\n';''', "2000", "mutex lock_guard data race")
    add("Incrementare un contatore atomico", "Usa fetch_add quando l'unico stato da sincronizzare è il contatore.", '''atomic<int> count{0};auto work=[&]{for(int i=0;i<1000;i++)count.fetch_add(1,memory_order_relaxed);};
{jthread first(work),second(work);}cout<<count.load()<<'\\n';''', "2000; relaxed non pubblica altri dati associati.", "atomic fetch_add relaxed")
    add("Restituire un risultato da async", "Lancia lavoro con policy esplicita e legge il risultato tramite future.", '''auto future=async(launch::async,[]{return 6*7;});cout<<future.get()<<'\\n';''', "42; get propaga un'eventuale eccezione del task.", "async future launch")
    add("Passare un risultato con promise e future", "Separa il produttore del valore dal consumatore che ne attende la disponibilità.", '''promise<int> result;auto future=result.get_future();jthread worker([&]{result.set_value(42);});cout<<future.get()<<'\\n';''', "42", "promise future producer consumer")
    add("Attendere una condizione con predicato", "Evita wake-up spurii tramite un predicato protetto dal medesimo mutex.", '''mutex gate;condition_variable cv;bool ready=false;
jthread producer([&]{{lock_guard<mutex> lock(gate);ready=true;}cv.notify_one();});
unique_lock<mutex> lock(gate);cv.wait(lock,[&]{return ready;});cout<<"pronto\\n";''', "pronto senza dipendere dall'ordine di scheduling.", "condition_variable predicate wait")
    # Diagnostics and language contracts: 7.
    add("Gestire un'eccezione per riferimento costante", "Conserva il tipo dinamico dell'errore e ne legge il messaggio.", '''try{throw invalid_argument("dato non valido");}catch(const exception& error){cout<<error.what()<<'\\n';}''', "dato non valido", "exception catch reference")
    add("Controllare indici con vector::at", "Trasforma un accesso fuori limite in out_of_range invece di comportamento indefinito.", '''vector<int> values{1,2};try{cout<<values.at(5);}catch(const out_of_range&){cout<<"indice non valido\\n";}''', "indice non valido", "vector at bounds debug")
    add("Verificare un contratto anche senza assert", "Mantiene attivo il controllo nelle build con NDEBUG.", '''auto require=[](bool ok){if(!ok)throw logic_error("contratto violato");};require(2+2==4);cout<<"contratto verificato\\n";''', "contratto verificato", "invariant testing release")
    add("Misurare durata con steady_clock", "Usa un clock monotono per una misura di tempo trascorso.", '''auto start=chrono::steady_clock::now();long long total=0;for(int i=0;i<10000;i++)total+=i;auto elapsed=chrono::steady_clock::now()-start;cout<<total<<' '<<chrono::duration_cast<chrono::nanoseconds>(elapsed).count()<<"ns\\n";''', "49995000 e durata variabile; un benchmark attendibile richiede controllo delle ottimizzazioni.", "chrono steady_clock benchmark")
    add("Distinguere dimensione e capacità di vector", "Riserva memoria senza creare elementi, poi aggiunge un valore.", '''vector<int> values;values.reserve(100);cout<<values.size()<<' '<<(values.capacity()>=100)<<'\\n';values.push_back(7);cout<<values.size()<<'\\n';''', "0 1 poi 1; reserve non autorizza l'accesso a indici non costruiti.", "vector capacity reserve size")
    add("Evitare invalidazione degli iteratori durante erase", "Usa l'iteratore restituito da erase per continuare una scansione valida.", '''list<int> values{1,2,3,4};for(auto it=values.begin();it!=values.end();){if(*it%2==0)it=values.erase(it);else ++it;}for(int n:values)cout<<n<<' ';''', "1 3", "iterator invalidation erase list")
    add("Comporre una pipeline lazy con ranges", "Filtra e trasforma senza creare contenitori intermedi.", '''vector<int> values{1,2,3,4};auto view=values|views::filter([](int n){return n%2==0;})|views::transform([](int n){return n*n;});for(int n:view)cout<<n<<' ';''', "4 16; view dipende dalla durata di values.", "ranges views lazy pipeline")
    program(b, "Progetto completo registro contatti C++", "Separa modello, ricerca, presentazione e test in un progetto C++20 senza dipendenze esterne.", '''#include "contacts.hpp"
#include <iostream>
int main(){Contacts contacts;contacts.add("Ada","ada@example.test");std::cout<<contacts.find("Ada").value_or("assente")<<'\\n';}''', filename="main.cpp", files={
      "contacts.hpp": '''#pragma once
#include <map>
#include <optional>
#include <string>
class Contacts{std::map<std::string,std::string> entries;public:void add(const std::string& name,const std::string& email);std::optional<std::string> find(const std::string& name)const;};''',
      "contacts.cpp": '''#include "contacts.hpp"
#include <stdexcept>
void Contacts::add(const std::string& name,const std::string& email){if(name.empty()||email.find('@')==std::string::npos)throw std::invalid_argument("Contatto non valido");entries.insert_or_assign(name,email);}
std::optional<std::string> Contacts::find(const std::string& name)const{auto it=entries.find(name);if(it==entries.end())return std::nullopt;return it->second;}''',
      "test.cpp": '''#include "contacts.hpp"
#include <stdexcept>
#include <iostream>
int main(){Contacts contacts;contacts.add("Ada","ada@example.test");if(contacts.find("Ada")!="ada@example.test")throw std::logic_error("Ricerca errata");if(contacts.find("assente"))throw std::logic_error("Assenza errata");try{contacts.add("","a");return 1;}catch(const std::invalid_argument&){}std::cout<<"3 contratti verificati\\n";}''',
      "CMakeLists.txt": '''cmake_minimum_required(VERSION 3.20)
project({{project_name}} LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_library(contacts contacts.cpp)
target_include_directories(contacts PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
add_executable(demo main.cpp)
target_link_libraries(demo PRIVATE contacts)
add_executable(contacts_test test.cpp)
target_link_libraries(contacts_test PRIVATE contacts)
enable_testing()
add_test(NAME contacts_contract COMMAND contacts_test)''',
      "README.md": "# Registro contatti C++\n\nC++20. Con GCC: compilare main.cpp e contacts.cpp per l'app, test.cpp e contacts.cpp per il test. In alternativa usare CMake 3.20+: `cmake -S . -B build`, `cmake --build build`, `ctest --test-dir build -C Debug`. Il registro è in memoria, ricerca per nome esatto e sostituisce il contatto quando il nome esiste. La validazione email è deliberatamente minima. Non compilare main.cpp e test.cpp nello stesso eseguibile perché entrambi definiscono main.\n"}, command="g++ -std=c++20 main.cpp contacts.cpp -o demo.exe\ng++ -std=c++20 test.cpp contacts.cpp -o tests.exe\n.\\tests.exe\n.\\demo.exe", expected="Test: 3 contratti verificati; demo: ada@example.test.", tags=("project","header","library","test","cmake","optional"), project=True, section="Progetti completi", parameters=[{"name":"project_name","label":"Nome progetto CMake","type":"identifier","default":"Contacts","required":True}])
    require_count(b,80)


if __name__=="__main__":
    build_all()
