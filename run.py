import logging
from time import sleep

from bitmex_api import BitMEX
from bitmex_websocket import BitMEXWebsocket
from config import ENDPOINT, API_KEY, API_SECRET, API_KEY_2, API_SECRET_2


def run():
    logger = setup_logger()

    # Instantiating the WS will make it connect. Be sure to add your api_key/api_secret.
    ws = BitMEXWebsocket(endpoint=ENDPOINT, symbol="",
                         api_key=API_KEY, api_secret=API_SECRET)

    logger.info("Instrument data: %s" % ws.get_instrument())

    api = BitMEX(base_url=ENDPOINT, apiKey=API_KEY_2, apiSecret=API_SECRET_2)
    executions_copied = {}

    # Run forever
    while(ws.ws.sock.connected):
        # logger.info("Market Depth: %s" % ws.market_depth())
        executions = ws.executions()

        for execution in executions:
            execID = execution['execID']
            if execID not in executions_copied:
                executions_copied[execID] = execution
                if execution['execType'] == 'New':
                    if execution['ordType'] == 'Limit':
                        api.place_order_limit(execution['orderQty'],execution['price'],execution['symbol'],execution['side'],execution['orderID'])
                    elif execution['ordType'] == 'Market':
                        api.place_order_market(execution['orderQty'],execution['symbol'],execution['side'],execution['orderID'])
                elif execution['execType'] == 'Canceled':
                    api.cancelByCl([execution['orderID']])


        sleep(1)


def setup_logger():
    # Prints logger info to terminal
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Change this to DEBUG if you want a lot more info
    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


if __name__ == "__main__":
    run()