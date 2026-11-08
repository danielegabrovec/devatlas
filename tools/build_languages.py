"""Build exactly 500 language recipes and nine complete projects."""
from languages_python import build_all as python
from languages_javascript import build_all as javascript
from languages_typescript import build_all as typescript
from languages_csharp import build_all as csharp
from languages_cpp import build_all as cpp
from languages_c import build_all as c
from languages_rust import build_all as rust
from languages_go import build_all as go
from languages_java import build_all as java


def build_all():
    for build in (python,javascript,typescript,csharp,cpp,c,rust,go,java):
        build()
    from languages_workflows import prune_replaced_directories
    prune_replaced_directories()


if __name__=="__main__":
    build_all()
