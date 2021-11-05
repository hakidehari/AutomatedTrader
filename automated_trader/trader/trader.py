from automated_trader.data_processor.processor import OANDAClient, TurleProcessor
import pandas as pd


class AutomatedTrader:
    def __init__(self, access_token):
        self.trader = OANDAClient(access_token=access_token)

    def execute_results(
        self, instrument: str, granularity: str, from_date: str, to_date: str
    ):
        """Executes results based on the analyzer"""
        pass

    def process_all_pairs(self):
        """Process all pairs"""
        pairs = self.trader.get_instruments()

        for pair in pairs:
            data = self.trader.get_historical_data(
                instrument=pair,
                granularity="D",
                to_date="2020-01-01",
                from_date="2010-01-01",
            )

            # Do turtle processing
            turtle_processor = TurleProcessor(data)
