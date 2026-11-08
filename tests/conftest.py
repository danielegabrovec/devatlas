import os
from pathlib import Path
import sys
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from devatlas.qt_bootstrap import configure_qt_plugins
configure_qt_plugins()

