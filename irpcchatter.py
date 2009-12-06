#!/usr/local/bin/python3
import asynchat, asyncore
import socket
import traceback
import json
import re
import pydoc

publishedFunctions = []

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
        asynchat.async_chat.__init__(self, sock = sock)
        self.sock = sock
        self.ibuffer = []
        self.obuffer = b""
        self.set_terminator(b"\n")
        self.addr = addr
        #self.fifo = asynchat.fifo()
        #self.push_with_producer(self.fifo)
        self.language = None
        
    def loop(self):
        try:
            asyncore.loop(map = {self.sock.fileno(): self})
        except asyncore.select.error:
            pass
        except:
            print("Error inesperado en el bucle de recepcion")
            print(traceback.format_exc())
            
        
        

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
            #print(repr(data))
            self.ibuffer.append(data)
        except:
            print(traceback.format_exc())

    def found_terminator(self):
        try:
            input_data = b"".join(self.ibuffer)        
            self.ibuffer = []
            self.process_data(input_data.decode("utf8"))
        except:
            print(traceback.format_exc())

    def process_data(self,data): # 15s
        if self.language:
            lines = data.split("\n")
            for line in lines:
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
            print("Command of type %s not in our known comandtype list" % commandtype)
            print(repr(commandline))
            return
        
        class_object = self.commandtype_list[commandtype]
        try:
            if class_object: class_object.process(commandline[1:])
        except:
            print("Exception occurred when trying to execute client command:")
            print(commandline)
            print(traceback.format_exc())
            
class CMD_Answer:
    def __init__(self,language):
        self.language = language
        self.chatter = language.chatter
        # todos devuelven en el siguiente formato:
        self.patternAnswer = re.compile("(?P<id>\w*)\t(?P<type>\w*)\t(?P<value>[^\t]*)\t")
    def process(self, command):
        try:
            ret = self._process(command)
        except:
            txtError = "unexpected error when parsing answer: %s\n" % command
            txtError += traceback.format_exc()
            ret = ProcessReturn(error = txtError)
            
        #self.fifo.push(self.encodeAnswer(ret))
        #self.chatter.push(self.encodeAnswer(ret))
        if ret.value:
            print(ret.value)
    
    def _process(self,answer):
        m1 = self.patternAnswer.match(answer)
        if not m1:
            return ProcessReturn(error = "Answer does not match the required pattern. (%s)" % answer)
        d1 = m1.groupindex
        
        print d1
        
        
        
        
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

    def registerFn(self,fn, name = None):
        if not name: name = fn.__name__
        self.registered_functions[name] = fn
        
    def getFunctionList(self):
        return list(self.registered_functions.keys())

    def addCmd(self, key, name, classtype, children):
        class_instance = classtype(parent = self)
        setattr(self.cmds,name,class_instance)
        self.registered_execCommands[key] = class_instance
        for cmd in children:
            class_instance.addCmd(cmd.key,cmd.name,cmd.classtype,cmd.children)

    
    def generateID(self):
        self.sequence_id += 1
        return "x%X" % self.sequence_id
        
    def encodeAnswer(self,ret):
        
        if ret.error:
            answer = ">%s\t%s\t%s\n" % (ret.id,"Exception",json.dumps(ret.error))
        else:
            answer = ">%s\t%s\t%s\n" % (ret.id,ret.type,json.dumps(ret.value))
        
        return answer.encode("utf8")
        
        
    def process(self, command):
        
        try:
            ret = self._process(command)
        except:
            txtError = "unexpected error when executing: %s\n" % command
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
                    val = json.loads(m1.group(2))
                except:
                    ret.error = "Error parsing arg value: %s\n" % param
                    ret.error += traceback.format_exc()
                    return ret
                     
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
                ret.error = "Error parsing arg value: %s (unknown format)\n" % param
                ret.error += traceback.format_exc()
                return ret
            
                
        if cmdname not in self.registered_execCommands:
            ret.error = "Error. %s not registered.\n" % cmdname
            ret.error += traceback.format_exc()
            return ret
            
        obj = self.registered_execCommands[cmdname]
        try:
            obj.execute(ret,cmdname,args1, kwargs1,*args2,**kwargs2)
        except:
            ret.error = "Error ocurred when trying to execute fn:"
            ret.error += traceback.format_exc()
            return ret
        
        return ret

        
class BaseExecFunction:
    def __init__(self, parent):
        self.parent = parent
        self.setup()
    
    def setup(self):
        pass
    
    def execute(self,ret,cmdname, far_args, far_kwargs, fn): 
        if fn not in self.parent.registered_functions:
            ret.error = "%s is not a registered function!" % fn
            return 
        try:
            funct = self.parent.registered_functions[fn]
            ret.value = self.call(funct,far_args,far_kwargs)
        except:
            ret.error = "Error ocurred executing %s\n" % fn
            ret.error += traceback.format_exc()
            
        return 
    
    def call(self, funct, args, kwargs):
        pass
        

class CallFunction(BaseExecFunction):
    def call(self, funct, args, kwargs):
        return funct(*args,**kwargs)
        


class HelpFunction(BaseExecFunction):
    def setup(self):
        self.help = pydoc.TextDoc()

    def call(self, funct, args, kwargs):
        return pydoc.plain(self.help.docroutine(funct))


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
        execute.children.append(execute_call)
        execute.children.append(execute_help)

        self.commands.append(execute)

        answer = CommandList(">","answer", CMD_Answer)
        self.commands.append(answer)
        
    def setup(self, chatter):
        global publishedFunctions
        
        for fn in publishedFunctions:
            chatter.language.cmds.execute.registerFn(fn)
    
# ----- Decorators -------
def published(fn):
    global publishedFunctions
    publishedFunctions.append(fn)
    return fn


# ----------------------------

def main():

    @published
    def testFunction(x = None):
        "A test to try the @published decorator. It returns repr(x)"
        return "testValue " + repr(x)

    conndest = ('', 10123)
    lang = BaseLanguageSpec()
    
    sck1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sck1.bind(conndest)
    sck1.listen(1)
    conn, addr = sck1.accept()

    chat1 = BaseChatter(sock = conn, addr = addr)
    chat1.setup(lang) # Configura y da de alta todo el lenguaje 
    # Creación de los distintos permisos de ejecucion
    
    

    print("Starting asyncore loop")
    try:
        import cProfile
        #cProfile.run('asyncore.loop()')
        chat1.loop()
        #asyncore.loop()
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
