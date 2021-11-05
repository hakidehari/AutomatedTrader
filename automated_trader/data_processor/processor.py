import pandas as pd
from oandapyV20 import API
from automated_trader.settings.settings import TRADING_PAIRS
from oandapyV20.contrib.factories import InstrumentsCandlesFactory


class OANDAClient:

    def __init__(self, access_token):
        self.client = API(access_token=access_token)

    def get_historical_data(self, instrument: str, granularity: str, from_date: str, to_date: str):
        """Gathers historical data for specified timeframe for specified Pairing"""
        params = {
            "to": to_date,
            "from": from_date,
            "granularity": granularity
        }
        request = InstrumentsCandlesFactory(instrument=instrument, params=params)

        response = self.client.request(request)


