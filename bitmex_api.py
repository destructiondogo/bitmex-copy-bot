import time
from urllib.parse import urlparse
import hmac
import hashlib
import json
import requests
from requests.auth import AuthBase
import uuid
import base64
import datetime

class BitMEX(object):

    """BitMEX API Connector."""

    def __init__(self, base_url=None, symbol=None, login=None, password=None, otpToken=None,
                 apiKey=None, apiSecret=None, shouldWSAuth=True):
        """Init connector."""
        self.base_url = base_url
        self.symbol = symbol
        self.token = None
        # User/pass auth is no longer supported
        if (login or password or otpToken):
            raise Exception("User/password authentication is no longer supported via the API. Please use " +
                            "an API key. You can generate one at https://www.bitmex.com/app/apiKeys")
        if (apiKey is None):
            raise Exception("Please set an API key and Secret to get started. See " +
                            "https://github.com/BitMEX/sample-market-maker/#getting-started for more information."
                            )
        self.apiKey = apiKey
        self.apiSecret = apiSecret
        # Prepare HTTPS session
        self.session = requests.Session()
        # These headers are always sent
        self.session.headers.update({'user-agent': 'liquidbot-' + 'v1.1'})
        self.session.headers.update({'content-type': 'application/json'})
        self.session.headers.update({'accept': 'application/json'})

    def __del__(self):
        self.exit()

    def exit(self):
        self.ws.exit()


    def authentication_required(function):
        """Annotation for methods that require auth."""
        def wrapped(self, *args, **kwargs):
            if not (self.apiKey):
                msg = "You must be authenticated to use this method"
                print(time.strftime("%d %b %Y %H:%M:%S",time.gmtime()),msg)
            else:
                return function(self, *args, **kwargs)
        return wrapped


    @authentication_required
    def close(self, symbol):
        endpoint = "order"
        # Generate a unique clOrdID with our prefix so we can identify it.
        clOrdID = base64.b64encode(uuid.uuid4().bytes).decode('utf-8').rstrip('=\n')
        postdict = {
            'symbol': symbol,
            'ordType': "Market",
            'execInst': "Close",
            'clOrdID': clOrdID
        }
        return self._curl_bitmex(api=endpoint, postdict=postdict, verb="POST")

    @authentication_required
    def place_order_limit(self,quantity, price, symbol, side, clOrdID,execInst):
        endpoint = "order"

        postdict = {
            'symbol': symbol,
            'orderQty': quantity,
            'price': price,
            'side': side,
            'clOrdID': clOrdID,
            'execInst': execInst
        }
        return self._curl_bitmex(api=endpoint, postdict=postdict, verb="POST")

    @authentication_required
    def place_order_market(self, quantity, symbol, side, clOrdID,execInst):
        endpoint = "order"
        postdict = {
            'symbol': symbol,
            'orderQty': quantity,
            'ordType': 'Market',
            'side': side,
            'clOrdID': clOrdID,
            'execInst': execInst
        }
        return self._curl_bitmex(api=endpoint, postdict=postdict, verb="POST")


    @authentication_required
    def place_order_stop(self,quantity,ordType, stopPx, symbol,side,clOrdID,execInst,pegPriceType,pegOffsetValue):
        """Place an order."""
        if stopPx < 0:
            raise Exception("Price must be positive.")
        endpoint = "order"
        postdict = {
            'symbol': symbol,
            'orderQty': quantity,
            'ordType': ordType,
            'stopPx': stopPx,
            'side': side,
            'clOrdID': clOrdID,
            'execInst': execInst,
            'pegPriceType': pegPriceType,
            'pegOffsetValue': pegOffsetValue

        }
        return self._curl_bitmex(api=endpoint, postdict=postdict, verb="POST")

    @authentication_required
    def cancelByCl(self, clOrdID):
        """Cancel an existing order."""
        api = "order"
        postdict = {
            'clOrdID': clOrdID,
        }
        return self._curl_bitmex(api=api, postdict=postdict, verb="DELETE")

    @authentication_required
    def cancel(self, orderID):
        """Cancel an existing order."""
        api = "order"
        postdict = {
            'orderID': orderID,
        }
        return self._curl_bitmex(api=api, postdict=postdict, verb="DELETE")

    def _curl_bitmex(self, api, query=None, postdict=None, timeout=3, verb=None):
        """Send a request to BitMEX Servers."""
        # Handle URL
        url = self.base_url + api

        # Default to POST if data is attached, GET otherwise
        if not verb:
            verb = 'POST' if postdict else 'GET'

        # Auth: Use Access Token by default, API Key/Secret if provided
        auth = AccessTokenAuth(self.token)
        if self.apiKey:
            auth = APIKeyAuthWithExpires(self.apiKey, self.apiSecret)

        # Make the request
        try:
            req = requests.Request(verb, url, json=postdict, auth=auth, params=query)
            prepped = self.session.prepare_request(req)
            response = self.session.send(prepped, timeout=timeout)
            # Make non-200s throw
            response.raise_for_status()

        except requests.exceptions.HTTPError as e:
            # 401 - Auth error. This is fatal with API keys.
            if response.status_code == 401:
                print(time.strftime("%d %b %Y %H:%M:%S",time.gmtime()),"Login information or API Key incorrect, please check and restart.")

            # 404, can be thrown if order canceled does not exist.
            elif response.status_code == 404:
                if verb == 'DELETE':
                    # print(time.strftime("%d %b %Y %H:%M:%S",time.gmtime()),"Order not found: %s" % postdict['orderID'])
                    print("Order being canceled does not exist")
                    return
                print("Unable to contact the BitMEX API (404). ")

            # 429, ratelimit; cancel orders & wait until X-Ratelimit-Reset
            elif response.status_code == 429:
                print(time.strftime("%d %b %Y %H:%M:%S",time.gmtime()),"Ratelimited on current request. Sleeping, then trying again. Try fewer " +
                                  "order pairs or contact support@bitmex.com to raise your limits. " +
                                  "Request: %s \n %s" % (url, json.dumps(postdict)))

                # Figure out how long we need to wait.
                ratelimit_reset = response.headers['X-Ratelimit-Reset']
                to_sleep = int(ratelimit_reset) - int(time.time())
                reset_str = datetime.datetime.fromtimestamp(int(ratelimit_reset)).strftime('%X')

                print(time.strftime("%d %b %Y %H:%M:%S",time.gmtime()),"Your ratelimit will reset at %s. Sleeping for %d seconds." % (reset_str, to_sleep))
                time.sleep(to_sleep)

                # Retry the request.
                return self._curl_bitmex(api, query, postdict, timeout, verb)

            # 503 - BitMEX temporary downtime, likely due to a deploy. Try again
            elif response.status_code == 503:
                print(time.strftime("%d %b %Y %H:%M:%S",time.gmtime()),"Unable to contact the BitMEX API (503), retrying. " +
                                    "Request: %s \n %s" % (url, json.dumps(postdict)))
                time.sleep(3)
                return self._curl_bitmex(api, query, postdict, timeout, verb)

            elif response.status_code == 400:
                error = response.json()['error']
                message = error['message'].lower()
                # Duplicate clOrdID: that's fine, probably a deploy, go get the order and return it
                if 'duplicate clordid' in message:

                    order = self._curl_bitmex('/order',
                                              query={'filter': json.dumps({'clOrdID': postdict['clOrdID']})},
                                              verb='GET')[0]
                    if (
                            order['orderQty'] != abs(postdict['orderQty']) or
                            order['side'] != ('Buy' if postdict['orderQty'] > 0 else 'Sell') or
                            order['price'] != postdict['price'] or
                            order['symbol'] != postdict['symbol']):
                        raise Exception('Attempted to recover from duplicate clOrdID, but order returned from API ' +
                                        'did not match POST.\nPOST data: %s\nReturned order: %s' % (
                                            json.dumps(postdict), json.dumps(order)))
                    # All good
                    return order
                elif 'insufficient available balance' in message:
                    raise Exception('Account out of funds. The message: %s' % error['message'])

            # If we haven't returned or re-raised yet, we get here.
            print("Error: %s: %s" % (e, response.text))
            print(time.strftime("%d %b %Y %H:%M:%S",time.gmtime()),"Endpoint was: %s %s: %s" % (verb, api, json.dumps(postdict)))
            raise e

        except requests.exceptions.Timeout as e:
            # Timeout, re-run this request
            print(time.strftime("%d %b %Y %H:%M:%S",time.gmtime()),"Timed out, retrying...")
            return self._curl_bitmex(api, query, postdict, timeout, verb)

        except requests.exceptions.ConnectionError as e:
            print(time.strftime("%d %b %Y %H:%M:%S",time.gmtime()),"Unable to contact the BitMEX API (ConnectionError). Please check the URL. Retrying. " +
                                "Request: %s \n %s" % (url, json.dumps(postdict)))
            time.sleep(1)
            return self._curl_bitmex(api, query, postdict, timeout, verb)

        return response.json()



def generate_signature(secret, verb, url, nonce, data):

    parsedURL = urlparse(url)
    path = parsedURL.path
    if parsedURL.query:
        path = path + '?' + parsedURL.query
    if isinstance(data, (bytes, bytearray)):
        data = data.decode('utf8')
    message = verb + path + str(nonce) + data
    signature = hmac.new(bytes(secret, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()
    return signature

class APIKeyAuthWithExpires(AuthBase):

    def __init__(self, apiKey, apiSecret):
        self.apiKey = apiKey
        self.apiSecret = apiSecret

    def __call__(self, r):
        # modify and return the request
        expires = int(round(time.time()) + 5)  # 5s grace period in case of clock skew
        r.headers['api-expires'] = str(expires)
        r.headers['api-key'] = self.apiKey
        r.headers['api-signature'] = generate_signature(self.apiSecret, r.method, r.url, expires, r.body or '')

        return r

class AccessTokenAuth(AuthBase):
    def __init__(self, accessToken):
        self.token = accessToken

    def __call__(self, r):
        if (self.token):
            r.headers['access-token'] = self.token
        return r