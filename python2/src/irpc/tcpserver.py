#!/usr/bin/python
# -*- coding: utf-8 -*-
import shelve
import socket
import threading
import SocketServer as socketserver 
import signal
import time
import random
import irpcchatter

exit = False
default_root_username = 'root'
default_root_password = 'irpc'

def sigINT(signum, frame):
    global exit
    print "Recieved signal %d! " % (signum)
    exit = True

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
	self.server.active_requests.append(self)
        self.local_address = self.request.getsockname()
        self.remote_address = self.request.getpeername()
        self.request.setblocking(0)
        # print "Starting recieving thread for", self.remote_address  # DEBUG
        self.chatter = irpcchatter.BaseChatter(sock = self.request, addr = self.remote_address)
        self.chatter.setup(self.server.lang) # Configura y da de alta todo el lenguaje 
        self.chatter.loop()
	self.server.active_requests.remove(self)
        # print "Ending thread for", self.remote_address  # DEBUG
    

        

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    active_requests = []
    def exit(self):
	try:
	    if irpcchatter.BaseChatter.security_shelve:
		irpcchatter.BaseChatter.security_shelve.close()
	except:
	    pass
	for req in self.active_requests:
	    req.chatter.error = True
	    req.request.setblocking(0)
	    req.request.close()
	time.sleep(0.01)    
	if hasattr(self,"shutdown"):
	    self.shutdown()
	
def securityShelveInstallUsers(security_shelve):
    global default_root_username, default_root_password
    
    rootUser = {
	'username' : default_root_username,
	'auth-methods' : ['trust','password'],
	'password' : irpcchatter.hashPassword(default_root_password),
	'publickeys' : [],
	'security-perms' : irpcchatter.securityPerms,
    }
    
    users = {
	default_root_username : rootUser
    }
    security_shelve['users'] = users
    security_shelve.sync()
    
def securityShelveInstall(security_shelve):
    if 'users' not in security_shelve: securityShelveInstallUsers(security_shelve)
    
    

def startServer(HOST="", PORT=10000, security_shelve_filename='security.shelve'):
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    server.lang = irpcchatter.BaseLanguageSpec()
    security_shelve = shelve.open(security_shelve_filename, writeback=True)
    
    securityShelveInstall(security_shelve)
    
    irpcchatter.BaseChatter.security_shelve = security_shelve
    
    
    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    if not hasattr(server_thread,"name"):
        server_thread.name = "Thread-%d" % random.randint(1,250)
    # Exit the server thread when the main thread terminates
    server_thread.setDaemon(True)
    server_thread.start()
    
    return server, server_thread
    
    

    

def import_examplefuncitons():
    import examplefunctions


def main():
    global exit
    #import_examplefuncitons()
    #irpcchatter.BaseChatter.stdout_debug = True
    exit = False
    signal.signal(signal.SIGINT, sigINT)
    server, thread = startServer(PORT=10123)
    print "Server loop running in thread:", thread.name
    while not exit:
        time.sleep(0.1)
        
    server.exit()
    del server
    del thread
    

if __name__ == "__main__":
    # Import Psyco if available
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    main()
