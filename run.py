import logging
from time import sleep

from bitmex_api import BitMEX
from bitmex_websocket import BitMEXWebsocket
from config import LEADERS, FOLLOWERS


def run():
    logger = setup_logger()

    ws = {}
    api = {}

    leader_follower_map = {}
    for follower in FOLLOWERS:
        for leader in FOLLOWERS[follower]['FOLLOWS']:
            if leader_follower_map.get(leader) is None:
                leader_follower_map[leader] = {}
                leader_follower_map[leader][follower] = FOLLOWERS[follower]['FOLLOWS'][leader]
            else:
                leader_follower_map[leader][follower] = FOLLOWERS[follower]['FOLLOWS'][leader]

    # Instantiating the WS will make it connect. Be sure to add your api_key/api_secret.
    for leader in LEADERS:
        ws[leader] = BitMEXWebsocket(endpoint=LEADERS[leader]['ENDPOINT'], symbol="",
                                     api_key=LEADERS[leader]['API_KEY'], api_secret=LEADERS[leader]['API_SECRET'])
        logger.info("Instrument data: %s" % ws[leader].get_instrument())

    for follower in FOLLOWERS:
        api[follower] = BitMEX(base_url=FOLLOWERS[follower]['ENDPOINT'], apiKey=FOLLOWERS[follower]['API_KEY'], apiSecret=FOLLOWERS[follower]['API_SECRET'])


    executions_copied = {}

    # Run forever
    while True:
        for ws_leader in ws:

            if ws[ws_leader].ws.sock.connected:
                # logger.info("Market Depth: %s" % ws.market_depth())
                executions = ws[ws_leader].executions()

                for execution in executions:
                    execID = execution['execID']
                    if execID not in executions_copied:
                        executions_copied[execID] = execution

                        for follower in leader_follower_map[ws_leader]:

                            if execution['execType'] == 'New':
                                if execution['ordType'] == 'Limit':
                                    api[follower].place_order_limit(percentage(execution['orderQty'],leader_follower_map[ws_leader][follower]), execution['price'], execution['symbol'],
                                                          execution['side'], execution['orderID'])
                                elif execution['ordType'] == 'Market':
                                    api[follower].place_order_market(percentage(execution['orderQty'],leader_follower_map[ws_leader][follower]), execution['symbol'], execution['side'],
                                                           execution['orderID'])
                            elif execution['execType'] == 'Canceled':
                                api[follower].cancelByCl([execution['orderID']])
            else:
                #reconnect
                logger.error("websocket disconnect, restart")
                pass

        sleep(1)


def percentage(quantity, percentage):
    return round(quantity * float(percentage.strip('%'))/100.0)


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
