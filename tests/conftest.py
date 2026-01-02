import sys
from pathlib import Path

# Ajoute le dossier src/ au PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

sys.path.insert(0, str(SRC_DIR))
