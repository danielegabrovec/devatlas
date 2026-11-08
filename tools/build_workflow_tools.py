"""Original local workflow examples; generation never runs their commands."""
from __future__ import annotations
import json
import textwrap
from catalog_support import Book, STACKS, slug
from desktop_tools_common import save_book

PS = [
("Creare oggetti strutturati nella pipeline","Usare PSCustomObject invece di righe testuali non tipizzate.",'$items = @([pscustomobject]@{Name="api";Port=8000},[pscustomobject]@{Name="web";Port=3000})\n$items | Format-Table -AutoSize'),
("Filtrare oggetti con Where-Object","Selezionare valori prima della formattazione finale.",'1..10 | Where-Object { $_ % 2 -eq 0 }'),
("Ordinare una collezione per proprietà","Ordinare oggetti numerici senza convertirli in testo.",'@([pscustomobject]@{Name="B";Size=20},[pscustomobject]@{Name="A";Size=3}) | Sort-Object Size | Format-Table'),
("Proiettare proprietà con Select-Object","Restituire soltanto i campi richiesti e una colonna calcolata.",'Get-Process | Select-Object -First 5 Name,Id,@{Name="MemoryMiB";Expression={[math]::Round($_.WorkingSet64/1MB,1)}}'),
("Raggruppare elementi e contarli","Usare Group-Object per aggregare eventi per categoria.",'"build","test","build","package","test","test" | Group-Object | Sort-Object Count -Descending | Select-Object Name,Count'),
("Esportare e reimportare un CSV","Mantenere intestazioni e Unicode con Export-Csv e Import-Csv.",'$path = Join-Path ([IO.Path]::GetTempPath()) ("demo-"+[guid]::NewGuid()+".csv")\n@([pscustomobject]@{Nome="Città";Valore=42}) | Export-Csv -LiteralPath $path -NoTypeInformation -Encoding utf8\nImport-Csv -LiteralPath $path'),
("Serializzare JSON annidato con profondità esplicita","Evitare che oggetti annidati vengano trasformati in stringhe.",'$value = @{Project="Demo";Build=@{Mode="Debug";Targets=@("app","tests")}}\n$json = $value | ConvertTo-Json -Depth 6\n$json\n($json | ConvertFrom-Json).Build.Targets'),
("Gestire parametri obbligatori in uno script","Validare un parametro prima di eseguire il corpo.",'param([Parameter(Mandatory)][ValidateSet("Debug","Release")][string]$Configuration)\n"Configurazione: $Configuration"'),
("Catturare errori di filesystem con try e catch","Convertire l'errore in un messaggio gestito usando ErrorAction Stop.",'try { Get-Content -LiteralPath "file-che-non-esiste.txt" -ErrorAction Stop } catch { "Lettura fallita: $($_.Exception.Message)" }'),
("Costruire percorsi con spazi senza concatenazioni fragili","Usare Join-Path e LiteralPath per evitare espansione wildcard.",'$folder = Join-Path ([IO.Path]::GetTempPath()) ("demo cartella "+[guid]::NewGuid())\nNew-Item -ItemType Directory -Path $folder | Out-Null\n$file = Join-Path $folder "appunti [1].txt"\nSet-Content -LiteralPath $file -Value "Ciao" -Encoding utf8\nGet-Content -LiteralPath $file'),
("Leggere un file UTF-8 come stringa unica","Usare Raw per preservare righe e spazi di un documento.",'$file = Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString()+".txt")\nSet-Content -LiteralPath $file -Value "prima`nseconda" -Encoding utf8\n$text = Get-Content -LiteralPath $file -Raw -Encoding utf8\n$text.Length'),
("Calcolare SHA-256 di un file locale","Produrre un digest verificabile senza leggere manualmente i byte.",'$file = Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString()+".txt")\nSet-Content -LiteralPath $file -Value "contenuto" -Encoding utf8\nGet-FileHash -LiteralPath $file -Algorithm SHA256'),
("Creare un archivio ZIP da una cartella dedicata","Usare un'area temporanea per distinguere sorgenti e archivio.",'$folder = Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString())\nNew-Item -ItemType Directory -Path $folder | Out-Null\nSet-Content -LiteralPath (Join-Path $folder "readme.txt") -Value "Pacchetto"\n$zip = $folder+".zip"\nCompress-Archive -Path (Join-Path $folder "*") -DestinationPath $zip\nGet-Item -LiteralPath $zip'),
("Estrarre uno ZIP in una cartella nuova","Creare prima un archivio dimostrativo e verificare il file estratto.",'$root = Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString())\nNew-Item -ItemType Directory -Path $root | Out-Null\nSet-Content -LiteralPath (Join-Path $root "note.txt") -Value "Demo"\nCompress-Archive -LiteralPath (Join-Path $root "note.txt") -DestinationPath ($root+".zip")\nExpand-Archive -LiteralPath ($root+".zip") -DestinationPath ($root+"-estratto")\nGet-ChildItem -LiteralPath ($root+"-estratto")'),
("Cercare righe con Select-String","Estrarre numero di riga e contenuto corrispondente a un pattern.",'"INFO start","ERROR esempio","INFO end" | Select-String -Pattern "^ERROR" | Select-Object LineNumber,Line'),
("Sostituire un pattern con gruppi nominati","Usare il motore regex per normalizzare codici testuali.",'$text="v1.2.3"\n$text -replace "^v(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)$",\'${major}-${minor}-${patch}\''),
("Misurare la durata di un comando","Usare Measure-Command senza dipendere dall'orologio di calendario.",'$elapsed = Measure-Command { $sum = (1..10000 | Measure-Object -Sum).Sum }\n$elapsed.TotalMilliseconds'),
("Invocare un eseguibile con argomenti separati","Usare l'operatore di chiamata e controllare il codice di uscita.",'$exe=(Get-Command pwsh).Source\n& $exe -NoProfile -Command "exit 7"\n$code=$LASTEXITCODE\n"Codice: $code"\nif($code -ne 7){throw "Codice inatteso"}'),
("Definire una funzione con pipeline input","Elaborare ogni oggetto nella sezione process di una funzione avanzata.",'function Get-Square { [CmdletBinding()] param([Parameter(ValueFromPipeline)][int]$Value) process { $Value*$Value } }\n1..5 | Get-Square'),
("Usare una tabella hash come indice","Effettuare lookup per chiave senza scandire tutta una lista.",'$ports=@{api=8000;web=3000}\nif($ports.ContainsKey("api")){"API: $($ports.api)"}'),
("Eseguire operazioni in parallelo con limite","Usare ForEach-Object Parallel in PowerShell 7 e ordinare il risultato.",'1..8 | ForEach-Object -Parallel { [pscustomobject]@{Value=$_;Square=$_*$_} } -ThrottleLimit 3 | Sort-Object Value'),
("Avviare e raccogliere un job locale","Ricevere l'output e rimuovere soltanto il job appena creato.",'$job=Start-Job -ScriptBlock { 1..5 | Measure-Object -Sum }\ntry { $job | Wait-Job | Receive-Job } finally { Remove-Job -Job $job }'),
("Elencare variabili d'ambiente senza esportare segreti","Interrogare esclusivamente il nome controllato dalla ricetta.",'$env:RECIPE_MODE="debug"\n[Environment]::GetEnvironmentVariable("RECIPE_MODE","Process")\nRemove-Item Env:RECIPE_MODE'),
("Verificare la disponibilità di un comando","Usare Get-Command ErrorAction SilentlyContinue per una dipendenza opzionale.",'$tool=Get-Command git -ErrorAction SilentlyContinue\nif($null -eq $tool){"Git non trovato"}else{& $tool.Source --version}'),
("Leggere il contenuto di una directory in modo stabile","Usare LiteralPath e ordinare esplicitamente i risultati.",'Get-ChildItem -LiteralPath . -File | Sort-Object Name | Select-Object Name,Length'),
("Produrre un report HTML da oggetti","Convertire una piccola tabella in un file HTML autonomo.",'$file=Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString()+".html")\n@([pscustomobject]@{Step="Build";Status="OK"},[pscustomobject]@{Step="Test";Status="OK"}) | ConvertTo-Html -Title "Report locale" | Set-Content -LiteralPath $file -Encoding utf8\n$file'),
("Implementare ShouldProcess in una funzione","Fornire WhatIf per un'operazione con effetti controllati.",'function Set-DemoValue { [CmdletBinding(SupportsShouldProcess)] param([string]$Value) if($PSCmdlet.ShouldProcess("stato demo","Imposta $Value")){"Valore applicato: $Value"} }\nSet-DemoValue -Value "release" -WhatIf'),
("Analizzare un documento XML senza stringhe concatenate","Usare la struttura XML per selezionare attributi.",'[xml]$document=\'<project><target name="build"/><target name="test"/></project>\'\n$document.SelectNodes("/project/target") | ForEach-Object { $_.GetAttribute("name") }'),
("Gestire risorse IDisposable con finally","Chiudere esplicitamente un MemoryStream anche in presenza di errori.",'$stream=[IO.MemoryStream]::new()\ntry { $bytes=[Text.Encoding]::UTF8.GetBytes("Ciao");$stream.Write($bytes,0,$bytes.Length);$stream.Length } finally { $stream.Dispose() }'),
("Confrontare due insiemi di file attesi","Usare Compare-Object per distinguere elementi mancanti e aggiuntivi.",'$expected=@("app.exe","README.md","LICENSE.txt")\n$actual=@("app.exe","README.md","debug.log")\nCompare-Object -ReferenceObject $expected -DifferenceObject $actual'),
]

BASH = [
("Proteggere variabili e percorsi con spazi","Quotare espansioni e usare array per argomenti distinti.",'args=("prima parola" "seconda parola")\nprintf "<%s>\\n" "${args[@]}"'),
("Leggere righe senza perdere backslash","Usare IFS vuoto e read -r per input testuale.",'while IFS= read -r line; do printf "Riga: %s\\n" "$line"; done <<\'DATA\'\nC:\\demo\\file\nseconda riga\nDATA'),
("Verificare argomenti obbligatori","Interrompere lo script con messaggio e codice di uscita non nullo.",'if (( $# != 1 )); then printf "Uso: bash example.sh nome\\n" >&2; exit 2; fi\nprintf "Nome: %s\\n" "$1"'),
("Creare file temporanei e pulirli con trap","Registrare la pulizia prima di utilizzare il file temporaneo.",'scratch=$(mktemp)\ntrap \'rm -f -- "$scratch"\' EXIT\nprintf "dati temporanei\\n" > "$scratch"\ncat -- "$scratch"'),
("Gestire un errore previsto con if","Evitare che set -e trasformi una ricerca senza risultati in crash.",'if printf "alpha\\nbeta\\n" | grep -q "gamma"; then printf "trovato\\n"; else printf "nessuna corrispondenza\\n"; fi'),
("Definire una funzione con output e return","Restituire dati su stdout e usare return per lo stato.",'square(){ local value=$1; printf "%d\\n" "$((value*value))"; }\nresult=$(square 7)\nprintf "Risultato: %s\\n" "$result"'),
("Iterare nomi file tramite separatore NUL","Usare find -print0 per gestire spazi e newline nei nomi.",'find . -maxdepth 1 -type f -print0 | while IFS= read -r -d "" path; do printf "%q\\n" "$path"; done'),
("Selezionare campi con awk","Calcolare il totale di una colonna numerica.",'printf "api 12\\nweb 8\\n" | awk \'{total+=$2} END {print total}\''),
("Sostituire testo con sed senza modificare l'originale","Applicare una sostituzione a stdin e stampare il risultato.",'printf "mode=debug\\nname=demo\\n" | sed \'s/^mode=.*/mode=release/\''),
("Ordinare e contare righe uniche","Combinare sort e uniq -c per una frequenza deterministica.",'printf "test\\nbuild\\ntest\\npackage\\n" | LC_ALL=C sort | uniq -c'),
("Misurare la durata di una pipeline","Usare time sul blocco completo anziché su un solo comando.",'time { printf "%s\\n" {1..1000} | awk \'{sum+=$1} END {print sum}\'; }'),
("Validare un intero con espressione regolare Bash","Usare [[ =~ ]] prima di un'operazione aritmetica.",'value="42"\nif [[ $value =~ ^[0-9]+$ ]]; then printf "%d\\n" "$((10#$value+1))"; else exit 2; fi'),
("Associare chiavi a valori in Bash","Usare un array associativo disponibile da Bash 4.",'declare -A ports=([api]=8000 [web]=3000)\nprintf "API: %s\\n" "${ports[api]}"'),
("Catturare il codice di uscita di un processo","Gestire esplicitamente un comando che termina con codice atteso.",'code=0\nbash -c \'exit 7\' || code=$?\nprintf "Codice: %d\\n" "$code"\n[[ $code -eq 7 ]]'),
("Avviare due lavori e attenderne la conclusione","Conservare i PID e usare wait per entrambi.",'(printf "Lavoro A\\n") &\nfirst=$!\n(printf "Lavoro B\\n") &\nsecond=$!\nwait "$first"\nwait "$second"'),
("Analizzare opzioni brevi con getopts","Gestire -n e una opzione sconosciuta con messaggio d'uso.",'name="mondo"\nwhile getopts ":n:" flag; do case "$flag" in n) name=$OPTARG;; *) printf "Uso: -n nome\\n" >&2; exit 2;; esac; done\nprintf "Ciao %s\\n" "$name"'),
("Controllare dipendenze prima di usarle","Usare command -v e terminare con un messaggio mirato.",'for tool in tar sha256sum; do command -v "$tool" >/dev/null || { printf "Manca %s\\n" "$tool" >&2; exit 1; }; done\nprintf "Dipendenze presenti\\n"'),
("Creare e ispezionare un archivio tar","Lavorare in una directory temporanea per un esempio ripetibile.",'scratch=$(mktemp -d)\ntrap \'rm -rf -- "$scratch"\' EXIT\nprintf "contenuto\\n" > "$scratch/note.txt"\ntar -czf "$scratch/package.tar.gz" -C "$scratch" note.txt\ntar -tzf "$scratch/package.tar.gz"'),
("Calcolare e verificare un checksum SHA-256","Usare sha256sum -c nel medesimo percorso relativo.",'scratch=$(mktemp -d)\ntrap \'rm -rf -- "$scratch"\' EXIT\nprintf "contenuto\\n" > "$scratch/app.txt"\n(cd "$scratch"; sha256sum app.txt > SHA256SUMS; sha256sum -c SHA256SUMS)'),
("Impostare una variabile soltanto per un comando","Limitare l'ambiente del processo figlio senza esportarlo nella shell intera.",'RECIPE_MODE=release bash -c \'printf "Modalità: %s\\n" "$RECIPE_MODE"\'\nprintf "Nella shell chiamante: %s\\n" "${RECIPE_MODE-non impostata}"'),
]

GIT = [
("Leggere lo stato compatto del repository","Distinguere indice e working tree con status --short.",'git status --short --branch'),
("Confrontare modifiche non indicizzate","Visualizzare una patch prima di aggiungerla all'indice.",'Add-Content README.md "Seconda riga"\ngit diff -- README.md'),
("Confrontare modifiche già indicizzate","Usare diff --cached per il contenuto del prossimo commit.",'Add-Content README.md "Riga indicizzata"\ngit add README.md\ngit diff --cached'),
("Aggiungere un solo file all'indice","Usare un percorso esplicito invece di includere file inattesi.",'Set-Content note.txt "Nota locale"\ngit add -- note.txt\ngit status --short'),
("Creare un commit con messaggio concreto","Salvare lo snapshot dell'indice, non i file non indicizzati.",'Set-Content note.txt "Nota locale"\ngit add note.txt\ngit commit -m "Aggiungi nota dimostrativa"\ngit log -1 --oneline'),
("Creare e selezionare un branch","Usare switch -c per un ramo nuovo dal commit corrente.",'git switch -c feature/note\ngit branch --show-current'),
("Tornare al branch principale","Cambiare branch con working tree pulito.",'git switch -c feature/note\ngit switch main\ngit branch --show-current'),
("Elencare branch con ultimo commit","Usare branch -vv per una panoramica locale.",'git branch feature/note\ngit branch -vv'),
("Unire un branch con merge esplicito","Conservare un nodo di merge anche se sarebbe possibile il fast forward.",'git switch -c feature/note\nSet-Content note.txt "Nota"\ngit add note.txt\ngit commit -m "Aggiungi nota"\ngit switch main\ngit merge --no-ff feature/note -m "Integra note"\ngit log --oneline --graph --all'),
("Creare un tag annotato locale","Associare metadati a un punto di rilascio senza pubblicarlo.",'git tag -a v0.1.0 -m "Prima versione dimostrativa"\ngit show v0.1.0 --stat'),
("Leggere la cronologia a grafo","Mostrare i riferimenti insieme ai commit in forma compatta.",'git log --oneline --decorate --graph --all'),
("Limitare la cronologia a un file","Seguire soltanto le modifiche al percorso richiesto.",'git log --oneline -- README.md'),
("Visualizzare il contenuto di un commit","Leggere un file dallo snapshot senza cambiarne la copia locale.",'git show HEAD:README.md'),
("Trovare l'origine delle righe con blame","Mostrare commit e autore per ogni riga del file.",'git blame -- README.md'),
("Cercare testo nei file tracciati","Usare git grep per escludere file ignorati e non tracciati.",'git grep -n "Demo" -- README.md'),
("Ignorare cartelle generate","Creare .gitignore e verificare la regola applicata.",'Set-Content .gitignore "build/`n.venv/"\nNew-Item -ItemType Directory build | Out-Null\nSet-Content build/output.txt "generato"\ngit check-ignore -v build/output.txt'),
("Rimuovere un file soltanto dall'indice","Usare rm --cached per mantenere il file nel working tree.",'git rm --cached README.md\ngit status --short\nTest-Path README.md'),
("Togliere una modifica dallo staging","Usare restore --staged mantenendo la modifica nel file.",'Add-Content README.md "Modifica"\ngit add README.md\ngit restore --staged README.md\ngit status --short'),
("Ripristinare un file di prova dal commit","Scartare consapevolmente soltanto la modifica del repository temporaneo.",'Add-Content README.md "Da scartare"\ngit restore --source=HEAD -- README.md\ngit diff --exit-code -- README.md'),
("Accantonare modifiche con stash","Conservare e riapplicare modifiche non committate.",'Add-Content README.md "Lavoro in corso"\ngit stash push -m "Demo WIP"\ngit stash list\ngit stash pop'),
("Accantonare anche file non tracciati","Usare -u quando lo stash deve includere nuovi file.",'Set-Content new.txt "Nuovo"\ngit stash push -u -m "Include nuovi file"\ngit stash pop\ngit status --short'),
("Annullare un commit con revert","Creare una nuova modifica inversa senza riscrivere la cronologia.",'Set-Content note.txt "Nota"\ngit add note.txt\ngit commit -m "Aggiungi nota"\ngit revert --no-edit HEAD\ngit log -2 --oneline'),
("Correggere l'ultimo messaggio locale","Usare amend soltanto su un commit non condiviso del repository dimostrativo.",'git commit --amend -m "Inizializza repository dimostrativo"\ngit log -1 --oneline'),
("Applicare un singolo commit con cherry-pick","Trasferire una modifica da un ramo senza unire tutta la storia.",'git switch -c feature/note\nSet-Content note.txt "Nota"\ngit add note.txt\ngit commit -m "Aggiungi nota"\n$revision=git rev-parse HEAD\ngit switch main\ngit cherry-pick $revision'),
("Ribasare un ramo locale su main","Riapplicare un commit locale dopo una modifica indipendente di main.",'git switch -c feature/note\nSet-Content note.txt "Nota"\ngit add note.txt\ngit commit -m "Nota feature"\ngit switch main\nSet-Content config.txt "config"\ngit add config.txt\ngit commit -m "Config principale"\ngit switch feature/note\ngit rebase main\ngit log --oneline --graph'),
("Consultare reflog per recuperare un riferimento","Leggere i movimenti locali di HEAD senza effettuare reset.",'git switch -c feature/demo\ngit switch main\ngit reflog -5 --oneline'),
("Esportare uno snapshot ZIP tracciato","Usare git archive per escludere file non versionati.",'git archive --format=zip --output=source.zip HEAD\nGet-Item source.zip'),
("Produrre una patch del commit corrente","Usare format-patch per trasferire una modifica senza un server.",'Set-Content note.txt "Nota"\ngit add note.txt\ngit commit -m "Aggiungi nota"\ngit format-patch -1 HEAD --output-directory patches'),
("Verificare una patch prima di applicarla","Usare apply --check contro la base corretta della patch.",'Add-Content README.md "Modifica patch"\ngit diff --output=change.patch\ngit restore README.md\ngit apply --check change.patch\ngit apply change.patch\ngit diff -- README.md'),
("Creare un remote bare locale","Usare un repository su disco per esercitarsi senza rete o credenziali.",'$remote=Join-Path ([IO.Path]::GetTempPath()) ("bare-"+[guid]::NewGuid()+".git")\ngit init --bare $remote\ngit remote add origin $remote\ngit push -u origin main\ngit remote -v'),
("Scaricare riferimenti senza effettuare merge","Usare fetch su un remote locale configurato nella dimostrazione.",'$remote=Join-Path ([IO.Path]::GetTempPath()) ("bare-"+[guid]::NewGuid()+".git")\ngit init --bare $remote\ngit remote add origin $remote\ngit push -u origin main\ngit fetch origin\ngit branch -r'),
("Clonare un repository locale in una nuova cartella","Distinguere la copia di lavoro di origine dalla nuova clone.",'$target=Join-Path ([IO.Path]::GetTempPath()) ("clone-"+[guid]::NewGuid())\ngit clone . $target\ngit -C $target log -1 --oneline'),
("Aprire un secondo working tree su un ramo nuovo","Usare worktree per evitare stash durante lavori paralleli.",'$target=Join-Path ([IO.Path]::GetTempPath()) ("worktree-"+[guid]::NewGuid())\ngit worktree add -b feature/parallel $target\ngit worktree list'),
("Rilevare spazi problematici nelle patch","Usare diff --check prima di creare il commit.",'Add-Content README.md "Riga valida"\ngit diff --check\nif($LASTEXITCODE -ne 0){throw "Problemi whitespace"}'),
("Normalizzare i fine riga tramite gitattributes","Dichiarare LF per script e testo indipendentemente dalla piattaforma.",'Set-Content .gitattributes "* text=auto`n*.sh text eol=lf`n*.ps1 text eol=crlf"\ngit add .gitattributes\ngit check-attr text eol -- README.md example.sh'),
("Elencare soltanto i file tracciati","Usare ls-files come inventario dei sorgenti versionati.",'git ls-files'),
("Contare aggiunte e rimozioni in una modifica","Usare diff --numstat per un formato elaborabile.",'Add-Content README.md "Nuova riga"\ngit diff --numstat'),
("Controllare integrità degli oggetti Git","Usare fsck in lettura su un repository locale.",'git fsck --full'),
("Trovare un commit tramite messaggio","Filtrare log con --grep e mostrare identificatori compatti.",'git log --oneline --grep="Iniziale"'),
]

GIT_SETUP='''$work=Join-Path ([IO.Path]::GetTempPath()) ("git-recipe-"+[guid]::NewGuid())
git init -b main $work
Set-Location -LiteralPath $work
git config user.name "Autore Demo"
git config user.email "demo@example.invalid"
Set-Content README.md "# Demo"
git add README.md
git commit -m "Iniziale"
'''

def basic(book,items,filename,shell,commands,extra=""):
    for title,description,code in items:
        if book.stack=="powershell":
            if code.startswith("param("):
                contents=code.split("\n",1)[0]+"\nSet-StrictMode -Version Latest\n$ErrorActionPreference='Stop'\n"+code.split("\n",1)[1]
            else:contents="Set-StrictMode -Version Latest\n$ErrorActionPreference='Stop'\n"+code
        elif book.stack=="bash":contents="#!/usr/bin/env bash\nset -euo pipefail\n"+code
        else:contents=GIT_SETUP+code
        use=commands
        if title=="Gestire parametri obbligatori in uno script":use+=' -Configuration Debug'
        if title=="Verificare argomenti obbligatori":use+=' esempio'
        book.add(slug(title),title,description,{filename:contents},commands=[{"shell":shell,"os":"Linux" if shell=="Bash" else "Windows","cwd":".","code":use}],explanation=f"## Scopo\n{description}\n\n## Esecuzione\nSalva {filename} in una cartella nuova ed esegui il comando da quella stessa cartella. {extra}\n\n## Lettura del risultato\n{description} Il codice è fornito per intero: leggi gli argomenti e i percorsi prima dell'esecuzione. Gli esempi che scrivono dati creano file temporanei o operano soltanto nel repository dimostrativo indicato.\n\n## Compatibilità\n{book.prerequisites}",expected=description,tags=[book.stack,slug(title),"workflow"],errors=["Comando non trovato: verificare la dipendenza e riaprire il terminale dopo l'installazione.","Accesso negato: scegliere una cartella di lavoro o temporanea scrivibile."])

def build_shells_git():
    assert len(PS)==30,len(PS)
    assert len(BASH)==20,len(BASH)
    assert len(GIT)==39,len(GIT)
    ps=Book("powershell","PowerShell 7.4+",["https://learn.microsoft.com/powershell/"],"PowerShell 7.4 o successivo (pwsh), non Windows PowerShell 5.1.",os=["Windows"])
    basic(ps,PS,"example.ps1","PowerShell","pwsh -NoProfile -File .\\example.ps1")
    save_book(ps)
    bash=Book("bash","Bash 5; GNU coreutils",["https://www.gnu.org/software/bash/manual/bash.html"],"Linux o distribuzione Linux in WSL, Bash 5 e strumenti GNU. Gli script non sono dichiarati verificati su macOS.",os=["Linux"])
    basic(bash,BASH,"example.sh","Bash","bash ./example.sh")
    save_book(bash)
    git=Book("git","Git 2.45+",["https://git-scm.com/docs"],"Git 2.45+ e PowerShell 7. La ricetta crea un repository nuovo nella cartella temporanea; non eseguirla dentro un repository di produzione per risparmiare il setup.",os=["Windows"])
    basic(git,GIT,"example.ps1","PowerShell","pwsh -NoProfile -File .\\example.ps1","Lo script crea un repository temporaneo, configura un autore soltanto localmente e vi si posiziona. Non contatta server remoti; gli eventuali remote sono bare repository locali.")
    script=GIT_SETUP+'''git switch -c feature/calcolo
Set-Content calc.ps1 'param([int]$Value) $Value * $Value'
git add calc.ps1
git commit -m "Aggiungi funzione quadrato"
$actual=& ./calc.ps1 -Value 7
if($actual -ne 49){throw "Test fallito"}
git switch main
git merge --no-ff feature/calcolo -m "Integra calcolo verificato"
git tag -a v0.1.0 -m "Versione demo"
git log --oneline --graph --decorate --all
'''
    git.add("progetto-branch-test","Progetto completo: branch, test e merge locali","Un laboratorio Git autonomo crea un repository isolato, implementa una funzione, esegue un controllo e integra il ramo.",{"lab.ps1":script,"README.md":"# Laboratorio Git\nEseguire lab.ps1 con PowerShell 7. Usa soltanto repository temporanei e nessuna rete.\n"},project=True,section="Progetti completi",commands="pwsh -NoProfile -File .\\lab.ps1",explanation="## Obiettivo\nIl laboratorio distingue il contenuto del branch feature dal ramo main. Un controllo locale verifica 7²=49 prima del merge. Il tag annotato identifica il risultato.\n\n## Avvio\nSalva i file nella stessa cartella e lancia lab.ps1. Il percorso temporaneo viene creato ad ogni esecuzione; il repository corrente non è modificato. La cronologia finale mostra un merge e il tag v0.1.0.\n\n## Limite\nNessuna pubblicazione, fetch Internet o invio a provider Git.",expected="La cronologia contiene commit iniziale, feature, merge e tag v0.1.0.",tags=["project","git","branch","merge","test"],errors=["Git non trovato nel PATH.","PowerShell non può eseguire script se la politica locale lo impedisce: usare un ambiente dove gli script locali sono consentiti."])
    save_book(git)

if __name__=="__main__":build_shells_git()
