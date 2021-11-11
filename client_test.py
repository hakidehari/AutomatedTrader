from automated_trader.trader.trader import AutomatedTrader

if __name__ == "__main__":
    trader = AutomatedTrader("oanda.cfg", entry_point_days=70, exit_point_days=8)

    trader.run()
