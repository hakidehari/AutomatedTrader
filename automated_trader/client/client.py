import tpqoa


class OANDAClient:
    def __init__(self, file_path):
        self.client = tpqoa.tpqoa(file_path)

    def get_instruments(self):
        """Gets list of instruments in pair1_pair2 format"""
        ins = self.client.get_instruments()
        return [element[1] for element in ins]

    def get_historical_data(
        self, instrument: str, granularity: str, from_date: str, to_date: str
    ):
        """Gathers historical data for specified timeframe for specified Pairing"""
        data = self.client.get_history(
            instrument=instrument, start=from_date, end=to_date, granularity="D"
        )
        return data
