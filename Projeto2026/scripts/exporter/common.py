from pathlib import Path
import json
from rdflib import Namespace

ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "data" / "1.21.11"
MANUAL_DIR = ROOT / "data" / "manual"
EXPORT_DIR = ROOT / "scripts" / "ontology"
ONTOLOGY_DIR = ROOT / "ontology"

MC = Namespace("http://rpcw.di.uminho.pt/2026/minecraft/")

EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_dataset(filename):
    return load_json(DATA_DIR / filename)


def load_manual(filename, default=None):
    path = MANUAL_DIR / filename
    if not path.exists():
        return [] if default is None else default
    return load_json(path)