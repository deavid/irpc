# Echo client program
import socket

HOST = '192.168.1.200'    # The remote host
PORT = 50007              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(0.01)
s.connect((HOST, PORT))
f1 = open("git/minirok/README")
t = f1.read()
n = s.send(t)
print n, "of" ,len(t) , "bytes sent"
f1.close()
data = []
try:
  while True: data.append(s.recv(1024))
except socket.timeout:
  print "timeout!"


s.close()
print 'Received', repr(data)
