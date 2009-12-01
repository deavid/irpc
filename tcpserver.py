#!/usr/local/bin/python3
import socket
import threading
import socketserver
import signal
import time
exit = False

def sigINT(signum, frame):
    global exit
    print("Recieved signal %d! " % (signum))
    exit = True

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(1024)
        cur_thread = threading.current_thread()
        response = bytes("%s: %s" % (cur_thread.getName(), data),'ascii')
        self.request.send(response)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    pass

def main():
    global exit
    signal.signal(signal.SIGINT, sigINT)
    
    HOST, PORT = "", 10123

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.setDaemon(True)
    server_thread.start()
    print("Server loop running in thread:", server_thread.name)
    exit = False
    while not exit:
        time.sleep(0.2)
        

    server.shutdown()
    

if __name__ == "__main__":
    main()
