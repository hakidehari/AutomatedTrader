from automated_trader.commons.logger import logger
import math
import tpqoa
import time


def determine_position_sizing(atr: float, account_details: dict, bid: float):
    """Determines a trade position size
    Units = 1% of Account / Market Dollar Volatility
    """
    one_percent_balance = 0.25 * float(account_details["balance"])
    dollar_volatility = atr * bid
    position_size = one_percent_balance / dollar_volatility
    return math.floor(position_size)


def get_open_positions(client: tpqoa.tpqoa):
    """Retrieves all open positions"""
    try:
        positions = client.get_positions()
        return positions
    except Exception as e:
        print(e)
        raise ConnectionAbortedError(
            "Failed to get open positions due to a connection error"
        )


def process_open_positions(
    client: tpqoa.tpqoa, positions: list, pair_dict: dict, exit_point_days: int
) -> dict:
    """Processes the open position based on turtle criteria and closes them should the exit criteria be met"""
    # iterate over all positions
    for position in positions:
        pair = position["instrument"]
        timeframe_exit_low = pair_dict[pair]["timeframe_exit_low"]
        timeframe_exit_high = pair_dict[pair]["timeframe_exit_high"]

        type_of_order = "long" if float(position["long"]["units"]) != 0.0 else "short"

        print(f"TYPE OF POSITION: {type_of_order}")

        open_position = position[type_of_order]

        price = open_position["averagePrice"]
        units = float(open_position["units"])

        if type_of_order == "long":
            if price < timeframe_exit_low:
                order_result = client.create_order(
                    instrument=pair,
                    units=-1 * units,
                    ret=True,
                )
                logger.log(
                    20,
                    f"Position closed because exit criteria met for position.  For this long position, {timeframe_exit_low} is the {exit_point_days} day low.\nPosition:\n{position}\nClose Response:\n{order_result}",
                )
        else:
            if price > timeframe_exit_high:
                order_result = client.create_order(
                    instrument=pair,
                    units=-1 * units,
                    ret=True,
                )
                logger.log(
                    20,
                    f"Position closed because exit criteria met for position.  For this short position, {timeframe_exit_high} is the {exit_point_days} High.\nPosition:\n{position}\nClose Response:\n{order_result}",
                )


def monitor_open_positions(client: tpqoa.tpqoa, exit_point_days: int, pair_dict: dict):
    """Constantly monitors open positions"""
    while 1:
        print("Processing open Positions for any exit criteria...")
        positions = get_open_positions(client)
        process_open_positions(client, positions, pair_dict, exit_point_days)

        # sleep timer of 1 second
        time.sleep(1)
