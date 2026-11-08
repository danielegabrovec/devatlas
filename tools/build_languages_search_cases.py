"""Curated language search acceptance cases, without consulting the search implementation."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CASES=[
 ("python leggere CSV con virgole dentro un campo","python","Analizzare campi CSV con virgole tra virgolette"),
 ("python elaborare righe senza caricare tutto il file","python","Leggere un file riga per riga"),
 ("python chiamata bloccante dentro asyncio","python","Spostare lavoro bloccante in un thread"),
 ("C++ out_of_range accesso vector","cpp","Controllare indici con vector::at"),
 ("cpp vista su array senza copiare i dati","cpp","Accedere a una sequenza con span"),
 ("C++ trasferire proprietà esclusiva di un oggetto","cpp","Gestire proprietà esclusiva con unique_ptr"),
 ("C# convertire input numero senza throw","csharp","Convertire un intero senza eccezioni"),
 ("dotnet aggiornare contatori thread safe per chiave","csharp","Aggiornare un dizionario concorrente"),
 ("C# rilevare overflow di int","csharp","Rilevare overflow aritmetico"),
 ("javascript togliere ripetizioni mantenendo ordine","javascript","Deduplicare un array con Set"),
 ("js callback perde this del metodo","javascript","Fissare this con bind"),
 ("javascript risultati di promise anche se falliscono","javascript","Raccogliere successi e fallimenti asincroni"),
 ("typescript JSON esterno senza any","typescript","Validare un oggetto JSON sconosciuto"),
 ("ts funzione conserva il tipo dell argomento","typescript","Mantenere il tipo con una funzione generica"),
 ("typescript controllare tutti i casi di union","typescript","Controllare l'esaustività con never"),
 ("rust trasferire una stringa a un worker","rust","Trasferire proprietà a un thread"),
 ("rust condividere contatore senza data race","rust","Condividere un contatore con Arc e Mutex"),
 ("rust restituire assenza senza null","rust","Usare un default con Option"),
 ("go annullare goroutine tramite contesto","go","Propagare cancellazione con context"),
 ("golang copia slice backing array indipendente","go","Copiare una slice senza condividere i dati"),
 ("go JSON rifiutare campi sconosciuti","go","Rifiutare proprietà JSON sconosciute"),
 ("java importi senza errore floating point","java","Calcolare importi esatti con BigDecimal"),
 ("java chiudere risorse automaticamente","java","Rilasciare automaticamente con try-with-resources"),
 ("java raggruppare parole e contare","java","Raggruppare e contare con Collectors"),
 ("C realloc fallisce conservare memoria originale","c","Ridimensionare con realloc senza perdere il puntatore"),
 ("C copiare buffer sovrapposti","c","Spostare memoria sovrapposta con memmove"),
 ("C convertire testo a intero controllando limiti","c","Convertire un intero con strtol"),
]


def main():
    by_title={}
    for stack in {case[1] for case in CASES}:
        for path in (ROOT/"catalog"/stack).glob("*/recipe.json"):
            data=json.loads(path.read_text(encoding="utf-8"))
            by_title[(stack,data["title"])]=data["id"]
    output=[{"query":query,"expected_ids":[by_title[(stack,title)]]} for query,stack,title in CASES]
    assert len(output)==27
    destination=ROOT/"reports"/"search-cases-languages.json"
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding="utf-8")
    print("27 language search cases")


if __name__=="__main__":main()
