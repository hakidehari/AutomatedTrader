import pandas as pd
import numpy as np


class TurtleProcessor:
    def __init__(self, data: pd.DataFrame, entry_point_days: int):
        self.data = data
        self.entry_point_days = entry_point_days

    def analyze_turtle_conditions(self) -> tuple:
        """Check if any turtle conditions are met"""
        # analyze conditions
        highs = self.data["h"]
        lows = self.data["l"]

        sliced_highs = highs.iloc[len(highs) - self.entry_point_days -1 : len(highs)-1]
        sliced_lows = lows.iloc[len(lows) - self.entry_point_days - 1 : len(lows)-1]

        timeframe_high = max(sliced_highs)
        timeframe_low = min(sliced_lows)

        high_low = self.data['h'] - self.data['l']
        high_close = np.abs(self.data['h'] - self.data['c'].shift())
        low_close = np.abs(self.data['l'] - self.data['c'].shift())

        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)

        atr = true_range.rolling(20).sum()/20
        atr = atr.iloc[len(atr)-1:len(atr)]

        return (timeframe_high, timeframe_low, atr.iloc[0])
