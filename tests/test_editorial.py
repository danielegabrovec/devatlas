from copy import deepcopy
from tools.catalog_support import enrich_editorial
from test_core import sample


def test_editorial_details_use_real_route_and_preserve_code_and_verification():
    record = sample("fastapi-upload", "fastapi", "Inviare file e descrizione")
    record["summary"] = "app.py contiene applicazione e rotta completa."
    record["assets"] = [{"id": "main", "path": "app.py", "role": "file", "content": "from fastapi import FastAPI, File, Form\napp=FastAPI()\n@app.post('/upload')\ndef upload(file=File(), description=Form()): return {'ok':True}\n"}]
    before = deepcopy(record)
    assert enrich_editorial(record)
    assert "POST /upload" in record["summary"] and "File, Form" in record["summary"]
    assert record["assets"] == before["assets"] and record["verification"] == before["verification"]
    assert not enrich_editorial(record)


def test_editorial_react_detects_usage_not_unused_imports():
    record = sample("react-form", "react", "Leggere il modulo")
    record["summary"] = "Il componente completo è in src/App.jsx."
    record["assets"] = [{"id": "main", "path": "src/App.jsx", "role": "file", "content": "import {useState,useEffect} from 'react'; export default function App(){const [x,setX]=useState(0); return <form onSubmit={e=>new FormData(e.currentTarget)}><input name='name'/></form>}"}]
    assert enrich_editorial(record)
    assert "useState" in record["summary"] and "useEffect" not in record["summary"]
    assert any("FormData" in fact for fact in record["editorial"]["facts"])

