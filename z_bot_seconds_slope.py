import cbpro
import time
import sys
from datetime import datetime
import math

class Queue:
    def __init__(self):
        self.queue = []
    
    def enqueue(self,val):
        self.queue.append(val)

    def dequeue(self):
        return self.queue.pop(0)

    def size(self):
        return len(self.queue)
    
    def slope(self):
        sum1 = 0
        sum2 = 0
        n=2
        for i in range(self.size()-n,self.size()-2*n ,-1):
            sum1 += self.queue[i-1]
        for i in range(self.size(),self.size()-n):
            sum2 += self.queue[i-1]
        print(sum2/n,sum1/n)
        return math.degrees(math.atan((sum2/n)-(sum1/n)))
        # return math.degrees(math.atan(self.queue[self.size()-1]-self.queue[self.size()-2]))


key = "2c6d3a1b53d5a2d31676254b3373db8d"
b64secret = "UpxX5+tMEyC8FruQTeW7tEE8s063CWLJea7PrcAofln+sy5xRV/FpAOTp2G7f1+BZwHhRfw5XsL97/JvHpSMjQ=="
passphrase = "auh4oolfqs"

public_client = cbpro.PublicClient()
auth_client = cbpro.AuthenticatedClient(key, b64secret, passphrase)

class bot:
    def __init__(self):
        self.url = "wss://ws-feed.pro.coinbase.com/"

        self.initialAmount = 1000.0
        self.currentAmount = 1000.0
        self.previousAmount = 1000.0
        self.currentCrypto = 0.0
        
        self.isBought = False

        self.a = 21 * 30 
        self.b =  9 * 30
        self.c =  5 * 30
        self.queuea = Queue()
        self.queueb = Queue()
        self.queuec = Queue()

        self.queueMAa = Queue()
        self.queueMAb = Queue()
        self.queueMAc = Queue()
        
        self.MAa = 0.0
        self.MAb = 0.0
        self.MAc = 0.0


        self.previousTime = None
        
        self.sum1min = 0.0

        self.i = 0

    def on_message(self, msg):
        global initialAmount

        currentTime = datetime.strptime(msg['time'][:19], '%Y-%m-%dT%H:%M:%S')
        currentPrice = float(msg['price'])
        # currentTime = msg['time'][11:19]
        
        if(self.previousTime != None and currentTime != self.previousTime):

            # if(self.i!=0):
            if(currentTime.minute %2 == 0 and currentTime.minute != self.previousTime.minute):
            # if(True):
                try:
                    print("{} : {} : current price {}$, current crypto : {},  current amount : {}$, MA21 : {}, MA9 : {}, MA5 : {}, slope21 : {}, slope9 : {}, slope5 : {}"
                    .format(coin,currentTime,currentPrice,round(self.currentCrypto,2),round(self.currentAmount,2),
                    round(self.MAa/self.a,2),round(self.MAb/self.b,2),round(self.MAc/self.c,2),
                    round(self.queueMAa.slope(),2),round(self.queueMAb.slope(),2),round(self.queueMAc.slope(),2)))
                    # print(self.queueMAa.queue)
                    # print(self.queuec.queue)
                except:
                    print("{} : {} : current price {}$, current crypto : {},  current amount : {}$, MA21 : {}, MA9 : {}, MA5 : {}"
                    .format(coin,currentTime,currentPrice,self.currentCrypto,round(self.currentAmount,2),round(self.MAa/self.a,2),round(self.MAb/self.b,2),round(self.MAc/self.c,2)))
            if self.queuea.size() < self.a:
                self.queuea.enqueue([currentPrice,currentTime])
                self.MAa += currentPrice
            else:
                self.MAa -= self.queuea.dequeue()[0]
                self.queuea.enqueue([currentPrice,currentTime])
                self.MAa += currentPrice

            if self.queueb.size() < self.b:
                self.queueb.enqueue([currentPrice,currentTime])
                self.MAb += currentPrice
            else:
                
                self.MAb -= self.queueb.dequeue()[0]
                self.queueb.enqueue([currentPrice,currentTime])
                self.MAb += currentPrice

            if self.queuec.size() < self.c:
                self.queuec.enqueue([currentPrice,currentTime])
                self.MAc += currentPrice
            else:
                self.MAc -= self.queuec.dequeue()[0]
                self.queuec.enqueue([currentPrice,currentTime])
                self.MAc += currentPrice
            
            if self.queuea.size() == self.a:
                if self.queueMAa.size() < 10:
                    self.queueMAa.enqueue(self.MAa/self.a)
                    self.queueMAb.enqueue(self.MAb/self.b)
                    self.queueMAc.enqueue(self.MAc/self.c)
                else:
                    self.queueMAa.dequeue()
                    self.queueMAa.enqueue(self.MAa/self.a)
                    self.queueMAb.dequeue()
                    self.queueMAb.enqueue(self.MAb/self.b)
                    self.queueMAc.dequeue()
                    self.queueMAc.enqueue(self.MAc/self.c)
                    if(self.MAc/self.c > self.MAa/self.a):
                        if(self.MAb/self.b > self.MAc/self.c and (self.MAc/self.c > self.MAa/self.a and self.MAb/self.b > self.MAa/self.a)):
                            if(self.isBought):
                                self.sell(currentPrice,currentTime)
                                self.isBought = False
                                print("@@@@@@ 1")
                        elif(self.MAb/self.b < self.MAc/self.c and (self.MAc/self.c > self.MAa/self.a and self.MAb/self.b > self.MAa/self.a) and self.queueMAb.slope() > 30.0 and self.queueMAc.slope() > 30.0): #and (self.MAc/self.c - self.MAb/self.b)>currentPrice*0.5/100
                            if(not self.isBought):
                                self.buy(currentPrice,currentTime)
                                self.isBought = True
                                print("@@@@@@ 2")
                        else:
                            if(self.queueMAa.slope() > 0.0 ):
                                if(not self.isBought):
                                    self.buy(currentPrice,currentTime)
                                    self.isBought = True
                                    print("@@@@@@ 3")
                            elif(self.queueMAb.slope() > 30.0 and self.queueMAc.slope() > 30.0 ):
                                if(not self.isBought):
                                    self.buy(currentPrice,currentTime)
                                    self.isBought = True
                                    print("@@@@@@ 4")
                    elif(self.MAc/self.c < self.MAa/self.a):
                        if(self.isBought):
                            self.sell(currentPrice,currentTime)
                            self.isBought = False
                            print("@@@@@@ 5")
                    else : pass
                
                

                # print("{} : {} : current price {}$, current crypto : {},  current amount : {}$, MA21 : {}, MA9 : {}, MA5 : {}"
                # .format(coin,currentTime,currentPrice,self.currentCrypto,self.currentAmount,self.MAa/self.a,self.MAb/self.b,self.MAc/self.c))

                # self.sum1min = 0
                # self.i = 0
                
            # else:
            #     self.i += 1
            #     self.sum1min += currentPrice
                
            self.previousTime = currentTime
        else: 
            self.previousTime = currentTime
        #print(json.dumps(msg, indent=4, sort_keys=True))
    
        # self.message_count += 1
        # except:
        #     print("error")

    def buy(self,price,time):
        
        self.previousAmount = self.currentAmount
        self.currentCrypto = self.currentAmount / price
        
        # auth_client.buy(funds=str(self.currentAmount), 
        #        order_type='market',
        #        product_id='{}-USD'.format(coin))

        self.currentAmount = 0.0
        print("\n#################################################################################################################\n")
        print("BUY")
        print("{} : {} : current price {}$, current crypto : {},  current amount : {}$, MA21 : {}, MA9 : {}, MA5 : {}, slope21 : {}, slope9 : {}, slope5 : {}"
                    .format(coin,time,price,round(self.currentCrypto,2),round(self.currentAmount,2),
                    round(self.MAa/self.a,2),round(self.MAb/self.b,2),round(self.MAc/self.c,2),
                    round(self.queueMAa.slope(),2),round(self.queueMAb.slope(),2),round(self.queueMAc.slope(),2)))

    def sell(self,price,time):
        self.currentAmount = price * self.currentCrypto
        self.currentCrypto = 0.0
        print("\nSELL")
        print("{} : {} : current price {}$, current crypto : {},  current amount : {}$, MA21 : {}, MA9 : {}, MA5 : {}, slope21 : {}, slope9 : {}, slope5 : {}"
                    .format(coin,time,price,round(self.currentCrypto,2),round(self.currentAmount,2),
                    round(self.MAa/self.a,2),round(self.MAb/self.b,2),round(self.MAc/self.c,2),
                    round(self.queueMAa.slope(),2),round(self.queueMAb.slope(),2),round(self.queueMAc.slope(),2)))
        
        print("trade profit : {}$ ({}%), total profit : {}$ ({}%)"
        .format(round(self.currentAmount-self.previousAmount,2),round((self.currentAmount - self.previousAmount)* 100/self.previousAmount,2)
        ,round(self.currentAmount-self.initialAmount,2),round((self.currentAmount - self.initialAmount)* 100/self.initialAmount,2)))
        print("\n#################################################################################################################\n")
        # auth_client.sell(size=str(self.currentCrypto), 
        #        order_type='market',
        #        product_id='{}-USD'.format(coin))


coin = sys.argv[1]
if(coin != None):
    bot = bot()
    while 1:
        
        bot.on_message(public_client.get_product_ticker(product_id='{}-USD'.format(coin)))
        time.sleep(1)
        