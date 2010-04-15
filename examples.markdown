---
layout: default
title: Examples of use of IRPC
subtitle: Secure, fast and open
---

Examples of use
========================

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


Example #1 - Monitoring your service from home
--------------------------------------------------------

Lets say we have written a piece of software which acts as a system deamon, waiting 
for someone put files in a folder via FTP, it reads the files, do some calulations and
move the file to other folder. Then, say we want to know from our computer any errors 
happened to the service, and we want to change the service configuration too.

With IRPC, your desktop application will connect to the service via TCP/IP (the service
will have a listening socket), will ask for errors between the last time the application
was connected to the service and now, and after that, will set up a event callback: 
the service will call you every time a new error occurs, with the information of it.
