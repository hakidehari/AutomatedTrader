from automated_trader.commons.logger import logger
from automated_trader.commons.trading_utils import determine_position_sizing, get_open_positions
from datetime import datetime, timedelta
import tpqoa

from v20.transaction import StopLossDetails, ClientExtensions
from v20.transaction import TrailingStopLossDetails, TakeProfitDetails


class OANDAClient(tpqoa.tpqoa):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.instruments = self.get_override_instruments()
        self.account_summary = self.get_account_summary()
        logger.log(20, f"Account Summary: \n{self.account_summary}")

    def get_override_instruments(self):
        """Gets list of instruments in pair1_pair2 format"""
        ins = self.get_instruments()
        return [element[1] for element in ins]

    def get_historical_data(self, instrument: str, granularity: str):
        """Gathers historical data for specified timeframe for specified Pairing"""
        from_date = (datetime.today() - timedelta(days=100)).strftime("%Y-%m-%d")
        to_date = datetime.today().strftime("%Y-%m-%d")

        data = self.get_history(
            instrument=instrument,
            start=from_date,
            end=to_date,
            granularity=granularity,
            price="M",
        )
        return data

    def create_order(self, instrument, units, price=None, sl_distance=None,
                     tsl_distance=None, tp_price=None, comment=None,
                     touch=False, suppress=False, ret=False):
        ''' Places order with Oanda.

        Parameters
        ==========
        instrument: string
            valid instrument name
        units: int
            number of units of instrument to be bought
            (positive int, eg 'units=50')
            or to be sold (negative int, eg 'units=-100')
        price: float
            limit order price, touch order price
        sl_distance: float
            stop loss distance price, mandatory eg in Germany
        tsl_distance: float
            trailing stop loss distance
        tp_price: float
            take profit price to be used for the trade
        comment: str
            string
        touch: boolean
            market_if_touched order (requires price to be set)
        suppress: boolean
            whether to suppress print out
        ret: boolean
            whether to return the order object
        '''
        client_ext = ClientExtensions(
            comment=comment) if comment is not None else None
        sl_details = (StopLossDetails(distance=sl_distance,
                                      clientExtensions=client_ext)
                      if sl_distance is not None else None)
        tsl_details = (TrailingStopLossDetails(distance=tsl_distance,
                                               clientExtensions=client_ext)
                       if tsl_distance is not None else None)
        tp_details = (TakeProfitDetails(
            price=tp_price, clientExtensions=client_ext)
            if tp_price is not None else None)
        if price is None:
            request = self.ctx.order.market(
                self.account_id,
                instrument=instrument,
                units=units,
                stopLossOnFill=sl_details,
                trailingStopLossOnFill=tsl_details,
                takeProfitOnFill=tp_details,
            )
        elif touch:
            request = self.ctx.order.market_if_touched(
                self.account_id,
                instrument=instrument,
                price=price,
                units=units,
                stopLossOnFill=sl_details,
                trailingStopLossOnFill=tsl_details,
                takeProfitOnFill=tp_details
            )
        else:
            request = self.ctx.order.limit(
                self.account_id,
                instrument=instrument,
                price=price,
                units=units,
                stopLossOnFill=sl_details,
                trailingStopLossOnFill=tsl_details,
                takeProfitOnFill=tp_details
            )

        print(f"REQUEST BODY: {request.body}")
        # First checking if the order is rejected
        if 'orderRejectTransaction' in request.body:
            order = request.get('orderRejectTransaction')
        elif 'orderFillTransaction' in request.body:
            order = request.get('orderFillTransaction')
        elif 'orderCreateTransaction' in request.body:
            order = request.get('orderCreateTransaction')
        else:
            # This case does not happen.  But keeping this for completeness.
            order = None

        if not suppress and order is not None:
            print('\n\n', order.dict(), '\n')
        if ret is True:
            return order.dict() if order is not None else None


class StreamingClient(OANDAClient):
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
            if self.check_if_position_exists(pair):
                logger.log(20, f"position already exists for pairing {pair}. Skipping...")
            else:
                logger.log(
                    20, f"Placing long order on pairing: {pair} with volatility: {atr}"
                )
                self.place_long_order(pair, atr, bid)
        
        if bid < timeframe_low:
            if self.check_if_position_exists(pair):
                logger.log(20, f"position already exists for pairing {pair}. Skipping...")
            else:
                logger.log(
                    20, f"Placing short order on pairing: {pair} with volatility: {atr}"
                )
                self.place_short_order(pair, atr, bid)

    def place_long_order(self, pair, atr, bid):
        """Places long order when breakout happens"""
        stop_loss = round(2 * atr, 5)
        print(f"STOP LOSS: {stop_loss}")
        account_summary = self.get_account_summary()
        position_size = determine_position_sizing(atr, account_summary, bid)

        order_result = self.create_order(
            instrument=pair,
            units=position_size,
            price=bid,
            sl_distance=stop_loss,
            ret=True,
        )

        logger.log(20, f"Order Placed!\nOrder Information: {order_result}")

    def place_short_order(self, pair, atr, bid):
        """Places short order when breakout happens"""
        stop_loss = round(2 * atr, 5)
        print(f"STOP LOSS: {stop_loss}")
        account_summary = self.get_account_summary()
        position_size = determine_position_sizing(atr, account_summary, bid)

        order_result = self.create_order(
            instrument=pair,
            units=-1 * position_size,
            price=bid,
            sl_distance=stop_loss,
            ret=True,
        )

        logger.log(20, f"Order Placed!\nOrder Information: {order_result}")

    def check_if_position_exists(self, pair):
        """Check if an open position already exists"""
        positions = get_open_positions(self)
        for position in positions:
            if position["instrument"] == pair:
                return True
        return False

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
