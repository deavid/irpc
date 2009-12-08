import irpcchatter
import random
listItems = []

@irpcchatter.published
def addItem(item):
    global listItems
    if random.randint(0,1200) == 0:
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
    """ 
        Devuelve una lista orrdenada a partir de la lista que se le pasa como parametro "lista"
    """
    return list(sorted(lista))
    
@irpcchatter.published
def reverselist(lista):
    """ 
        Devuelve una lista invertida a partir de la lista que se le pasa como parametro "lista"
    """
    return list(reversed(lista))
    
testEvent = irpcchatter.RemoteEvent(name="testEvent",signal_args=["item"])
