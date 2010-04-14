---
layout: default
title: IRPC by Deavid - Process control made easy
---

About
--------------------------------

IRPC is a protocol aimed to do really fast communications between applications 
and/or services over the network in a easy way. 

Developers often face the same problems when creating a new daemon. The daemon 
should interact somehow with other applications (often the applications should 
listen to the server for events and send orders to it) , and those apps can be local, over the 
local network, or somewhere in the Internet.And there are several technologies 
to face these situations, but all of these present some limitations or problems.
IRPC tries to be the right protocol to do such things.

Generally, RPC Protocols are good when they are mainly used to call server functions. 
IPC protocols are more likely to be used locally or over a fast network. Some 
other implementations (Like Java RMI) requires to the developer recompile all 
the clients and servers whenever the interacting part is updated. And, most 
important, there is almost bundled no support for authentication and ciphering 
in those protocols. You have to check every call for the credentials, and 
cryptography is generally done using https or some sort of SSL.

IRPC provides a simple way to code new services and client applications, the 
interface will be extensible without requiring to update services and apps at
the same time. With IRPC each action has a very small footprint in the bandwith.
And there are some tecniques aimed to avoid or mitigate network lags.

IRPC is designed to work best with very-high level languages like Python, Ruby
and so on. This makes IRPC very easy to integrate with your existent python project.

Actual Status
-----------------------------------------
Sadly, IRPC is at the moment only a concept. I have one initial implementation for
Python2.5 which covers most of the features for IRPCv1 (and probably some 
concepts from IRPCv2). I'm using versions of that implementation for my own projects
and seems to be very easy to use.

**At the moment, IRPCv2 is only a draft and 
there is no implementation available**

(There are lots of docs inside the git repo, with mixed ideas about what can be done in this protocol)
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

Speed and some benchmarks
----------------------------

IRPC messages tend to be small, most of them can be under 50 bytes long. Of course 
that number could be much much bigger depending on the size of data you are sending.

But most functions take 0-4 arguments, most of them are integers or small strings.

For example, if you use IRPC from a standard internet connection, you'll have 320kbps 
of upload available. That will mean about 800 messages per second in IRPC. Each 
message will cost less than 2ms to send it. The other part will recieve it about
40ms later because of the network lag. But we don't have to wait for response
before sending more commands, so we're not affected by the network lag (except 
whenever you need strictly a value before you do the next query).

Obviuosly, those numbers are 200x larger when you connect directly through LAN.

About CPU use, IRPC should be faster than others like XMLRPC because an XML Parser 
always uses more CPU than JSON decoding. And we use JSON only for value encoding,
for the protocol itself is a very simple binary protocol separated by `\n` and `\t`.

But in the other hand, the only implementation which is fully working is a pure
python module. The handicap here is, that were using a lot of CPU only because is 
Python (an interpreter) which decodes the messages.

My benchmarks show that one machine (Athlon64 @ 2Ghz) holding the server and the 
client can  process up to 1200 messages per second. (the size of each message 
doesn't matter)

If you are using XMLRPC over the internet and you feel that it isn't fast enough 
for you, probably that is because the lag added by each connection done every 
call in this protocol. I guess XMLRPC over internet could process 10 calls every 
second, which is enough for most applications.

A test done in D shows that compiled languages could handle IRPC messages up to 100
times faster than interpreted ones (like Python). In the future I want to create 
a IRPC module for Python written mostly in C and leaving to Python the logic.

License
----------------------------

[LGPLv2.1](http://www.gnu.org/licenses/lgpl-2.1.html) or [later](http://www.gnu.org/licenses/lgpl.html)

Authors
----------------------------

David Martínez Martí (deavidsedice@gmail.com)

Contact
----------------------------
Please contact me if you liked the main idea behind IRPC.

David Martínez Martí (deavidsedice@gmail.com)


Download
----------------------------

You can download this project 
in either [zip](http://github.com/deavid/irpc/zipball/master)
or [tar](http://github.com/deavid/irpc/tarball/master) formats.

You can also clone the project with [GIT](http://git-scm.com)
by running:

        $ git clone git://github.com/deavid/irpc



