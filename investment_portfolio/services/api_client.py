import yfinance as yf

# 10 companii populare
SYMBOLS = [
    "AAPL", "GOOGL", "TSLA", "AMZN", "NVDA",
    "MSFT", "META", "NFLX", "ORCL", "INTC"
]


def get_company_name(symbol: str) -> str:
    """
    Ia numele companiei din yfinance.
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        name = info.get("longName") or info.get("shortName") or symbol
        return name

    except Exception:
        return symbol

def get_price(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        price = ticker.history(period="1d")["Close"].iloc[-1]

        if price is None:
            return "N/A"

        return float(price)

    except Exception:
        return "N/A"


def get_company_info(symbol: str) -> dict:
    name = get_company_name(symbol)
    price = get_price(symbol)

    return {
        "symbol": symbol,
        "name": name,
        "price": price if price != "N/A" else "N/A"
    }

def list_companies_with_price() -> list[dict]:
    """
    Returnează lista completă cu nume + preț pentru 10 companii.
    """
    result = []
    for symbol in SYMBOLS:
        result.append(get_company_info(symbol))
    return result
