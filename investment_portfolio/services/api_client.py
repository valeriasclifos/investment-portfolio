import requests
import logging

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

API_KEY = "LN69T3GWCBLM5T9K"
BASE_URL = "https://www.alphavantage.co/query"

# doar lista de simboluri, numele vin din API
SYMBOLS = ["AAPL", "GOOGL", "TSLA", "AMZN", "NVDA", "MSFT"]


def _request_alpha_vantage(params: dict) -> dict | None:
    """Helper general cu tratare de erori pentru request-urile la Alpha Vantage."""
    try:
        response = requests.get(BASE_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if "Note" in data:
            # limită de request-uri atinsă
            logging.warning(f"API limită Alpha Vantage: {data['Note']}")
            return None

        if "Error Message" in data:
            logging.error(f"Eroare Alpha Vantage: {data['Error Message']}")
            return None

        return data

    except requests.exceptions.Timeout:
        logging.error("Timeout la cererea către Alpha Vantage")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Eroare HTTP/Network către Alpha Vantage: {e}")
        return None
    except Exception as e:
        logging.exception(f"Eroare neașteptată la request Alpha Vantage: {e}")
        return None


def get_company_name(symbol: str) -> str | None:
    """Ia numele companiei din endpoint-ul OVERVIEW."""
    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
        "apikey": API_KEY,
    }
    data = _request_alpha_vantage(params)
    if not data:
        return None

    name = data.get("Name")
    if not name:
        logging.error(f"Nu am găsit 'Name' în OVERVIEW pentru {symbol}: {data}")
        return None

    return name


def get_price(symbol: str) -> float | None:
    """Ia prețul curent din GLOBAL_QUOTE."""
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": API_KEY,
    }
    data = _request_alpha_vantage(params)
    if not data:
        return None

    quote = data.get("Global Quote", {})
    price_str = quote.get("05. price")

    if not price_str:
        logging.error(f"Nu am găsit '05. price' în GLOBAL_QUOTE pentru {symbol}: {data}")
        return None

    try:
        return float(price_str)
    except ValueError as e:
        logging.error(f"Eroare conversie preț pentru {symbol}: {price_str} ({e})")
        return None


def get_company_info(symbol: str) -> dict | None:
    """
    Întoarce un dict cu:
        { "symbol": ..., "name": ..., "price": ... }
    sau None dacă nu s-a putut obține nimic.
    """
    name = get_company_name(symbol)
    price = get_price(symbol)

    if name is None and price is None:
        # eșec complet
        return None

    return {
        "symbol": symbol,
        "name": name if name is not None else symbol,  # fallback la simbol
        "price": price,
    }


def list_companies_with_price() -> list[dict]:
    """
    Returnează o listă de companii cu nume + preț
    pentru simbolurile definite în SYMBOLS.
    """
    results = []
    for symbol in SYMBOLS:
        info = get_company_info(symbol)
        if info is None:
            # dacă a picat tot, punem ceva default ca să nu crape UI-ul
            results.append({
                "symbol": symbol,
                "name": symbol,
                "price": "N/A",
            })
        else:
            if info["price"] is None:
                info["price"] = "N/A"
            results.append(info)
    return results
