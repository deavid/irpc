---
layout: default
title: IRPC by Deavid - Process control made easy
---

About
--------------------------------

IRPC is a protocol aimed to do really fast communications between applications 
and/or services over the network in a easy way. 

There is a stable code for python 2.5 or later which implements IRPCv1

**At the moment, IRPCv2 is only a draft and 
there is no implementation available**
        
Benefits
-----------------------------------

### IRPC version 1 ###

* **Minimal use of bandwith:** IRPC is optimized <u>by design</u> for low 
    bandwidth. It uses JSON for value encoding instead of XML 
    to avoid excessive markup.
    
* **Human-readable protocol:** If you see what's going inside an IRPC server 
    connection you'll see a format readable and easy to understand.
    
* **Multiple commands per connection:** Instead of doind one call per connection 
    (like XMLRPC), with IRPC the connection is opened once, removing the connection 
    delay for each query.
    
* **Support for parallel queries:** It is possible to ask a new query without 
    waiting for the response of the prior one. This virtually removes the network 
    lag in some situations. 
    
* **Events/Callbacks:** Tired of polling your XMLRPC server to know when has 
    finished the work? IRPC supports event callbacks. When something happens in 
    the server you can set up a callback which will be called every time 
    the event fires.

### IRPC version 2 ###

* **Security:** There are features in IRPCv2 that allow to cipher some private 
    data like passwords. The daeomn does a dynamic ECC publickey generation 
    which doesn't require any initial setup.
    
* **Authentication:** The main problem in several RPC protocols is, that 
    everybody can connect and call your functions. IRPCv2 has authentication, 
    which can limit which users connect to which services, and inside each 
    service, a user can have several permissions. 
    
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
David Martínez Martí (deavidsedice@gmail.com)


Download
----------------------------

You can download this project 
in either [zip](http://github.com/deavid/irpc/zipball/master)
or [tar](http://github.com/deavid/irpc/tarball/master) formats.

You can also clone the project with [GIT](http://git-scm.com)
by running:

$ git clone git://github.com/deavid/irpc



