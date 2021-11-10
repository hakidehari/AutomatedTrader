from automated_trader.commons.logger import logger
import math
import tpqoa
import time


def determine_position_sizing(atr: float, account_details: dict, bid: float):
    """Determines a trade position size
    Units = 1% of Account / Market Dollar Volatility
    """
    one_percent_balance = 0.01 * float(account_details["balance"])
    dollar_volatility = atr * bid
    position_size = one_percent_balance / dollar_volatility
    return math.floor(position_size)


def get_open_positions(client: tpqoa.tpqoa):
    """Retrieves all open positions"""
    positions = client.get_positions()
    logger.log(20, f"Positions: \n{positions}")
    return positions


# TODO have to process open positions for exit conditions
def process_open_positions(client: tpqoa.tpqoa, positions: list, pair_dict: dict, exit_point_days: int) -> dict:
    """Processes the open position based on turtle criteria"""
    for position in positions:
        pair = position["instrument"]
        type_of_order = "long" if float(position["long"]["units"]) == 0.0 else "short"
        open_position = (
            position["long"]
            if float(position["long"]["units"]) != 0.0
            else position["short"]
        )
        price = open_position["averagePrice"]
        units = open_position["units"]

        if type_of_order == "long":
            if price < pair_dict[pair]["timeframe_exit_low"]:
                pass
        else:
            pass


# TODO build out position monitor and functionality
def monitor_open_positions(client: tpqoa.tpqoa, exit_point_days: int, pair_dict: dict):
    """Constantly monitors open positions"""
    while 1:
        print("Processing open Positions for any exit criteria...")
        positions = get_open_positions(client)
        positions_to_close = process_open_positions(client, positions, pair_dict, exit_point_days)

        # add logic for closing positions under here

        # sleep timer of 20 seconds
        time.sleep(1)
