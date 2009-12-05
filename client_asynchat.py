#!/usr/local/bin/python3


import asynchat, asyncore
import socket
import traceback
import json
import re


class chatter(asynchat.async_chat):
    def __init__(self,sock, addr):
        asynchat.async_chat.__init__(self, sock = sock)
        self.sock = sock
        self.ibuffer = []
        self.obuffer = b""
        self.set_terminator(b"\n")
        self.addr = addr

    def collect_incoming_data(self,data):
        try:
            #print(repr(data))
            self.ibuffer.append(data)
        except:
            print(traceback.format_exc())

    def found_terminator(self):
        try:
            input_data = b"".join(self.ibuffer)        
            self.ibuffer = []
            self.processprogram(input_data.decode("utf8"))
        except:
            print(traceback.format_exc())

    def processprogram(self, cmd):
        print(cmd)


class RemoteFunction:
    def __init__(self,remote, name):
        self.remote = remote
        self.name = name

    def call(self,*args,**kwargs): 
        #print(self.remote.addr, self.name, repr(args),repr(kwargs))
        trama_args = [
            "!call",
            "fn:%s" % self.name,
            ]
        for arg in args:
            val = json.dumps(arg) 
            tr1 = "=" + val 
            trama_args.append(tr1)

        for k,arg in kwargs.items():
            val = json.dumps(arg) 
            tr1 = k + "=" + val
            trama_args.append(tr1)
            
        trama = "\t".join(trama_args) + "\n"
        #print(">>>",trama)
        self.remote.socket.sendall(trama.encode("utf8"))
        tre = self.remote.socket.recv(4096)
        trama_recibida = tre
        while (len(tre) >4000):
            tre = self.remote.socket.recv(4096)
            trama_recibida += tre
            
            
        
        valortxt = trama_recibida[2:-1].decode("utf8")
        retval = None
        try:
            retval = json.loads(valortxt) 
        except:
            print("Error al procesar el valor de retorno!")
            print(traceback.format_exc())
        return retval
        
        

    

class Remote:
    def __init__(self,host, port):
        self.addr = host
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host,port))

        #self.chat = chatter(sock = self.socket, addr = host)
        
        self.remote_functions = [
                'getFunctionList',
            ]
        
        self.updateFunctions()        
        self.remote_functions = self.getFunctionList()
        self.updateFunctions()
        
    def updateFunctions(self):
        for rfunction in self.remote_functions:
            if not hasattr(self,rfunction):
                rFun = RemoteFunction(remote = self, name = rfunction)
                setattr(self,rfunction,rFun.call)

def check_test1():
    lista = [1,2,3]
    for i in range(10000):
        lista = lista[:3]
        suma = sum(lista)
        lista.append(suma)

        lista = list(reversed(lista))
        
        maximo = max(lista)
        lista.append(maximo)

    
    print(lista)
    

def test1():
    lista = [1,2,3]

    for i in range(1200):
        lista = lista[:3]
        suma = remote.mysum(lista)
        lista.append(suma)

        lista = remote.reverselist(lista)
        
        maximo = remote.mymax(lista)
        lista.append(maximo)
    
    print(lista)


def test2():
    lista = list(range(250))
    remote.reverselist(lista)

    print(lista)

def main():
    global remote
    remote = Remote(host='127.0.0.1', port=10123)
    test1()
    #import cProfile
    #cProfile.run('test1()')
    
    
    



if __name__ == '__main__':
    main()
