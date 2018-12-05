#Client/Server chat using threading

import socket
import sys
import threading



class Socket(object):
    def __init__(self,addr = socket.gethostbyname(socket.gethostname()),port = 5253,debug = True):
        self.addr = addr #Server Host IP
        self.port = port #Port
        self.debug = debug # For debugging purose
        self.connectionCount = 0 # Number of client getting connected
        self.connectionDetail = {} # Hold detail of each client such as address , file descriptor(fd)
    
    

    def startListening(self):
        #creating socket
        self._serverSocket = socket.socket()
        if self.debug == True :
            print("Socket Created")
        self._serverSocket.bind((self.addr,self.port))
        if self.debug == True:
            print("Socket Binded succefully")
        while True:
            print("{0} Listening for connection on port ...{1}".format(self.addr,self.port))
            self._serverSocket.listen(5)
            clientfd,addr = self._serverSocket.accept()
            print("Connected to host {0}".format(addr))

           # 'is_alive' parameter is used to check wether the client is alive or not 
            self.connectionDetail[addr] = {'sockd':clientfd ,'is_alive':True}
            self.connectionCount += 1
            # A Thread which will handle every new client get connected 
            threading.Thread(target = self.newConnectionHandler,args=(addr,)).start()
            
    
    def newConnectionHandler(self,addr):
        self.startChating(addr)

    def _sendmsg(self,addr):
        try:
            while True:
                 print("\n[Server:]    ",end='')
                 msg = input()
                 #Always check wether the client is online or not before send the message
                 #If it will break the while loop
                 if self.connectionDetail[addr]['is_alive'] == True :
                    self.connectionDetail[addr]['sockd'].send(bytes(msg,'utf-8'))
                 else:
                    break
        
            self.disconnect(addr)

        except OSError:
            print("Bye")

#whenver a client disconnects from the network it will send a close message to the server
#Server on reciving the close message will remove the client from the connection list
    def _recvmsg(self,addr):
        while self.connectionDetail[addr]['is_alive'] == True:
             msg = self.connectionDetail[addr]['sockd'].recv(4096)
             msg = msg.decode(encoding = 'utf-8')
             if msg == 'close':
                 self.connectionDetail[addr]['is_alive'] = False
             else:
                print("\n{0}    {1}".format(addr,msg))
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
                   print("{0} disconnected".format(addr))
        else:
            if address in self.connectionDetail:
                if self.connectionDetail[address]['sockd'] == True:
                    self.connectionDetail[address]['sockd'].send(bytes(('close'),'utf-8'))
                    self.connectionDetail[address]['sockd'].close()
                    del(self.connectionDetail[address])
                    self.connectionCount -= 1
            print("{0} disconnected".format(address))


    def _clenaup(self) :
        self.disconnect()
        #closing the server socket
        self._serverSocket.close()
        del self.connectionCount
        del self.connectionDetail
        del self.addr

    def closeConnection(self) :
        #Whenver this funciton in called it closes all the connection which are present is connection list
        self._clenaup()
        if self.debug == True:
            print("Socket closed succefully")


def main():
    s = Socket()
    try:
        s.startListening()
    except KeyboardInterrupt:
        s.closeConnection()
    del s

if __name__ == '__main__' :
    main()