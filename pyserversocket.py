import SocketServer

class MyTCPHandler(SocketServer.StreamRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
	self.data = "-"
	while self.data:
	  self.data = self.rfile.readline()
	  print "%s wrote:" % self.client_address[0]
	  print self.data.strip()
	  # Likewise, self.wfile is a file-like object used to write back
	  # to the client
	  self.wfile.write(self.data.upper())

if __name__ == "__main__":
    HOST, PORT = "192.168.1.200", 50007

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
