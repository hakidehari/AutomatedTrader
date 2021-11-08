from automated_trader.api_client.client import OANDAClient, StreamingClient
from automated_trader.data_processor.processor import TurtleProcessor
from automated_trader.commons.logger import logger
import asyncio


class AutomatedTrader:
    def __init__(self, file_path, entry_point_days, exit_point_days):
        self.client = OANDAClient(file_path=file_path)
        self.streaming_client = StreamingClient(file_path)
        self.entry_point_days = entry_point_days
        self.exit_point_days = exit_point_days

    def run(self):
        """Runs the automated trader"""
        pair_dict = self.process_all_pairs(self.entry_point_days)
        logger.log(20, f"Pair dictionary values: \n{pair_dict}")
        while 1:
            for pair in pair_dict:
                asyncio.run(
                    self.streaming_client.stream_data(
                        pair,
                        stop=1,
                        pair=pair,
                        timeframe_high=pair_dict[pair]["timeframe_high"],
                        timeframe_low=pair_dict[pair]["timeframe_low"],
                        atr=pair_dict[pair]["atr"],
                        entry_point_days=self.entry_point_days,
                        exit_point_days=self.exit_point_days,
                    )
                )

    def process_all_pairs(self, entry_point_days=55):
        """Process all pairs"""

        pair_dict = {}

        for pair in self.client.instruments:
            data = self.client.get_historical_data(instrument=pair, granularity="D")

            # Do turtle processing
            turtle_processor = TurtleProcessor(data, entry_point_days)

            timeframe_high, timeframe_low, atr = turtle_processor.analyze_turtle_conditions()
            pair_dict[pair] = dict()
            pair_dict[pair]["timeframe_high"] = timeframe_high
            pair_dict[pair]["timeframe_low"] = timeframe_low
            pair_dict[pair]["atr"] = atr

        return pair_dict
