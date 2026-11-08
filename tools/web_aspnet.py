from catalog_support import Book
from web_support import add

CSPROJ='<Project Sdk="Microsoft.NET.Sdk.Web"><PropertyGroup><TargetFramework>net10.0</TargetFramework><Nullable>enable</Nullable><ImplicitUsings>enable</ImplicitUsings></PropertyGroup></Project>'
PRE='using System.Text;\nusing System.Text.Json;\nusing System.Diagnostics;\nusing System.ComponentModel.DataAnnotations;\nusing Microsoft.AspNetCore.Http.HttpResults;\nusing Microsoft.AspNetCore.RateLimiting;\nusing System.Threading.RateLimiting;\nvar builder=WebApplication.CreateBuilder(args);\n'
# configurazione servizi | routing; ciascun programma è compilabile isolatamente.
ROWS=[
("Definire una Minimal API GET",'',"app.MapGet(\"/demo\",()=>new{ok=true});"),
("Convertire parametri percorso",'',"app.MapGet(\"/items/{id:int}\",(int id)=>new{id});"),
("Vincolare parametro con route constraint",'',"app.MapGet(\"/items/{id:int:min(1):max(100)}\",(int id)=>new{id});"),
("Leggere parametri query tipizzati",'',"app.MapGet(\"/demo\",(int? page,string? q)=>new{page=page??1,query=q??\"\"});"),
("Leggere query multivalore",'',"app.MapGet(\"/demo\",(HttpRequest r)=>r.Query[\"tag\"].ToArray());"),
("Leggere un header della richiesta",'',"app.MapGet(\"/demo\",(HttpRequest r)=>new{client=r.Headers[\"X-Client\"].ToString()});"),
("Impostare header di risposta",'',"app.MapGet(\"/demo\",(HttpResponse r)=>{r.Headers[\"X-App-Version\"]=\"1\";return Results.Ok(new{ok=true});});"),
("Restituire testo semplice",'',"app.MapGet(\"/demo\",()=>Results.Text(\"Ciao\",\"text/plain; charset=utf-8\"));"),
("Restituire HTML esplicito",'',"app.MapGet(\"/demo\",()=>Results.Content(\"<!doctype html><html lang='it'><title>Demo</title><h1>Ciao</h1></html>\",\"text/html\"));"),
("Restituire status201 e Location",'',"app.MapPost(\"/items\",()=>Results.Created(\"/items/1\",new{id=1}));"),
("Restituire204 dopo DELETE",'',"app.MapDelete(\"/items/{id:int}\",(int id)=>Results.NoContent());"),
("Produrre errore404 tipizzato",'',"app.MapGet(\"/items/{id:int}\",(int id)=>id==1?Results.Ok(new{id}):Results.NotFound(new{error=\"Assente\"}));"),
("Restituire Problem Details",'builder.Services.AddProblemDetails();',"app.MapGet(\"/demo\",()=>Results.Problem(title:\"Servizio non disponibile\",statusCode:503));"),
("Validare input prima del calcolo",'',"app.MapGet(\"/divide\",(double a,double b)=>b==0?Results.BadRequest(new{error=\"divisione per zero\"}):Results.Ok(a/b));"),
("Deserializzare body JSON con record",'',"app.MapPost(\"/items\",(Item item)=>Results.Ok(item));",'public record Item(string Name,decimal Price);'),
("Gestire PUT con percorso e body",'',"app.MapPut(\"/items/{id:int}\",(int id,Item item)=>Results.Ok(new{id,item.Name,item.Price}));",'public record Item(string Name,decimal Price);'),
("Gestire PATCH con proprietà facoltative",'',"app.MapPatch(\"/items/{id:int}\",(int id,Patch item)=>Results.Ok(new{id,changes=item}));",'public record Patch(string? Name,decimal? Price);'),
("Validare modello con DataAnnotations",'',"app.MapPost(\"/items\",(Item item)=>{var errors=new List<ValidationResult>();return Validator.TryValidateObject(item,new ValidationContext(item),errors,true)?Results.Ok(item):Results.BadRequest(errors.Select(e=>e.ErrorMessage));});",'public record Item([property:Required,StringLength(80)] string Name,[property:Range(0,100000)] decimal Price);'),
("Iniettare un servizio singleton",'builder.Services.AddSingleton<Counter>();',"app.MapGet(\"/demo\",(Counter c)=>new{value=c.Next()});",'public class Counter{private int value;public int Next()=>Interlocked.Increment(ref value);}'),
("Creare servizio scoped per richiesta",'builder.Services.AddScoped<RequestStamp>();',"app.MapGet(\"/demo\",(RequestStamp stamp)=>new{stamp.Id});",'public class RequestStamp{public Guid Id{get;}=Guid.NewGuid();}'),
("Iniettare una implementazione tramite interfaccia",'builder.Services.AddTransient<IGreeter,Greeter>();',"app.MapGet(\"/demo\",(IGreeter g)=>g.Hello());",'public interface IGreeter{string Hello();}public class Greeter:IGreeter{public string Hello()=>"Ciao";}'),
("Leggere configurazione da ambiente",'',"app.MapGet(\"/demo\",(IConfiguration c)=>new{mode=c[\"Demo:Mode\"]??\"locale\"});"),
("Scrivere log strutturati della richiesta",'',"app.MapGet(\"/items/{id:int}\",(int id,ILogger<Program> log)=>{log.LogInformation(\"Richiesto elemento {ItemId}\",id);return new{id};});"),
("Aggiungere request ID alla risposta",'',"app.Use(async(c,next)=>{c.Response.Headers[\"X-Request-ID\"]=c.TraceIdentifier;await next(c);});app.MapGet(\"/demo\",(HttpContext c)=>new{id=c.TraceIdentifier});"),
("Misurare durata con middleware",'',"app.Use(async(c,next)=>{var sw=Stopwatch.StartNew();c.Response.OnStarting(()=>{c.Response.Headers[\"X-Duration-Ms\"]=sw.ElapsedMilliseconds.ToString();return Task.CompletedTask;});await next(c);});app.MapGet(\"/demo\",()=>new{ok=true});"),
("Normalizzare errori non gestiti",'builder.Services.AddProblemDetails();',"app.UseExceptionHandler();app.MapGet(\"/demo\",()=>{throw new InvalidOperationException(\"Errore dimostrativo\");});"),
("Consentire CORS a origine specifica",'builder.Services.AddCors(o=>o.AddPolicy("local",p=>p.WithOrigins("http://localhost:5173").WithMethods("GET").WithHeaders("Content-Type")));',"app.UseCors();app.MapGet(\"/demo\",()=>new{ok=true}).RequireCors(\"local\");"),
("Applicare rate limiting a una rotta",'builder.Services.AddRateLimiter(o=>o.AddFixedWindowLimiter("demo",p=>{p.PermitLimit=5;p.Window=TimeSpan.FromMinutes(1);p.QueueLimit=0;}));',"app.UseRateLimiter();app.MapGet(\"/demo\",()=>new{ok=true}).RequireRateLimiting(\"demo\");"),
("Comprimere risposte con middleware",'builder.Services.AddResponseCompression();',"app.UseResponseCompression();app.MapGet(\"/demo\",()=>Results.Text(new string('a',5000)));"),
("Memorizzare output di endpoint",'builder.Services.AddOutputCache();',"app.UseOutputCache();app.MapGet(\"/demo\",()=>new{generated=DateTimeOffset.UtcNow}).CacheOutput(p=>p.Expire(TimeSpan.FromSeconds(30)));"),
("Servire file statici da wwwroot",'',"Directory.CreateDirectory(\"wwwroot\");File.WriteAllText(\"wwwroot/demo.txt\",\"Ciao\");app.UseStaticFiles();"),
("Raggruppare rotte con MapGroup",'',"var api=app.MapGroup(\"/v1\");api.MapGet(\"/items\",()=>new[]{new{id=1}});api.MapGet(\"/health\",()=>new{ok=true});"),
("Applicare filtro validazione a endpoint",'',"app.MapGet(\"/items/{id:int}\",(int id)=>new{id}).AddEndpointFilter(async(context,next)=>{var id=context.GetArgument<int>(0);if(id<1)return Results.BadRequest(\"ID positivo richiesto\");return await next(context);});"),
("Nominare endpoint e costruire collegamenti",'',"app.MapGet(\"/items/{id:int}\",(int id)=>new{id}).WithName(\"item\");app.MapGet(\"/demo\",(LinkGenerator links)=>new{path=links.GetPathByName(\"item\",new{id=1})});"),
("Esporre health check integrato",'builder.Services.AddHealthChecks();',"app.MapHealthChecks(\"/health\");"),
("Rispettare cancellazione della richiesta",'',"app.MapGet(\"/slow\",async(CancellationToken token)=>{await Task.Delay(500,token);return new{ok=true};});"),
("Trasmettere risultati come async enumerable",'',"app.MapGet(\"/stream\",()=>Rows());",'static async IAsyncEnumerable<int> Rows(){for(var i=0;i<3;i++){await Task.Delay(100);yield return i;}}'),
("Scaricare file CSV da buffer",'',"app.MapGet(\"/export\",()=>Results.File(Encoding.UTF8.GetBytes(\"nome,totale\\nAda,42\\n\"),\"text/csv\",\"report.csv\"));"),
("Servire file con supporto range",'',"var file=Path.GetFullPath(\"sample.bin\");File.WriteAllBytes(file,new byte[]{1,2,3,4});app.MapGet(\"/file\",()=>Results.File(file,\"application/octet-stream\",enableRangeProcessing:true));"),
("Impostare cookie di preferenza",'',"app.MapPost(\"/theme\",(HttpResponse r)=>{r.Cookies.Append(\"theme\",\"dark\",new CookieOptions{HttpOnly=true,SameSite=SameSiteMode.Lax,Secure=false});return Results.Ok();});"),
("Eliminare cookie usando lo stesso path",'',"app.MapPost(\"/logout\",(HttpResponse r)=>{r.Cookies.Delete(\"theme\",new CookieOptions{Path=\"/\"});return Results.NoContent();});"),
("Leggere cookie della richiesta",'',"app.MapGet(\"/theme\",(HttpRequest r)=>new{theme=r.Cookies[\"theme\"]??\"light\"});"),
("Rispondere con ETag e304",'',"app.MapGet(\"/demo\",(HttpContext c)=>{const string tag=\"\\\"v1\\\"\";c.Response.Headers.ETag=tag;return c.Request.Headers.IfNoneMatch==tag?Results.StatusCode(304):Results.Ok(new{version=1});});"),
("Impostare Cache Control esplicito",'',"app.MapGet(\"/demo\",(HttpResponse r)=>{r.Headers.CacheControl=\"public,max-age=60\";return new{version=1};});"),
("Accettare FormData senza autenticazione cookie",'',"app.MapPost(\"/form\",async(HttpRequest r)=>{var f=await r.ReadFormAsync();return Results.Ok(new{name=f[\"name\"].ToString()});});"),
("Leggere metadati di file multipart",'',"app.MapPost(\"/upload\",async(HttpRequest r)=>{var f=await r.ReadFormAsync();var file=f.Files.GetFile(\"file\");return file is null?Results.BadRequest(\"File richiesto\"):Results.Ok(new{file.FileName,file.Length,file.ContentType});});"),
("Limitare dimensione body sul server Kestrel",'builder.WebHost.ConfigureKestrel(o=>o.Limits.MaxRequestBodySize=1048576);',"app.MapPost(\"/body\",async(HttpRequest r)=>{using var reader=new StreamReader(r.Body);var text=await reader.ReadToEndAsync();return new{characters=text.Length};});"),
("Restituire redirect relativo",'',"app.MapGet(\"/old\",()=>Results.Redirect(\"/new\",permanent:true));app.MapGet(\"/new\",()=>\"Nuova pagina\");"),
("Gestire fallback per rotte assenti",'',"app.MapGet(\"/demo\",()=>new{ok=true});app.MapFallback(()=>Results.NotFound(new{error=\"Rotta assente\"}));"),
("Controllare ambiente development",'',"app.MapGet(\"/demo\",(IHostEnvironment env)=>new{env.EnvironmentName,isDevelopment=env.IsDevelopment()});"),
("Raggruppare dati risposta con proiezione",'',"app.MapGet(\"/demo\",()=>new[]{new{City=\"Roma\",Amount=10},new{City=\"Roma\",Amount=20}}.GroupBy(x=>x.City).Select(g=>new{city=g.Key,total=g.Sum(x=>x.Amount)}));"),
("Applicare paginazione stabile con cursore",'',"app.MapGet(\"/items\",(int? after)=>Enumerable.Range(1,10).Where(id=>id>(after??0)).Take(3).Select(id=>new{id}));"),
("Leggere JSON manualmente con gestione errori",'',"app.MapPost(\"/demo\",async(HttpRequest r)=>{try{using var doc=await JsonDocument.ParseAsync(r.Body);return Results.Ok(new{kind=doc.RootElement.ValueKind.ToString()});}catch(JsonException){return Results.BadRequest(\"JSON invalido\");}});"),
("Personalizzare serializzazione JSON camelCase",'builder.Services.ConfigureHttpJsonOptions(o=>o.SerializerOptions.PropertyNamingPolicy=JsonNamingPolicy.CamelCase);',"app.MapGet(\"/demo\",()=>new{ProductName=\"Tastiera\"});"),
("Serializzare enum come stringa",'builder.Services.ConfigureHttpJsonOptions(o=>o.SerializerOptions.Converters.Add(new System.Text.Json.Serialization.JsonStringEnumConverter()));',"app.MapGet(\"/demo\",()=>new{status=State.Ready});",'public enum State{Ready,Done}'),
("Nascondere una proprietà JSON interna",'',"app.MapGet(\"/demo\",()=>new Person());",'public class Person{public string Name{get;}="Ada";[System.Text.Json.Serialization.JsonIgnore]public string Internal{get;}="privato";}'),
("Ricevere DateOnly da query",'',"app.MapGet(\"/demo\",(DateOnly day)=>new{day,next=day.AddDays(1)});"),
("Verificare API key da ambiente",'',"app.MapGet(\"/demo\",(HttpRequest r,IConfiguration c)=>{var expected=c[\"DemoApiKey\"];if(string.IsNullOrEmpty(expected))return Results.Problem(\"Configurare DemoApiKey\",statusCode:503);return r.Headers[\"X-Api-Key\"]==expected?Results.Ok(new{ok=true}):Results.Unauthorized();});"),
("Registrare shutdown applicazione",'',"app.Lifetime.ApplicationStopping.Register(()=>app.Logger.LogInformation(\"Arresto richiesto\"));app.MapGet(\"/demo\",()=>new{ok=true});"),
("Aggiungere endpoint HEAD dedicato",'',"app.MapMethods(\"/demo\",new[]{\"HEAD\"},(HttpResponse r)=>{r.ContentType=\"text/plain\";return Results.Ok();});"),
("Restituire status202 per lavoro accettato",'',"app.MapPost(\"/jobs\",()=>Results.Accepted(\"/jobs/1\",new{id=1,status=\"accepted-demo\"}));app.MapGet(\"/jobs/{id:int}\",(int id)=>new{id,status=\"demo-only\"});"),
("Separare endpoint extension in file dedicato",'',"app.MapCatalog();",None,{'CatalogEndpoints.cs':'public static class CatalogEndpoints{public static void MapCatalog(this WebApplication app){app.MapGet("/catalog",()=>new[]{"Python","SQL"});}}'}),
("Rilevare disconnessione durante streaming",'',"app.MapGet(\"/events\",async(HttpContext c)=>{c.Response.ContentType=\"text/event-stream\";for(var i=0;i<3&&!c.RequestAborted.IsCancellationRequested;i++){await c.Response.WriteAsync($\"data: {i}\\n\\n\",c.RequestAborted);await c.Response.Body.FlushAsync(c.RequestAborted);await Task.Delay(100,c.RequestAborted);}});"),
]

def files(config,routes,tail='',extra=None):
    return {'Demo.csproj':CSPROJ,'Program.cs':PRE+config+'\nvar app=builder.Build();\n'+routes+'\napp.Run();\n'+(tail or ''),**(extra or {})}

def build_all():
    b=Book('aspnet','ASP.NET Core10; .NET SDK10',['https://learn.microsoft.com/en-us/aspnet/core/?view=aspnetcore-10.0'],'SDK.NET10 e browser. Eseguire dotnet run --urls http://127.0.0.1:5000. Ogni esempio è un progetto separato; dati in memoria solo dimostrativi.')
    for row in ROWS:
        title,config,routes,*rest=row
        tail=rest[0] if rest else '';extra=rest[1] if len(rest)>1 else None
        add(b,title,files(config,routes,tail,extra),commands='dotnet restore\ndotnet run --urls http://127.0.0.1:5000',note='Demo.csproj definisce il progetto Web; Program.cs registra servizi prima di Build e middleware/rotte prima di Run. Richiama la rotta indicata dal metodo Map con curl o browser; usa JSON per i body dei record. I cookie Secure=false sono soltanto per il laboratorio HTTP locale.')
    projects=[
      ('Progetto: API prodotti con repository concorrente',{'Product.cs':'public record Product(int Id,string Name,decimal Price);public record NewProduct(string Name,decimal Price);','ProductStore.cs':'using System.Collections.Concurrent;public class ProductStore{private readonly ConcurrentDictionary<int,Product> rows=new();private int next;public Product Add(NewProduct x){var p=new Product(Interlocked.Increment(ref next),x.Name.Trim(),x.Price);rows[p.Id]=p;return p;}public IEnumerable<Product> All()=>rows.Values.OrderBy(x=>x.Id);public Product? Find(int id)=>rows.GetValueOrDefault(id);}','Program.cs':'var b=WebApplication.CreateBuilder(args);b.Services.AddSingleton<ProductStore>();var app=b.Build();app.MapGet("/products",(ProductStore s)=>s.All());app.MapGet("/products/{id:int}",(int id,ProductStore s)=>s.Find(id) is Product p?Results.Ok(p):Results.NotFound());app.MapPost("/products",(NewProduct p,ProductStore s)=>string.IsNullOrWhiteSpace(p.Name)||p.Price<0?Results.BadRequest("Nome e prezzo non negativo richiesti"):Results.Created("/products",s.Add(p)));app.Run();','requests.http':'@host=http://127.0.0.1:5000\nGET {{host}}/products\n###\nPOST {{host}}/products\nContent-Type: application/json\n\n{"name":"Tastiera","price":50}\n###\nGET {{host}}/products/1'},'POST/products crea, GET elenca e legge per ID. Repository thread safe ma volatile: riavvio azzera. requests.http contiene prove ripetibili.'),
      ('Progetto: servizio preventivi con validazione Decimal',{'Quote.cs':'public record Quote(decimal Price,int Quantity,decimal Discount);public static class Pricing{public static decimal Total(Quote q){if(q.Price<0||q.Quantity<1||q.Discount<0||q.Discount>100)throw new ArgumentException("Valori invalidi");return decimal.Round(q.Price*q.Quantity*(1-q.Discount/100),2,MidpointRounding.AwayFromZero);}}','Program.cs':'var b=WebApplication.CreateBuilder(args);var app=b.Build();app.MapPost("/quote",(Quote q)=>{try{return Results.Ok(new{total=Pricing.Total(q)});}catch(ArgumentException e){return Results.BadRequest(new{error=e.Message});}});app.MapGet("/health",()=>Results.Ok(new{ok=true}));app.Run();','requests.http':'POST http://127.0.0.1:5000/quote\nContent-Type: application/json\n\n{"price":10,"quantity":3,"discount":10}\n###\nPOST http://127.0.0.1:5000/quote\nContent-Type: application/json\n\n{"price":-1,"quantity":1,"discount":0}'},'Il preventivo10×3 con sconto10% restituisce27.00; prezzo negativo risponde400. La logica economica usa decimal e vive fuori dagli endpoint.')]
    for title,extra,note in projects:
        f={'Demo.csproj':CSPROJ,**extra,'README.md':'# '+title+'\n'+note+'\nEseguire dotnet restore e dotnet run --urls http://127.0.0.1:5000. Usare requests.http da VSCode REST Client oppure curl equivalente. Nessun database o servizio esterno.'}
        add(b,title,f,commands='dotnet restore\ndotnet run --urls http://127.0.0.1:5000',project=True,section='Progetti completi',note=note,expected=note)
    from web_lifecycle import apply
    apply(b)
    assert len(b.recipes)==65,len(b.recipes)
    b.save()

if __name__=='__main__':build_all()
