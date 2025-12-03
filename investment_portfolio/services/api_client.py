import requests

# 10 companii populare
SYMBOLS = [
    "AAPL", "GOOGL", "TSLA", "AMZN", "NVDA",
    "MSFT", "META", "NFLX", "ORCL", "INTC",
]

# ⬇️ AICI PUI CHEIA TA REALĂ (cea cu care ai testat în browser)
API_KEY = "K5QZI11AF8O6GDIT"
BASE_URL = "https://www.alphavantage.co/query"


def _get_global_quote(symbol: str) -> dict | None:
    """
    Aduce GLOBAL_QUOTE pentru un simbol de la Alpha Vantage.
    Dacă apare eroare / limită / structură ciudată, întoarce None.
    """
    try:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": API_KEY,
        }
        r = requests.get(BASE_URL, params=params, timeout=5)
        data = r.json()

        # dacă API-ul se plânge de limită sau de cheie
        if "Error Message" in data or "Note" in data:
            print("AlphaVantage error:", data)  # doar pentru debugging în consolă
            return None

        quote = data.get("Global Quote") or data.get("Global_Quote")
        if not quote:
            print("No Global Quote field:", data)
            return None

        return quote
    except Exception as e:
        print("Exception in _get_global_quote:", e)
        return None


def get_price(symbol: str):
    """
    Returnează prețul curent (float) sau None dacă nu se poate obține.
    """
    quote = _get_global_quote(symbol)
    if not quote:
        return None

    price_str = quote.get("05. price")
    if not price_str:
        print("Missing '05. price' in quote:", quote)
        return None

    try:
        return float(price_str)
    except ValueError:
        print("Could not convert price to float:", price_str)
        return None


def get_company_name(symbol: str) -> str:
    """
    Pentru simplitate, folosim simbolul ca nume afișat.
    """
    return symbol


def get_company_info(symbol: str) -> dict:
    """
    Returnează:
      {
        "symbol": ...,
        "name": ...,
        "price": ... (float sau None)
      }
    """
    price = get_price(symbol)
    return {
        "symbol": symbol,
        "name": get_company_name(symbol),
        "price": price,
    }


def list_companies_with_price() -> list[dict]:
    """
    Lista completă cu info pentru cele 10 companii.
    """
    result: list[dict] = []
    for s in SYMBOLS:
        result.append(get_company_info(s))
    return result
