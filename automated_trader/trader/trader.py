from automated_trader.api_client.client import OANDAClient, StreamingClient
from automated_trader.data_processor.processor import TurtleProcessor
from automated_trader.commons.logger import logger
from automated_trader.commons.trading_utils import monitor_open_positions
from datetime import datetime
from pytz import timezone
from multiprocessing import Process
import asyncio
import datetime as dt


class AutomatedTrader:
    """The main trader class. All functionality is run from here"""

    def __init__(self, file_path, entry_point_days, exit_point_days):
        self.client = OANDAClient(file_path=file_path)
        self.streaming_client = StreamingClient(file_path)
        self.entry_point_days = entry_point_days
        self.exit_point_days = exit_point_days

        self.pair_dict = self.process_all_pairs(self.entry_point_days)

        # start monitor thread
        self.monitor_thread = Process(
            target=monitor_open_positions,
            args=(
                self.client.client,
                self.exit_point_days,
                self.pair_dict,
            ),
        )
        self.monitor_thread.start()

    @staticmethod
    def trigger_pair_reprocessing():
        """Checks if the time has passed 5 PM EST"""
        tz = timezone("EST")
        current_datetime = datetime.now(tz)
        current = dt.time(
            current_datetime.hour, current_datetime.minute, current_datetime.second
        )
        start = dt.time(17, 0, 0)
        end = dt.time(17, 5, 0)
        return start <= current <= end

    def run(self):
        """Runs the automated trader"""
        logger.log(20, f"Pair dictionary values: \n{self.pair_dict}")
        while 1:

            if self.trigger_pair_reprocessing():
                # kill thread
                self.monitor_thread.terminate()
                # reprocess pairs
                self.pair_dict = self.process_all_pairs(
                    self.entry_point_days, self.exit_point_days
                )
                # restart thread
                self.monitor_thread = Process(
                    target=monitor_open_positions,
                    args=(
                        self.client.client,
                        self.exit_point_days,
                        self.pair_dict,
                    ),
                )
                self.monitor_thread.start()
                logger.log(
                    20, f"Reprocessing Pair dictionary values: \n{self.pair_dict}"
                )

            for pair in self.pair_dict:
                asyncio.run(
                    self.streaming_client.stream_data(
                        pair,
                        stop=1,
                        pair=pair,
                        timeframe_high=self.pair_dict[pair]["timeframe_high"],
                        timeframe_low=self.pair_dict[pair]["timeframe_low"],
                        atr=self.pair_dict[pair]["atr"],
                        entry_point_days=self.entry_point_days,
                        exit_point_days=self.exit_point_days,
                    )
                )

    def process_all_pairs(self, entry_point_days=55, exit_point_days=20) -> dict:
        """Process all pairs
        params:
            entry_point_days: int -> breakout parameter, defaults to 55
        returns
            pair_dict: dict -> required data for all pairings
        """

        pair_dict = {}

        for pair in self.client.instruments:
            data = self.client.get_historical_data(instrument=pair, granularity="D")

            # Do turtle processing
            turtle_processor = TurtleProcessor(data, entry_point_days, exit_point_days)
            (
                timeframe_high,
                timeframe_low,
                timeframe_exit_low,
                timeframe_exit_high,
                atr,
            ) = turtle_processor.analyze_turtle_conditions()

            pair_dict[pair] = dict()
            pair_dict[pair]["timeframe_high"] = timeframe_high
            pair_dict[pair]["timeframe_low"] = timeframe_low
            pair_dict[pair]["timeframe_exit_low"] = timeframe_exit_low
            pair_dict[pair]["timeframe_exit_high"] = timeframe_exit_high
            pair_dict[pair]["atr"] = atr

        return pair_dict
