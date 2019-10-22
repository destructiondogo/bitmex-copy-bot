import sys
import os
import logging
from time import sleep

from bitmex_api import BitMEX
from bitmex_websocket import BitMEXWebsocket
from config import LEADERS, FOLLOWERS


def run():
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
        # logger.info("Instrument data: %s" % ws[leader].get_instrument())

    for follower in FOLLOWERS:
        api[follower] = BitMEX(base_url=FOLLOWERS[follower]['ENDPOINT'], apiKey=FOLLOWERS[follower]['API_KEY'], apiSecret=FOLLOWERS[follower]['API_SECRET'])


    executions_copied = {}

    # Run forever
    while True:
        for ws_leader in ws:

            if ws[ws_leader].ws.sock.connected:
                # logger.info("Market Depth: %s" % ws.market_depth())
                sleep(0.1)
                executions = ws[ws_leader].executions()

                for execution in executions:
                    execID = execution['execID']
                    if execID not in executions_copied:
                        executions_copied[execID] = execution
                        logger.info(f">>> Execution data: {execution}\n")

                        for follower in leader_follower_map[ws_leader]:

                            if execution['execType'] == 'New':
                                if execution['ordType'] == 'Limit':
                                    api[follower].place_order_limit(percentage(execution['orderQty'],leader_follower_map[ws_leader][follower]), execution['price'], execution['symbol'],
                                                          execution['side'], execution['orderID'],execution['execInst'])
                                elif execution['ordType'] == 'Market':
                                    api[follower].place_order_market(percentage(execution['orderQty'],leader_follower_map[ws_leader][follower]), execution['symbol'], execution['side'],
                                                           execution['orderID'],execution['execInst'])
                                elif execution['ordType'] == 'Stop' or execution['ordType'] == 'StopLimit' or execution['ordType'] == 'MarketIfTouched' or execution['ordType'] == 'LimitIfTouched':
                                    api[follower].place_order_stop(percentage(execution['orderQty'],leader_follower_map[ws_leader][follower]),execution['ordType'],execution['stopPx'],execution['price'],execution['symbol'],
                                                            execution['side'], execution['orderID'],execution['execInst'],execution['pegPriceType'],execution['pegOffsetValue'])
                            elif execution['execType'] == 'Canceled':
                                api[follower].cancelByCl([execution['orderID']])
                            elif execution['execType'] == 'Trade':
                                pass
                            elif execution['execType'] == 'Replaced':
                                api[follower].amendOrderByCl(execution["orderID"], percentage(execution["orderQty"],leader_follower_map[ws_leader][follower]), execution["price"], execution["stopPx"], execution["pegOffsetValue"])
                            elif execution['execType'] == 'Settlement':
                                pass  # similar to a filled trade.
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


def main():
    logger.info(">>> Starting BitMEX COPY BOT...")

    while True:
        try:
            # Start the bot
            run()
        except KeyboardInterrupt:
            # User quit (Ctrl+C)
            logger.info(">>> Ctrl+C detected! Shutting down...")
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
        except Exception as e:
            # Other exception
            logger.exception(e)
            logger.info(">>> Error occurred. The bot will restart in 5 seconds...")
            sleep(5)
            main()


if __name__ == "__main__":
    logger = setup_logger()
    main()
