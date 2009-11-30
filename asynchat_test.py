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

    def mysplit(self,data):
        return data.split("\n")
        
    def processprogram(self,data): # 15s
        lines = self.mysplit(data)
        
        #  1st line of program is always a command.
        #print("recieved<", repr(data))
        ret = process(lines) # -> 100% CPU es executeCommand (5/15s)
        txt = json.dumps(ret) # 1.1s
        #print("response>", txt)
        bytes =b">\t" + txt.encode("utf8") + b"\n"
        #self.push(bytes)
        self.sock.sendall(bytes) # 7/15s
    
def reverselist(mylist):
    return list(reversed(mylist))
        
def getfunctionlist():
    global registered_functions
    return list(registered_functions.keys())

registered_functions = {
        'mysum' : sum, 
        'mymax' : max, 
        'mymin' : min,
        'reverselist' : reverselist,
        'getfunctionlist' : getfunctionlist,
    }    
        
def callFunction(cmdname, far_args, far_kwargs, fn):
    """
        Inmediate call of a function. It waits until the execution finish.
    """
    ret =  None
    if fn not in registered_functions:
        print("%s is not a registered function!" % fn)
        return None
    try:
        funct = registered_functions[fn]
        ret = funct(*far_args,**far_kwargs)
    except:
        print("Error ocurred executing %s" % fn)
        print(traceback.format_exc())
        
    return ret
    

registered_execCommands = {
        "!call" : callFunction,
        #"!set" : setVariable,
    }
pattern1 = re.compile("(\w*)=([^\t]*)")
pattern2 = re.compile("(\w*):(\w+)")

def executeCommand(commandline,data): # 30% CPU
    global pattern1, pattern2
    # An execute command is separated using tabs:
    cmdline = commandline.split("\t")
    
    # the 1st param is the command name
    cmdname = cmdline[0]
    # extra params are in the form: name = value
    args1 = []
    args2 = []
    
    kwargs1 = {}
    kwargs2 = {}
    
    for param in cmdline[1:]:
        m1 = pattern1.match(param)
        if not m1:
            m2 = pattern2.match(param)
        if m1: 
            key = m1.group(1)
            try:
                val = json.loads(m1.group(2))
            except:
                print("Error parsing arg value: %s" % param)
                print(traceback.format_exc())
                return None
            if key:
                kwargs1[key] = val
            else:
                args1.append(val)
        elif m2:
            key = m2.group(1)
            val = m2.group(2)
            if key:
                kwargs2[key] = val
            else:
                args2.append(val)
            
            
        else:
            print("Error parsing arg value: %s (unknown format)" % param)
        
            
    if cmdname not in registered_execCommands:
        print("Error. %s not registered." % cmdname)
        return None
        
    fn = registered_execCommands[cmdname]
    try:
        ret = fn(cmdname,args1, kwargs1,*args2,**kwargs2)
    except:
        print("Error ocurred when trying to execute fn:")
        print(traceback.format_exc())
        return None
    
    return ret
    

def commentCommand(commandline,data):
    print("comment: %s" % commandline)
    
commandtype_list = {
        "!" : executeCommand,
        "#" : commentCommand,
        
    }

def process(data):
    global commandtype_list
    # The command is a list separated by tabs.
    if len(data) == 0: return None
    
    
    commandline = data.pop(0)
    
    # The first arg must be always a single character
    commandtype = commandline[0]

    if commandtype not in commandtype_list:
        print("Command of type %s not in our known comandtype list" % commandtype)
        print(repr(commandline))
        return None
    
    fn = commandtype_list[commandtype]
    try:
        ret = fn(commandline,data)
    except:
        print("Exception occurred when trying to execute client command:")
        print(commandline)
        print(traceback.format_exc())
        return None
        
    return ret
        
	    
	
        
def main():

    conndest = ('', 10123)

    sck1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sck1.bind(conndest)
    sck1.listen(1)
    conn, addr = sck1.accept()

    chat1 = chatter(sock = conn, addr = addr)

    print("Starting asyncore loop")
    try:
        import cProfile
        #cProfile.run('asyncore.loop()')
        asyncore.loop()
    except:
        print(traceback.format_exc())
    print("End loop")
    try:
        conn.close()
    except:
        pass

    try:
        sck1.close()
    except:
        pass


if __name__ == '__main__':
    main()
