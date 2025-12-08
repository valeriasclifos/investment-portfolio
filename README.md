# 💸 Investment Portfolio App

Aplicație completă pentru gestionarea portofoliului de investiții, realizată în Python cu Streamlit, SQLAlchemy și SQLite.  
Utilizatorii își pot crea un cont, pot adăuga bani, pot cumpăra și vinde acțiuni, pot vizualiza valoarea portofoliului în timp real și pot urmări istoricul tranzacțiilor.

---

## ⭐ Caracteristici principale

### 🔐 Autentificare & cont
- Creare cont nou
- Parole securizate (hash SHA-256)
- Login cu verificare
- Vizualizare sold
- Adăugare bani în cont

### 🏢 Companii & prețuri în timp real
- Afișare listă companii (AAPL, TSLA, AMZN, MSFT etc.)
- Recuperare prețuri bursiere din API extern (Alpha Vantage)
- Cumpărare acțiuni la prețul actual
- Validări fonduri și cantitate

### 📈 Portofoliu investițional
- Vizualizare acțiuni deținute
- Calcul automat preț mediu de cumpărare
- Preț curent & valoare totală
- Profit/Pierdere calculat dinamic

### 📜 Istoric tranzacții
- Listă completă BUY / SELL
- Ordinate cronologic descrescător
- Salvate în baza de date

---

## 🧰 Tehnologii folosite

- **Python 3.10+**
- **Streamlit** – interfața aplicației
- **SQLite** – ca bază de date locală
- **SQLAlchemy ORM** – definire modele & interacțiune DB
- **Alpha Vantage API** – prețuri live
- **Hashlib (SHA-256)** – securizarea parolelor

---

## 🗂️ Structura Proiect
investment_portfolio/
│
├── app.py                     # aplicația Streamlit
│
├── models/
│   ├── __init__.py            # încărcare modele + init DB
│   ├── user.py                # model User
│   ├── investment.py          # model Investment
│   └── transactions.py        # model Transaction
│
├── services/
│   ├── api_client.py          # API extern pentru prețuri
│   ├── auth_services.py       # login, register, hashing
│   ├── portfolio_services.py  # logica Buy/Sell
│   ├── database.py            # SQLite + SQLAlchemy + init_db()
│   └── storage_services.py    # legacy JSON utils
│
└── investment.db              # baza de date SQLite
