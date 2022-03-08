"""
Main App file
"""
from automated_trader.trader.trader import AutomatedTrader
import os


def main():
    """Entry point for program"""

    trader = AutomatedTrader(
        ".." + os.path.sep + "oanda.cfg", entry_point_days=55, exit_point_days=20
    )
    trader.run()
