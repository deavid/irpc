#!/usr/local/bin/python3
import socket
import threading
import time
import json

import irpcchatter

class ExecuteRemoteCommand:
    def __init__(self,chatter, command, local_args = [], local_kwargs = {}, args = [], kwargs = {}):
        self.chatter = chatter
        self.prepared = False
        self.started = False
        self.executed = False
        self.returnValue = None
        self.queuedAnswer = None
        
        self.command = command
        self.local_args = local_args
        self.local_kwargs = local_kwargs
        self.args = args
        self.kwargs = kwargs
        self.trama = ""
        
    def getUnqueuedRandID(self):
        def key():
            import random
            i = random.randint(0,255)
            return "x%X" % i
        k = key()
        while k in self.chatter.language.cmds.answer.answerqueue: k = key()
        return k

    def prepare(self, id = "auto"):
        # Complete all stuff here and set the bytes to send
        if self.prepared: return
        
        if id == "auto":
            id = self.getUnqueuedRandID()
        if id is None:
            idobj = ""
        else:
            idobj = "@" + id
        self.queuedAnswer = self.chatter.language.cmds.answer.queueAnswerFor(id)
            
        trama_args = [
            "!%s%s" % (self.command,idobj),
            ]
        for arg in self.local_args:
            tr1 = ":" + arg 
            trama_args.append(tr1)

        for k,arg in self.local_kwargs.items():
            tr1 = k + ":" + arg
            trama_args.append(tr1)
            
        for arg in self.args:
            val = json.dumps(arg) 
            tr1 = "=" + val 
            trama_args.append(tr1)

        for k,arg in self.kwargs.items():
            val = json.dumps(arg) 
            tr1 = k + "=" + val
            trama_args.append(tr1)
            
        self.trama = "\t".join(trama_args) + "\n"

        
        self.prepareds = True
        
    def start(self):
        if not self.prepared: self.prepare()
        self.chatter.push(self.trama.encode("utf8"))
        self.started = True

    def getReturnValue(self, timeout = None):    
        if not self.started: self.start()
        if self.executed:
            return self.returnValue
        
        if not self.queuedAnswer.wait(timeout):
            print("timeout!!!")
            return None
        
        self.returnValue = self.processAnswer(self.queuedAnswer)
        self.executed = True
        
        return self.returnValue
    
    def processAnswer(self,answer):
        if answer.type == "":
            return answer.value
        
        if answer.type == "Exception":
            raise(NameError,answer.value)
            


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
        self.timeout = 30

    def call(self, fn, *args,getReturnValue = True, **kwargs): 
        #ret = self.execute("call",local_kwargs={"fn":fn},args = args,kwargs = kwargs)
        #print(ret.type)
        #print(ret.value)
        exe = ExecuteRemoteCommand(self.chatter, "call", local_kwargs={"fn":fn},args = args,kwargs = kwargs)
        exe.start()
        if getReturnValue:
            ret = exe.getReturnValue()
            return ret
        else:
            return exe


        
        


    
def testSerialized(remote,iterations):
    for n in range(iterations):
        remote.call("addItem", item=n)
    
def testConcurrent(remote,iterations):
    lstExe = []
    for n in range(iterations):
        lstExe.append(remote.call("addItem", item=n, getReturnValue = False))
        
    for exe in lstExe: exe.getReturnValue()
    
    

def main():
    remote = RemoteIRPC("localhost",10123)
    
    remote.call("clearItems")
    #testSerialized(remote,iterations = 10000)
    testConcurrent(remote,iterations = 10000)
    print(sum(remote.call("getItems")))
    
    print("done")
    

if __name__ == "__main__":
    main()
