#!/usr/local/bin/python3
import socket
import threading
import time

import irpcchatter

class RemoteIRPC:
    def __init__(self,host, port):
        self.addr = host
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host,port))
        self.lang = irpcchatter.BaseLanguageSpec()

        self.local_address = self.socket.getsockname()
        self.remote_address = self.socket.getpeername()
        print("Conected to ", self.remote_address)

        self.chatter = irpcchatter.BaseChatter(sock = self.socket, addr = self.addr)
        self.chatter.setup(self.lang) # Configura y da de alta todo el lenguaje 
        self.thread = threading.Thread(target=self.chatter.loop)
        self.thread.setDaemon(True)
        self.thread.start()

        


    

    

def main():
    remote = RemoteIRPC("localhost",10123)

if __name__ == "__main__":
    main()
