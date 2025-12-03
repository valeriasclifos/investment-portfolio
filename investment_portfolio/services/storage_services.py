import json
from pathlib import Path

def _ensure_dir(path):
    """
    Creează folderul părinte pentru fișierul dat, dacă nu există.
    Ex: pentru 'data/users.json' va crea folderul 'data'.
    """
    p = Path(path)
    if p.parent:
        p.parent.mkdir(parents=True, exist_ok=True)

def load_json(path, default):
    """
    Citește JSON-ul din 'path'. Dacă nu există fișierul, întoarce 'default'.
    Acceptă atât string, cât și Path.
    """
    p = Path(path)
    if not p.exists():
        return default

    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    """
    Salvează dict/list în JSON la 'path'.
    Creează automat directorul părinte dacă nu există.
    Acceptă atât string, cât și Path.
    """
    p = Path(path)
    _ensure_dir(p)

    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
