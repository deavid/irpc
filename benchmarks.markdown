---
layout: default
title: IRPC Speed
subtitle: Because speed matters
---

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

