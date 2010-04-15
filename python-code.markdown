---
layout: default
title: Python implementation of IRPC
subtitle: Secure, fast and open
---

Python implementation of IRPCv1
=========================================

With the implementation we made for python, is really easy to create the 
connection between the two parts. There are some examples:

Basic IRPC Server
---------------------------
{% highlight python %}
import irpc.tcpserver
import signal
import my_public_functions

exit = False

def sigINT(signum, frame):
    global exit
    print "Recieved signal %d! " % (signum)
    exit = True

def main():
    global exit
    exit = False
    signal.signal(signal.SIGINT, sigINT)
    server, thread = irpc.tcpserver.startServer(PORT=10123)
    print "Server loop running in thread:", thread.name
    while not exit:
        time.sleep(0.2)
        
    server.exit()
    del server
    del thread

if __name__ == "__main__":
    main()

{% endhighlight %}

This briefly starts a IRPC server, there is a *my_public_functions* import which 
can have your public functions for IRPC.

That file can be like this:
{% highlight python %}
from irpc import irpcchatter

listItems = []

@irpcchatter.published()
def addItem(item):
    global listItems
    listItems.append(item)
    return True

@irpcchatter.published()
def removeItem(item):
    global listItems
    listItems.remove(item)
    return True

@irpcchatter.published()
def getItems():
    global listItems
    return listItems

@irpcchatter.published()
def clearItems():
    global listItems
    listItems = []
    return True
    
{% endhighlight %}

That should work as a server.

Take a look into the decorator `@irpcchatter.published()`, it is the only needed
change to make a function public to anyone. And with this small code we are
giving a service of maintaining a list of items and can be readed and modified
by anyone.


Basic IRPC Client
-----------------------------
{% highlight python %}
import irpc.tcpclient

def main():
    remote = irpc.tcpclient.RemoteIRPC("localhost",10123)
    remote.call("clearItems")
    for n in range(10):
        remote.call("addItem", item=n)
    print sum(remote.call("getItems"))
    print "done"
    remote.exit()

if __name__ == "__main__":
    main()

{% endhighlight %}

This simple code does a lot of things: it connects to the remote server, and clears
the item list, does ten consecutive calls of *addItem* and finally computes the
sum of all the items on the list. Notice that the arguments are commonly passed 
by name and not by order.

What can I say? In almost 64 lines of code we have a full working example of IRPC
demostrating how to call different functions.
