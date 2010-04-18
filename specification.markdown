---
layout: default
title: IRPC specification
subtitle: Interactive cloud computing
---

Actual Specification
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

1. message type *execute* `!`: A request to the other part of the connection.
2. message type *answer* `>`: A response to a previous command from the other end.

Each message type can have its own format and decoders, but generally they share 
the same structure. Generally, all messages have several fields separated by tabs
`\t`, in those commands that character is reserved for that use.

### layer 2.1 - command format ###

Commands must follow this syntax:

1. message type character, which is always `!`
2. command name, for example `call`
3. optionally, an id for this command (must be prefixed with @) `@3a`
4. none or more parameters (explained bellow) separated by tabs `\t`
5. end with newline `\n`

A parameter can be an internal parameter, or an external argument, depending on the case
the syntax is:

1. internal parameters have the format `param_name:raw_value`
2. external arguments have the format `arg_name:json_value`

* where param_name and arg_name can be any literal following the conventions for naming 
  a variable. That is, following this regexp `[a-zA-Z][a-zA-Z0-9_]*`. Optionally
  they could be empty, meaning that is an ordered argument call, but that method is 
  discouraged.
* where raw_value is almost any literal which can be represented in 
  7-bits and doesn't include any control character.
* where json_value is any valid JSON string.

Some command examples:

    !call   fn:sortlist     lista=[5,2,7,9,1,6,3,7,4,2,8,0]
    !help   fn:reverselist
    !monitor@mo2787 ev:testEvent

Command names are also defined by the IRPC, and at the moment the list of command names is:

* **call:** calls a remote function specified by *fn* bypassing to that function 
  the arguments (also works with events using *ev* instead of *fn*)
* **help:** returns a help string (actually is not machine-friendly) about a 
  function *fn* (also works with events using *ev* instead of *fn*)
* **montior:** starts or stops* the monitoring for a event change.

NOTE: Actual implementation of monitor doesn't allow stop yet.

### layer 2.2 - response format ###

Responses follow this format:
1. message type character, which is always `>`
2. optionally the id for the originating command `3a`
3. tab separator `\t`
4. type of the data returned, generally an empty string
5. tab separator `\t`
6. Value of the response encoded using JSON
7. end with newline `\n`

Some examples of response:

    >       "getFunctionList(self) method of irpcchatter.CMD_Execute instance\n"
    >01     "signal testEvent(item)"
    >       null


### layer 3.1 - predefined functions ###

IRPC also defines some base functions for introspection, authentication, and some more.
There is a list of the existent functions at the moment:

* **getFunctionList**: returns a list containing all functions published. 
* **getEventList**: returns a list containing all events published. *(not working in the actual implementation)*
* **login**: authenticates using login and password. Optionally can use public key method or PSK *(actual implementation only works with password)*
* **whoami**: returns the username currently logged or None.
* **whaticando**: returns a list of security permissions that are granted.
* **passwd**: changes the password of the currently logged user.

### layer 3.2 - predefined events ###

Actually there aren't any predefined events in IRPC, but it is possible to have
some in the future.


Future changes to IRPCv1
----------------------------------

#### Event notification ####

the actual system for event or signal notification doesn't follow the rest of
the standard, so it will be replaced with:

* Monitoring an event:

Before, the monitoring of an event was done in this way:

	!call@mo123   monitor   ev:testEvent

and there was some inconsistency on the return value (there was more than one per call to monitor)

now it will be:

	!callback add:callbackName ev:testEvent

it will add a callback named callbackName and will be called whenever the event testEvent is fired.
A message will be recieved like:

	!callback fired:callbackName arg1=2val1' arg2='val2'

And a callback can be removed like:

	!callback remove:callbackName 

**Some possible advantages:**

Adding conditions for calling a callback:

	!callback add:callbackName ev:testEvent where={
	          'objecttype.equals' : 'string'}

Adding new static arguments for calling a callback: 

	!callback add:callbackName ev:testEvent addargs={'special' : True}
	!callback fired:callbackName arg1='val1' arg2='val2' special=True

Discarding arguments:

	!callback add:callbackName ev:testEvent rmargs=['arg1']
	!callback fired:callbackName arg2='val2' 


