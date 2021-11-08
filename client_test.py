from automated_trader.api_client.client import OANDAClient
from automated_trader.data_processor.processor import TurleProcessor
from automated_trader.trader.trader import AutomatedTrader


trader = AutomatedTrader("oanda.cfg", entry_point_days=55, exit_point_days=20)

trader.run()
