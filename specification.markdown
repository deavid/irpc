---
layout: default
title: IRPC specification
subtitle: Interactive cloud computing
---

Specification
==========================

IRPC defines the protocol in layers, which are configurable inside the implementation
to allow future changes or different versions of IRPC. 

Take into account that IRPC is a session oriented protocol, the connection is open
once, and is reused infinitely over all queries.

### layer 0 - transport ###

First of all, IRPC is a stream protocol. It works whenever the points are 
connected through a stream. In practice, this would be a TCP/IP stack, but in 
practice is anything which can connect the two parts and recieves and sends the 
data in order and with error control.

For TCP/IP we use a socket. One of the parts has to place a listener socket 
(generally is the service) and once the connection is stablished, we can use that
link to send our data.


### layer 1 - message format ###

All in IRPC are messages, and those are ended with `\n` (this character is 
reserved for this use).
The first character of a message is the message type. Probably we can have up to 
90 message types, but actually we're using mainly two:

1. message type command `!`: A request to the other part of the connection.
2. message type response `>`: A response to a previous command from the other end.

Each message type can have its own format and decoders, but generally they share 
the same structure. Generally, all messages have several fields separated by tabs
`\t`, in those commands that character is reserved for that use.

### layer 2.1 - command format ###

### layer 2.2 - response format ###

