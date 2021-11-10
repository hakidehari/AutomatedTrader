from automated_trader.trader.trader import AutomatedTrader

if __name__ == "__main__":
    trader = AutomatedTrader("oanda.cfg", entry_point_days=55, exit_point_days=20)

    trader.run()
