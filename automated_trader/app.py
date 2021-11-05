from automated_trader.client.client import OANDAClient


def main():
    """Entry point for program"""
    client = OANDAClient("oanda.cfg")
    print(client.get_instruments())
