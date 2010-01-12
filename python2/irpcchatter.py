#!/usr/bin/python
# encoding: UTF-8

import asynchat, asyncore
import socket
import traceback
import threading
import cjson

import re
import pydoc
import taskshed
import time 

publishedFunctions = []
publishedEvents = []

class ProcessReturn:
    def __init__(self, id = "", type = "", value = None, error = None):
        self.id = id
        self.type = type
        self.value = value
        self.error = error
        
class BaseClass:
    def __init__(self,family = None, type = None, name = None):
        self.family = family 
        self.type = type
        self.name = name
        

class BaseChatter(asynchat.async_chat):
    def __init__(self,sock, addr):
        try:
            asynchat.async_chat.__init__(self, sock = sock) 
        except:
            asynchat.async_chat.__init__(self, conn = sock) # python 2.5
            
        self.sock = sock
        self.ibuffer = []
        self.obuffer = ""
        self.set_terminator("\n")
        self.addr = addr
        #self.fifo = asynchat.fifo()
        #self.push_with_producer(self.fifo)
        self.language = None
        self.comm_rlock = threading.RLock()
        self.consecutive_errors = 0
        self.found_terminator = False
        self.error = False
    
    def loop(self):
        while not self.error:
            try:
                self.sock.setblocking(1)
            except:
                self.error = True
                return False
            data = ""
            try:
                data = self.sock.recv(4096)
            except socket.error:
		import sys
		v, t = sys.exc_info()[1]
		print v,t
		if v == 11:
		    time.sleep(0.1)
		data = ""
		
		
            if len(data):
                self.ibuffer.append(data)
                if '\n' in data: self.found_terminator = True
                if self.found_terminator: self.processInputBuffer()
	    else:
		time.sleep(0.01)
		

    def processInputBuffer(self):
        try:
            input_data = "".join(self.ibuffer)        
            input_lines = input_data.split("\n")
            self.found_terminator = False
            if len(input_lines[-1])>0:
                self.ibuffer = [input_lines[-1]]
            else:
                self.ibuffer = []
                
            for line in input_lines[:-1]:
                #print "<<<", line
                self.comm_rlock.acquire()
                self.process_data(line.decode("utf8"))
                self.comm_rlock.release()
        except:
            print traceback.format_exc()
            

    
    def _loop(self):
        n = None
        try:
            n = self.sock.fileno()
        except:
            n = None
        if n is None: return False
        try:
            asyncore.loop(map = {n : self},timeout = 0.01)
        #except asyncore.select.error:
        #    pass
        except:
            print u"Error inesperado en el bucle de recepcion"
            print traceback.format_exc()
            
    def push(self, string):
        r = False
        if self.error: return False
        self.comm_rlock.acquire()
        try:
            r = self._push(string)
        except:
            r = False
        self.comm_rlock.release()
        
        if r:
            self.consecutive_errors = 0
        else:
            self.consecutive_errors += 1
            if self.consecutive_errors > 3:
                print "Error en el envio"
                self.error = True
                self.sock.close()
        return r
        
    def _push(self, string):
        #print ">>>",repr(string)   # DEBUG
        #ret = asynchat.async_chat.push(self,string) 
        try:
            if self.sock.fileno() < 0: 
                self.sock.close()
                return False
        except:
            self.sock.close()
            return False
        done = False
        error = False
        errors = 0
        self.obuffer += string
        bytes = 0
        while not done:
            try:
                bytes = self.sock.send(self.obuffer[:4096])
                if bytes == 0: break
                self.obuffer = self.obuffer[bytes:] 
                if len(self.obuffer)==0 : done = True
            except socket.error , e:
                
                done = False
                #if not error:  print "Network overflow, waiting. . . "
                error = True
                errors +=1
                if errors>4: 
                    print "Packet NOT sent! %d times retried." % errors
                    print "Error:", e
                    self.sock.close()
                    return False
                    break
                time.sleep(0.02)
            
            
        
        return True

    def setup(self, languageSpec):
        self.language = LanguageProcessor(chatter = self)
        for cmd in languageSpec.commands:
            self.language.addCmd(cmd.key,cmd.name,cmd.classtype,cmd.children)
        #self.language.addType("!","execute",CMD_Execute)
        # self.cmds = self.language.cmds
        languageSpec.setup(self)
        """ 
            permite accdeder a los comandos del siguiente modo:
            
            self.language.cmds.exec
            self.language.cmds.exec.cmds.call
            
        """
        

    def collect_incoming_data(self,data):
        try:
            #print repr(data)
            self.ibuffer.append(data)
        except:
            print traceback.format_exc()

    def found_terminator(self):
        try:
            input_data = "".join(self.ibuffer)        
            self.ibuffer = []
            self.comm_rlock.acquire()
            self.process_data(input_data.decode("utf8"))
            self.comm_rlock.release()
        except:
            print traceback.format_exc()

    def process_data(self,data): # 15s
        if self.language:
            lines = data.split("\n")
            for line in lines:
                #print "<<<",repr(line)  # DEBUG
                self.language.process(line)
            
            
"""class ServerChatter(BaseChatter):
    def __init__(self,sock,addr):
        BaseChatter.__init__(self, sock, addr)
"""        
        

class LanguageProcessor:
    def __init__(self,chatter):
        self.chatter = chatter
        self.commandtype_list = {
            }
        self.cmds = BaseClass()
        # "!" : CMD_Execute(self),
        # "#" : None, # Comment
        # "@" : None,
        # ">" : None, # Return Value

    def addCmd(self, key, name, classtype, children):
        class_instance = classtype(language = self)
        setattr(self.cmds,name,class_instance)
        self.commandtype_list[key] = class_instance
        for cmd in children:
            class_instance.addCmd(cmd.key,cmd.name,cmd.classtype,cmd.children)
    
    def process(self, commandline):
        # The first arg must be always a single character
        if len(commandline)==0: return
        commandtype = commandline[0]

        if commandtype not in self.commandtype_list:
            print u"Command of type %s not in our known comandtype list" % commandtype
            print repr(commandline)
            return
        
        class_object = self.commandtype_list[commandtype]
        try:
            if class_object: class_object.process(commandline[1:])
        except:
            print u"Exception occurred when trying to execute client command:"
            print commandline
            print traceback.format_exc()

class QueuedAnswer:
    def __init__(self, id, cmdanswer = None, autoremove = True):
        if id in cmdanswer.answerqueue:
            raise(NameError,"QueuedAnswer %s already queued!" % id)
        self.id = id
        self.type = ""
        self.value = ""
        self.answered = False
        self.answered_event = threading.Event()
        self.autoremove = autoremove
        self.cmdanswer = cmdanswer
        self.callback = None
        if self.cmdanswer:
            self.cmdanswer.answerqueue[id] = self

    def wait(self, timeout = None):
        self.answered_event.wait(timeout)
        return self.answered
        
    def setAnswer(self,type,value):
        self.type = type
        self.value = value
        self.answered = True
        self.answered_event.set()
        if self.autoremove and self.cmdanswer:  del self.cmdanswer.answerqueue[self.id]
        #if type:       print "Answer:",self.id,type,value, self.callback
            
            
        
        if self.callback: 
            try:
                self.callback(self)
            except:
                print u"Error trying to execute callback %s", self.callback.__name__
                print traceback.format_exc()
                
        
        
        
        

class CMD_Answer:
    def __init__(self,language):
        self.language = language
        self.chatter = language.chatter
        # todos devuelven en el siguiente formato:
        self.patternAnswer = re.compile("(?P<id>\w*)\t(?P<type>\w*)\t(?P<value>[^\t]*)")
        self.answerqueue = {}
        
    def queueAnswerFor(self,id, autoremove = True):
        return QueuedAnswer(id, self, autoremove)
    
    
    def process(self, command):

        try:
            ret = self._process(command)
        except:
            txtError = u"unexpected error when parsing answer: %s\n" % command
            txtError += traceback.format_exc()
            print txtError
            ret = ProcessReturn(error = txtError)
            
        #self.fifo.push(self.encodeAnswer(ret))
        #self.chatter.push(self.encodeAnswer(ret))
        if ret.value:
            print ret.value
    
    def _process(self,answer):
        ret = ProcessReturn()
        m1 = self.patternAnswer.match(answer)
        if not m1:
            print "Pattern match error on answer"
            ret.error = u"Answer does not match the required pattern. (%s)" % answer
            return ret
        d1 = m1.groupdict("")
        id = d1['id']
        type = d1['type']
        try:
            value = cjson.decode(d1['value'])
        except:
            ret.error = u"Error parsing return value: %s\n" % param
            ret.error += traceback.format_exc()
            return ret

        if id not in self.answerqueue:
            print u"WARN: Received answer id %s which is not in the answerQueue." % repr(id)
        else:
            self.answerqueue[id].setAnswer(type,value)
            
            

        return ret
        
        
        
        
class CMD_Execute:
    def __init__(self,language):
        self.language = language
        self.chatter = language.chatter
        self.patternRemoteArg = re.compile("(\w*)=([^\t]*)")
        self.patternLocalArg = re.compile("(\w*):(\w+)")
        self.sequence_id = 0
        self.cmds = BaseClass()
        self.registered_execCommands = {
            }
        #self.registered_execCommands = {
        #    "call" : CallFunction(),
            #"!set" : setVariable,
        #}
        self.registered_functions = {
        }    
        self.registerFn(self.getFunctionList)

        self.registered_events = {
        }    
        self.registerFn(self.getEventList)

    def registerFn(self,fn, name = None):
        if not name: name = fn.__name__
        self.registered_functions[name] = fn

    def registerEvent(self,event):
        name = event.name
        self.registered_events[name] = event
        
    def getFunctionList(self):
        return list(self.registered_functions.keys())

    def getEventList(self):
        return list(self.registered_events.keys())

    def addCmd(self, key, name, classtype, children):
        class_instance = classtype(parent = self)
        setattr(self.cmds,name,class_instance)
        self.registered_execCommands[key] = class_instance
        for cmd in children:
            class_instance.addCmd(cmd.key,cmd.name,cmd.classtype,cmd.children)

    
    def generateID(self):
        self.sequence_id += 1
        return u"x%X" % self.sequence_id
        
    def encodeAnswer(self,ret):
        
        if ret.error:
            answer = u">%s\t%s\t%s\n" % (ret.id,"Exception",cjson.encode(ret.error))
        else:
            answer = u">%s\t%s\t%s\n" % (ret.id,ret.type,cjson.encode(ret.value))
        
        return answer.encode("utf8")
        
        
    def process(self, command):
        
        try:
            ret = self._process(command)
        except:
            txtError = u"unexpected error when executing: %s\n" % command
            txtError += traceback.format_exc()
            ret = ProcessReturn(error = txtError)
            
        #self.fifo.push(self.encodeAnswer(ret))
        self.chatter.push(self.encodeAnswer(ret))
            
        
    
    def _process(self, command):
        # An execute command is separated using tabs:
        cmdline = command.split("\t")
        
        # the 1st param is the command name
        list_arg0 = cmdline[0].split("@")
        cmdname = list_arg0[0]
        idnum = ""
        if len(list_arg0)>1:
            idnum = list_arg0[1]
            if len(idnum) == 0:
                idnum = self.generateID()

        ret = ProcessReturn(id = idnum)

        # extra params are in the form: name = value
        args1 = []
        args2 = []
        
        kwargs1 = {}
        kwargs2 = {}
        
        for param in cmdline[1:]:
            m1 = self.patternRemoteArg.match(param)
            if not m1:
                m2 = self.patternLocalArg.match(param)
            if m1: 
                key = m1.group(1)
                try:
                    val = cjson.decode(m1.group(2))
                except:
                    ret.error = u"Error parsing arg value: %s\n" % param
                    ret.error += traceback.format_exc()
                    return ret
                     
                if key:
                    kwargs1[str(key)] = val
                else:
                    args1.append(val)
            elif m2:
                key = m2.group(1)
                val = m2.group(2)
                if key:
                    kwargs2[str(key)] = val
                else:
                    args2.append(val)
                
                
            else:
                ret.error = u"Error parsing arg value: %s (unknown format)\n" % param
                ret.error += traceback.format_exc()
                return ret
            
                
        if cmdname not in self.registered_execCommands:
            ret.error = u"Error. %s not registered.\n" % cmdname
            ret.error += traceback.format_exc()
            return ret
            
        obj = self.registered_execCommands[cmdname]
        try:
            obj.execute(ret,cmdname,args1, kwargs1,*args2,**kwargs2)
        except:
            ret.error = u"Error ocurred when trying to execute fn:"
            ret.error += traceback.format_exc()
            return ret
        
        return ret

class RemoteEvent:
    def __init__(self,name, signal_args = [], returnTypes = [], docstring = "", public = True, *args,**kwargs):
        self.name = name # event's name
        self.signal_kwargs = signal_args
        self.callback_list = []
        self.returnTypes = returnTypes
        self.event = threading.Event()
        self.docstring = docstring
        if public:
            global publishedEvents
            publishedEvents.append(self)
        
    def getSignalSignature(self):
        sig = u"signal %s(%s)" % (self.name, ", ".join(self.signal_kwargs))
        if len(self.returnTypes):
            sig += u" -> ( %s )" % (" | ".join([x.__name__ for x in self.returnTypes]))
        if self.docstring:
            sig += u"\n%s\n" % self.docstring
        return sig
    
    def registerCallback(self, fn, *args, **kwargs):
        self.callback_list.append((fn,args,kwargs))
        
    def unregisterCallback(self, fn, *args, **kwargs):
        self.callback_list.remove((fn,args,kwargs))
        
    def signalRaise(self,*args,**kwargs):
        for k in kwargs.keys():
            if k not in self.signal_kwargs:
                raise NameError("Unexpected argument '%s'" % k)
        lstargs = list(args)    
        for k in self.signal_kwargs:
            if k not in kwargs:
                try:
                    newarg = lstargs.pop(0)
                except IndexError:
                    print u"Not enough arguments for raising signal (expecting arg %s)" % k
                    return None
                kwargs[k] = newarg
        
        self.event.set()
        returned_values = []
        for fn,fargs,fkwargs in self.callback_list:
            try:
                tkwargs = dict(tuple(kwargs.items()) + tuple(fkwargs.items()))
                ret = fn(*fargs,**tkwargs)
                if len(self.returnTypes):
                    validret = False
                    for t in self.returnTypes:
                        if type(ret) is t:
                            returned_values.append(ret)
                            validret = True
                            break
                    if not validret:
                        print u"WARN: callback %s -> %s returned a invalid value: %s" % (self.name,fn.__name__, repr(ret))
            except:
                print u"Error in callback %s -> %s ; traceback follows:" % (self.name,fn.__name__)
                print traceback.format_exc()
                
            
        
        self.event.clear()
        
        return returned_values 
    
        
class BaseExecFunction:
    def __init__(self, parent):
        self.parent = parent
        self.setup()
    
    def setup(self):
        pass
    
    def execute(self,ret,cmdname, far_args, far_kwargs, fn = None, ev = None): 
        if fn:
            if fn not in self.parent.registered_functions:
                ret.error = u"%s is not a registered function!" % fn
                return 
            try:
                funct = self.parent.registered_functions[fn]
                ret.value = self.callFn(funct,far_args,far_kwargs,ret)
            except:
                ret.error = u"Error ocurred executing %s\n" % fn
                ret.error += traceback.format_exc()
            return 
        if ev:
            if ev not in self.parent.registered_events:
                ret.error = u"%s is not a registered event!" % ev
                return 
            try:
                event = self.parent.registered_events[ev]
                ret.value = self.callEv(event,far_args,far_kwargs,ret)
            except:
                ret.error = u"Error ocurred executing EVENT %s\n" % ev
                ret.error += traceback.format_exc()
            return 
    
    def callFn(self, funct, args, kwargs,ret):
        raise NameError("This command does NOT have support for functions!")

    def callEv(self, event, args, kwargs,ret):
        raise NameError("This command does NOT have support for events!")
    
        

class CallFunction(BaseExecFunction):
    def callFn(self, funct, args, kwargs,ret):
        return funct(*args,**kwargs)
        
    def callEv(self, event, args, kwargs,ret):
        return event.signalRaise(*args,**kwargs)


class HelpFunction(BaseExecFunction):
    def setup(self):
        self.help = pydoc.TextDoc()

    def callFn(self, funct, args, kwargs,ret):
        return pydoc.plain(self.help.docroutine(funct))

    def callEv(self, event, args, kwargs,ret):
        return event.getSignalSignature()

class MonitorFunction(BaseExecFunction):
    def callEv(self, event, args, kwargs,ret):
        event.registerCallback(self.event_callback,event_id = ret.id)
    
    def event_callback(self,event_id, **kwargs):
        ret = ProcessReturn(id = event_id, type = "Signal", value = kwargs)
        self.parent.chatter.push(self.parent.encodeAnswer(ret))
        


class CommandList:
    def __init__(self, key, name, classtype):
        self.key = key
        self.name = name
        self.classtype = classtype
        self.children = []

    
class LanguageSpec:
    def __init__(self):
        self.commands = []
        
    
        

class BaseLanguageSpec(LanguageSpec):
    def __init__(self):
        LanguageSpec.__init__(self)

        execute = CommandList("!","execute", CMD_Execute)
        execute_call = CommandList("call","call", CallFunction)
        execute_help = CommandList("help","help", HelpFunction)
        execute_monitor = CommandList("monitor","monitor", MonitorFunction)
        execute.children.append(execute_call)
        execute.children.append(execute_help)
        execute.children.append(execute_monitor)

        self.commands.append(execute)

        answer = CommandList(">","answer", CMD_Answer)
        self.commands.append(answer)
        
    def setup(self, chatter):
        global publishedFunctions
        global publishedEvents
        
        for fn in publishedFunctions:
            chatter.language.cmds.execute.registerFn(fn)
        
        for event in publishedEvents:
            chatter.language.cmds.execute.registerEvent(event)
    
# ----- Decorators -------
def published(fn):
    global publishedFunctions
    publishedFunctions.append(fn)
    return fn


# ----------------------------

def main():

    @published
    def testFunction(x = None):
        u"A test to try the @published decorator. It returns repr(x)"
        return u"testValue " + repr(x)

    conndest = ('', 10123)
    lang = BaseLanguageSpec()
    
    sck1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sck1.bind(conndest)
    sck1.listen(1)
    conn, addr = sck1.accept()

    chat1 = BaseChatter(sock = conn, addr = addr)
    chat1.setup(lang) # Configura y da de alta todo el lenguaje 
    # Creación de los distintos permisos de ejecucion
    
    

    print u"Starting asyncore loop"
    try:
        import cProfile
        #cProfile.run('asyncore.loop()')
        chat1.loop()
        #asyncore.loop()
    except:
        print traceback.format_exc()
    print u"End loop"
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
