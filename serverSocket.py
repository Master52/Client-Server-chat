#Client/Server chat using threading

import socket
import sys
import threading
from colorama import Style,Fore,Back


class Socket(object):
    def __init__(self,addr = socket.gethostbyname(socket.gethostname()),port = 5253,debug = True):
        self.addr = addr #Server Host IP
        self.port = port #Port
        self.debug = debug # For debugging purose
        self.connectionCount = 0 # Number of client getting connected
        self.connectionDetail = {} # Hold detail of each client such as address , file descriptor(fd)

        #COLOR FOR PRETTY DISPLAY
        self.green = Fore.GREEN
        self.reset = Style.RESET_ALL
        self.bright = Style.BRIGHT
        self.blue = Fore.BLUE
        self.red = Fore.RED
        self.yellow = Fore.YELLOW
    
    

    def startListening(self):
        #creating socket
        self._serverSocket = socket.socket()
        try :
            if self.debug == True :
                print(self.green + self.bright +"Socket Created"+ self.reset)
            self._serverSocket.bind((self.addr,self.port))

            if self.debug == True:
               print("Socket Binded succefully")

            while True:
                print(self.yellow + self.bright +"{0} Listening for connection on port {1} ...".format(self.addr,self.port)+self.reset)
                self._serverSocket.listen(5)
                clientfd,addr = self._serverSocket.accept()
                print(self.blue + self.bright +"Connected to host {0}".format(addr[0]) + self.reset)
               # 'is_alive' parameter is used to check wether the client is alive or not 
                self.connectionDetail[addr] = {'sockd':clientfd ,'is_alive':True}
                self.connectionCount += 1
                # A Thread which will handle every new client get connected 
                threading.Thread(target = self.newConnectionHandler,args=(addr,)).start()

        except OSError:
            print(self.red + self.bright +"Another server is running on the same port number" + self.reset)
    
    def newConnectionHandler(self,addr):
        self.startChating(addr)

    def _sendmsg(self,addr):
        try:
            while self.connectionDetail[addr]['is_alive']:
                 print(self.blue + self.bright +"\n[Server:] ",end=''+ self.reset)
                 msg = input(self.yellow + self.bright)
                 #Always check wether the client is online or not before send the message
                 #If it will break the while loop
                 if self.connectionDetail[addr]['is_alive']:

                     if msg == 'q' or msg == 'Q':
                        self.connectionDetail[addr]['sockd'].send(bytes('close','utf-8'))
                        self.connectionDetail[addr]['is_alive'] = False
                        break
                    
                     self.connectionDetail[addr]['sockd'].send(bytes(msg,'utf-8'))

                 else:
                    break
            self.disconnect(addr)

        except OSError:
            print("Bye")

        except KeyError:
            pass

#whenver a client disconnects from the network it will send a close message to the server
#Server on reciving the close message will remove the client from the connection list
    def _recvmsg(self,addr):
        while self.connectionDetail[addr]['is_alive']:
             msg = self.connectionDetail[addr]['sockd'].recv(4096)
             msg = msg.decode(encoding = 'utf-8')
             if msg == 'close':
                 self.connectionDetail[addr]['sockd'].send(bytes('close','utf-8'))
                 break

             else:
                print(self.blue + self.bright +"\n[{0}] ".format(addr[0]) + self.green + "{0}".format(msg) + self.reset)
        #Comming out from this loop simply mean the client has been disconnected so it call disconnects method to remove it

        self.disconnect(addr)

    def startChating(self,addr):
        #Creating two thread which run parallely on will send the message 
        #The other will recivies the messsage
        t1 = threading.Thread(target=self._sendmsg,args=(addr,))
        t2 = threading.Thread(target=self._recvmsg,args=(addr,))
        
        t1.start()
        t2.start()


    def disconnect(self,address = None):
        #If no address is pass that means all the connection should be disconnected
        if address == None:
            for addr,value in self.connectionDetail.items():

                if value['is_alive'] == True: #Checking wether the client is still online or not
                   value['sockd'].send(bytes(('close'),'utf-8'))
                   value['sockd'].close()
                   value['is_alive'] = False
                   self.connectionCount -= 1
                   print(self.red + self.bright +"{0} disconnected".format(addr) + self.reset)
                   print(self.red + self.bright +"Press Enter to quit" + self.reset)
        else:
            #checking wether the address is present in client list or not
            if address in self.connectionDetail:
                if self.connectionDetail[address]['is_alive']:
                    self.connectionDetail[address]['sockd'].send(bytes(('close'),'utf-8'))
                    self.connectionDetail[address]['sockd'].close()
                    self.connectionDetail[address]['is_alive'] = False
                    del(self.connectionDetail[address])
                    self.connectionCount -= 1
                    print(self.red + self.bright + "{0} disconnected".format(address) + self.reset)


    def __del__(self) :
        #closing the server socket
        self._serverSocket.close()

        if self.debug == True:
            print(self.green + self.bright + "Socket closed succefully" + self.reset)

        del self.connectionCount,self.addr
        del self.connectionDetail

        del self.green,self.red,self.yellow,self.blue
        del self.bright,self.reset



def main():
    s = Socket()
    try:
        s.startListening()
    except KeyboardInterrupt:
        s.disconnect()


if __name__ == '__main__' :
    main()
