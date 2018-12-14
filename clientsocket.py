#Client/Server using mult threading

import socket
import sys
import time
import threading
from colorama import Style,Fore

class ClientSocket(object):
    def __init__(self,addr=socket.gethostbyname(socket.gethostname()),port = 5253,debug = True):
        self.addr = addr
        self.port = port
        self.debug = debug
        self.connection_is_alive = False #For checking wether the server is still alive or not

        #COLOR FOR PRETTY DISPLAY
        self.green = Fore.GREEN
        self.reset = Style.RESET_ALL
        self.bright = Style.BRIGHT
        self.blue = Fore.BLUE
        self.red = Fore.RED
        self.yellow = Fore.YELLOW

    def start_connection(self) :
        self.clientfd = socket.socket()
        if self.debug == True:
              print(self.green + self.bright + "Socket created succefullt" + self.reset )

        print(self.blue + self.bright + "Establishing connection...." + self.reset)

        try:
            self.clientfd.connect((self.addr,self.port))
        except ConnectionRefusedError:
            #If server is not fount it will try to reconnect after 5 sec.
            print(self.red + self.bright + "Cannot find server.\n trying to reconnect.." + self.reset)
            time.sleep(5)
            self.start_connection()

        self.connection_is_alive = True
        self.startChatting()

    def _sendmsg(self):
        try:
            while self.connection_is_alive:
              print(self.blue + self.bright + "\n[ME:]   ",end=''+ self.reset)
              msg = input(self.yellow + self.bright)
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
                         print(self.red + self.bright +"Server is down " + self.reset)
                         self.connection_is_alive = False
                         break
                     print(self.blue + self.bright+"\n[Client:]" +"  {0}".format(self.green + msg + self.reset))

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
        print(self.blue + self.bright + "\nPress enter to Quit" + self.reset)

    def __del__(self):
        #Closes the connection
        self.clientfd.close()
        if self.debug == True :
            print(self.green + self .bright + "Connection closed succefully" + self.reset)
        del self.clientfd

        del self.yellow,self.green,self.blue,self.red
        del self.bright,self.reset

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
