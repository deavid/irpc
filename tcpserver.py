#!/usr/local/bin/python3
import socket
import threading
import socketserver
import signal
import time

import serverchatter

exit = False

def sigINT(signum, frame):
    global exit
    print("Recieved signal %d! " % (signum))
    exit = True

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        self.local_address = self.request.getsockname()
        self.remote_address = self.request.getpeername()
        print("Starting recieving thread for", self.remote_address)
        self.chatter = serverchatter.BaseChatter(sock = self.request, addr = self.remote_address)
        self.chatter.setup(self.server.lang) # Configura y da de alta todo el lenguaje 
        self.chatter.loop()
        print("Ending thread for", self.remote_address)
    

        

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    pass

def startServer(HOST="", PORT=10000):
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    server.lang = serverchatter.BaseLanguageSpec()

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.setDaemon(True)
    server_thread.start()
    
    return server, server_thread
    
@serverchatter.published
def ordenarLista(lista):
    """ 
        Devuelve una lista orrdenada a partir de la lista que se le pasa como parametro "lista"
    """
    return list(sorted(lista))
    

listItems = []

@serverchatter.published
def addItem(item):
    global listItems
    listItems.append(item)
    return True

@serverchatter.published
def removeItem(item):
    global listItems
    listItems.remove(item)
    return True
    

@serverchatter.published
def getItems():
    global listItems
    return listItems
    
@serverchatter.published
def clearItems():
    global listItems
    listItems = []
    return True
    
    


def main():
    global exit
    exit = False
    signal.signal(signal.SIGINT, sigINT)
    server, thread = startServer(PORT=10123)
    print("Server loop running in thread:", thread.name)
    while not exit:
        time.sleep(0.1)
        

    server.shutdown()
    

if __name__ == "__main__":
    main()
