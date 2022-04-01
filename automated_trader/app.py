"""
Main App file
"""
from automated_trader.trader.trader import AutomatedTrader
import os


def main():
    """Entry point for program"""

    trader = AutomatedTrader(
        os.getcwd() + os.path.sep + "oanda.cfg",
        entry_point_days=70,
        exit_point_days=8,
    )
    trader.run()
