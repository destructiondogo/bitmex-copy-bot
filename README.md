# Bitmex Copy Bot

A python bot that copies all trades in realtime from your primary bitmex account to secondary using bitmex api.
- Supports copy of all instruments (XBTUSD, XRPU19 etc)
- Supports copy of all order types : limit orders, market orders, close order, cancellation of orders, stop orders and trailing stops.
- Copy order amendments(for both drag order on UI and panel amend)
- Copy a percentage or a ratio of primary account(can be used for leverage)
- Copy to/from multiple accounts.
- Realtime copy ~1 second.

# Compatibility
Python 3.6+
Check python version by typing in shell

    python --version

If <3.6, download latest python version.

# Install

    git clone https://github.com/destructiondogo/bitmex-copy-bot.git
    cd bitmex-copy-bot
    pip install -r requirements.txt

# Configure
Modify your api keys in the config.py file.

Change ENDPOINT from TESTNET_URL to BITMEX_URL if you want to try it directly on bitmex. It's suggested that you try running it on testnet first.

    ENDPOINT : BITMEX_URL

LEADERS are the primary bitmex accounts. Create key here https://www.bitmex.com/app/apiKeys

    'API_KEY' : 'rCkGLrr2hF',
    'API_SECRET' : 'seiJbiBGLrxrPBmgsV'

FOLLOWERS are the copiers. Make sure api keys have both read + modify order access.

FOLLOWS can be used to follow multiple leaders with different percentage quantities.
If leader creates a 1000 quantity buy order, follower with 30% follow will create 300 quantity buy order.


# Run
    python run.py

# Need help?

DM on twitter for any errors/suggestions/help.
[https://twitter.com/destructionDogo](https://twitter.com/destructionDogo)

# Independent contributors
- [https://github.com/tolgamorf](https://github.com/tolgamorf) 
    Added support for amending orders, optimisation of bot, bot restart if websocket disconnects, testing the bot.

