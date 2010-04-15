---
layout: default
title: IRPC by Deavid
subtitle: Process control made easy
---

About
--------------------------------
Interactive Remote Process Control (IRPC) is a mix between Remote Process Control 
and Inter-Process Communication, and is aimed for its use over the network 
to publish services, specially where other protocol standards doesn't fit at all. 
It's meant to be used like XMLRPC, but IRPC has some powerful features that 
other protocols lack. It makes use of JSON for value encoding (which is a 
well known standard) and the message commands are very simple. 

The main idea here is to enable remote applications (with probably a poor 
net connection between them) interact like they were local and they were two 
different parts of the same program. We want to publish services to do specific 
things, some of these things could be privileged actions like deleting comments 
on a blog or shutting down a service like Apache. And we also want to enable these
services to (optionally) use other services as they need. So, when we write a 
new application, we mainly join the existent pieces and we have created a new GUI
for those services, or a new service to manage those pieces in a different way.



Actual Status
-----------------------------------------
I have one initial implementation for Python2.5 which covers most of the features for IRPCv1. 

I'm using versions of that implementation for my own projects and seems to be very easy to use.

**At the moment, IRPCv2 is only a draft and 
there is no implementation available**

(There are lots of docs inside the git repo in *spanish*, with mixed ideas about what can be done in this protocol)
I'm looking for people to help me with this project. If you have any ideas, please contact me!

Benefits
-----------------------------------

### IRPC version 1 ###

* **Minimal use of bandwith:** IRPC is optimized <u>by design</u> for low 
    bandwidth. It uses JSON for value encoding instead of XML 
    to avoid excessive markup.
    
* **Human-readable protocol:** If you see what's going inside an IRPC server 
    connection you'll see a format readable and easy to understand.
    
* **Multiple commands per connection:** Instead of doing one call per connection 
    (like XMLRPC), with IRPC the connection is opened once, removing the connection 
    delay for each query.
    
* **Support for parallel queries:** It is possible to ask a new query without 
    waiting for the response of the prior one. This virtually removes the network 
    lag in some situations. 
    
* **Events/Callbacks:** Tired of polling your XMLRPC server to know when has 
    finished the work? IRPC supports event callbacks. When something happens in 
    the server you can set up a callback which will be called every time 
    the event fires.
    
* **Introspection:** There are functions to see what is inside each 
    service, which functions are callable, etc.
    
* **Authentication:** The main problem in several RPC protocols is, that 
    everybody can connect and call your functions. IRPCv1 has authentication, 
    which can limit which users can make use of which functions.

### IRPC version 2 ###

* **Security:** There are features in IRPCv2 that allow to cipher some private 
    data like passwords. The daeomn does a dynamic ECC publickey generation 
    which doesn't require any initial setup.
    
* **Authentication:** IRPCv2 has server authentication, 
    which can limit which users connect to which services.
    
* **Client Service Design:** Don't worry about listening ports if you want to 
    write a new service or a client application. Your software will be always 
    the client part in a TPC/IP connection. IRPCv2 has a daemon which routes 
    the client applications to the services.

License
----------------------------

[LGPLv2.1](http://www.gnu.org/licenses/lgpl-2.1.html) or [later](http://www.gnu.org/licenses/lgpl.html)

Authors
----------------------------

David Martínez Martí (deavidsedice@gmail.com)

Contact
----------------------------
Please contact me if you liked the main idea behind IRPC.

mailing list: irpcprotocol@googlegroups.com

