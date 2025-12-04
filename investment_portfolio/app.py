import streamlit as st

# Importăm funcțiile care folosesc API-ul cu cheie (Alpha Vantage) din services/api_client.py
from services.api_client import (
    SYMBOLS,
    get_company_name,
    get_price,
    get_company_info,
    list_companies_with_price,
)

# Importăm serviciile de autentificare și portofoliu
from services.auth_services import register, login
from services.portfolio_services import (   # <- atenție: portfolio_service, nu portfolio_services
    get_user_balance,
    add_money,
    buy_stock,
    get_user_portfolio,
    sell_stock,
    get_user_transactions,
    get_portfolio_value,
)

# ---------- Config pagină ----------
st.set_page_config(
    page_title="Portofoliu Investiții",
    page_icon="💸",
    layout="wide",
)

# ---------- Helperi pentru sesiune ----------
if "username" not in st.session_state:
    st.session_state.username = None
if "last_message" not in st.session_state:
    st.session_state.last_message = None
if "last_message_type" not in st.session_state:
    st.session_state.last_message_type = None
# ---------- Header ----------
st.title("💸 Aplicație de gestionare a portofoliului de investiții")
# Afișăm ultimul mesaj global (ex: "Ai cumpărat..." / "Ai vândut...")
if st.session_state.last_message:
    if st.session_state.last_message_type == "success":
        st.success(st.session_state.last_message)
    elif st.session_state.last_message_type == "error":
        st.error(st.session_state.last_message)

# ---------- SECȚIUNE AUTENTIFICARE ----------
if st.session_state.username is None:
    tab_login, tab_register = st.tabs(["🔐 Login", "🆕 Register"])

    with tab_register:
        st.subheader("Creare cont nou")
        new_user = st.text_input("Username nou")
        new_pass = st.text_input("Parolă", type="password")
        new_pass2 = st.text_input("Confirmare parolă", type="password")

        if st.button("Creează cont"):
            if not new_user or not new_pass:
                st.error("Completează username și parola.")
            elif new_pass != new_pass2:
                st.error("Parolele nu coincid.")
            else:
                ok, msg = register(new_user, new_pass)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

    with tab_login:
        st.subheader("Intră în cont")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Parolă", type="password", key="login_pass")

        if st.button("Login"):
            if not username or not password:
                st.error("Completează username și parola.")
            else:
                ok, data_or_msg = login(username, password)
                if ok:
                    st.session_state.username = username
                    st.success("Autentificare reușită!")
                    st.rerun()
                else:
                    st.error(data_or_msg)

else:
    # sidebar info + logout
    with st.sidebar:
        st.write(f"👤 Conectat ca **{st.session_state.username}**")
        balance = get_user_balance(st.session_state.username)
        st.write(f"💰 Sold curent: **{balance:.2f}**")
        portfolio_value = get_portfolio_value(st.session_state.username)
        st.write(f"📊 Valoare portofoliu: **{portfolio_value:.2f}**")

        if st.button("Logout"):
            st.session_state.username = None
            st.rerun()

# ---------- Dacă nu e logat, ne oprim aici ----------
if st.session_state.username is None:
    st.info("Autentifică-te sau creează un cont nou pentru a continua.")
    st.stop()

username = st.session_state.username

# ---------- TAB-URI PRINCIPALE ----------
tab_cont, tab_companii, tab_portofoliu, tab_istoric = st.tabs(
    ["💼 Cont", "🏢 Companii", "📈 Portofoliu", "📜 Istoric"]
)

# ---------- TAB CONT ----------
with tab_cont:
    st.subheader("💼 Gestionare cont")

    current_balance = get_user_balance(username)
    st.metric(label="Sold curent", value=f"{current_balance:.2f}")

    st.markdown("---")
    st.write("### Adăugare bani")

    amount = st.number_input("Sumă de adăugat", min_value=0.0, step=10.0, format="%.2f")

    if st.button("Adaugă bani"):
        ok, msg, new_balance = add_money(username, amount)
        if ok:
            st.success(f"{msg} Sold nou: {new_balance:.2f}")
            st.rerun()  # 🔥 REFRESH INSTANT
        else:
            st.error(msg)

# ---------- TAB COMPANII ----------
with tab_companii:
    st.subheader("🏢 Lista de companii și prețul curent")

    companies = []

    for symbol in SYMBOLS:
        companies.append(get_company_info(symbol))

    st.table(companies)

    st.markdown("---")
    st.write("### Cumpără acțiuni")

    symbols = [row["symbol"] for row in companies]
    if symbols:
        symbol_buy = st.selectbox("Alege simbol", symbols)
        qty_buy = st.number_input("Cantitate", min_value=1, step=1)

        if st.button("Cumpără"):
            ok, msg = buy_stock(username, symbol_buy, int(qty_buy))
            if ok:
                st.session_state.last_message = msg
                st.session_state.last_message_type = "success"
                st.rerun()
            else:
                st.session_state.last_message = msg
                st.session_state.last_message_type = "error"
                st.rerun()

# ---------- TAB PORTOFOLIU ----------
with tab_portofoliu:
    st.subheader("📈 Portofoliul tău")

    user_portfolio = get_user_portfolio(username)

    if not user_portfolio:
        st.info("Nu ai încă acțiuni.")
    else:
        rows = []
        for symbol, info in user_portfolio.items():
            quantity = info["quantity"]
            avg_buy_price = info["avg_buy_price"]
            current_price = get_price(symbol)

            if current_price is not None:
                current_value = current_price * quantity
                profit = (current_price - avg_buy_price) * quantity
            else:
                current_value = "N/A"
                profit = "N/A"

            rows.append({
                "Symbol": symbol,
                "Cantitate": quantity,
                "Preț mediu cumpărare": round(avg_buy_price, 2),
                "Preț curent": round(current_price, 2) if current_price is not None else "N/A",
                "Valoare curentă": round(current_value, 2) if isinstance(current_value, (int, float)) else "N/A",
                "Profit/Pierdere": round(profit, 2) if isinstance(profit, (int, float)) else "N/A",
            })

        st.table(rows)

        st.markdown("---")
        st.write("### Vinde acțiuni")

        symbol_options = list(user_portfolio.keys())
        symbol_sell = st.selectbox("Alege simbol", symbol_options)
        max_qty = user_portfolio[symbol_sell]["quantity"]

        qty_sell = st.number_input(
            "Cantitate", min_value=1, max_value=int(max_qty), step=1
        )

        if st.button("Vinde"):
            ok, msg = sell_stock(username, symbol_sell, int(qty_sell))
            if ok:
                st.session_state.last_message = msg
                st.session_state.last_message_type = "success"
                st.rerun()
            else:
                st.session_state.last_message = msg
                st.session_state.last_message_type = "error"
                st.rerun()

# ---------- TAB ISTORIC ----------
with tab_istoric:
    st.subheader("📜 Istoricul tranzacțiilor")

    transactions = get_user_transactions(username)

    if not transactions:
        st.info("Nu există tranzacții.")
    else:
        transactions_sorted = sorted(
            transactions, key=lambda tx: tx.get("timestamp", ""), reverse=True
        )
        st.table(transactions_sorted)
