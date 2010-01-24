#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import threading
import time
import cjson

import irpcchatter

class ExecuteRemoteCommand:
    def __init__(self,chatter, command, local_args = [], local_kwargs = {}, args = [], kwargs = {}, autoremove_id = True):
        self.chatter = chatter
        self.prepared = False
        self.started = False
        self.executed = False
        self.returnValue = None
        self.queuedAnswer = None
        self.autoremove_id = autoremove_id
        
        self.command = command
        self.local_args = local_args
        self.local_kwargs = local_kwargs
        self.args = args
        self.kwargs = kwargs
        self.trama = ""
        
    def getUnqueuedRandID(self):
        if self.autoremove_id:
            def key():
                import random
                i = random.randint(0,255)
                return "x%X" % i
        else:
            def key():
                import random
                i = random.randint(0,256*256-1)
                return "%s%X" % (self.command[:2],i)
            
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
        self.queuedAnswer = self.chatter.language.cmds.answer.queueAnswerFor(id, self.autoremove_id)
            
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
            val = cjson.encode(arg) 
            tr1 = "=" + val 
            trama_args.append(tr1)

        for k,arg in self.kwargs.items():
            val = cjson.encode(arg) 
            tr1 = k + "=" + val
            trama_args.append(tr1)
            
        self.trama = "\t".join(trama_args) + "\n"

        
        self.prepared = True
        
    def start(self):
        if not self.prepared: self.prepare()
        self.chatter.push(self.trama.encode("utf8"))
        self.started = True

    def getReturnValue(self, timeout = 10):    
        if not self.started: self.start()
        if self.executed:
            return self.returnValue
        
        if not self.queuedAnswer.wait(timeout):
            print "timeout!!!"
            return None
        
        self.returnValue = self.processAnswer(self.queuedAnswer)
        self.executed = True
        
        return self.returnValue
    
    def processAnswer(self,answer):
        if answer.type == "":
            return answer.value
        
        if answer.type == "Exception":
            raise NameError(answer.value)
            


class RemoteIRPC:
    def __init__(self,host, port):
        self.addr = host
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host,port))
        self.socket.setblocking(0)
        
        self.lang = irpcchatter.BaseLanguageSpec()

        self.local_address = self.socket.getsockname()
        self.remote_address = self.socket.getpeername()
        # print "Conected to ", self.remote_address # debug

        self.chatter = irpcchatter.BaseChatter(sock = self.socket, addr = self.addr)
        self.chatter.setup(self.lang) # Configura y da de alta todo el lenguaje 
        self.thread = threading.Thread(target=self.chatter.loop)
        self.thread.setDaemon(True)
        self.thread.start()
        self.timeout = 30
        self.monitored_events = {}
        
    def exit(self):
	self.chatter.exit = True
        self.socket.setblocking(0)
        self.socket.close()
	self.thread.join(timeout=0.01)
	
    def call(self, fn, *args, **kwargs): 
	return self.execmd("call",{'fn':fn}, *args, **kwargs)

    def call_ev(self, fn, *args, **kwargs): 
	return self.execmd("call",{'ev':fn}, *args, **kwargs)
	
    def help(self, fn, *args, **kwargs): 
	return self.execmd("help",{'fn':fn}, *args, **kwargs)

    def help_ev(self, fn, *args, **kwargs): 
	return self.execmd("help",{'ev':fn}, *args, **kwargs)

    def execmd(self, cmd, local_kwargs, *args, **kwargs): 
        #ret = self.execute("call",local_kwargs={"fn":fn},args = args,kwargs = kwargs)
        #print ret.type
        #print ret.value
        getReturnValue = True
        if "getReturnValue" in kwargs:
            getReturnValue = kwargs["getReturnValue"]
            del kwargs["getReturnValue"]
        
        exe = ExecuteRemoteCommand(self.chatter, cmd, local_kwargs=local_kwargs,args = args,kwargs = kwargs)
        exe.start()
        if getReturnValue:
            ret = exe.getReturnValue()
            return ret
        else:
            return exe

    
    def monitor(self, ev, *args, **kwargs): 
        if ev in self.monitored_events:
            raise NameError("Error: tried to monitor event '%s' twice." % ev)
        
        exe = ExecuteRemoteCommand(self.chatter, "monitor", local_kwargs={"ev":ev},args = args,kwargs = kwargs, autoremove_id = False)

        exe.prepare()
        exe.queuedAnswer.event_name = ev
        exe.queuedAnswer.callback = self.monitor_callback
        exe.queuedAnswer.connected_functions = []
        exe.start()
        self.monitored_events[ev] = exe
    
    def monitor_callback(self, answer):
        if answer.type != "Signal": return
        if hasattr(answer,"connected_functions"):
            try:
                akwargs = dict(answer.value)
                for fn, fargs, fkwargs in answer.connected_functions:
                    kwargs = dict(list(akwargs.items()) + list(fkwargs.items()))
                    try:
                        fn(*fargs,**kwargs)
                    except:
                        print "Error ocurred when calling connected functions for event:"
                        print traceback.format_exc()
                        
            except:
                print "Error ocurred when calling connected functions for event:"
                print traceback.format_exc()
                
                
        #print "Received signal for event %s: %s" % (answer.event_name,answer.value)
        
        
    def connect(self, ev, fn, *args, **kwargs):
        """
        Connects the event 'ev' to the function 'fn'.
        The function fn is called every time the event is raised.
        The function receives the keyword arguments from the signal.
        """
        if ev not in self.monitored_events: self.monitor(ev)
        
        exe = self.monitored_events[ev] 
        obj = (fn,args,kwargs)
        if obj not in exe.queuedAnswer.connected_functions:
            exe.queuedAnswer.connected_functions.append(obj)
        else:
            print "Warning: function connected twice to the event. Ignoring."
            
    
    def disconnect(self, ev, fn, *args, **kwargs):
        """
        Disconnects the function fn from the event ev
        """
        obj = (fn,args,kwargs)
        if obj in exe.queuedAnswer.connected_functions:
            exe.queuedAnswer.connected_functions.remove(obj)
        else:
            print "Warning: function not connected to the event. Ignoring."
            
        
        
        
        


    
def testSerialized(remote,iterations):
    for n in range(iterations):
        remote.call("addItem", item=n)
    
def testConcurrent(remote,iterations):
    lstExe = []
    for n in range(iterations):
        lstExe.append(remote.call("addItem", item=n, getReturnValue = False))
        
    for exe in lstExe: exe.getReturnValue()
    
    
def testEvent(item):
    print "Event for Item:",item

def main():
    remote = RemoteIRPC("localhost",10123)
    remote.connect("testEvent",testEvent)
    remote.call("clearItems")
    #testSerialized(remote,iterations = 1000)
    testConcurrent(remote,iterations = 1000)
    #print sum(remote.call("getItems"))
    
    print "done"
    remote.exit()
    

if __name__ == "__main__":
    # Import Psyco if available
    try:
        import psyco
        #psyco.full()
    except ImportError:
        pass
    
    main()
