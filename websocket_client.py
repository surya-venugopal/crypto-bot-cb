# cbpro/WebsocketClient.py
# original author: Daniel Paquin
# mongo "support" added by Drew Rice
#
#
# Template object to receive messages from the Coinbase Websocket Feed

from __future__ import print_function
import json
import base64
import hmac
import hashlib
import time
from threading import Thread
from websocket import create_connection, WebSocketConnectionClosedException
from pymongo import MongoClient
from cbpro.cbpro_auth import get_auth_headers
import datetime as dt


class WebsocketClient(object):
    def __init__(
            self,
            url="wss://ws-feed.pro.coinbase.com",
            products=None,
            message_type="subscribe",
            mongo_collection=None,
            should_print=True,
            auth=True,
            api_key="2c6d3a1b53d5a2d31676254b3373db8d",
            api_secret="UpxX5+tMEyC8FruQTeW7tEE8s063CWLJea7PrcAofln+sy5xRV/FpAOTp2G7f1+BZwHhRfw5XsL97/JvHpSMjQ==",
            api_passphrase="auh4oolfqs",
            # Make channels a required keyword-only argument; see pep3102
            *,
            # Channel options: ['ticker', 'user', 'matches', 'level2', 'full']
            channels=None):
        self.url = url
        self.products = products
        self.channels = channels
        self.type = message_type
        self.stop = True
        self.error = None
        self.ws = None
        self.thread = None
        self.auth = auth
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.should_print = should_print
        self.mongo_collection = mongo_collection

    def start(self):
        def _go():
            self._connect()
            self._listen()
            self._disconnect()

        self.stop = False
        self.on_open()
        self.thread = Thread(target=_go)
        self.keepalive = Thread(target=self._keepalive)
        self.thread.start()

    def _connect(self):
        if self.products is None:
            self.products = ["BTC-USD"]
        elif not isinstance(self.products, list):
            self.products = [self.products]

        if self.url[-1] == "/":
            self.url = self.url[:-1]

        if self.channels is None:
            self.channels = [{"name": "ticker", "product_ids": [product_id for product_id in self.products]}]
            sub_params = {'type': 'subscribe', 'product_ids': self.products, 'channels': self.channels}
        else:
            sub_params = {'type': 'subscribe', 'product_ids': self.products, 'channels': self.channels}

        if self.auth:
            timestamp = str(time.time())
            message = timestamp + 'GET' + '/users/self/verify'
            auth_headers = get_auth_headers(timestamp, message, self.api_key, self.api_secret, self.api_passphrase)
            sub_params['signature'] = auth_headers['CB-ACCESS-SIGN']
            sub_params['key'] = auth_headers['CB-ACCESS-KEY']
            sub_params['passphrase'] = auth_headers['CB-ACCESS-PASSPHRASE']
            sub_params['timestamp'] = auth_headers['CB-ACCESS-TIMESTAMP']

        self.ws = create_connection(self.url)

        self.ws.send(json.dumps(sub_params))

    def _keepalive(self, interval=30):
        while self.ws.connected:
            self.ws.ping("keepalive")
            time.sleep(interval)

    def _listen(self):
        self.keepalive.start()
        while not self.stop:
            try:
                data = self.ws.recv()
                msg = json.loads(data)
            except ValueError as e:
                self.on_error(e)
            except Exception as e:
                self.on_error(e)
            else:
                self.on_message(msg)

    def _disconnect(self):
        try:
            if self.ws:
                self.ws.close()
        except WebSocketConnectionClosedException as e:
            pass
        finally:
            self.keepalive.join()

        self.on_close()

    def close(self):
        self.stop = True   # will only disconnect after next msg recv
        self._disconnect() # force disconnect so threads can join
        self.thread.join()

    def on_open(self):
        if self.should_print:
            print("-- Subscribed! --\n")

    def on_close(self):
        if self.should_print:
            print("\n-- Socket Closed --")

    def on_message(self, msg):
        if self.should_print:
            print(msg)
        if self.mongo_collection:  # dump JSON to given mongo collection
            self.mongo_collection.insert_one(msg)

    def on_error(self, e, data=None):
        self.error = e
        self.stop = True
        print('{} - data: {}'.format(e, data))




if __name__ == "__main__":
    import sys
    import cbpro
    import time

    class Queue:
        def __init__(self):
            self.queue = []
        
        def enqueue(self,val):
            self.queue.append(val)

        def dequeue(self):
            return self.queue.pop(0)
            

        def size(self):
            return len(self.queue)


    class MyWebsocketClient(WebsocketClient):
        def on_open(self):
            self.url = "wss://ws-feed.pro.coinbase.com/"
            self.products = ["ETH-USD"]

            self.initialAmount = 1000.0
            self.currentAmount = self.initialAmount
            self.currentCrypto = 0.0
            
            self.isBought = False

            self.a = 21
            self.b = 9

            self.queuea = Queue()
            self.queueb = Queue()
            
            self.MAa = 0.0
            self.MAb = 0.0


            self.previousTime = ""
            
            self.sum1min = 0.0

            self.i = 0

            # self.message_count = 0
            print("Let's count the messages!")

        def on_message(self, msg):
            global initialAmount
            try:
                # print(msg['product_id'])
                currentPrice = float(msg['price'])
                currentTime = msg['time'][11:19]
                
                if(self.previousTime != "" and currentTime != self.previousTime):

                    if(currentTime[3:5] != self.previousTime[3:5]):
                        
                        if self.queuea.size() < self.a:
                            self.queuea.enqueue([self.sum1min/self.i,currentTime])
                            self.MAa += self.sum1min/self.i
                        else:
                            self.MAa -= self.queuea.dequeue()[0]
                            self.queuea.enqueue([self.sum1min/self.i,currentTime])
                            self.MAa += self.sum1min/self.i

                        if self.queueb.size() < self.b:
                            self.queueb.enqueue([self.sum1min/self.i,currentTime])
                            self.MAb += self.sum1min/self.i
                        else:
                            
                            self.MAb -= self.queueb.dequeue()[0]
                            self.queueb.enqueue([self.sum1min/self.i,currentTime])
                            self.MAb += self.sum1min/self.i
                        
                        if self.queuea.size() == self.a:
                            if(self.MAb/self.b > self.MAa/self.a):
                                if(not self.isBought):
                                    self.buy(currentPrice,currentTime)
                                    self.isBought = True
                            elif(self.MAb/self.b < self.MAa/self.a):
                                if(self.isBought):
                                    self.sell(currentPrice,currentTime)
                                    self.isBought = False
                            else : pass
                        print("{} : current price {}$, current crypto : {},  current amount : {}$, MA21 : {}, MA9 : {}"
                        .format(currentTime,currentPrice,self.currentCrypto,self.currentAmount,self.MAa/self.a,self.MAb/self.b))

                        self.sum1min = 0
                        self.i = 0
                    else:
                        self.i += 1
                        self.sum1min += currentPrice
                    self.previousTime = currentTime
                else: 
                    self.previousTime = currentTime
            except:
                print("error")

        
        def buy(self,price,time):
            self.currentCrypto = self.currentAmount / price
            self.currentAmount = 0.0
            print("\n#################################################################################################################\n")
            print("BUY")

            
        def sell(self,price,time):
            self.currentAmount = price * self.currentCrypto
            self.currentCrypto = 0.0
            print("\nSELL")
            print("{} : current price {}$, current crypto : {},  current amount : {}$, profit : {}$ ({})"
            .format(time,price,self.currentCrypto,self.currentAmount,self.currentAmount-self.initialAmount,(self.currentAmount - self.initialAmount)* 100/self.initialAmount))
            print("\n#################################################################################################################\n")


        def on_close(self):
            print("-- Goodbye! --")


    wsClient = MyWebsocketClient()
    wsClient.start()
    print(wsClient.url, wsClient.products)
    try:
        
        while True:
            # print("\nMessageCount =", "%i \n" % wsClient.message_count)
            
            time.sleep(1)
    except KeyboardInterrupt:
        wsClient.close()

    if wsClient.error:
        sys.exit(1)
    else:
        sys.exit(0)
