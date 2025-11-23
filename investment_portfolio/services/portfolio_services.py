import json
from pathlib import Path
from datetime import datetime

from .api_client import get_price

# Folderul data este la același nivel cu folderul "services"
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

USERS_PATH = DATA_DIR / "users.json"
PORTFOLIO_PATH = DATA_DIR / "portfolio.json"
TRANSACTIONS_PATH = DATA_DIR / "transactions.json"


# ---------- Helperi generali pentru fișiere JSON ----------

def _ensure_data_dir():
    """Creează folderul data dacă nu există."""
    DATA_DIR.mkdir(exist_ok=True)


def _load_json(path: Path, default):
    _ensure_data_dir()
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # dacă fișierul e corupt / gol, îl resetăm cu default
        return default


def _save_json(path: Path, data):
    _ensure_data_dir()
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ---------- Utilizatori: citire / scriere / sold ----------

def _get_all_users() -> dict:
    """
    users.json are structura:
    {
      "valeria": {
        "password_hash": "...",
        "balance": 1000.0
      },
      ...
    }
    """
    return _load_json(USERS_PATH, {})


def _save_all_users(users: dict) -> None:
    _save_json(USERS_PATH, users)


def get_user_balance(username: str) -> float:
    users = _get_all_users()
    user = users.get(username)
    if not user:
        return 0.0
    return float(user.get("balance", 0.0))


def add_money(username: str, amount: float):
    """
    Adaugă bani în contul utilizatorului.
    Returnează (success: bool, mesaj: str, noul_sold: float | None)
    """
    if amount <= 0:
        return False, "Suma trebuie să fie mai mare decât 0.", None

    users = _get_all_users()
    if username not in users:
        return False, "Utilizator inexistent.", None

    current_balance = float(users[username].get("balance", 0.0))
    new_balance = current_balance + amount
    users[username]["balance"] = new_balance
    _save_all_users(users)

    return True, "Banii au fost adăugați cu succes.", new_balance


# ---------- Portofoliu: citire / scriere ----------

def _load_portfolio() -> dict:
    """
    portfolio.json are structura:
    {
      "valeria": {
        "AAPL": {
          "quantity": 10,
          "avg_buy_price": 180.0
        },
        "TSLA": {...}
      },
      "alt_user": {...}
    }
    """
    return _load_json(PORTFOLIO_PATH, {})


def _save_portfolio(portfolio: dict) -> None:
    _save_json(PORTFOLIO_PATH, portfolio)


def get_user_portfolio(username: str) -> dict:
    portfolio = _load_portfolio()
    return portfolio.get(username, {})


# ---------- Tranzacții: istoric ----------

def _load_transactions() -> list:
    """
    transactions.json are structura:
    [
      {
        "username": "valeria",
        "symbol": "AAPL",
        "quantity": 5,
        "price": 180.0,
        "side": "BUY",
        "timestamp": "2025-11-23T12:34:56"
      },
      ...
    ]
    """
    return _load_json(TRANSACTIONS_PATH, [])


def _save_transactions(transactions: list) -> None:
    _save_json(TRANSACTIONS_PATH, transactions)


def get_user_transactions(username: str) -> list:
    all_tx = _load_transactions()
    return [tx for tx in all_tx if tx.get("username") == username]


# ---------- Logica de CUMPĂRARE ----------

def buy_stock(username: str, symbol: str, quantity: int):
    """
    Cumpără 'quantity' acțiuni din 'symbol' la prețul curent din API.
    Actualizează:
      - sold utilizator
      - portofoliu utilizator
      - istoric tranzacții

    Returnează: (success: bool, mesaj: str)
    """
    if quantity <= 0:
        return False, "Cantitatea trebuie să fie mai mare decât 0."

    users = _get_all_users()
    if username not in users:
        return False, "Utilizator inexistent."

    # Prețul curent din API
    price = get_price(symbol)
    if price is None:
        return False, "Nu s-a putut obține prețul actual din API. Încearcă mai târziu."

    cost = price * quantity
    balance = float(users[username].get("balance", 0.0))

    if balance < cost:
        return False, f"Fonduri insuficiente. Ai {balance:.2f}, costul este {cost:.2f}."

    # 1) Scădem banii din sold
    new_balance = balance - cost
    users[username]["balance"] = new_balance
    _save_all_users(users)

    # 2) Actualizăm portofoliul
    portfolio = _load_portfolio()
    user_portfolio = portfolio.get(username, {})

    if symbol in user_portfolio:
        old_qty = user_portfolio[symbol]["quantity"]
        old_avg_price = user_portfolio[symbol]["avg_buy_price"]

        # Recalculăm prețul mediu de cumpărare
        total_shares = old_qty + quantity
        new_avg_price = (old_qty * old_avg_price + quantity * price) / total_shares

        user_portfolio[symbol]["quantity"] = total_shares
        user_portfolio[symbol]["avg_buy_price"] = new_avg_price
    else:
        user_portfolio[symbol] = {
            "quantity": quantity,
            "avg_buy_price": price
        }

    portfolio[username] = user_portfolio
    _save_portfolio(portfolio)

    # 3) Adăugăm tranzacția în istoric
    transactions = _load_transactions()
    transactions.append({
        "username": username,
        "symbol": symbol,
        "quantity": quantity,
        "price": price,
        "side": "BUY",
        "timestamp": datetime.now().isoformat()
    })
    _save_transactions(transactions)

    return True, f"Ai cumpărat {quantity} x {symbol} la {price:.2f}. Sold nou: {new_balance:.2f}."


# ---------- Logica de VÂNZARE ----------

def sell_stock(username: str, symbol: str, quantity: int):
    """
    Vinde 'quantity' acțiuni din 'symbol' la prețul curent din API.
    Actualizează:
      - sold utilizator
      - portofoliu utilizator
      - istoric tranzacții

    Returnează: (success: bool, mesaj: str)
    """
    if quantity <= 0:
        return False, "Cantitatea trebuie să fie mai mare decât 0."

    users = _get_all_users()
    if username not in users:
        return False, "Utilizator inexistent."

    portfolio = _load_portfolio()
    user_portfolio = portfolio.get(username, {})

    if symbol not in user_portfolio:
        return False, f"Nu ai nicio acțiune {symbol} în portofoliu."

    current_qty = user_portfolio[symbol]["quantity"]
    if current_qty < quantity:
        return False, f"Nu ai suficiente acțiuni {symbol} de vândut. Ai doar {current_qty}."

    # Prețul curent din API
    price = get_price(symbol)
    if price is None:
        return False, "Nu s-a putut obține prețul actual din API. Încearcă mai târziu."

    # 1) Scădem acțiunile din portofoliu
    new_qty = current_qty - quantity
    if new_qty == 0:
        del user_portfolio[symbol]
    else:
        user_portfolio[symbol]["quantity"] = new_qty

    portfolio[username] = user_portfolio
    _save_portfolio(portfolio)

    # 2) Adăugăm banii în sold
    revenue = price * quantity
    balance = float(users[username].get("balance", 0.0))
    new_balance = balance + revenue
    users[username]["balance"] = new_balance
    _save_all_users(users)

    # 3) Istoric tranzacții
    transactions = _load_transactions()
    transactions.append({
        "username": username,
        "symbol": symbol,
        "quantity": quantity,
        "price": price,
        "side": "SELL",
        "timestamp": datetime.now().isoformat()
    })
    _save_transactions(transactions)

    return True, f"Ai vândut {quantity} x {symbol} la {price:.2f}. Sold nou: {new_balance:.2f}."


# ---------- Funcții de calcul (opțional, pentru afișat în UI) ----------

def get_portfolio_value(username: str) -> float:
    """
    Calculează valoarea totală a portofoliului utilizatorului,
    folosind prețurile curente din API.
    """
    portfolio = get_user_portfolio(username)
    total = 0.0
    for symbol, info in portfolio.items():
        qty = info["quantity"]
        current_price = get_price(symbol)
        if current_price is not None:
            total += qty * current_price
    return total
