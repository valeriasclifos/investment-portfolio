import hashlib
from pathlib import Path
from .storage_services import load_json, save_json

# înainte aveai: DATA_PATH = Path("data/users.json")
# acum facem să fie identic cu ce folosește portfolio_service
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "users.json"


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_all_users():
    return load_json(DATA_PATH, {})

def save_all_users(users):
    save_json(DATA_PATH, users)

def register(username, password):
    users = get_all_users()
    if username in users:
        return False, "Utilizatorul există deja."
    users[username] = {
        "password_hash": hash_password(password),
        "balance": 0.0
    }
    save_all_users(users)
    return True, "Cont creat cu succes."

def login(username, password):
    users = get_all_users()
    if username not in users:
        return False, "Utilizator inexistent."
    if users[username]["password_hash"] != hash_password(password):
        return False, "Parolă greșită."
    return True, users[username]
