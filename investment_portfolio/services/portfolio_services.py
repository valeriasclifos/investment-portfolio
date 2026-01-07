from datetime import datetime

from services.database import SessionLocal
from models.user import User
from models.investment import Investment
from models.transactions import Transaction

from services.api_client import get_price


# ------------- SOLD UTILIZATOR -------------


def get_user_balance(username: str) -> float:
    """
    Returnează soldul utilizatorului din baza de date.
    Dacă utilizatorul nu există, întoarce 0.0.
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(username=username).first()
        if not user:
            return 0.0
        return float(user.balance or 0.0)
    finally:
        db.close()


def add_money(username: str, amount: float):
    """
    Adaugă bani în contul utilizatorului.
    Returnează (success: bool, mesaj: str, noul_sold: float | None)
    """
    if amount <= 0:
        return False, "Suma trebuie să fie mai mare decât 0.", None

    db = SessionLocal()
    try:
        user = db.query(User).filter_by(username=username).first()
        if not user:
            return False, "Utilizator inexistent.", None

        current_balance = float(user.balance or 0.0)
        new_balance = current_balance + amount
        user.balance = new_balance

        db.commit()
        db.refresh(user)

        return True, "Banii au fost adăugați cu succes.", new_balance
    finally:
        db.close()


# ------------- PORTOFOLIU UTILIZATOR -------------


def get_user_portfolio(username: str) -> dict:
    """
    Returnează portofoliul utilizatorului sub formă de dict:

    {
        "AAPL": {
            "quantity": 10,
            "avg_buy_price": 180.0
        },
        ...
    }

    Astfel, app.py poate rămâne neschimbat.
    """
    db = SessionLocal()
    try:
        investments = (
            db.query(Investment)
            .filter_by(username=username)
            .all()
        )

        portfolio = {}
        for inv in investments:
            portfolio[inv.symbol] = {
                "quantity": inv.quantity,
                "avg_buy_price": float(inv.avg_buy_price or 0.0),
            }

        return portfolio
    finally:
        db.close()


# ------------- TRANZACȚII UTILIZATOR -------------


def get_user_transactions(username: str) -> list:
    """
    Returnează lista tranzacțiilor utilizatorului ca listă de dict-uri
    compatibile cu ce așteaptă app.py:

    [
      {
        "username": "...",
        "symbol": "AAPL",
        "quantity": 5,
        "price": 180.0,
        "side": "BUY",
        "timestamp": "2025-11-23T12:34:56"
      },
      ...
    ]
    """
    db = SessionLocal()
    try:
        tx_list = (
            db.query(Transaction)
            .filter_by(username=username)
            .order_by(Transaction.timestamp.desc())
            .all()
        )

        result = []
        for tx in tx_list:
            result.append(
                {
                    "username": tx.username,
                    "symbol": tx.symbol,
                    "quantity": tx.quantity,
                    "price": float(tx.price or 0.0),
                    "side": tx.side,
                    "timestamp": tx.timestamp.isoformat() if tx.timestamp else "",
                }
            )
        return result
    finally:
        db.close()


# ------------- CUMPĂRARE ACȚIUNI -------------


def buy_stock(username: str, symbol: str, quantity: int):
    """
    Cumpără 'quantity' acțiuni din 'symbol' la prețul curent din API.

    Actualizează:
      - sold utilizator
      - portofoliu utilizator (Investment)
      - istoric tranzacții (Transaction)

    Returnează: (success: bool, mesaj: str)
    """
    if quantity <= 0:
        return False, "Cantitatea trebuie să fie mai mare decât 0."

    db = SessionLocal()
    try:
        user = db.query(User).filter_by(username=username).first()
        if not user:
            return False, "Utilizator inexistent."

        # Prețul curent din API
        price = get_price(symbol)
        if price is None:
            return False, "Nu s-a putut obține prețul actual din API. Încearcă mai târziu."

        cost = price * quantity
        balance = float(user.balance or 0.0)

        if balance < cost:
            return False, f"Fonduri insuficiente. Ai {balance:.2f}, costul este {cost:.2f}."

        # 1) Scădem banii din sold
        new_balance = balance - cost
        user.balance = new_balance

        # 2) Actualizăm portofoliul (Investment)
        investment = (
            db.query(Investment)
            .filter_by(username=username, symbol=symbol)
            .first()
        )

        if investment:
            old_qty = investment.quantity
            old_avg_price = float(investment.avg_buy_price or 0.0)

            total_shares = old_qty + quantity
            new_avg_price = (old_qty * old_avg_price + quantity * price) / total_shares

            investment.quantity = total_shares
            investment.avg_buy_price = new_avg_price
        else:
            investment = Investment(
                username=username,
                symbol=symbol,
                quantity=quantity,
                avg_buy_price=price,
            )
            db.add(investment)

        # 3) Adăugăm tranzacția în istoric (Transaction)
        tx = Transaction(
            username=username,
            symbol=symbol,
            quantity=quantity,
            price=price,
            side="BUY",
            timestamp=datetime.utcnow(),
        )
        db.add(tx)

        db.commit()

        return True, f"Ai cumpărat {quantity} x {symbol} la {price:.2f}. Sold nou: {new_balance:.2f}."
    except Exception as e:
        db.rollback()
        return False, f"Eroare la cumpărare: {e}"
    finally:
        db.close()


# ------------- VÂNZARE ACȚIUNI -------------


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

    db = SessionLocal()
    try:
        user = db.query(User).filter_by(username=username).first()
        if not user:
            return False, "Utilizator inexistent."

        investment = (
            db.query(Investment)
            .filter_by(username=username, symbol=symbol)
            .first()
        )

        if not investment:
            return False, f"Nu ai nicio acțiune {symbol} în portofoliu."

        current_qty = investment.quantity
        if current_qty < quantity:
            return False, f"Nu ai suficiente acțiuni {symbol} de vândut. Ai doar {current_qty}."

        # Prețul curent din API
        price = get_price(symbol)
        if price is None:
            return False, "Nu s-a putut obține prețul actual din API. Încearcă mai târziu."

        # 1) Scădem acțiunile din portofoliu
        new_qty = current_qty - quantity
        if new_qty == 0:
            db.delete(investment)
        else:
            investment.quantity = new_qty

        # 2) Adăugăm banii în sold
        revenue = price * quantity
        balance = float(user.balance or 0.0)
        new_balance = balance + revenue
        user.balance = new_balance

        # 3) Istoric tranzacții
        tx = Transaction(
            username=username,
            symbol=symbol,
            quantity=quantity,
            price=price,
            side="SELL",
            timestamp=datetime.utcnow(),
        )
        db.add(tx)

        db.commit()

        return True, f"Ai vândut {quantity} x {symbol} la {price:.2f}. Sold nou: {new_balance:.2f}."
    except Exception as e:
        db.rollback()
        return False, f"Eroare la vânzare: {e}"
    finally:
        db.close()


# ------------- VALOARE PORTOFOLIU -------------


def get_portfolio_value(username: str) -> float:
    """
    Calculează valoarea totală a portofoliului utilizatorului,
    folosind prețurile curente din API.
    """
    db = SessionLocal()
    try:
        investments = (
            db.query(Investment)
            .filter_by(username=username)
            .all()
        )
    finally:
        db.close()

    total = 0.0
    for inv in investments:
        current_price = get_price(inv.symbol)
        if current_price is not None:
            total += inv.quantity * current_price
    return total
