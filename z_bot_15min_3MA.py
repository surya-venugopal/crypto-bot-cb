import cbpro
import time
import sys
from datetime import datetime

class Queue:
    def __init__(self):
        self.queue = []
    
    def enqueue(self,val):
        self.queue.append(val)

    def dequeue(self):
        return self.queue.pop(0)
        

    def size(self):
        return len(self.queue)



public_client = cbpro.PublicClient()


class bot:
    def __init__(self):
        self.url = "wss://ws-feed.pro.coinbase.com/"
        self.products = ["ADA-USD"]

        self.initialAmount = 1000.0
        self.currentAmount = self.initialAmount
        self.currentCrypto = 0.0
        
        self.isBought = False

        self.a = 21 
        self.b = 9
        self.c = 5

        self.queuea = Queue()
        self.queueb = Queue()
        self.queuec = Queue()
        
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

            if(currentTime.minute in (15,30,45,0) and currentTime.minute != self.previousTime.minute and self.i!=0):
                
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

                if self.queuec.size() < self.c:
                    self.queuec.enqueue([self.sum1min/self.i,currentTime])
                    self.MAc += self.sum1min/self.i
                else:
                    
                    self.MAc -= self.queuec.dequeue()[0]
                    self.queuec.enqueue([self.sum1min/self.i,currentTime])
                    self.MAc += self.sum1min/self.i
                
                if self.queuea.size() == self.a:
                    if(self.MAc/self.c > self.MAa/self.a):
                        if(not self.isBought):
                            self.buy(currentPrice,currentTime)
                            self.isBought = True
                    elif(self.MAc/self.c < self.MAa/self.a):
                        if(self.isBought):
                            self.sell(currentPrice,currentTime)
                            self.isBought = False
                    elif(self.MAb/self.b > self.MAc/self.c and (self.MAb/self.b > self.MAa/self.a and self.MAc/self.c > self.MAa/self.a) ):
                        if(self.isBought):
                            self.sell(currentPrice,currentTime)
                            self.isBought = False
                    elif(self.MAb/self.b < self.MAc/self.c and (self.MAb/self.b > self.MAa/self.a and self.MAc/self.c > self.MAa/self.a) and (self.MAc/self.c - self.MAb/self.b)>5):
                        if(not self.isBought):
                            self.buy(currentPrice,currentTime)
                            self.isBought = True
                    else : pass
                print("{} : {} : current price {}$, current crypto : {},  current amount : {}$, MA21 : {}, MA9 : {}, MA5 : {}"
                .format(coin,currentTime,currentPrice,self.currentCrypto,self.currentAmount,self.MAa/self.a,self.MAb/self.b,self.MAc/self.c))

                self.sum1min = 0
                self.i = 0
                
            else:
                self.i += 1
                self.sum1min += currentPrice
                
            self.previousTime = currentTime
        else: 
            self.previousTime = currentTime
        #print(json.dumps(msg, indent=4, sort_keys=True))
    
        # self.message_count += 1
        # except:
        #     print("error")


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


coin = sys.argv[1]
if(coin != None):
    bot = bot()
    while 1:
        try:
            bot.on_message(public_client.get_product_ticker(product_id='{}-USD'.format(coin)))
        except:
            pass