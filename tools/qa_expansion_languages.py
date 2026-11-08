"""Scoped evidence for the 110 new recipes; no modification of original stacks."""
from __future__ import annotations
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/".cache/expansion-languages"
QUOTAS={"kotlin":30,"swift":25,"php":30,"dart":25}
PHP=ROOT/".cache/php-8.4.27-1/php.exe"


def execute(command,folder,timeout=45):
    started=time.perf_counter()
    try:
        process=subprocess.run(command,cwd=folder,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=timeout)
        return {"ok":process.returncode==0,"command":command,"returncode":process.returncode,"seconds":round(time.perf_counter()-started,3),"output":(process.stdout+process.stderr)[-6000:]}
    except Exception as error:return {"ok":False,"command":command,"seconds":round(time.perf_counter()-started,3),"output":str(error)}


def compiler_paths():
    cache=Path(os.environ["USERPROFILE"])/".gradle/caches/modules-2/files-2.1"
    coordinates=[("org.jetbrains.kotlin","kotlin-compiler-embeddable","2.3.21"),("org.jetbrains.kotlin","kotlin-stdlib","2.3.21"),("org.jetbrains.kotlin","kotlin-script-runtime","2.3.21"),("org.jetbrains.kotlin","kotlin-reflect","1.6.10"),("org.jetbrains.kotlin","kotlin-daemon-embeddable","2.3.21"),("org.jetbrains.kotlinx","kotlinx-coroutines-core-jvm","1.8.0"),("org.jetbrains","annotations","13.0")]
    paths=[]
    for group,name,version in coordinates:
        matches=list((cache/group/name/version).glob("*/*.jar"))
        assert matches,(group,name,version)
        paths.append(str(matches[0]))
    return paths,paths[1]


def main():
    WORK.mkdir(parents=True,exist_ok=True)
    temporary=WORK/"temp";temporary.mkdir(exist_ok=True)
    for key in ("TEMP","TMP","TMPDIR"):os.environ[key]=str(temporary)
    sys.path.insert(0,str(ROOT/".cache/expansion-parsers"))
    from tree_sitter_language_pack import get_parser,configure,PackConfig
    configure(PackConfig(cache_dir=str(ROOT/".cache/expansion-parser-grammars")))
    parsers={language:get_parser(language) for language in QUOTAS}
    recipes=[];results=[];retry_ids=None
    if "--retry-failed" in sys.argv or "--ids" in sys.argv:
        previous=json.loads((ROOT/"reports/expansion-languages-qa.json").read_text(encoding="utf-8"))
        retry_ids=set(sys.argv[sys.argv.index("--ids")+1].split(",")) if "--ids" in sys.argv else {item["id"] for item in previous["results"] if not item["ok"]}
        results=[item for item in previous["results"] if item["id"] not in retry_ids]
    for stack,quota in QUOTAS.items():
        paths=sorted((ROOT/"catalog"/stack).glob("*/recipe.json"));assert len(paths)==quota,(stack,len(paths))
        assert sum(json.loads(path.read_text(encoding="utf-8"))["project"] for path in paths)==1
        for path in paths:
            data=json.loads(path.read_text(encoding="utf-8"));folder=WORK/stack/data["id"];folder.mkdir(parents=True,exist_ok=True)
            sources=[]
            for asset in data["assets"]:
                if asset["role"]=="command":continue
                source=(path.parent/asset["source"]).read_text(encoding="utf-8")
                target=folder/asset["path"];target.parent.mkdir(parents=True,exist_ok=True);target.write_text(source,encoding="utf-8")
                sources.append((asset,target))
                if retry_ids is not None and data["id"] not in retry_ids:continue
                if target.suffix in (".kt",".kts",".swift",".php",".dart"):
                    tree=parsers[stack].parse(source.encode("utf-8"))
                    problems=[]
                    def walk(node):
                        if node.type=="ERROR" or node.is_missing:problems.append({"type":node.type,"line":node.start_point.row+1,"column":node.start_point.column+1,"text":source.encode()[node.start_byte:node.end_byte].decode(errors="replace")[:160]})
                        for child in node.children:walk(child)
                    if tree.root_node.has_error:walk(tree.root_node)
                    results.append({"id":data["id"],"file":asset["path"],"check":"tree-sitter syntax","ok":not tree.root_node.has_error,"problems":problems})
                elif target.suffix==".json":
                    try:json.loads(source);results.append({"id":data["id"],"file":asset["path"],"check":"JSON parse","ok":True})
                    except Exception as error:results.append({"id":data["id"],"file":asset["path"],"check":"JSON parse","ok":False,"output":str(error)})
            recipes.append((data,path,folder,sources))
    jars,stdlib=compiler_paths();runtime_cp=os.pathsep.join([stdlib,jars[-1]])
    compiler=["java","-cp",os.pathsep.join(jars),"org.jetbrains.kotlin.cli.jvm.K2JVMCompiler","-no-stdlib","-no-reflect","-classpath",runtime_cp,"-jvm-target","17"]
    jobs=[]
    for data,path,folder,files in recipes:
        if retry_ids is not None and data["id"] not in retry_ids:continue
        if data["stack"]=="kotlin" and not any(asset["role"]=="snippet" for asset,_ in files):
            mains=[str(target) for asset,target in files if target.suffix==".kt" and "test" not in target.relative_to(folder).parts]
            if data["project"]:mains=[str(target) for asset,target in files if target.suffix==".kt" and "/src/main/" in target.as_posix()]
            output=folder/"classes";output.mkdir(exist_ok=True)
            jobs.append((data["id"],"kotlin compile",compiler+["-d",str(output),*mains],folder))
        elif data["stack"]=="php":
            for asset,target in files:
                if target.suffix==".php":jobs.append((data["id"],"php lint",[str(PHP),"-l",str(target)],folder))
    def check(job):
        rid,kind,command,folder=job;result=execute(command,folder);result.update(id=rid,check=kind)
        if not result["ok"]:print("FAIL",rid,kind,result["output"][-2200:],flush=True)
        return result
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results.extend(pool.map(check,jobs))
    for data,path,folder,files in recipes:
        if retry_ids is not None and data["id"] not in retry_ids:continue
        if any(not item["ok"] for item in results if item["id"]==data["id"]):continue
        if data["stack"]=="kotlin" and not any(asset["role"]=="snippet" for asset,_ in files):
            # Program execution is separate from Gradle/interactive workflow claims.
            if "endpoint-http" in data["id"] or "debuggare" in data["id"]:continue
            if data["project"]:
                cli="InventoryCliKt";tests=folder/"test-classes";tests.mkdir(exist_ok=True)
                compile_tests=execute(compiler+["-d",str(tests),str(folder/"src/main/kotlin/Inventory.kt"),str(folder/"src/test/kotlin/InventoryTest.kt")],folder)
                compile_tests.update(id=data["id"],check="kotlin capstone tests compile");results.append(compile_tests)
                if compile_tests["ok"]:
                    test=execute(["java","-cp",str(tests)+os.pathsep+runtime_cp,"InventoryTestKt"],folder);test.update(id=data["id"],check="kotlin contracts execute");results.append(test)
            else:cli="ChecksKt" if (folder/"Checks.kt").exists() else "MainKt"
            run=execute(["java","-cp",str(folder/"classes")+os.pathsep+runtime_cp,cli],folder);run.update(id=data["id"],check="kotlin program execute");results.append(run)
        elif data["stack"]=="php":
            if (folder/"main.php").exists() and not (folder/"composer.json").exists():
                run=execute([str(PHP),"-d","extension_dir="+str(PHP.parent/"ext"),"-d","extension=pdo_sqlite","main.php"],folder);run.update(id=data["id"],check="php program execute");results.append(run)
            if (folder/"tests.php").exists():
                test=execute([str(PHP),"tests.php"],folder);test.update(id=data["id"],check="php contracts execute");results.append(test)
            if data["project"]:
                for command in ([str(PHP),"tests/smoke.php"],[str(PHP),"bin/addressbook.php","data/contacts.json","list"]):
                    result=execute(command,folder);result.update(id=data["id"],check="php capstone execute");results.append(result)
            if (folder/"build-phar.php").exists():
                for command in ([str(PHP),"-d","phar.readonly=0","build-phar.php"],[str(PHP),"dist/atlas.phar"]):
                    result=execute(command,folder);result.update(id=data["id"],check="php PHAR execute");results.append(result)
    report={"date":"2026-10-29","platform":"Windows x64","recipes":110,"projects":4,"quotas":QUOTAS,"toolchain":{"kotlin":"Kotlin compiler2.3.21 embeddable da cache Gradle, JDK25.0.4.1, targetJVM17","php":"PHP8.4.27-1 ufficiale NTSx64, locale .cache","syntax":"tree-sitter-language-pack1.22.1/tree-sitter0.26.0","swift":"SDK assente; nessuna compilazione/esecuzione Linux/macOS attestata","dart":"SDK assente; nessuna compilazione/esecuzione attestata"},"checks":len(results),"failures":sum(not item["ok"] for item in results),"results":results}
    (ROOT/"reports/expansion-languages-qa.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({key:value for key,value in report.items() if key!="results"},ensure_ascii=False))
    for result in results:
        if not result["ok"]:print("FAIL",result["id"],result.get("file",""),result.get("problems",result.get("output",""))[-1500:],flush=True)
    if report["failures"]:raise SystemExit(1)
    manifest={}
    for data,path,folder,files in recipes:
        rid=data["id"];proof=[item for item in results if item["id"]==rid]
        program_ran=any("execute" in item["check"] for item in proof)
        workflow=data["section"] in {"Inizializzazione","Compilazione","Debug","Test","Distribuzione"} and not data["project"]
        status="eseguito" if program_ran and (not workflow or data["section"]=="Test" or "PHAR" in data["title"]) else "compilato" if any(item["check"]=="kotlin compile" for item in proof) else "statico"
        details="Controlli reali su Windows x64: "+", ".join(sorted({item["check"] for item in proof}))+". Report: reports/expansion-languages-qa.json. "
        if data["stack"]=="kotlin":details+="Compilatore Kotlin2.3.21 della cache Gradle, JDK25.0.4.1, target17. Pipeline Gradle, sessioni debugger e SDK Android non eseguiti."
        elif data["stack"]=="php":details+="PHP8.4.27-1 portabile ufficiale in .cache; Xdebug e Composer non eseguiti."
        else:details+="Solo analisi sintattica; SDK/compilatore assente. Nessuna esecuzione Swift/Dart né Apple SDK attestata."
        verification={"status":status,"date":"2026-10-29","details":details}
        hashes={asset["path"]:hashlib.sha256((path.parent/asset["source"]).read_text(encoding="utf-8").encode()).hexdigest() for asset in data["assets"] if asset["role"]!="command"}
        manifest[rid]={"assets":hashes,"verification":verification};data["verification"]=verification
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    (ROOT/"tools/expansion_languages_verification.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")


if __name__=="__main__":main()
