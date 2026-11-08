"""Exercise only the three newly added local endpoints, then stop owned processes."""
import http.cookiejar
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from qa_expansion_languages import ROOT,WORK,PHP,compiler_paths


def unused_port():
    with socket.socket() as stream:stream.bind(("127.0.0.1",0));return stream.getsockname()[1]


def await_url(url,process,opener=None):
    for _ in range(30):
        if process.poll() is not None:raise RuntimeError("Server terminato prima della richiesta")
        try:return (opener.open(url,timeout=1) if opener else urllib.request.urlopen(url,timeout=1))
        except (OSError,urllib.error.URLError):time.sleep(.1)
    raise TimeoutError(url)


def main():
    results=[]
    _,stdlib=compiler_paths()
    kotlin=next((WORK/"kotlin").glob("kotlin-esporre-un-endpoint-http*"))
    php_rows=[("php-restituire-un-endpoint-json-php-locale","json"),("php-verificare-un-token-csrf-per-un-form-php","csrf")]
    jobs=[("kotlin",kotlin,["java","-cp",str(kotlin/"classes")+os.pathsep+stdlib,"MainKt"],8085,"health")]
    for rid,kind in php_rows:
        folder=WORK/"php"/rid;port=unused_port()
        jobs.append(("php",folder,[str(PHP),"-S",f"127.0.0.1:{port}","-t","public"],port,kind))
    for stack,folder,command,port,kind in jobs:
        process=subprocess.Popen(command,cwd=folder,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding="utf-8",errors="replace",creationflags=subprocess.CREATE_NO_WINDOW if os.name=="nt" else 0)
        started=time.perf_counter();details=[]
        try:
            base=f"http://127.0.0.1:{port}"
            if kind=="health":
                with await_url(base+"/health",process) as response:assert response.status==200 and response.read()==b"ok"
                details.append("GET /health:200, bodyok")
            elif kind=="json":
                with await_url(base+"/?page=2",process) as response:assert response.status==200 and json.load(response)["page"]==2
                try:urllib.request.urlopen(base+"/?page=bad",timeout=2);raise AssertionError("Input invalido accettato")
                except urllib.error.HTTPError as error:assert error.code==400
                details.extend(["page=2:200","page=bad:400"])
            else:
                opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
                with await_url(base,process,opener) as response:html=response.read().decode()
                token=re.search(r'name="csrf" value="([a-f0-9]+)"',html).group(1)
                try:opener.open(base,data=urllib.parse.urlencode({"csrf":"alterato"}).encode(),timeout=2);raise AssertionError("Token invalido accettato")
                except urllib.error.HTTPError as error:assert error.code==403
                with opener.open(base,data=urllib.parse.urlencode({"csrf":token}).encode(),timeout=2) as response:assert response.status==200 and b"accettata" in response.read()
                details.extend(["GET form:200 con token/cookie","POST token alterato:403","POST token valido:200"])
            result={"id":folder.name,"check":"local HTTP execute","ok":True,"command":command,"details":details}
        except Exception as error:result={"id":folder.name,"check":"local HTTP execute","ok":False,"command":command,"output":str(error)}
        finally:
            if kind=="health":
                try:stdout,stderr=process.communicate("\n",timeout=5)
                except subprocess.TimeoutExpired:process.kill();stdout,stderr=process.communicate()
            else:
                process.terminate()
                try:stdout,stderr=process.communicate(timeout=5)
                except subprocess.TimeoutExpired:process.kill();stdout,stderr=process.communicate()
            result["seconds"]=round(time.perf_counter()-started,3)
            result["server_output"]=(stdout+stderr)[-2000:]
        results.append(result);print(folder.name,result["ok"],result.get("details",result.get("output")),flush=True)
    path=ROOT/"reports/expansion-languages-qa.json"
    report=json.loads(path.read_text(encoding="utf-8"))
    report["results"]=[item for item in report["results"] if item["check"]!="local HTTP execute"]+results
    report["checks"]=len(report["results"]);report["failures"]=sum(not item["ok"] for item in report["results"])
    report["php_distribution"]={"version":"8.4.27-1 NTSx64","url":"https://downloads.php.net/~windows/releases/php-8.4.27-1-nts-Win32-vs17-x64.zip","sha256":"dbae154a0a89791f36c3d48e68bae797878333e7d6cb5721e74617de59b63ab7","installation":"Estratto solo in .cache; nessun PATH/registro globale modificato"}
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    assert not report["failures"]
    evidence_path=ROOT/"tools/expansion_languages_verification.json"
    evidence=json.loads(evidence_path.read_text(encoding="utf-8"))
    for result in results:
        rid=result["id"];entry=evidence[rid];entry["verification"]["status"]="eseguito"
        entry["verification"]["details"]+=" Endpoint HTTP locale eseguito fuori dal sandbox: "+"; ".join(result["details"])+"."
        stack=rid.split("-",1)[0];metadata=ROOT/"catalog"/stack/rid/"recipe.json";data=json.loads(metadata.read_text(encoding="utf-8"));data["verification"]=entry["verification"];metadata.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")


if __name__=="__main__":main()
