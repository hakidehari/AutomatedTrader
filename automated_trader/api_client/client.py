from automated_trader.commons.logger import logger
from datetime import datetime, timedelta
import tpqoa


class OANDAClient:
    def __init__(self, file_path):
        self.client = tpqoa.tpqoa(file_path)
        self.instruments = self.get_instruments()
        self.account_summary = self.get_account_summary()
        logger.log(20, f"Account Summary: \n{self.account_summary}")

    def get_account_summary(self):
        """Retrieves account summary"""
        return self.client.get_account_summary()

    def get_instruments(self):
        """Gets list of instruments in pair1_pair2 format"""
        ins = self.client.get_instruments()
        return [element[1] for element in ins]

    def get_historical_data(self, instrument: str, granularity: str):
        """Gathers historical data for specified timeframe for specified Pairing"""
        from_date = (datetime.today() - timedelta(days=100)).strftime("%Y-%m-%d")
        to_date = datetime.today().strftime("%Y-%m-%d")

        data = self.client.get_history(
            instrument=instrument,
            start=from_date,
            end=to_date,
            granularity=granularity,
            price="M",
        )
        return data


class StreamingClient(tpqoa.tpqoa):
    def on_success(
        self,
        time,
        bid,
        ask,
        pair=None,
        timeframe_high=None,
        timeframe_low=None,
        atr=None,
        entry_point_days=None,
        exit_point_days=None,
    ):
        """Monitor bid price to determine if price breakout happens"""
        bid = "{:.5f}".format(bid)
        bid = float(bid)
        logger.log(20, f"Bid price: {bid}\nPair: {pair}")

        if bid > timeframe_high:
            self.place_long_order(pair, atr)
        if bid < timeframe_low:
            self.place_short_order(pair, atr)

    # TODO
    def place_long_order(self, pair, atr):
        """Places long order when breakout happens"""
        account_deets = self.get_account_summary()
        stop_loss = 2*atr
        add_pos_condition = 0.5*atr

    # TODO
    def place_short_order(self, pair, atr):
        """Places short order when breakout happens"""
        account_deets = self.get_account_summary()
        stop_loss = 2*atr
        add_pos_condition = 0.5*atr
    
    async def stream_data(
        self,
        instrument,
        stop=None,
        ret=False,
        callback=None,
        pair=None,
        timeframe_high=None,
        timeframe_low=None,
        atr=None,
        entry_point_days=None,
        exit_point_days=None,
    ):
        """Starts a real-time data stream.
        Parameters
        ==========
        instrument: string
            valid instrument name
        """
        self.stream_instrument = instrument
        self.ticks = 0
        response = self.ctx_stream.pricing.stream(
            self.account_id, snapshot=True, instruments=instrument
        )
        msgs = []
        for msg_type, msg in response.parts():
            msgs.append(msg)
            # print(msg_type, msg)
            if msg_type == "pricing.ClientPrice":
                self.ticks += 1
                self.time = msg.time
                if callback is not None:
                    callback(
                        msg.instrument,
                        msg.time,
                        float(msg.bids[0].dict()["price"]),
                        float(msg.asks[0].dict()["price"]),
                    )
                else:
                    self.on_success(
                        msg.time,
                        float(msg.bids[0].dict()["price"]),
                        float(msg.asks[0].dict()["price"]),
                        pair=pair,
                        timeframe_high=timeframe_high,
                        timeframe_low=timeframe_low,
                        atr=atr,
                        entry_point_days=entry_point_days,
                        exit_point_days=exit_point_days,
                    )
                if stop is not None:
                    if self.ticks >= stop:
                        if ret:
                            return msgs
                        break
            if self.stop_stream:
                if ret:
                    return msgs
                break
