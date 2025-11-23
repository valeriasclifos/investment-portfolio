from datetime import datetime

class Transaction:
    def __init__(self, username, symbol, company_name, quantity, price, side):
        self.username = username
        self.symbol = symbol
        self.company_name = company_name
        self.quantity = quantity
        self.price = price
        self.side = side
        self.timestamp = datetime.now().isoformat()
