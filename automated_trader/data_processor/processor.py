import pandas as pd
import numpy as np


class TurtleProcessor:
    """TurtleProcessor class analyzes conditions for the turtle trading method"""

    def __init__(self, data: pd.DataFrame, entry_point_days: int, exit_point_days: int):
        self.data = data
        self.entry_point_days = entry_point_days
        self.exit_point_days = exit_point_days

    def get_exit_price_conditions(self, highs, lows):
        """Gets exit price conditions"""
        sliced_highs = highs.iloc[
            len(highs) - self.exit_point_days - 1 : len(highs) - 1
        ]
        sliced_lows = lows.iloc[len(lows) - self.exit_point_days - 1 : len(lows) - 1]
        timeframe_high = max(sliced_highs)
        timeframe_low = min(sliced_lows)

        return timeframe_high, timeframe_low

    def analyze_turtle_conditions(self) -> tuple:
        """Check if any turtle conditions are met
        returns:
             tuple of 3 values:
                 timeframe_high: float
                 timeframe_low: float
                 atr: float
        """
        # analyze conditions
        highs = self.data["h"]
        lows = self.data["l"]

        sliced_highs = highs.iloc[
            len(highs) - self.entry_point_days - 1 : len(highs) - 1
        ]
        sliced_lows = lows.iloc[len(lows) - self.entry_point_days - 1 : len(lows) - 1]

        timeframe_high = max(sliced_highs)
        timeframe_low = min(sliced_lows)

        high_low = self.data["h"] - self.data["l"]
        high_close = np.abs(self.data["h"] - self.data["c"].shift())
        low_close = np.abs(self.data["l"] - self.data["c"].shift())

        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)

        atr = true_range.rolling(20).sum() / 20
        atr = atr.iloc[len(atr) - 1 : len(atr)]

        timeframe_exit_low, timeframe_exit_high = self.get_exit_price_conditions(
            highs, lows
        )

        return (
            timeframe_high,
            timeframe_low,
            timeframe_exit_low,
            timeframe_exit_high,
            atr.iloc[0],
        )
