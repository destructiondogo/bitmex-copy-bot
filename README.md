# Bitmex Copy Bot

A python bot that copies all trades in realtime from your primary bitmex account to secondary using bitmex api.
- Supports copy of all instruments (XBTUSD, XRPU19 etc)
- Supports copy of limit orders, market orders, close order, cancellation of orders.
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

    ENDPOINT = BITMEX_URL

API_KEY is the primary bitmex account. Ensure it is read only.

    API_KEY = 'rCkGLrr2hF'
    API_SECRET = 'seiJbiBGLrxrPBmgsV'

API_KEY2 is secondary bitmex account. Make sure it can read + create order.

    API_KEY_2 = 'dXNlP_fwgor'
    API_SECRET_2 = 'dfPHP8IVHyno-rgPJP2eq'


# Run
    python run.py

# Need help?

DM on twitter for any errors/suggestions/help.
[https://twitter.com/destructionDogo](https://twitter.com/destructionDogo)

# Features coming in few days
- Copy only a percentage of primary account
- Copy Stops and Trailing stops
- Copy to/from multiple accounts.
