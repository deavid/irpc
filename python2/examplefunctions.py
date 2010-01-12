#!/usr/bin/python
# encoding: UTF-8

import irpcchatter
import random
listItems = []
itera_1 = 0
@irpcchatter.published
def addItem(item):
    global listItems, itera_1
    itera_1 += 1
    if itera_1 > 100:
	itera_1 = 0
        testEvent.signalRaise(item=item)
    listItems.append(item)
    return True

@irpcchatter.published
def removeItem(item):
    global listItems
    listItems.remove(item)
    return True
    

@irpcchatter.published
def getItems():
    global listItems
    return listItems
    
@irpcchatter.published
def clearItems():
    global listItems
    listItems = []
    return True
    

@irpcchatter.published
def mysum(itemlist):
    return sum(itemlist)
    

@irpcchatter.published
def mymax(itemlist):
    return max(itemlist)
    

@irpcchatter.published
def mymin(itemlist):
    return min(itemlist)
    
    
@irpcchatter.published
def sortlist(lista):
    u""" 
        Devuelve una lista orrdenada a partir de la lista que se le pasa como parametro "lista"
    """
    return list(sorted(lista))
    
@irpcchatter.published
def reverselist(lista):
    u""" 
        Devuelve una lista invertida a partir de la lista que se le pasa como parametro "lista"
    """
    return list(reversed(lista))
    
testEvent = irpcchatter.RemoteEvent(name=u"testEvent",signal_args=[u"item"])
