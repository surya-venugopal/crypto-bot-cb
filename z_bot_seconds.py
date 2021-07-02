import sys
import cbpro
import sys
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



public_client = cbpro.PublicClient()


class bot:
    def __init__(self):
        self.url = "wss://ws-feed.pro.coinbase.com/"
        self.products = ["ADA-USD"]

        self.initialAmount = 1000.0
        self.currentAmount = 1000.0
        self.previousAmount = 1000.0
        self.currentCrypto = 0.0
        
        self.isBought = False

        self.a = 1260 
        self.b = 540
        self.c = 300

        self.queuea = Queue()
        self.queueb = Queue()
        self.queuec = Queue()
        
        self.MAa = 0.0
        self.MAb = 0.0
        self.MAc = 0.0


        self.previousTime = ""
        
        self.sum1min = 0.0

        self.i = 0

    def on_message(self, msg):
        global initialAmount
        
        # try:
        # print(msg['product_id'])
        currentPrice = float(msg['price'])
        currentTime = msg['time'][11:19]
        
        if(self.previousTime != "" and currentTime != self.previousTime):

            if(currentTime[3:5] != self.previousTime[3:5]):
                print("{} : {} : current price {}$, current crypto : {},  current amount : {}$"
                .format(coin,currentTime,currentPrice,self.currentCrypto,self.currentAmount))
                
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
                    if(self.MAc/self.c > self.MAa/self.a):
                        if(self.MAb/self.b > self.MAc/self.c and (self.MAc/self.c > self.MAa/self.a and self.MAb/self.b > self.MAa/self.a)):
                            if(self.isBought):
                                self.sell(currentPrice,currentTime)
                                self.isBought = False
                        elif(self.MAb/self.b < self.MAc/self.c and (self.MAc/self.c > self.MAa/self.a and self.MAb/self.b > self.MAa/self.a) ): #and (self.MAc/self.c - self.MAb/self.b)>currentPrice*0.5/100
                            if(not self.isBought):
                                self.buy(currentPrice,currentTime)
                                self.isBought = True
                        elif(not self.isBought):
                            self.buy(currentPrice,currentTime)
                            self.isBought = True
                    elif(self.MAc/self.c < self.MAa/self.a):
                        if(self.isBought):
                            self.sell(currentPrice,currentTime)
                            self.isBought = False
                    else : pass
            

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
        self.currentAmount = 0.0
        print("\n#################################################################################################################\n")
        print("BUY")

        
    def sell(self,price,time):
        self.currentAmount = price * self.currentCrypto
        self.currentCrypto = 0.0
        print("\nSELL")
        print("{} : current price {}$, current crypto : {},  current amount : {}$, trade profit : {}$ ({}%), total profit : {}$ ({}%)"
        .format(time,price,self.currentCrypto,self.currentAmount
        ,self.currentAmount-self.previousAmount,(self.currentAmount - self.previousAmount)* 100/self.previousAmount
        ,self.currentAmount-self.initialAmount,(self.currentAmount - self.initialAmount)* 100/self.initialAmount))
        print("\n#################################################################################################################\n")

coin = sys.argv[1]
if(coin != None):
    bot = bot()
    while 1:
        try:
            bot.on_message(public_client.get_product_ticker(product_id='{}-USD'.format(coin)))
        except:
            pass