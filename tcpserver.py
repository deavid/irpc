#!/usr/local/bin/python3
import socket
import threading
import socketserver
import signal
import time

import irpcchatter

exit = False

def sigINT(signum, frame):
    global exit
    print("Recieved signal %d! " % (signum))
    exit = True

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        self.local_address = self.request.getsockname()
        self.remote_address = self.request.getpeername()
        self.request.setblocking(0)
        print("Starting recieving thread for", self.remote_address)
        self.chatter = irpcchatter.BaseChatter(sock = self.request, addr = self.remote_address)
        self.chatter.setup(self.server.lang) # Configura y da de alta todo el lenguaje 
        self.chatter.loop()
        print("Ending thread for", self.remote_address)
    

        

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    pass

def startServer(HOST="", PORT=10000):
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    server.lang = irpcchatter.BaseLanguageSpec()

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.setDaemon(True)
    server_thread.start()
    
    return server, server_thread
    
    

    

def import_examplefuncitons():
    import examplefunctions


def main():
    global exit
    import_examplefuncitons()
    exit = False
    signal.signal(signal.SIGINT, sigINT)
    server, thread = startServer(PORT=10123)
    print("Server loop running in thread:", thread.name)
    while not exit:
        time.sleep(0.1)
        

    server.shutdown()
    

if __name__ == "__main__":
    main()
