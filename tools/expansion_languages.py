"""110 original Kotlin, Swift, PHP and Dart recipes; never rewrites older stacks."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from textwrap import dedent
from catalog_support import Book,ROOT,slug
from expansion_language_errors import frequent_errors

SOURCES={
 "kotlin":["https://kotlinlang.org/docs/command-line.html","https://kotlinlang.org/docs/collections-overview.html","https://kotlinlang.org/docs/gradle-configure-project.html"],
 "swift":["https://www.swift.org/documentation/","https://www.swift.org/install/linux/","https://www.swift.org/install/macos/","https://www.swift.org/blog/swift-6.4-released/"],
 "php":["https://www.php.net/manual/en/","https://www.php.net/supported-versions.php"],
 "dart":["https://dart.dev/language","https://dart.dev/resources/whats-new","https://dart.dev/tools/dart-compile"],
}
VERSIONS={"kotlin":"Kotlin2.3.21/JVM17; Gradle9.3.0 per i progetti Gradle", "swift":"Swift6.4; Package.swift tools-version6.0, Linux/macOS", "php":"PHP8.4/8.5 CLI, strict_types; estensioni indicate nella singola scheda", "dart":"Dart3.13.x; librerie SDK, nessuna dipendenza Pub esterna"}
PREREQUISITES={
 "kotlin":"JDK17+ e compilatore Kotlin2.3.21. Per Gradle usare9.3.0 e plugin Kotlin2.3.21 (prima acquisizione plugin richiede rete/cache). Le varianti Android richiedono un progetto Android già configurato e relativo SDK.",
 "swift":"Toolchain Swift6.4 su Linux o macOS. Per SwiftUI/iOS occorrono macOS, Xcode e un target Apple. Non sono attestati esecuzioni o compilazioni Swift su Windows.",
 "php":"PHP8.4 o8.5 CLI nel PATH. PDO SQLite richiede pdo_sqlite; le altre estensioni necessarie sono indicate. Il server incorporato è destinato al laboratorio locale.",
 "dart":"Dart SDK3.13.x nel PATH. Gli esempi dart:io sono nativi; per riusarli su web occorre sostituire accesso filesystem/isolate dove non supportato. Nessun package esterno necessario ai capstone.",
}


def text(value):return dedent(value).strip()+"\n"
def js(value):return json.dumps(value,ensure_ascii=False,indent=2)
def commands(code,os="Windows",shell="PowerShell"):
    return [{"shell":shell,"os":os,"cwd":".","code":code}]


class Author:
    def __init__(self,stack):
        self.stack=stack
        self.book=Book(stack,VERSIONS[stack],SOURCES[stack],PREREQUISITES[stack],os=["Linux","macOS"] if stack=="swift" else ["Windows","Linux","macOS"],ide=["Xcode","VS Code"] if stack=="swift" else ["IntelliJ IDEA","Android Studio"] if stack=="kotlin" else ["VS Code"])
    def add(self,title,summary,files,command,expected,*,section="Codice applicativo",tags=(),guide="",errors="",project=False,os=None,roles=None,sources=()):
        explanation=f"## Risultato\n\n{summary}\n\n## Procedura\n\n{guide or 'Esporta tutti i file nella stessa cartella conservando i percorsi. Apri un terminale nella radice esportata ed esegui i comandi della scheda. Il sorgente contiene dati sintetici e un punto di ingresso completo.'}\n\n## Risultato atteso e contratto\n\n{expected}\n\n## Diagnostica\n\n{errors or 'Controlla la versione della toolchain e la directory di lavoro. Non ignorare gli errori di tipo o i valori di ritorno delle operazioni fallibili.'}\n\nLa consultazione e l’esportazione sono offline; il primo download di SDK o strumenti può richiedere rete. La sezione Verifica riporta soltanto prove registrate; parsing sintattico non equivale a compilazione, collegamento o esecuzione.\n"
        error_list=([errors] if errors else [])+frequent_errors(self.stack,title,section,project)
        recipe=self.book.add(slug(title),title,summary,{path:text(content) for path,content in files.items()},commands=command if isinstance(command,list) else commands(command),section=section,explanation=explanation,expected=expected,tags=list(tags),errors=list(dict.fromkeys(error_list))[:3],project=project,os=os,file_roles=roles,sources=SOURCES[self.stack]+list(sources))
        evidence=ROOT/"tools"/"expansion_languages_verification.json"
        if evidence.exists():
            entry=json.loads(evidence.read_text(encoding="utf-8")).get(recipe["id"])
            actual={a["path"]:hashlib.sha256(a["content"].encode()).hexdigest() for a in recipe["assets"] if a["role"]!="command"}
            if entry and entry["assets"]==actual:recipe["verification"]=entry["verification"]
        return recipe
    def kotlin(self,title,summary,body,expected,tags=(),imports="",definitions=""):
        return self.add(title,summary,{"Main.kt":imports+"\n"+definitions+"\nfun main() {\n"+body+"\n}"},"kotlinc Main.kt -jvm-target 17 -include-runtime -d example.jar\njava -jar example.jar",expected,tags=tags)
    def swift(self,title,summary,body,expected,tags=(),definitions=""):
        return self.add(title,summary,{"main.swift":"import Foundation\n"+definitions+"\n"+body},commands("swift main.swift","Linux/macOS","Bash"),expected,tags=tags)
    def php(self,title,summary,body,expected,tags=()):
        return self.add(title,summary,{"main.php":"<?php\ndeclare(strict_types=1);\n"+body},"php main.php",expected,tags=tags)
    def dart(self,title,summary,body,expected,tags=(),imports="",definitions=""):
        return self.add(title,summary,{"main.dart":imports+"\n"+definitions+"\nFuture<void> main() async {\n"+body+"\n}"},"dart run main.dart",expected,tags=tags)
    def save(self,count):
        assert len(self.book.recipes)==count,(self.stack,len(self.book.recipes))
        assert sum(r["project"] for r in self.book.recipes)==1
        for section in ("Inizializzazione","Compilazione","Debug","Test","Distribuzione"):
            assert any(r["section"]==section for r in self.book.recipes),(self.stack,section)
        self.book.save()


def kotlin_book():
    a=Author("kotlin")
    a.kotlin("Gestire null con safe call ed Elvis","Conserva l'assenza nel tipo e usa un valore alternativo soltanto quando serve.",'val nickname: String? = null\nprintln(nickname?.uppercase() ?: "Nome assente")',"Nome assente; nessun operatore !! necessario.",("nullable","elvis","safe call"))
    a.kotlin("Validare un input con when","Gestisce classi di input attraverso condizioni ordinate e un ramo residuale.",'val value = 82\nval grade = when { value >= 90 -> "A"; value >= 75 -> "B"; value >= 60 -> "C"; else -> "D" }\nprintln(grade)',"B; la prima condizione vera seleziona il risultato.",("when","validation"))
    a.kotlin("Copiare una data class mantenendo il valore originale","Deriva un nuovo record con copy e uguaglianza strutturale.",'val original = User("Ada", 36)\nval next = original.copy(age = 37)\nprintln("${original.age} ${next.age}")',"36 37; copy è superficiale per proprietà che sono riferimenti mutabili.",("data class","copy"),definitions="data class User(val name: String, val age: Int)")
    a.kotlin("Trasformare e filtrare una lista tipizzata","Ottiene i quadrati dei valori pari senza modificare la lista sorgente.",'val values = listOf(1, 2, 3, 4)\nprintln(values.filter { it % 2 == 0 }.map { it * it })',"[4, 16]",("collections","map","filter"))
    a.kotlin("Raggruppare record per categoria","Usa groupBy per associare ogni categoria ai rispettivi record.",'val groups = listOf(Item("A",2),Item("B",4),Item("A",3)).groupBy { it.category }\nprintln(groups.mapValues { (_,rows) -> rows.sumOf { it.amount } })',"A=5 e B=4.",("groupBy","sumOf"),definitions="data class Item(val category: String, val amount: Int)")
    a.kotlin("Deduplicare oggetti per una chiave","Mantiene il primo record per ID con distinctBy.",'val users = listOf(User(1,"prima"),User(1,"seconda"),User(2,"terza"))\nprintln(users.distinctBy { it.id }.map { it.name })',"[prima, terza]",("distinctBy","deduplicate"),definitions="data class User(val id: Int, val name: String)")
    a.kotlin("Ordinare con più comparatori","Ordina per cognome e risolve i pareggi con il nome.",'val rows = listOf(Person("Rossi","Luca"),Person("Rossi","Ada"))\nprintln(rows.sortedWith(compareBy<Person> { it.surname }.thenBy { it.name }))',"Ada precede Luca; la lista originale resta invariata.",("sorting","compareBy"),definitions="data class Person(val surname: String,val name: String)")
    a.kotlin("Ridurre una collezione con fold","Definisce un accumulatore iniziale valido anche per input vuoti.",'val product = listOf(2,3,4).fold(1) { total,value -> total * value }\nprintln(product)',"24; una lista vuota restituirebbe1.",("fold","aggregation"))
    a.kotlin("Elaborare una sequence lazy","Ferma la produzione dopo i primi tre risultati validi senza materializzare tutta la sequenza.",'val values = generateSequence(1) { it + 1 }.filter { it % 2 == 0 }.take(3).toList()\nprintln(values)',"[2, 4, 6]",("sequence","lazy","take"))
    a.kotlin("Estrarre campi con Regex e gruppi nominati","Valida l'intera stringa prima di leggere il numero di un identificativo.",'val pattern = Regex("""item-(?<id>\\d+)""")\nval match = pattern.matchEntire("item-123")\nprintln(match?.groups?.get("id")?.value)',"123; per testo non conforme il risultato è null.",("regex","named groups"))
    a.kotlin("Analizzare date civili con java.time","Interopera con LocalDate e un formatter esplicito senza dipendere dalla locale predefinita.",'val day = LocalDate.parse("29/10/2026", DateTimeFormatter.ofPattern("dd/MM/uuuu"))\nprintln(day.plusDays(7))',"2026-11-05",("date","java.time"),imports="import java.time.LocalDate\nimport java.time.format.DateTimeFormatter")
    a.kotlin("Leggere e scrivere UTF-8 in un file temporaneo","Chiude gli stream e rimuove il file nel finally per supportare anche Windows.",'val path = Files.createTempFile("kotlin-catalog-", ".txt")\ntry { Files.writeString(path,"Città",Charsets.UTF_8); println(Files.readString(path,Charsets.UTF_8)) } finally { Files.deleteIfExists(path) }',"Città; nessun file permanente viene lasciato dal percorso riuscito.",("file","utf8","cleanup"),imports="import java.nio.file.Files")
    a.kotlin("Rilasciare automaticamente una risorsa con use","Applica il contratto Closeable e garantisce la chiusura dello stream.",'ByteArrayInputStream("esempio".toByteArray()).use { stream -> println(stream.readBytes().toString(Charsets.UTF_8)) }',"esempio; use chiude lo stream anche in presenza di eccezioni.",("use","Closeable"),imports="import java.io.ByteArrayInputStream")
    a.kotlin("Modellare risultati con una gerarchia sealed","Rende espliciti successo ed errore e consente un when esaustivo.",'val result: Outcome = Outcome.Success(42)\nprintln(when(result) { is Outcome.Success -> result.value.toString(); is Outcome.Failure -> result.message })',"42; aggiungendo una variante occorre aggiornare il when.",("sealed","when","result"),definitions="sealed class Outcome {\n data class Success(val value:Int):Outcome()\n data class Failure(val message:String):Outcome()\n}")
    a.kotlin("Convertire eccezioni in Result con runCatching","Restituisce il fallimento come valore e sceglie un fallback esplicito.",'val result = runCatching { "non numero".toInt() }\nprintln(result.getOrElse { -1 })',"-1; isFailure consente di distinguere il fallback da un valore reale.",("Result","runCatching","exceptions"))
    a.kotlin("Aggiungere una extension function pura","Specializza una trasformazione senza cambiare la classe String.",'println("  ada  ".label())',"ADA; l'extension è risolta staticamente.",("extension","string"),definitions="fun String.label():String = trim().uppercase()")
    a.kotlin("Inizializzare un valore soltanto al primo accesso","Usa lazy per rinviare una costruzione e riutilizzarne il risultato.",'var calls = 0\nval config by lazy { calls++; "pronto" }\nprintln(calls); println(config); println(config); println(calls)',"0, pronto, pronto, 1; lazy di default sincronizza l'inizializzazione.",("lazy","delegation"))
    a.kotlin("Attendere un thread JVM e conservare il risultato","Protegge il punto di completamento con join senza introdurre una dipendenza coroutines.",'var result = 0\nval worker = Thread { result = 6 * 7 }\nworker.start(); worker.join()\nprintln(result)',"42; join stabilisce la visibilità del risultato dopo la terminazione.",("thread","JVM","join"))
    a.kotlin("Limitare lavori tramite un ExecutorService","Invia operazioni indipendenti a un pool e lo chiude nel finally.",'val pool = Executors.newFixedThreadPool(2)\ntry { val results = (1..4).map { value -> pool.submit<Int> { value * value } }; println(results.map { it.get() }) } finally { pool.shutdown() }',"[1, 4, 9, 16]; get propaga il fallimento di un task.",("executor","concurrency"),imports="import java.util.concurrent.Executors")
    a.kotlin("Esporre un endpoint HTTP locale con il JDK","Crea un server dimostrativo su loopback senza framework e senza dipendenze Maven.",'val server = HttpServer.create(InetSocketAddress("127.0.0.1",8085),0)\nserver.createContext("/health") { exchange -> val data = "ok".toByteArray(); exchange.sendResponseHeaders(200,data.size.toLong()); exchange.responseBody.use { it.write(data) } }\nserver.start(); println("http://127.0.0.1:8085/health - premi Invio per terminare")\ntry { readlnOrNull() } finally { server.stop(0) }',"GET /health risponde200 con ok; il processo resta attivo finché non premi Invio.",("backend","HTTP","HttpServer"),imports="import com.sun.net.httpserver.HttpServer\nimport java.net.InetSocketAddress")
    a.kotlin("Calcolare SHA-256 di un payload UTF-8","Usa MessageDigest del JDK e converte ogni byte in due cifre esadecimali.",'val digest = MessageDigest.getInstance("SHA-256").digest("abc".toByteArray(Charsets.UTF_8))\nprintln(digest.joinToString("") { "%02x".format(it.toInt() and 0xff) })',"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",("hash","sha256"),imports="import java.security.MessageDigest")
    a.add("Conservare un'opzione Android con SharedPreferences","Isola la persistenza di una preferenza in una classe completa per un target Android già configurato.",{"src/main/java/example/Preferences.kt":'package example\nimport android.content.Context\nclass Preferences(context:Context) {\n private val store=context.getSharedPreferences("catalog_demo",Context.MODE_PRIVATE)\n var showDetails:Boolean\n  get()=store.getBoolean("details",false)\n  set(value){store.edit().putBoolean("details",value).apply()}\n}'},".\\gradlew.bat assembleDebug","Il valore sopravvive alla ricreazione dell'Activity; apply salva in modo asincrono.",tags=("Android","SharedPreferences","persistence"),os=["Android"],roles={"src/main/java/example/Preferences.kt":"snippet"},guide="Inserisci Preferences.kt nel source set main di un progetto Android esistente, adattando package alla tua app. Da Activity usa Preferences(this).showDetails=true; per leggerlo crea la stessa classe con il medesimo context. La scheda non contiene un progetto Android completo né sostituisce AndroidManifest/Gradle del target.",sources=("https://developer.android.com/training/data-storage/shared-preferences",))
    a.add("Condividere testo da Android con un Intent","Apre il selettore di condivisione del sistema senza associare l'app a un servizio specifico.",{"src/main/java/example/Share.kt":'package example\nimport android.app.Activity\nimport android.content.Intent\nfun shareText(activity:Activity,text:String){\n val intent=Intent(Intent.ACTION_SEND).apply{type="text/plain";putExtra(Intent.EXTRA_TEXT,text)}\n activity.startActivity(Intent.createChooser(intent,"Condividi testo"))\n}'},".\\gradlew.bat assembleDebug","Il chooser Android offre le app che gestiscono text/plain.",tags=("Android","Intent","sharing"),os=["Android"],roles={"src/main/java/example/Share.kt":"snippet"},guide="Aggiungi Share.kt al source set main del progetto Android, con il package appropriato. Richiama shareText(this, testo) da una Activity attiva, per esempio nel callback di un pulsante; non eseguire il lancio da un contesto di background senza rispettarne le restrizioni.",sources=("https://developer.android.com/training/sharing/send",))
    a.kotlin("Consumare uno Stream Java da Kotlin","Interopera con lo Stream JVM e lo chiude con use quando possiede risorse.",'val total = Stream.of(2,3,5).use { stream -> stream.mapToInt { it }.sum() }\nprintln(total)',"10; per collezioni Kotlin normali è spesso più semplice usare le funzioni della standard library.",("interop","Java Stream","use"),imports="import java.util.stream.Stream")
    kotlin_workflows(a)
    kotlin_project(a)
    a.save(30)


def kotlin_workflows(a):
    a.add("Inizializzare una console Kotlin JVM","Controlla compilatore e JDK e genera un JAR con runtime Kotlin incorporato.",{"Main.kt":'fun main(args:Array<String>){println("Ciao ${args.firstOrNull() ?: "Ada"}")}'},"kotlinc -version\njava -version\nkotlinc Main.kt -jvm-target 17 -include-runtime -d starter.jar\njava -jar starter.jar Luca","Ciao Luca; il destinatario deve avere Java17+ anche se il runtime Kotlin è incluso.",section="Inizializzazione",tags=("setup","kotlinc","JVM"),guide="Installa il compilatore Kotlin2.3.21 e JDK17+. Non confondere Kotlin runtime con JVM: -include-runtime incorpora stdlib Kotlin, non Java. Su Linux/macOS i comandi sono identici. Per Android usa un progetto Android Studio con plugin Android e SDK, non questo JAR console.")
    a.add("Compilare Kotlin con un progetto Gradle bloccato","Configura plugin2.3.21, target JVM17 e punto d'ingresso riproducibile.",{"settings.gradle.kts":'rootProject.name = "kotlin-build"',"build.gradle.kts":'plugins { kotlin("jvm") version "2.3.21"; application }\nrepositories { mavenCentral() }\njava { sourceCompatibility=JavaVersion.VERSION_17;targetCompatibility=JavaVersion.VERSION_17 }\nkotlin { compilerOptions { jvmTarget.set(org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17) } }\napplication { mainClass.set("MainKt") }',"src/main/kotlin/Main.kt":'fun main(){println(listOf(2,3,5).sum())}'},"gradle --version\ngradle build\ngradle run","Build completa e programma che stampa10.",section="Compilazione",tags=("Gradle","build","jvmTarget"),guide="Usa Gradle9.3.0, compatibile con Kotlin Gradle Plugin2.3.21 secondo la matrice ufficiale. Il progetto non include un wrapper binario; usa Gradle installato oppure genera il wrapper con gradle wrapper --gradle-version9.3.0 dopo aver verificato la distribuzione. Il primo accesso al plugin/stdlib richiede Maven Central o cache. Le versioni plugin sono bloccate e JVM target Java/Kotlin coincide.")
    a.add("Debuggare Kotlin JVM con JDWP","Avvia un processo Java sospeso su loopback e collega IntelliJ IDEA o un debugger JVM.",{"Main.kt":'fun total(values:List<Int>):Int{val result=values.sum();return result}\nfun main(){println(total(listOf(2,3,5)))}'},"kotlinc Main.kt -jvm-target 17 -include-runtime -d debug.jar\njava -agentlib:jdwp=transport=dt_socket,server=y,suspend=y,address=127.0.0.1:5005 -jar debug.jar","Il processo attende il debugger; dopo continue stampa10.",section="Debug",tags=("JDWP","breakpoint","IntelliJ"),guide="Compila il JAR, apri Main.kt in IntelliJ e crea una configurazione Remote JVM Debug con host127.0.0.1 e porta5005. Imposta un breakpoint nella funzione total, avvia il comando e collega il debugger. Ispeziona values/result dopo l'assegnazione. suspend=y è intenzionale; chiudi il processo prima di riusare la porta.")
    a.add("Testare funzioni Kotlin senza framework esterni","Esegue contratti sempre attivi con check invece di assert dipendente dai flag JVM.",{"Math.kt":'fun area(width:Int,height:Int):Int {require(width>=0&&height>=0);return Math.multiplyExact(width,height)}',"Checks.kt":'fun main(){check(area(3,4)==12);check(runCatching{area(-1,2)}.isFailure);println("2 contratti verificati")}'},"kotlinc Math.kt Checks.kt -jvm-target 17 -include-runtime -d checks.jar\njava -jar checks.jar","2 contratti verificati; un fallimento genera un'eccezione e codice di uscita non zero.",section="Test",tags=("check","testing","contracts"))
    a.add("Distribuire una console Kotlin con installDist","Produce script di avvio e librerie runtime senza pubblicare su repository esterni.",{"settings.gradle.kts":'rootProject.name="kotlin-dist"',"build.gradle.kts":'plugins { kotlin("jvm") version "2.3.21"; application }\nrepositories { mavenCentral() }\njava { sourceCompatibility=JavaVersion.VERSION_17;targetCompatibility=JavaVersion.VERSION_17 }\nkotlin { compilerOptions { jvmTarget.set(org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17) } }\napplication { mainClass.set("MainKt") }',"src/main/kotlin/Main.kt":'fun main(){println("Distribuzione pronta")}'},"gradle installDist\n.\\build\\install\\kotlin-dist\\bin\\kotlin-dist.bat","La cartella build/install/kotlin-dist contiene bin/lib e stampa Distribuzione pronta.",section="Distribuzione",tags=("installDist","application","JAR"),guide="Usa Gradle9.3.0 e JDK compatibile. Consegna l'intera cartella installata, non soltanto lo script .bat. Il destinatario deve avere una JVM17+; su Linux/macOS usa lo script senza .bat. installDist non crea un APK e non incorpora una JVM. Non eseguire publish per una consegna locale.")


def kotlin_project(a):
    a.add("Progetto completo inventario Kotlin JVM","Separa dominio, CLI e test; somma quantità con validazione e impedisce overflow.",{
      "settings.gradle.kts":'rootProject.name="kotlin-inventory"',
      "build.gradle.kts":'''plugins { kotlin("jvm") version "2.3.21"; application }
repositories { mavenCentral() }
java { sourceCompatibility=JavaVersion.VERSION_17;targetCompatibility=JavaVersion.VERSION_17 }
kotlin { compilerOptions { jvmTarget.set(org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17) } }
application { mainClass.set("InventoryCliKt") }
tasks.register<JavaExec>("smoke") { dependsOn("testClasses");classpath=sourceSets["test"].runtimeClasspath;mainClass.set("InventoryTestKt") }''',
      "src/main/kotlin/Inventory.kt":'''class Inventory {
 private val quantities=linkedMapOf<String,Int>()
 fun add(name:String,quantity:Int){val key=name.trim();require(key.isNotEmpty()&&quantity>0){"Nome e quantita positiva richiesti"};quantities[key]=Math.addExact(quantities[key]?:0,quantity)}
 fun quantity(name:String):Int=quantities[name]?:0
 fun snapshot():Map<String,Int> = quantities.toMap()
}''',
      "src/main/kotlin/InventoryCli.kt":'''fun main(){
 val inventory=Inventory()
 listOf("viti" to 3,"dadi" to 2,"viti" to 4).forEach{(name,quantity)->inventory.add(name,quantity)}
 inventory.snapshot().forEach{(name,quantity)->println("$name: $quantity")}
}''',
      "src/test/kotlin/InventoryTest.kt":'''fun main(){val inventory=Inventory();inventory.add("viti",3);inventory.add("viti",4);check(inventory.quantity("viti")==7);check(runCatching{inventory.add("",0)}.isFailure);val snapshot=inventory.snapshot();inventory.add("viti",1);check(snapshot["viti"]==7);println("3 contratti verificati")}''',
      "README.md":"# Inventario Kotlin\n\nKotlin/JVM2.3.21, Gradle9.3.0, JDK17+. Nessuna dipendenza applicativa esterna; stdlib segue la versione del plugin. `gradle smoke`, `gradle run`, `gradle installDist`. Per compilazione CLI: `kotlinc src/main/kotlin/Inventory.kt src/main/kotlin/InventoryCli.kt -jvm-target 17 -include-runtime -d inventory.jar` e `java -jar inventory.jar`. Per test CLI includi Inventory.kt e src/test/kotlin/InventoryTest.kt, poi avvia il JAR. Stato in memoria e dati sintetici: viti7,dadi2. snapshot restituisce una copia; non è un repository concorrente. Il primo restore Gradle richiede rete/cache. La distribuzione richiede JVM17+ e non produce un'app Android.\n"},"gradle smoke\ngradle run\ngradle installDist","Tre contratti verificati; CLI: viti7 e dadi2.",project=True,section="Inizializzazione",tags=("project","inventory","Gradle","testing","JVM"))


def swift_book():
    a=Author("swift")
    a.swift("Gestire assenza con Optional e nil coalescing","Legge un valore opzionale senza forzare l'unwrapping.",'let nickname: String? = nil\nprint(nickname?.uppercased() ?? "Nome assente")',"Nome assente; nessuna eccezione da force unwrap.",("optional","nil","coalescing"))
    a.swift("Validare un valore con guard","Uscire anticipatamente mantiene il percorso valido libero da annidamenti.",'print(positive("12") ?? -1)',"12; input non intero o non positivo restituisce nil.",("guard","validation"),definitions='func positive(_ text:String)->Int?{guard let value=Int(text),value>0 else{return nil};return value}')
    a.swift("Modellare eventi con enum associati","Mantiene il payload legato alla variante corretta e gestisce tutti i casi.",'let event=Event.moved(x:2,y:3)\nswitch event {case .moved(let x,let y):print(x,y);case .closed:print("chiusa")}',"2 3",("enum","associated values","switch"),definitions="enum Event {case moved(x:Int,y:Int);case closed}")
    a.swift("Codificare e decodificare JSON con Codable","Deriva un contratto dati tipizzato e verifica la presenza dei campi durante la decodifica.",'let item=Item(name:"libro",cents:1250)\nlet data=try JSONEncoder().encode(item)\nlet decoded=try JSONDecoder().decode(Item.self,from:data)\nprint(decoded.name,decoded.cents)',"libro1250; il decoder segnala tipi/campi mancanti anziché presumere la validità.",("Codable","JSONEncoder","JSONDecoder"),definitions="struct Item:Codable {let name:String;let cents:Int}")
    a.swift("Scartare conversioni fallite con compactMap","Trasforma stringhe in numeri mantenendo soltanto le conversioni valide.",'let values=["2","abc","5"].compactMap(Int.init)\nprint(values)',"[2, 5]",("compactMap","optional","collection"))
    a.swift("Raggruppare elementi con Dictionary grouping","Associa record a chiavi e calcola totali senza perdere i gruppi.",'let rows=[("A",2),("B",4),("A",3)]\nlet grouped=Dictionary(grouping:rows,by:{$0.0})\nprint(grouped.mapValues{$0.reduce(0){$0+$1.1}})',"A=5 e B=4; l'ordine di stampa del dizionario non è garantito.",("Dictionary","grouping","reduce"))
    a.swift("Ordinare record con chiavi multiple","Usa una tupla di stringhe come criterio lessicografico senza alterare la sorgente.",'let rows=[("Rossi","Luca"),("Rossi","Ada")]\nprint(rows.sorted{($0.0,$0.1)<($1.0,$1.1)}.map{$0.1})',"[Ada, Luca]",("sorted","tuple","comparison"))
    a.swift("Calcolare differenze tra Set","Distingue elementi aggiunti e rimossi fra due snapshot.",'let before:Set<String>=["a","b"],after:Set<String>=["b","c"]\nprint(after.subtracting(before).sorted())\nprint(before.subtracting(after).sorted())',"Aggiunto c, rimosso a.",("Set","subtracting","difference"))
    a.swift("Contare grafemi e byte Unicode","Distingue caratteri percepiti e byte della rappresentazione UTF-8.",'let value="👩🏽‍💻"\nprint(value.count,value.utf8.count)',"1 grafema esteso e15byte UTF-8.",("Unicode","grapheme","utf8"))
    a.swift("Analizzare un istante ISO8601 UTC","Converte testo standard in Date e ne stampa una rappresentazione indipendente dalla locale.",'let formatter=ISO8601DateFormatter()\nif let date=formatter.date(from:"2026-10-29T10:00:00Z"){print(formatter.string(from:date))}',"2026-10-29T10:00:00Z",("ISO8601DateFormatter","Date","UTC"))
    a.swift("Costruire URL con query percent encoded","Conserva il significato dei più anche per parser server che interpretano il query string come form-urlencoded.",'var parts=URLComponents(string:"https://example.test/search")!\nlet unreserved=CharacterSet(charactersIn:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~")\nlet value="C++ e Swift".addingPercentEncoding(withAllowedCharacters:unreserved)!\nparts.percentEncodedQuery="q="+value\nprint(parts.url!.absoluteString)',"Il valore contiene C%2B%2B%20e%20Swift; plus e spazi non sono ambigui per un parser form-urlencoded.",("URLComponents","percentEncodedQuery","percent encoding"))
    a.swift("Leggere testo UTF-8 in un file temporaneo","Usa FileManager e rimuove la risorsa con defer.",'let path=FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString).appendingPathExtension("txt")\ntry "Città".write(to:path,atomically:true,encoding:.utf8)\ndefer{try? FileManager.default.removeItem(at:path)}\nprint(try String(contentsOf:path,encoding:.utf8))',"Città; il file viene rimosso al termine dello scope.",("FileManager","defer","UTF8"))
    a.swift("Restituire un fallimento con Result","Espone un errore di dominio tipizzato senza nasconderlo con un fallback numerico.",'let result:Result<Int,InputError> = .failure(.notPositive)\nswitch result{case .success(let value):print(value);case .failure:print("valore non positivo")}',"valore non positivo",("Result","Error","failure"),definitions="enum InputError:Error{case notPositive}")
    a.swift("Garantire cleanup con defer anche dopo throw","Mantiene il rilascio nello stesso scope dell'acquisizione della risorsa simulata.",'do{try work()}catch{print("errore gestito")}',"apertura, chiusura, errore gestito.",("defer","throw","cleanup"),definitions='enum DemoError:Error{case failed}\nfunc work()throws{print("apertura");defer{print("chiusura")};throw DemoError.failed}')
    a.swift("Descrivere un contratto con protocol e generics","Accetta valori diversi che espongono la medesima proprietà richiesta.",'print(label(User(name:"Ada")))',"Utente Ada",("protocol","generic","constraints"),definitions='protocol Named{var name:String{get}}\nstruct User:Named{let name:String}\nfunc label<T:Named>(_ value:T)->String{"Utente "+value.name}')
    a.add("Navigare tra viste SwiftUI con NavigationStack","Usa destinazioni tipizzate per aprire un dettaglio da una lista senza gestire manualmente un controller.",{"ContentView.swift":'import SwiftUI\nstruct ContentView:View{\n let topics=["Optional","Package","Concurrency"]\n var body:some View{NavigationStack{List(topics,id:\\.self){topic in NavigationLink(topic,value:topic)}.navigationTitle("Guide").navigationDestination(for:String.self){topic in Text("Guida: \\(topic)").padding()}}}\n}'},commands("xcodebuild -list","macOS","Bash"),"Selezionando una riga si apre il dettaglio; la navigazione indietro è gestita dallo stack.",os=["macOS","iOS"],roles={"ContentView.swift":"snippet"},tags=("SwiftUI","NavigationStack","iOS","macOS"),guide="In un progetto Xcode SwiftUI con target iOS17+ o macOS14+ sostituisci ContentView.swift; conserva l'App generata con WindowGroup che istanzia ContentView. La scheda fornisce la vista completa e richiede Apple SDK, non un package CLI Linux. NavigationLink usa String come valore Hashable; navigationDestination gestisce lo stesso tipo.",sources=("https://developer.apple.com/documentation/swiftui/navigationstack",))
    a.swift("Proteggere stato asincrono con un actor","Serializza l'accesso a un contatore usando l'isolamento degli actor.",'let counter=Counter()\nawait counter.increment()\nprint(await counter.current())',"1; un chiamante esterno usa await per attraversare il confine dell'actor.",("actor","async","isolation"),definitions="actor Counter{private var count=0;func increment(){count+=1};func current()->Int{count}}")
    a.add("Conservare una preferenza Apple con UserDefaults","Usa un dominio dimostrativo separato e ripristina il valore tramite la medesima chiave.",{"main.swift":'import Foundation\nlet domain="example.catalog.preferences.demo"\nlet defaults=UserDefaults(suiteName:domain)!\ndefaults.set(true,forKey:"details")\nprint(defaults.bool(forKey:"details"))\ndefaults.removePersistentDomain(forName:domain)'},commands("swift main.swift","macOS","Bash"),"true; il dominio dimostrativo viene rimosso alla fine.",os=["macOS"],tags=("UserDefaults","Apple","preferences"),guide="Su macOS esegui lo script. In un'app iOS riusa le operazioni set/bool nel modello del target; non incollare istruzioni top-level in un file qualsiasi della app. Il dominio scelto è dedicato al laboratorio e viene eliminato: non sostituirlo con il dominio di un'app reale.",sources=("https://developer.apple.com/documentation/foundation/userdefaults",))
    a.add("Mostrare stato e azioni in una vista SwiftUI iOS","Collega un contatore a una vista con @State e aggiorna la presentazione attraverso un pulsante.",{"ContentView.swift":'import SwiftUI\nstruct ContentView:View{\n @State private var count=0\n var body:some View{VStack{Text("Conteggio: \\(count)");Button("Aggiungi"){count+=1}}.padding()}\n}'},commands("xcodebuild -list","macOS","Bash"),"Il pulsante incrementa il testo della vista senza mutare manualmente una label.",os=["macOS","iOS"],roles={"ContentView.swift":"snippet"},tags=("SwiftUI","iOS","State"),guide="In Xcode crea un progetto iOS App con interfaccia SwiftUI e target iOS17+. Sostituisci ContentView.swift con il file fornito e conserva l'App generata che mostra ContentView nel WindowGroup. Seleziona simulatore e premi Run. xcodebuild -list serve a identificare scheme/target del progetto esistente; questa scheda contiene la vista completa, non un progetto Xcode o certificati di firma.",sources=("https://developer.apple.com/documentation/swiftui/state",))
    swift_workflows(a);swift_project(a);a.save(25)


def swift_package(name,library=False):
    targets=f'.target(name:"{name}"),.testTarget(name:"{name}Tests",dependencies:["{name}"])' if library else f'.executableTarget(name:"{name}")'
    return f'// swift-tools-version: 6.0\nimport PackageDescription\nlet package=Package(name:"{name}",targets:[{targets}])'


def swift_workflows(a):
    a.add("Inizializzare un package Swift CLI su Linux o macOS","Verifica la toolchain e descrive il target eseguibile attraverso Swift Package Manager.",{"Package.swift":swift_package("SwiftStarter"),"Sources/SwiftStarter/main.swift":'print("Package Swift pronto")'},commands("swift --version\nswift package describe\nswift run SwiftStarter","Linux/macOS","Bash"),"Il package contiene il target SwiftStarter e la console stampa Package Swift pronto.",section="Inizializzazione",tags=("SPM","setup","Linux","macOS"),guide="Installa Swift6.4 per la distribuzione/architettura supportata da Swift.org; su macOS seleziona la toolchain corretta se usi Xcode. I file esportati rappresentano il package già inizializzato: in una directory vuota l'alternativa è swift package init --type executable. Non eseguire init sopra il package esportato.")
    a.add("Compilare un target Swift con configurazioni Debug e Release","Distingue le build di sviluppo da quelle ottimizzate e non assume che i simboli siano equivalenti.",{"Package.swift":swift_package("SwiftBuild"),"Sources/SwiftBuild/main.swift":'let values=[2,3,5]\nprint(values.reduce(0,+))'},commands("swift build -c debug\nswift build -c release\n.build/release/SwiftBuild","Linux/macOS","Bash"),"Il target Release stampa10; Debug e Release occupano output distinti.",section="Compilazione",tags=("swift build","Release","SPM"),guide="Apri la radice con Package.swift. Compila prima Debug per lo sviluppo e poi Release per l'artefatto da consegnare. Gli output .build sono specifici della piattaforma e possono contenere sottodirectory/alias del target; swift build --show-bin-path -c release fornisce il percorso effettivo.")
    a.add("Debuggare Swift con LLDB e simboli locali","Prepara una CLI non ottimizzata e la arresta nella funzione di calcolo.",{"main.swift":'func total(_ values:[Int])->Int{let result=values.reduce(0,+);return result}\nprint(total([2,3,5]))'},commands("swiftc -g -Onone main.swift -o debug-app\nlldb ./debug-app","Linux/macOS","Bash"),"Un breakpoint nella funzione total consente di osservare values/result; l'output finale è10.",section="Debug",tags=("LLDB","breakpoint","symbols"),guide="Installa LLDB compatibile con la toolchain Swift. Nella console LLDB usa breakpoint set -r total, run, next, frame variable, continue, quit. Su macOS l'esecuzione del debugger può richiedere la normale autorizzazione strumenti di sviluppo. La sessione è interattiva e rimane aperta fino a quit.")
    a.add("Eseguire test Swift Package con XCTest","Aggiunge un target di test al package e verifica il contratto pubblico della libreria.",{"Package.swift":swift_package("MathCore",True),"Sources/MathCore/Math.swift":'public func area(_ width:Int,_ height:Int)->Int{width*height}',"Tests/MathCoreTests/MathCoreTests.swift":'import XCTest\n@testable import MathCore\nfinal class MathCoreTests:XCTestCase{func testArea(){XCTAssertEqual(area(3,4),12)}}'},commands("swift test","Linux/macOS","Bash"),"Il test testArea passa; un valore atteso errato fa fallire il comando.",section="Test",tags=("XCTest","swift test","SPM"),guide="Il test importa il modulo del target, non un file di una cartella arbitraria. XCTest è fornito dall'ecosistema Swift supportato; non viene aggiunta una dipendenza di terze parti. Usa swift test -v per diagnosticare errori di compilazione o di discovery.")
    a.add("Preparare una CLI Swift per la distribuzione nativa","Produce un binario ottimizzato e lo prova dalla cartella di consegna senza promettere cross-compilazione automatica.",{"main.swift":'print("CLI Swift pronta")'},commands("swiftc -O main.swift -o atlas-swift\nmkdir -p dist\ncp atlas-swift dist/\n./dist/atlas-swift","Linux/macOS","Bash"),"CLI Swift pronta; dist contiene il binario della piattaforma usata per la build.",section="Distribuzione",tags=("swiftc","distribution","native"),guide="Compila sul target previsto e prova l'artefatto in un ambiente equivalente. Su Linux verifica le librerie dinamiche con ldd; su macOS usa otool -L. Un file prodotto su macOS non è un eseguibile Linux. Questa ricetta non incorpora automaticamente runtime/framework di sistema né firma/notarizza un'app Apple.")


def swift_project(a):
    a.add("Progetto completo report spese Swift Package","Legge JSON sintetico, valida centesimi non negativi e aggrega per categoria con controllo overflow.",{
      "Package.swift":'''// swift-tools-version: 6.0
import PackageDescription
let package=Package(name:"ExpenseReport",products:[.executable(name:"expense-cli",targets:["ExpenseCLI"])],targets:[.target(name:"ExpenseCore"),.executableTarget(name:"ExpenseCLI",dependencies:["ExpenseCore"]),.testTarget(name:"ExpenseCoreTests",dependencies:["ExpenseCore"])])''',
      "Sources/ExpenseCore/Expense.swift":'''import Foundation
public struct Expense:Codable,Sendable{public let category:String;public let cents:Int;public init(category:String,cents:Int){self.category=category;self.cents=cents}}
public enum LedgerError:Error{case invalidAmount;case overflow}
public func totals(_ rows:[Expense])throws->[String:Int]{var result:[String:Int]=[:];for row in rows{guard !row.category.isEmpty,row.cents>=0 else{throw LedgerError.invalidAmount};let(next,overflow)=(result[row.category] ?? 0).addingReportingOverflow(row.cents);guard !overflow else{throw LedgerError.overflow};result[row.category]=next};return result}''',
      "Sources/ExpenseCLI/main.swift":'''import Foundation
import ExpenseCore
#if canImport(Glibc)
import Glibc
#else
import Darwin
#endif
let path=CommandLine.arguments.dropFirst().first ?? "data/expenses.json"
do{let data=try Data(contentsOf:URL(fileURLWithPath:path));let rows=try JSONDecoder().decode([Expense].self,from:data);let result=try totals(rows);for key in result.keys.sorted(){print("\\(key): \\(result[key]!)")}}catch{FileHandle.standardError.write(Data("Errore: \\(error)\\n".utf8));exit(1)}''',
      "Tests/ExpenseCoreTests/ExpenseCoreTests.swift":'''import XCTest
@testable import ExpenseCore
final class ExpenseCoreTests:XCTestCase{func testTotals()throws{XCTAssertEqual(try totals([Expense(category:"casa",cents:120),Expense(category:"casa",cents:30)]),["casa":150])};func testInvalid(){XCTAssertThrowsError(try totals([Expense(category:"A",cents:-1)]))}}''',
      "data/expenses.json":js([{"category":"casa","cents":1250},{"category":"libri","cents":2000},{"category":"casa","cents":750}]),
      "README.md":"# Report spese Swift\n\nToolchain di riferimento Swift6.4 su Linux/macOS, manifest tools-version6.0, nessuna dipendenza esterna. `swift test`, `swift run expense-cli data/expenses.json`, `swift build -c release`. I dati sintetici producono casa2000/libri2000 centesimi. Il programma lavora su un file locale passato come argomento e restituisce errore nonzero per input invalido. I test sono in un target XCTest separato. Non è un progetto iOS: il core value-type può essere riusato in un target Apple; l'accesso al file va adattato al sandbox dell'app. Nessuna esecuzione su Windows attestata.\n"},commands("swift test\nswift run expense-cli data/expenses.json\nswift build -c release","Linux/macOS","Bash"),"Due test passano; output ordinato casa:2000 e libri:2000.",project=True,section="Inizializzazione",tags=("project","Swift Package","Codable","JSON","XCTest"))


def php_book():
    a=Author("php")
    a.php("Validare un intero senza perdere il valore zero","Distingue false da0 nel risultato di filter_var.",'''foreach (['0','42','abc'] as $text) {
 $value=filter_var($text,FILTER_VALIDATE_INT);
 echo $value===false ? "non valido\\n" : "$value\\n";
}''',"0,42 e non valido.",("filter_var","validation","integer"))
    a.php("Selezionare un valore con match esaustivo","Usa confronti stretti e un default esplicito per gli input inattesi.",'''$command='start';
$message=match($command){'start'=>'avviato','stop'=>'fermato',default=>throw new InvalidArgumentException('Comando sconosciuto')};
echo $message,PHP_EOL;''',"avviato; match non effettua coercizione debole.",("match","strict comparison"))
    a.php("Definire un DTO readonly tipizzato","Impedisce riassegnazioni dopo la costruzione e convalida l'importo.",'''final readonly class Product {
 public function __construct(public string $name,public int $cents){if($name===''||$cents<0)throw new InvalidArgumentException('Prodotto non valido');}
}
$product=new Product('libro',1250);
echo $product->name,':',$product->cents,PHP_EOL;''',"libro:1250; readonly non rende automaticamente immutabili altri oggetti referenziati.",("readonly","DTO","constructor"))
    a.php("Applicare un default soltanto quando il dato manca","Usa null coalescing senza sostituire0 o una stringa vuota.",'''$input=['count'=>0,'name'=>''];
var_export([$input['count']??99,$input['name']??'anonimo',$input['missing']??'default']);''',"Restano0 e stringa vuota; soltanto missing usa default.",("null coalescing","array"))
    a.php("Trasformare valori con array_map","Mantiene separata la sorgente mentre deriva una sequenza di quadrati.",'''$values=[2,3,4];
$squares=array_map(static fn(int $value):int=>$value*$value,$values);
echo json_encode($squares,JSON_THROW_ON_ERROR),PHP_EOL;''',"[4,9,16]",("array_map","closure"))
    a.php("Filtrare e reindicizzare un array","Ripristina indici consecutivi dopo array_filter per ottenere un JSON array.",'''$values=[1,2,3,4];
$even=array_values(array_filter($values,static fn(int $value):bool=>$value%2===0));
echo json_encode($even,JSON_THROW_ON_ERROR),PHP_EOL;''',"[2,4]; senza array_values gli indici mancanti potrebbero produrre un oggetto JSON.",("array_filter","array_values","JSON"))
    a.php("Ridurre una sequenza con un accumulatore","Fornisce un'identità esplicita per gestire anche un array vuoto.",'''$total=array_reduce([2,3,5],static fn(int $sum,int $value):int=>$sum+$value,0);
echo $total,PHP_EOL;''',"10",("array_reduce","sum"))
    a.php("Indicizzare record con array_column","Costruisce una mappa ID-nome a partire da record associativi.",'''$rows=[['id'=>7,'name'=>'Ada'],['id'=>9,'name'=>'Luca']];
print_r(array_column($rows,'name','id'));''',"Chiave7Ada e chiave9Luca; ID duplicati fanno prevalere l'ultimo record.",("array_column","index","records"))
    a.php("Ordinare record con il comparatore spaceship","Combina cognome e nome in un comparatore totale e leggibile.",'''$rows=[['surname'=>'Rossi','name'=>'Luca'],['surname'=>'Rossi','name'=>'Ada']];
usort($rows,static fn(array $a,array $b):int=>[$a['surname'],$a['name']]<=>[$b['surname'],$b['name']]);
echo $rows[0]['name'],PHP_EOL;''',"Ada; usort reindicizza l'array.",("usort","spaceship","sorting"))
    a.php("Raggruppare importi per categoria","Accumula totali su chiavi associando il valore iniziale quando manca.",'''$totals=[];
foreach([['A',2],['B',4],['A',3]] as [$category,$amount]){$totals[$category]=($totals[$category]??0)+$amount;}
echo json_encode($totals,JSON_THROW_ON_ERROR),PHP_EOL;''',"A5 e B4.",("grouping","associative array"))
    a.php("Gestire JSON malformato con eccezioni","Attiva JSON_THROW_ON_ERROR e conserva Unicode nell'output.",'''try {
 $record=json_decode('{"name":"Città"}',true,512,JSON_THROW_ON_ERROR);
 echo json_encode($record,JSON_UNESCAPED_UNICODE|JSON_THROW_ON_ERROR),PHP_EOL;
} catch(JsonException $error){fwrite(STDERR,$error->getMessage().PHP_EOL);exit(1);}''',"JSON con Città leggibile; input malformato arriva al catch.",("JSON_THROW_ON_ERROR","JsonException"))
    a.php("Manipolare una data senza mutare l'originale","Usa DateTimeImmutable e DateInterval per un intervallo civile esplicito.",'''$start=new DateTimeImmutable('2026-10-29T00:00:00+00:00');
$end=$start->add(new DateInterval('P7D'));
echo $start->format('Y-m-d'),' ',$end->format('Y-m-d'),PHP_EOL;''',"2026-10-29 e2026-11-05.",("DateTimeImmutable","DateInterval"))
    a.php("Verificare una password con password_hash","Affida sale e algoritmo all'API invece di memorizzare il testo in chiaro.",'''$hash=password_hash('segreto-dimostrativo',PASSWORD_DEFAULT);
var_export(password_verify('segreto-dimostrativo',$hash));
echo PHP_EOL;''',"true; il digest cambia fra esecuzioni e va conservato integralmente.",("password_hash","password_verify","authentication"))
    a.php("Escapare testo per un contesto HTML","Codifica virgolette e caratteri speciali prima dell'inserimento in testo/attributi HTML.",'''$input='<script>alert("demo")</script>';
echo htmlspecialchars($input,ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8'),PHP_EOL;''',"Il testo contiene &lt;script&gt; e virgolette codificate; non è un escaping per JavaScript o SQL.",("htmlspecialchars","escaping","XSS"))
    a.php("Estrarre gruppi nominati con preg_match","Valida l'intera stringa e gestisce anche gli errori del motore regex.",'''$result=preg_match('/\\Aitem-(?<id>\\d+)\\z/','item-123',$match);
if($result===false)throw new RuntimeException(preg_last_error_msg());
echo $result===1?$match['id']:'assente',PHP_EOL;''',"123",("preg_match","named groups","regex"))
    a.php("Produrre risultati lazy con un Generator","Genera campioni su richiesta invece di allocare tutti i valori.",'''function numbers(int $count):Generator{for($i=0;$i<$count;$i++)yield $i*$i;}
foreach(numbers(4) as $value)echo $value,' ';
echo PHP_EOL;''',"0 1 4 9",("yield","Generator","lazy"))
    a.php("Chiudere una risorsa nel finally","Controlla fopen e rilascia lo stream anche se il lavoro fallisce.",'''$stream=fopen('php://temp','w+');
if($stream===false)throw new RuntimeException('Stream non disponibile');
try{fwrite($stream,'esempio');rewind($stream);echo stream_get_contents($stream),PHP_EOL;}
finally{fclose($stream);}''',"esempio; php://temp può spostarsi su disco oltre la propria soglia.",("resource","finally","stream"))
    a.php("Sostituire un file usando un temporaneo adiacente","Scrive completamente prima del rename e pulisce il file provvisorio in caso di errore.",'''$dir=sys_get_temp_dir().DIRECTORY_SEPARATOR.'atlas-'.bin2hex(random_bytes(8));
if(!mkdir($dir))throw new RuntimeException('mkdir');
$target=$dir.DIRECTORY_SEPARATOR.'data.json';$temp=tempnam($dir,'pending-');
try{if($temp===false||file_put_contents($temp,'{"ok":true}',LOCK_EX)===false)throw new RuntimeException('write');if(!rename($temp,$target))throw new RuntimeException('rename');echo file_get_contents($target),PHP_EOL;}
finally{if(is_string($temp)&&is_file($temp))unlink($temp);if(is_file($target))unlink($target);rmdir($dir);}''',"JSON con oktrue; questo non garantisce persistenza dopo perdita di alimentazione o coordinamento fra più writer.",("file","rename","atomic write"))
    a.php("Eseguire query PDO SQLite parametrizzate","Associa i valori senza concatenare testo SQL e usa errori come eccezioni.",'''$db=new PDO('sqlite::memory:',null,null,[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);
$db->exec('CREATE TABLE items(name TEXT)');
$insert=$db->prepare('INSERT INTO items(name) VALUES (:name)');$insert->execute(['name'=>"L'acqua"]);
$read=$db->prepare('SELECT name FROM items WHERE name=:name');$read->execute(['name'=>"L'acqua"]);
echo $read->fetchColumn(),PHP_EOL;''',"L'acqua; richiede estensione pdo_sqlite.",("PDO","SQLite","prepared statements"))
    a.php("Annullare una transazione PDO dopo un vincolo violato","Rende atomiche due scritture e chiama rollback quando il secondo inserimento fallisce.",'''$db=new PDO('sqlite::memory:',null,null,[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);
$db->exec('CREATE TABLE items(id INTEGER PRIMARY KEY)');
try{$db->beginTransaction();$db->exec('INSERT INTO items VALUES(1)');$db->exec('INSERT INTO items VALUES(1)');$db->commit();}
catch(PDOException $error){if($db->inTransaction())$db->rollBack();}
echo $db->query('SELECT COUNT(*) FROM items')->fetchColumn(),PHP_EOL;''',"0 righe; la prima scrittura viene annullata insieme alla seconda. Richiede pdo_sqlite.",("PDO","transaction","rollback"))
    a.add("Restituire un endpoint JSON PHP locale","Valida il parametro page e restituisce status/content-type coerenti senza framework.",{"public/index.php":'''<?php
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
$page=filter_var($_GET['page']??'1',FILTER_VALIDATE_INT,['options'=>['min_range'=>1]]);
if($page===false){http_response_code(400);echo json_encode(['error'=>'page non valida'],JSON_THROW_ON_ERROR);return;}
echo json_encode(['page'=>$page,'items'=>['Ada','Luca']],JSON_THROW_ON_ERROR);'''},"php -S 127.0.0.1:8084 -t public","GET /?page=2 restituisce page2; page=abc restituisce400.",tags=("backend","HTTP","JSON"),guide="Avvia il server incorporato nella cartella esportata e visita http://127.0.0.1:8084/?page=2. Il processo rimane attivo fino a Ctrl+C. Il server PHP incorporato serve il laboratorio e non sostituisce una configurazione di produzione con webserver/FPM.",sources=("https://www.php.net/manual/en/features.commandline.webserver.php",))
    a.add("Verificare un token CSRF per un form PHP","Confronta un token di sessione con hash_equals prima di accettare una richiesta POST.",{"public/index.php":'''<?php
declare(strict_types=1);
session_start(['cookie_httponly'=>true,'cookie_samesite'=>'Lax']);
$_SESSION['csrf']??=bin2hex(random_bytes(32));
if(($_SERVER['REQUEST_METHOD']??'GET')==='POST'){
 $token=$_POST['csrf']??'';
 if(!is_string($token)||!hash_equals($_SESSION['csrf'],$token)){http_response_code(403);exit('Token non valido');}
 echo 'Richiesta accettata';return;
}
$token=htmlspecialchars($_SESSION['csrf'],ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8');
echo '<form method="post"><input type="hidden" name="csrf" value="'.$token.'"><button>Invia</button></form>';'''},"php -S 127.0.0.1:8084 -t public","Il form valido è accettato; token mancante/alterato restituisce403.",tags=("CSRF","session","hash_equals","form"),guide="Usa il server locale e conserva il cookie di sessione nel browser. In produzione il cookie richiede Secure con HTTPS e la configurazione di sessione del deploy. Il token non sostituisce autenticazione o autorizzazione; protegge il caso illustrato di form autenticabile a sessione.",sources=("https://www.php.net/manual/en/function.hash-equals.php",))
    a.php("Analizzare opzioni CLI con getopt","Distingue un'opzione obbligatoria da un default usando nomi lunghi.",'''$options=getopt('',['name:','count:']);
$name=$options['name']??'Ada';$count=filter_var($options['count']??'1',FILTER_VALIDATE_INT,['options'=>['min_range'=>1,'max_range'=>5]]);
if(!is_string($name)||$count===false)throw new InvalidArgumentException('Opzioni non valide');
for($i=0;$i<$count;$i++)echo "Ciao $name",PHP_EOL;''',"Senza opzioni stampa Ciao Ada; prova php main.php --name=Luca --count=2.",("getopt","CLI","arguments"))
    a.add("Caricare classi PSR-4 con Composer","Separa namespace e file e lascia che Composer generi l'autoloader.",{"composer.json":js({"name":"example/catalog-autoload","require":{"php":">=8.4 <8.6"},"autoload":{"psr-4":{"Atlas\\":"src/"}}}),"src/Greeter.php":'<?php\ndeclare(strict_types=1);\nnamespace Atlas;\nfinal class Greeter{public function greet(string $name):string{return "Ciao ".$name;}}',"main.php":'<?php\ndeclare(strict_types=1);\nrequire __DIR__."/vendor/autoload.php";\necho (new Atlas\\Greeter())->greet("Ada"),PHP_EOL;'},"composer install --no-interaction\nphp main.php","Ciao Ada; non sono richiesti pacchetti applicativi di terze parti.",tags=("PSR-4","Composer","autoload"),guide="Installa Composer2 compatibile con PHP8.4/8.5. Il prefisso Atlas deve corrispondere alla cartella src e al namespace della classe. composer install genera vendor/autoload.php; conserva composer.lock generato per fissare un eventuale successivo grafo di dipendenze. Non modificare a mano l'autoloader.",sources=("https://getcomposer.org/doc/04-schema.md#autoload",))
    php_workflows(a);php_project(a);a.save(30)


def php_workflows(a):
    a.add("Inizializzare PHP CLI con una configurazione esplicita","Individua php.ini e abilita diagnostica locale senza stampare errori al pubblico.",{"main.php":'<?php\ndeclare(strict_types=1);\necho "PHP ",PHP_VERSION," pronto",PHP_EOL;',"development.ini":"display_errors=On\nerror_reporting=E_ALL\nlog_errors=On"},"php --version\nphp --ini\nphp -c development.ini main.php","Versione PHP e messaggio pronto; il file di configurazione effettivo è visibile con --ini.",section="Inizializzazione",tags=("PHP CLI","php.ini","setup"),guide="Installa PHP8.4/8.5 CLI e aggiungi il binario al PATH. Il file development.ini configura soltanto il laboratorio; non è una configurazione FPM/produzione né include le estensioni del tuo php.ini standard. Se servono estensioni mantieni l'opportuno extension_dir e le relative righe di caricamento.")
    a.add("Controllare sintassi PHP prima della consegna","Usa il lint del runtime per intercettare errori di parsing senza eseguire lo script.",{"main.php":'<?php\ndeclare(strict_types=1);\nfunction total(array $values):int{return array_sum($values);}\necho total([2,3,5]),PHP_EOL;'},"php -l main.php\nphp main.php","Lint senza errori e output10; -l non valida accessi a database, file o rotte.",section="Compilazione",tags=("lint","syntax","build"),guide="PHP normalmente esegue il sorgente tramite runtime, senza una fase equivalente a un linker C. Il lint è il controllo preliminare, non una compilazione in eseguibile autonomo. Ripetilo per ogni file modificato; per cache bytecode di produzione configura OPcache nel server appropriato.")
    a.add("Debuggare PHP CLI con Xdebug e VS Code","Collega il processo CLI a un listener locale mantenendo il php.ini già configurato con Xdebug.",{"main.php":'<?php\ndeclare(strict_types=1);\n$values=[2,3,5];\n$total=array_sum($values);\necho $total,PHP_EOL;',".vscode/launch.json":js({"version":"0.2.0","configurations":[{"name":"Listen Xdebug","type":"php","request":"launch","port":9003,"hostname":"127.0.0.1"}]})},"php --ri xdebug\nphp -d xdebug.mode=debug -d xdebug.start_with_request=yes -d xdebug.client_host=127.0.0.1 main.php","Con il listener avviato il breakpoint permette di ispezionare values/total; output10.",section="Debug",tags=("Xdebug","VS Code","breakpoint"),guide="Installa Xdebug3 compatibile con versione/architettura di PHP e abilitalo nel php.ini effettivo, poi verifica --ri xdebug. Installa PHP Debug per VS Code, avvia Listen Xdebug e imposta un breakpoint prima della somma. Il comando -d conserva le altre estensioni di php.ini e abilita il debug soltanto per questa invocazione.",sources=("https://xdebug.org/docs/step_debug",))
    a.add("Eseguire contratti PHP sempre attivi","Evita che una configurazione zend.assertions disabiliti i test del dominio.",{"Math.php":'<?php\ndeclare(strict_types=1);\nfunction area(int $width,int $height):int{if($width<0||$height<0)throw new InvalidArgumentException("Lati negativi");return $width*$height;}',"tests.php":'<?php\ndeclare(strict_types=1);\nrequire __DIR__."/Math.php";\nif(area(3,4)!==12)throw new RuntimeException("Area errata");\ntry{area(-1,2);throw new RuntimeException("Validazione assente");}catch(InvalidArgumentException $expected){}\necho "2 contratti verificati",PHP_EOL;'},"php tests.php","2 contratti verificati; i controlli sono espliciti e non vengono eliminati da zend.assertions.",section="Test",tags=("test","contracts","exceptions"))
    a.add("Creare un archivio PHAR PHP locale","Incorpora uno script in un PHAR firmato con digest SHA256 senza pubblicarlo online.",{"app/main.php":'<?php\ndeclare(strict_types=1);\necho "PHAR pronto",PHP_EOL;',"build-phar.php":'''<?php
declare(strict_types=1);
$directory=__DIR__.'/dist';if(!is_dir($directory)&&!mkdir($directory))throw new RuntimeException('mkdir');
$path=$directory.'/atlas.phar';if(is_file($path)&&!unlink($path))throw new RuntimeException('output bloccato');
$archive=new Phar($path,0,'atlas.phar');$archive->startBuffering();
$archive->addFile(__DIR__.'/app/main.php','main.php');
$archive->setStub("<?php Phar::mapPhar('atlas.phar');require 'phar://atlas.phar/main.php';__HALT_COMPILER();");
$archive->setSignatureAlgorithm(Phar::SHA256);$archive->stopBuffering();echo $path,PHP_EOL;'''},"php -d phar.readonly=0 build-phar.php\nphp dist/atlas.phar","PHAR pronto; l'artefatto richiede un runtime PHP compatibile sulla macchina destinataria.",section="Distribuzione",tags=("PHAR","distribution","SHA256"),guide="L'estensione Phar deve essere disponibile. phar.readonly=0 è applicato soltanto al processo di build, non a una configurazione server permanente. Il digest rileva modifiche dell'archivio e non equivale a un certificato di un editore fidato. Il builder sovrascrive soltanto dist/atlas.phar nella cartella esportata.",sources=("https://www.php.net/manual/en/book.phar.php",))


def php_project(a):
    a.add("Progetto completo rubrica JSON PHP","Realizza una CLI con persistenza, validazione email, test e struttura src/bin senza dipendenze Composer esterne.",{
      "composer.json":js({"name":"example/catalog-addressbook","type":"project","require":{"php":">=8.4 <8.6"}}),
      "src/AddressBook.php":'''<?php
declare(strict_types=1);
namespace Atlas;
final class AddressBook{
 private array $contacts=[];
 public function __construct(private readonly string $path){if(is_file($path)){$data=json_decode((string)file_get_contents($path),true,512,JSON_THROW_ON_ERROR);if(!is_array($data))throw new \\UnexpectedValueException('Rubrica non valida');foreach($data as $name=>$email){if(!is_string($name)||!is_string($email)||filter_var($email,FILTER_VALIDATE_EMAIL)===false)throw new \\UnexpectedValueException('Contatto non valido');}$this->contacts=$data;}}
 public function add(string $name,string $email):void{if(trim($name)===''||filter_var($email,FILTER_VALIDATE_EMAIL)===false)throw new \\InvalidArgumentException('Nome/email non validi');$this->contacts[trim($name)]=$email;$temp=tempnam(dirname($this->path),'atlas-');if($temp===false)throw new \\RuntimeException('Temporaneo non disponibile');try{if(file_put_contents($temp,json_encode($this->contacts,JSON_PRETTY_PRINT|JSON_THROW_ON_ERROR),LOCK_EX)===false||!rename($temp,$this->path))throw new \\RuntimeException('Salvataggio fallito');}finally{if(is_file($temp))unlink($temp);}}
 public function list():array{$copy=$this->contacts;ksort($copy);return $copy;}
}''',
      "bin/addressbook.php":'''<?php
declare(strict_types=1);
require __DIR__.'/../src/AddressBook.php';
try{$path=$argv[1]??__DIR__.'/../data/contacts.json';$book=new Atlas\\AddressBook($path);$command=$argv[2]??'list';if($command==='add'){$book->add($argv[3]??'',$argv[4]??'');}elseif($command!=='list'){throw new InvalidArgumentException('Comando sconosciuto');}foreach($book->list() as $name=>$email)echo $name,': ',$email,PHP_EOL;}catch(Throwable $error){fwrite(STDERR,$error->getMessage().PHP_EOL);exit(1);}''',
      "tests/smoke.php":'''<?php
declare(strict_types=1);
require __DIR__.'/../src/AddressBook.php';
$path=tempnam(sys_get_temp_dir(),'atlas-php-');if($path===false)throw new RuntimeException('tempfile');unlink($path);
try{$book=new Atlas\\AddressBook($path);$book->add('Ada','ada@example.test');if((new Atlas\\AddressBook($path))->list()!==['Ada'=>'ada@example.test'])throw new RuntimeException('Persistenza');try{$book->add('','bad');throw new RuntimeException('Validazione assente');}catch(InvalidArgumentException $expected){}echo '2 contratti verificati',PHP_EOL;}finally{if(is_file($path))unlink($path);}''',
      "data/contacts.json":js({"Ada":"ada@example.test"}),
      "README.md":"# Rubrica PHP\n\nPHP8.4/8.5 CLI, nessun pacchetto esterno. `php tests/smoke.php`, `php bin/addressbook.php data/contacts.json list`, `php bin/addressbook.php data/contacts.json add Luca luca@example.test`. data/contacts.json contiene soltanto contatti sintetici. Il salvataggio usa un temporaneo adiacente e rename; il modello non coordina aggiornamenti simultanei da più processi. La cartella del file deve già esistere. composer.json documenta il vincolo runtime ma l'autoload qui è esplicito e Composer non è necessario per l'avvio. I test usano un percorso temporaneo separato.\n"},"php tests/smoke.php\nphp bin/addressbook.php data/contacts.json list","Due contratti verificati e contatto Ada stampato dalla CLI.",project=True,section="Inizializzazione",tags=("project","PHP CLI","JSON","persistence","testing"))


def dart_book():
    a=Author("dart")
    a.dart("Gestire null senza force unwrap in Dart","Conserva0 e stringa vuota e usa il default soltanto per null.",'''String? nickname=null;
print(nickname?.toUpperCase() ?? 'Nome assente');''',"Nome assente; nessun operatore ! necessario.",("null safety","nullable","coalescing"))
    a.dart("Definire parametri nominati obbligatori","Rende esplicito il contratto della chiamata e un default per l'opzione facoltativa.","print(greet(name:'Ada'));","Ciao Ada; omettere name è un errore statico.",("named parameters","required"),definitions="String greet({required String name,String prefix='Ciao'}) => '$prefix $name';")
    a.dart("Destrutturare un record posizionale","Usa un numero fisso di componenti tipizzati senza creare una classe apposita.",'''final point=(3,4);
final (x,y)=point;
print(x*x+y*y);''',"25; i record sono value-type con uguaglianza strutturale.",("records","patterns","destructuring"))
    a.dart("Costruire un modello immutabile con invarianti","Mantiene i campi final e valida i dati prima di esporre il prodotto.","final product=Product('libro',1250);\nprint('${product.name}:${product.cents}');","libro:1250; il modello puro Dart può essere condiviso con una UI Flutter senza dipendere da widget.",("immutable","model","Flutter reuse"),definitions="final class Product{final String name;final int cents;Product(this.name,this.cents){if(name.trim().isEmpty||cents<0)throw ArgumentError('Prodotto non valido');}}")
    a.dart("Trasformare una lista con map e toList","Materializza una trasformazione lazy soltanto quando serve un risultato indicizzabile.",'''final source=[2,3,4];
final squares=source.map((value)=>value*value).toList();
print(squares);''',"[4,9,16]; source non è modificata.",("map","Iterable","toList"))
    a.dart("Filtrare elementi con where","Seleziona valori pari tramite un predicato senza cancellare gli originali.","final values=[1,2,3,4];\nprint(values.where((value)=>value.isEven).toList());","[2,4]",("where","filter","predicate"))
    a.dart("Raggruppare elementi con putIfAbsent","Costruisce una mappa di liste usando solo la libreria standard.",'''final groups=<String,List<int>>{};
for(final (category,value) in [('A',2),('B',4),('A',3)]){groups.putIfAbsent(category,()=>[]).add(value);}
print(groups);''',"A contiene[2,3] e B[4].",("Map","putIfAbsent","grouping"))
    a.dart("Ordinare record con più chiavi","Confronta cognome e nome e dichiara un criterio deterministico per i pareggi.",'''final people=[('Rossi','Luca'),('Rossi','Ada')];
people.sort((a,b){final first=a.$1.compareTo(b.$1);return first!=0?first:a.$2.compareTo(b.$2);});
print(people.map((item)=>item.$2).toList());''',"[Ada,Luca]; sort modifica la lista su cui viene invocato.",("sort","compareTo","records"))
    a.dart("Calcolare differenze fra insiemi","Ottiene aggiunte e rimozioni tra due snapshot di identificativi.",'''final before={'a','b'},after={'b','c'};
print(after.difference(before));
print(before.difference(after));''',"Aggiunto c e rimosso a; l'ordine di un Set non è un criterio di confronto dei risultati.",("Set","difference"))
    a.dart("Validare JSON con un map pattern tipizzato","Controlla tipi e presenza dei campi prima di usare dati esterni.",'''final Object? value=jsonDecode('{"name":"Ada","age":36}');
if(value case {'name':String name,'age':int age}){print('$name:$age');}
else{throw const FormatException('Record non valido');}''',"Ada:36; campi aggiuntivi sono ammessi da questo pattern.",("JSON","map pattern","validation"),imports="import 'dart:convert';")
    a.dart("Convertire un istante in UTC","Legge un offset ISO8601 e stampa un valore UTC indipendente dalla zona locale.","final instant=DateTime.parse('2026-10-29T10:00:00+02:00');\nprint(instant.toUtc().toIso8601String());","2026-10-29T08:00:00.000Z",("DateTime","UTC","ISO8601"))
    a.dart("Codificare parametri URL con Uri","Conserva più e spazi nella query senza concatenare manualmente i valori.","final uri=Uri.https('example.test','/search',{'q':'C++ e Dart'});\nprint(uri);\nprint(uri.queryParameters['q']);","La query codifica correttamente il parametro e la lettura restituisce C++ e Dart.",("Uri","queryParameters","percent encoding"))
    a.dart("Attendere risultati concorrenti con Future wait","Raccoglie più Future preservando l'ordine della lista di partenza.","final values=await Future.wait([Future.value(2),Future.value(3)]);\nprint(values);","[2,3]; un errore segue la semantica di Future.wait.",("Future.wait","async","concurrency"))
    a.dart("Applicare un timeout a una Future","Gestisce TimeoutException distinguendo il limite di attesa dalla cancellazione del lavoro.",'''try{await Future<int>.delayed(const Duration(seconds:1),()=>42).timeout(const Duration(milliseconds:1));}
on TimeoutException{print('tempo scaduto');}''',"tempo scaduto; il timer/lavoro sottostante può continuare dopo il timeout.",("timeout","TimeoutException"),imports="import 'dart:async';")
    a.dart("Produrre risultati progressivi con uno Stream","Consuma un generatore async* senza accumulare tutti gli eventi.","await for(final value in samples()){print(value);}","1 e2 in eventi separati.",("Stream","async*","await for"),definitions="Stream<int> samples() async* {yield 1;yield 2;}")
    a.dart("Spostare un calcolo CPU in un isolate","Usa Isolate.run per non occupare l'isolate chiamante durante un calcolo indipendente.","final values=List<int>.generate(10000,(index)=>index);\nfinal total=await Isolate.run(()=>values.fold<int>(0,(sum,value)=>sum+value));\nprint(total);","49995000; payload e risultato devono essere trasferibili fra isolate, esempio nativo.",("Isolate.run","CPU","parallelism"),imports="import 'dart:isolate';")
    a.dart("Leggere e scrivere UTF-8 con dart io","Usa una directory temporanea dedicata e la rimuove dopo il round-trip.",'''final directory=await Directory.systemTemp.createTemp('atlas-dart-');
try{final file=File('${directory.path}/note.txt');await file.writeAsString('Città',encoding:utf8);print(await file.readAsString(encoding:utf8));}
finally{await directory.delete(recursive:true);}''',"Città; questo sorgente richiede un runtime Dart nativo, non il browser.",("dart:io","File","UTF8"),imports="import 'dart:io';\nimport 'dart:convert';")
    a.dart("Gestire un risultato sealed con switch esaustivo","Mantiene successo e fallimento tipizzati e obbliga a trattare tutte le varianti.",'''final Outcome<int> result=Success(42);
final label=switch(result){Success<int>(value:final value)=>'valore $value',Failure<int>(message:final message)=>message};
print(label);''',"valore42; l'aggiunta di nuove varianti richiede l'aggiornamento dello switch.",("sealed","switch expression","patterns"),definitions="sealed class Outcome<T>{const Outcome();}\nfinal class Success<T> extends Outcome<T>{final T value;const Success(this.value);}\nfinal class Failure<T> extends Outcome<T>{final String message;const Failure(this.message);}")
    a.dart("Aggiungere una extension per validare testo","Riutilizza una trasformazione pura senza ereditare dalla classe String.","print('  Ada  '.requiredLabel());","Ada; una stringa vuota genera ArgumentError.",("extension","String","validation"),definitions="extension RequiredLabel on String{String requiredLabel(){final value=trim();if(value.isEmpty)throw ArgumentError('Testo vuoto');return value;}}")
    dart_workflows(a);dart_project(a);a.save(25)


def pubspec(name):return f"name: {name}\nversion: 0.1.0\npublish_to: none\nenvironment:\n  sdk: '>=3.13.0 <3.14.0'\n"


def dart_workflows(a):
    a.add("Inizializzare un package Dart senza dipendenze","Dichiara il vincolo SDK e avvia una CLI da una struttura bin/lib riconoscibile da Pub.",{"pubspec.yaml":pubspec("dart_starter"),"lib/greeting.dart":"String greet(String name)=>'Ciao $name';","bin/main.dart":"import '../lib/greeting.dart';\nvoid main(){print(greet('Ada'));}"},"dart --version\ndart pub get --offline\ndart run bin/main.dart","Ciao Ada; il package non richiede download di librerie Pub esterne.",section="Inizializzazione",tags=("Dart SDK","Pub","setup"),guide="Installa SDK3.13.x o usa l'SDK Dart incluso nella versione Flutter compatibile, poi controlla dart --version. I file esportati rappresentano un package già inizializzato: non eseguire dart create sopra questi file. Il vincolo SDK è esplicito; aggiornalo solo dopo verifica con la nuova toolchain.")
    a.add("Analizzare e compilare una CLI Dart nativa","Esegue controlli statici prima della compilazione AOT per il computer corrente.",{"main.dart":"void main(){final values=[2,3,5];print(values.fold<int>(0,(sum,value)=>sum+value));}"},"dart analyze main.dart\ndart compile exe main.dart -o app.exe\n.\\app.exe","Il programma compilato stampa10; su Linux/macOS scegliere un nome senza .exe.",section="Compilazione",tags=("dart analyze","AOT","compile exe"),guide="dart analyze è il controllo statico del codice; compile exe produce un eseguibile nativo con runtime essenziale. L'output appartiene a un OS/architettura: non promette automaticamente un binario iOS/Android. Una app Flutter mobile richiede la relativa pipeline Flutter e SDK di piattaforma.")
    a.add("Debuggare Dart con VM Service e VS Code","Arresta l'isolate all'avvio e permette di osservare variabili e stack durante una CLI.",{"main.dart":"int total(List<int> values){final result=values.fold<int>(0,(sum,value)=>sum+value);return result;}\nvoid main(){print(total([2,3,5]));}",".vscode/launch.json":js({"version":"0.2.0","configurations":[{"name":"Debug Dart","type":"dart","request":"launch","program":"main.dart"}]})},"dart run --observe=8181 --pause-isolates-on-start main.dart","Il servizio VM ascolta localmente e il programma può restare sospeso fino al collegamento; dopo continue stampa10.",section="Debug",tags=("VM Service","DevTools","breakpoint"),guide="Installa Dart extension in VS Code, metti un breakpoint in total e premi F5 per il percorso più diretto. In alternativa il comando observe abilita VM Service: usa l'URL/token stampato dal processo per DevTools, senza esporlo su interfacce pubbliche. Il debug JIT non è identico a una build AOT; una distribuzione va ricollaudata separatamente.",sources=("https://dart.dev/tools/dart-run",))
    a.add("Eseguire contratti Dart senza package test esterni","Usa verifiche esplicite che restano attive anche quando assert è disabilitato.",{"lib/math_core.dart":"int area(int width,int height){if(width<0||height<0)throw ArgumentError('Lati negativi');return width*height;}","test/contracts.dart":"import '../lib/math_core.dart';\nvoid expect(bool value,String label){if(!value)throw StateError(label);}\nvoid main(){expect(area(3,4)==12,'area');try{area(-1,2);throw StateError('Validazione assente');}on ArgumentError{}print('2 contratti verificati');}"},"dart run test/contracts.dart","2 contratti verificati; non è necessario acquisire package:test.",section="Test",tags=("testing","contracts","exceptions"),guide="Per una suite più ampia è possibile introdurre package:test con una versione bloccata e relativo lockfile. Qui il runner è intenzionalmente una normale CLI SDK: usa StateError per fare fallire il processo e non dipende dall'attivazione di assert.")
    a.add("Distribuire un eseguibile Dart per lo stesso host","Conserva l'artefatto AOT in dist e ne distingue l'uso da una snapshot che richiede il runtime.",{"main.dart":"import 'dart:io';\nvoid main(){print('Dart su ${Platform.operatingSystem}');}"},"New-Item -ItemType Directory -Path dist -Force | Out-Null\ndart compile exe main.dart -o dist/atlas-dart.exe\n.\\dist\\atlas-dart.exe","Dart su windows nel caso Windows; il nome binario e il comando di avvio cambiano sugli altri host.",section="Distribuzione",tags=("distribution","AOT","native"),guide="Consegna l'eseguibile creato per il target e provalo sull'ambiente destinatario. Su Linux/macOS usa mkdir -p dist, output dist/atlas-dart e ./dist/atlas-dart. Una snapshot AOT senza runtime richiederebbe dartaotruntime; compile exe incorpora invece il runtime minimo. Nessuna firma di distribuzione viene generata.")


def dart_project(a):
    a.add("Progetto completo report spese Dart","Separa modello, validazione JSON, aggregazione e CLI; i test restano indipendenti da package Pub esterni.",{
      "pubspec.yaml":pubspec("atlas_ledger"),
      "lib/ledger.dart":'''import 'dart:convert';
final class Expense{final String category;final int cents;const Expense(this.category,this.cents);}
List<Expense> parseExpenses(String text){final Object? value=jsonDecode(text);if(value is! List)throw const FormatException('Lista richiesta');return value.map<Expense>((item){if(item case {'category':String category,'cents':int cents}){if(category.trim().isEmpty||cents<0)throw const FormatException('Spesa non valida');return Expense(category,cents);}throw const FormatException('Record non valido');}).toList();}
Map<String,int> totals(List<Expense> rows){final result=<String,int>{};for(final row in rows){result[row.category]=(result[row.category]??0)+row.cents;}return result;}''',
      "bin/ledger.dart":'''import 'dart:io';
import '../lib/ledger.dart';
Future<void> main(List<String> args)async{try{final path=args.isEmpty?'data/expenses.json':args.first;final rows=parseExpenses(await File(path).readAsString());final result=totals(rows);for(final key in result.keys.toList()..sort()){stdout.writeln('$key: ${result[key]}');}}catch(error){stderr.writeln('Errore: $error');exitCode=1;}}''',
      "test/smoke.dart":'''import '../lib/ledger.dart';
void expect(bool value,String label){if(!value)throw StateError(label);}
void main(){final rows=parseExpenses('[{"category":"casa","cents":120},{"category":"casa","cents":30}]');expect(totals(rows)['casa']==150,'somma');try{parseExpenses('[{"category":"A","cents":-1}]');throw StateError('Validazione assente');}on FormatException{}print('2 contratti verificati');}''',
      "data/expenses.json":js([{"category":"casa","cents":1250},{"category":"libri","cents":2000},{"category":"casa","cents":750}]),
      "README.md":"# Report spese Dart\n\nSDK3.13.x, nessun package Pub esterno. `dart pub get --offline`, `dart run test/smoke.dart`, `dart run bin/ledger.dart data/expenses.json`. I dati sintetici danno casa2000/libri2000 centesimi. Il modello e l'aggregazione non dipendono da Flutter e possono essere riusati in un'app Android/iOS Flutter; la CLI con dart:io richiede invece runtime nativo e accesso al file. I test usano controlli espliciti, non assert disattivabili. Gli importi del laboratorio sono piccoli interi; per sistemi finanziari reali va definita e testata anche la politica di overflow/range del target e la valuta. Nessun server o dato reale necessario.\n"},"dart pub get --offline\ndart run test/smoke.dart\ndart run bin/ledger.dart data/expenses.json","Due contratti verificati; CLI: casa2000 e libri2000.",project=True,section="Inizializzazione",tags=("project","Dart CLI","JSON","testing","Flutter reuse"))


def main():
    for build in (kotlin_book,swift_book,php_book,dart_book):build()
    build_search_cases()


def build_search_cases():
    cases=[
      ("Kotlin nome nullable valore alternativo Elvis","kotlin","Gestire null con safe call ed Elvis"),
      ("Kotlin totali per categoria groupBy sumOf","kotlin","Raggruppare record per categoria"),
      ("Android Kotlin salvare opzione tra riavvii SharedPreferences","kotlin","Conservare un'opzione Android con SharedPreferences"),
      ("Kotlin collegare debugger JVM porta 5005","kotlin","Debuggare Kotlin JVM con JDWP"),
      ("Kotlin digest SHA256 testo UTF8","kotlin","Calcolare SHA-256 di un payload UTF-8"),
      ("Swift convertire JSON in modello Codable","swift","Codificare e decodificare JSON con Codable"),
      ("Swift emoji conta un carattere ma molti byte","swift","Contare grafemi e byte Unicode"),
      ("SwiftUI aprire dettaglio da lista NavigationStack","swift","Navigare tra viste SwiftUI con NavigationStack"),
      ("Swift Package test automatico XCTest","swift","Eseguire test Swift Package con XCTest"),
      ("Swift CLI report spese JSON con test","swift","Progetto completo report spese Swift Package"),
      ("PHP filter_var zero è un intero valido","php","Validare un intero senza perdere il valore zero"),
      ("PHP dopo array_filter JSON deve restare array","php","Filtrare e reindicizzare un array"),
      ("PHP PDO SQLite query con apostrofo senza concatenare","php","Eseguire query PDO SQLite parametrizzate"),
      ("PHP rifiutare form con token CSRF alterato","php","Verificare un token CSRF per un form PHP"),
      ("PHP creare PHAR da distribuire localmente","php","Creare un archivio PHAR PHP locale"),
      ("Dart lavoro CPU su Isolate.run","dart","Spostare un calcolo CPU in un isolate"),
      ("Dart raggruppare numeri per categoria putIfAbsent","dart","Raggruppare elementi con putIfAbsent"),
      ("Dart VM Service DevTools breakpoint CLI","dart","Debuggare Dart con VM Service e VS Code"),
      ("Dart controllare tipi ricevuti da JSON map pattern","dart","Validare JSON con un map pattern tipizzato"),
      ("Dart scrivere e rileggere file UTF8 nativo","dart","Leggere e scrivere UTF-8 con dart io"),
    ]
    output=[{"query":query,"expected_ids":[stack+"-"+slug(title)]} for query,stack,title in cases]
    for case in output:
        rid=case["expected_ids"][0];stack=rid.split("-",1)[0]
        assert (ROOT/"catalog"/stack/rid/"recipe.json").exists(),rid
    assert len(output)==20
    (ROOT/"reports/search-cases-expansion-languages.json").write_text(js(output),encoding="utf-8")


if __name__=="__main__":main()

