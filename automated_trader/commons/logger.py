"""Instantiates logger for the package"""
import logging
import logging.handlers

logger = logging.getLogger("MyLogger")
logger.setLevel(logging.DEBUG)

handler = logging.handlers.TimedRotatingFileHandler(
    "automated_trader.log", when="D", backupCount=5
)

logger.addHandler(handler)
