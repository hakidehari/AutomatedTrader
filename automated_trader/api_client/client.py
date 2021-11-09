from automated_trader.commons.logger import logger
from automated_trader.commons.trading_utils import determine_position_sizing
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
    """Streaming Client which overrides the tpqoa library for on_success and stream_data functions"""

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
        print(f"Bid price: {bid}\nPair: {pair}")

        if bid > timeframe_high:
            logger.log(
                20, f"Placing long order on pairing: {pair} with volatility: {atr}"
            )
            self.place_long_order(pair, atr, bid)
        if bid < timeframe_low:
            logger.log(
                20, f"Placing short order on pairing: {pair} with volatility: {atr}"
            )
            self.place_short_order(pair, atr, bid)

    def place_long_order(self, pair, atr, bid):
        """Places long order when breakout happens"""
        stop_loss = 2 * atr
        account_summary = self.get_account_summary()
        position_size = determine_position_sizing(atr, account_summary, bid)

        order_result = self.create_order(
            instrument=pair,
            units=position_size,
            price=bid,
            sl_distance=stop_loss,
        )

        logger.log(20, f"Order Placed!\nOrder Information: {order_result}")

    def place_short_order(self, pair, atr, bid):
        """Places short order when breakout happens"""
        stop_loss = 2 * atr
        account_summary = self.get_account_summary()
        position_size = determine_position_sizing(atr, account_summary, bid)

        order_result = self.create_order(
            instrument=pair,
            units=-1 * position_size,
            price=bid,
            sl_distance=stop_loss,
        )

        logger.log(20, f"Order Placed!\nOrder Information: {order_result}")

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
