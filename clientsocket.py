#Client/Server using mult threading
import socket
import sys
import time
import threading

class ClientSocket(object):
    def __init__(self,addr=socket.gethostbyname(socket.gethostname()),port = 5253,debug = True):
        self.addr = addr
        self.port = port
        self.debug = debug
        self.connection_is_alive = False #For checking wether the server is still alive or not
    def start_connection(self) :
        self.clientfd = socket.socket()
        if self.debug == True:
              print("Socket created succefullt")

        print("Establishing connection")
        try:
            self.clientfd.connect((self.addr,self.port))
        except ConnectionRefusedError:
            #If server is not fount it will try to reconnect after 5 sec.
            print("Cannot find server.\n trying to reconnect..")
            time.sleep(5)
            self.start_connection()
        self.connection_is_alive = True
        self.startChatting()

    def _sendmsg(self):
        try:
            while self.connection_is_alive:
              print("\n[ME:]   ",end='')
              msg = input()
            #Always checking wether the server is still alive or not
              if self.connection_is_alive:
                    if msg == 'q' or msg == 'Q':
                        self.connection_is_alive = False
                        self.clientfd.send(bytes(('close'),'utf-8'))
                        break
                    self.clientfd.send(bytes(msg,'utf-8'))
              else:
                    return
        except OSError:
            print(OSError)

    def _recvmsg(self):
        try :
            while self.connection_is_alive:
                 msg = self.clientfd.recv(4096)
                 msg = msg.decode(encoding = 'utf-8')
                 if self.connection_is_alive:
                     if msg == 'close':
                         print("Server is down ")
                         self.connection_is_alive = False
                         break
                     print("\n[Client:]    {0}".format(msg))
        except OSError:
            return
    def startChatting(self):
        #Again starting two threads one will recivie the message 
        #The other will send the message
        self.t1 = threading.Thread(target = self._recvmsg,args=())
        self.t2 = threading.Thread(target = self._sendmsg,args=())
        self.t1.start()
        self.t2.start()
        self.t1.join()
        self.t2.join()
        #It will wait for both the thead to complelte i.e. it will exit when the user want to exit

    def closeconnection(self):
        #First send server a message that it is closing
        if self.connection_is_alive:
            self.clientfd.send(bytes(('close'),'utf-8'))
            #Stops the infinite loop of all the threads
            self.connection_is_alive = False
        print("\nPress enter to Quit")

    def __del__(self):
        #Closes the connection
        self.clientfd.close()
        if self.debug == True :
            print("Connection closed succefully")
        
        del self.debug


def main():
    c = ClientSocket()
    try:
       c.start_connection()
       del c
    #If the user presses C-c to c:w
    # loes  the chat
    except KeyboardInterrupt:
         c.closeconnection()


if __name__ == '__main__' :
    main()
