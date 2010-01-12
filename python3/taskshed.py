# -*- coding: utf-8 -*-

# Task sheduler
import threading 
import time
import traceback

class Task:
    def __init__(self, function = None, args = [], kwargs = {}):
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.return_value = None
        self.finished = False
        self.inprocess = False
        self.eventFinished = threading.Event()
        
    def process(self):
        self.inprocess = True
        try:
            self.return_value = self.function(*self.args,**self.kwargs)
        except:
            print("Error executing task:")
            print(traceback.format_exc())
        self.finished = True
        self.inprocess = False
        self.eventFinished.set()


class TaskQueue:    
    def __init__(self, creatorisvalidthread = True):
        self.queue = []
        self.timedout = False
        self.processingThreads = set([])
        if creatorisvalidthread:
            self.declareValidThread()

    def declareValidThread(self):
        thread = threading.currentThread()
        self.processingThreads |= set([thread])
    
    def execute(self,function = None, args = [], kwargs = {}, wait = True):
        thread = threading.currentThread()
        task = Task(function,args,kwargs)
        if thread in self.processingThreads:
            task.process()
        else:
            if self.timedout: return None
            self.queue.append(task)
            n = 0
            t = 0.1
            q = 0
            while (not task.finished) and wait: 
                task.eventFinished.wait(t)
                if task.eventFinished.isSet(): break
                #time.sleep(t)
                if n > q + 5:
                    q = n
                    print("%s waiting for process (%.2f sec timeout)" % (repr(thread),n))
                    if n > 15:
                        print("%s aborting process" % (repr(thread)))
                        self.timedout = True
                        wait = False
                
                n+=t
            
        return task.return_value
        
    def processQueue(self,timeout=None):
        self.timedout = False
        timeStart = time.time()
        thread = threading.currentThread()
        if thread not in self.processingThreads:
            raise NameError("You must not call this funtcion from this thread!")
        n = 0    
        sz = len(self.queue)
        if sz == 0: return
        
        while sz>0:
            if timeout and n>0:
                if time.time() - timeStart < timeout:
                    break
            
            task = self.queue.pop(0)
            sz = len(self.queue)
            task.process()
            n+=1

        # if n < sz:  print "Warning: one iteration processed %d tasks and %d are still remaining" % (n,sz)
        # if n >0:  print "Processed %d queries" % n
        # if sz>0:  print "%d queries left" % sz
        return n

    # Decorators
    def queue(f):
        def calledfn(*args,**kwargs):
            return self.execute(f,args,kwargs, wait = True)
            
        return calledfn    

    def queue_nowait(f):
        def calledfn(*args,**kwargs):
            return self.execute(f,args,kwargs, wait = False)
            
        return calledfn    
        

globalQueue = TaskQueue()


    
    
    