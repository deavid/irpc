module irpcsocket;

import std.c.time;
import std.stdio;
import std.socket;
import std.thread;
import messagequeue;
import irpcchatter;

const bool irpc_socket_debug = false;

class ThreadProcessor : Thread
{
    irpcClientSocket ics; // Parent al que está asociado.
    messageQueue recvQueue; // Cola que tiene vigilada
    
    BaseChatter chatter;
    
}


class irpcClientSocket
{
    Socket cSocket;
    messageQueue recvQueue;  // per connection !!!!
    messageQueue sendQueue;
    
    irpcSocket parent;
    string remoteAddress;
    bool socket_closing = false;
    ThreadProcessor processor;
    
    this(irpcSocket theparent, Socket cn)
    {
	parent = theparent;
	cSocket = cn;
	recvQueue = new messageQueue();
	sendQueue = new messageQueue();
	assert(cSocket.isAlive());
	//Leer ahora remoteaddress evita que luego no lo podamos leer
	// especial para sacar info de un error.
	remoteAddress = cSocket.remoteAddress().toString();
	cSocket.blocking(false);
	parent.update_socketstats();
	static if (irpc_socket_debug) writefln("nuevo socket " ~ remoteAddress);
    }
    
    ~this()
    {
        static if (irpc_socket_debug) writefln("liberando socket " ~ remoteAddress);
        close();
        delete cSocket;
	delete recvQueue;
	delete sendQueue;
    }
    
    void close()
    {
	if (cSocket && cSocket.isAlive() && !socket_closing) 
	{
	    socket_closing = true;
	    static if (irpc_socket_debug) writefln("cerrando socket " ~ remoteAddress);
	    cSocket.blocking(true);
	    cSocket.shutdown(SocketShutdown.BOTH);
	    static if (irpc_socket_debug) writefln("socket shutdown done");
	    char[1024] buf;
	    int read = cSocket.receive(buf);
	    while (read > 0)
	    {
		writefln("received extra data in socket shutdown: %d bytes", read);
		read = cSocket.receive(buf);
	    }
	    cSocket.close();
	    parent.update_socketstats();
	}
    }
    
    bool sendMessage(string msg)
    {
	sendQueue.waitForWriteSpace();
	bool ret = sendQueue.putItem(msg.dup);
	parent.writer.resume(); // Reenciende el thread escritor si no lo estaba.
	return ret;
    }
    
    int send()
    {
	if (socket_closing) return 0;
	char[] buf;
	
	buf = sendQueue.read(1024);
	if (buf.length < 1) return -1;
	
	int sent = cSocket.send(buf);
	if (sent < 0) return 0;
	if (sent > buf.length)
	{
	    writefln("ERROR: %d -> %d", buf.length, sent);
	    sent = buf.length;
	    
	    writefln(buf);
	}
	
	try
	{
	sendQueue.readACK(sent);
	} catch (Object o) {
	    writefln("Unknown error in readACK!");
	    writefln(o.toString());
	}
	
	return sent;
	
    }

    int recv()
    {
	if (socket_closing) return 0;
	char[1024] buf;
	int read = cSocket.receive(buf);

	bool to_be_closed = true;
	if (read > 0)
	{
	    try
	    {
		//static if (irpc_socket_debug) printf("*>%.*s", buf[0 .. read]);
		recvQueue.write(buf[0 .. read]);
		to_be_closed = false;
	    }
	    catch 
	    {
		static if (irpc_socket_debug) writefln("Unknown error.");
		to_be_closed = true;
	    }
	}
	else if (read == Socket.ERROR) 
	{
	    static if (irpc_socket_debug) printf("Connection error.\n");
	} 
	else if(read == 0) 
	{
	    static if (irpc_socket_debug) printf("Connection from %.*s closed.\n", remoteAddress);
	    cSocket.close(); // REAL CLOSE!
	    to_be_closed = false;
	    socket_closing = true;
	} 
	else 
	{
	    static if (irpc_socket_debug) printf("Unknown error code %d, closing socket.\n", read);
	}
	
	
	if (to_be_closed) 
	{
	    close();
	    // Falta notificar al padre de que hemos cerrado.
	    /*alive_sockets--;
	    dead_sockets++;
	    static if (irpc_socket_debug) printf("\tTotal connections: %d (and %d dead waiting gc)\n", alive_sockets, dead_sockets);	    
	*/
	}
	return read;
    }
        
 
}

int thread_readloop(void *sck)
{
    irpcSocket sckServer = cast(irpcSocket) sck;
    return sckServer.readloop();
}

int thread_writeloop(void *sck)
{
    irpcSocket sckServer = cast(irpcSocket) sck;
    return sckServer.writeloop();
}

class irpcSocket
{
public:
    const int SERVER_ACCEPT_QUEUE = 16;
    const int RESERVED_CONNECTIONS = 8;
    irpcClientSocket[] icscks;
    //Socket[] clientSockets;
    InternetAddress listenAddress;
    Socket listener;
    SocketSet sset; // para comprobar el tope, ver sset.max()
    //messageQueue recvQueue;  // per connection !!!!
    //messageQueue sendQueue;
    
    int port = 10123;
    bool exitReadLoop = false;

    int dead_sockets = 0, alive_sockets = 0;
    irpcClientSocket[] alive_socket_list;

    Thread reader; // Hilo encargado de las lecturas. Pausa si no hay nada que leer.
    Thread writer; // Hilo encargado de las escrituras. Si no hay nada que escribir, pausa.
    
public:
    this(int port_ = 10123, bool autostart = true)
    {
	port = port_;
	if (autostart) start_server();
    }
    
    ~this()
    {
	close_server();
    }
    
    void close_server()
    {
	if (listener || sset || listenAddress)
	{
	    closeAll();
	    foreach(irpcClientSocket ics; icscks) 
	    {
		if (ics) delete ics;
	    }
	    static if (irpc_socket_debug) writefln("Closing server socket...");

	    if (listener) 
	    {
		static if (irpc_socket_debug) writefln("cerrando listener socket ");
		//listener.blocking(true);
		listener.shutdown(SocketShutdown.BOTH);
		static if (irpc_socket_debug) writefln("listener socket shutdown done");
		char[1024] buf;
		int read = listener.receive(buf);
		while (read > 0)
		{
		    writefln("received extra data in listener socket shutdown: %d bytes", read);
		    read = listener.receive(buf);
		}
		listener.close();
		
		delete listener;
	    }
	    if (sset) delete sset;
	    if (listenAddress) delete listenAddress;
	    static if (irpc_socket_debug) writefln("(done)");
	}
    }
    
    void reset_server()
    {
	close_server();
    }
    
    bool start_server()
    {
	assert(port < 65536);
	static if (irpc_socket_debug) writefln("creating listener socket:");
	reset_server();
        listener = new TcpSocket();
	sset = new SocketSet();
	assert(listener.isAlive);
        listenAddress = new InternetAddress(cast(ushort)port);
	listener.blocking = false;
	listener.bind(listenAddress);
	listener.listen(SERVER_ACCEPT_QUEUE);
	static if (irpc_socket_debug) writefln("(ok) listening on port %d.", port);
	static if (irpc_socket_debug) writefln("up to %d sockets can be managed.", sset.max());
	
	reader = new Thread( &thread_readloop,cast(void *)this);
	reader.start();
	
	writer = new Thread( &thread_writeloop,cast(void *)this);
	writer.start();
	return true;
    }
    
    /*
	Intenta aceptar una conexión entrante.
    */
    bool accept_connection()
    {
	Socket sn;
	try
	{
	    sn = listener.accept();
	    assert(sn.isAlive);
	    assert(listener.isAlive);
	    
	    if(icscks.length < sset.max() - RESERVED_CONNECTIONS)
	    {
		icscks ~= new irpcClientSocket(this,sn);
		static if (irpc_socket_debug) printf("Connection from %.*s established.\n", sn.remoteAddress().toString());
		alive_sockets++;
		static if (irpc_socket_debug) printf("\tTotal connections: %d (and %d dead waiting gc)\n", alive_sockets, dead_sockets);
		return true;
	    }
	    else
	    {
		sn.close();
		static if (irpc_socket_debug) printf("Rejected connection from %.*s; too many connections.\n", sn.remoteAddress().toString());
		assert(!sn.isAlive);
	    }
	}
	catch(Exception e)
	{
	    static if (irpc_socket_debug) printf("Error accepting: %.*s\n", e.toString());
	    if(sn)  sn.close();
	    return false;
	}
	static if (irpc_socket_debug) printf("Unexpected code exit!!\n");
	return false;
    }
    
    void closeAll() // un método que asegura cerrado rápido
    {
	exitReadLoop = true;
	
	try {reader.resume();} catch {}
	try {writer.resume();} catch {}
	foreach(irpcClientSocket ics; icscks) 
	{
	    if (ics) ics.close();
	}
	usleep(1000);
	try {reader.wait(100);} catch{}
	try {writer.wait(100);} catch{}
	if (listener.isAlive()) listener.close();
	// Probablemente, aunque el socket esté bloqueando, esto debería provocar un error por cierre.
    }
    
    int writeloop()
    {
	exitReadLoop = false;
	while(!exitReadLoop) //TODO: debería cambiarse a exitWriteLoop.
	{
	    int status = 0;
	    try {
	    status = process_write_queue();
	    } catch (Object o) {
		writefln("Unknown error in process_write_queue");
		writefln(o.toString());
		return 1;
	    }
	    if (status == 0) // No quedan datos para escribir
	    {
		writer.pause(); // Pausado hasta que hayan más eventos de escritura
	    }
	    if (status == 1) // Todos datos para escribir están a la espera.
	    {
		writer.yield(); // pausa breve para ver si se vacía la cola.
	    }
	
	}
	return 0;
    }
    
    int process_write_queue()
    {
	int empty = 0, waiting = 0, working = 0;
	
	foreach(irpcClientSocket ics; alive_socket_list) 
	{
	    int sent = ics.send();
	    if (sent == -1) empty ++;
	    if (sent == 0)  waiting ++;
	    if (sent > 0)  working ++;
	}
	if (working) return 2;
	if (waiting) return 1;
	return 0;
    }
    
    int readloop(int timeout_msec = 100)
    {
	exitReadLoop = false;
	while(!exitReadLoop)
	{
	    try {
	    process_read_events(timeout_msec);
	    } catch (Object o) {
		writefln("Unknown error in process_read_events");
		writefln(o.toString());
		return 1;
	    }
	}
	return 0;
    }
    
    void update_socketstats()
    {
	int dead_sockets = 0, alive_sockets = 0;
	irpcClientSocket[] aux_socket_list;
	
	foreach(irpcClientSocket ics; icscks) 
	{
	    if (ics.cSocket.isAlive()) 
	    {
		aux_socket_list~=ics;
		alive_sockets ++;
	    }
	    else dead_sockets ++;
	}
	
	alive_socket_list=aux_socket_list;
	
	socketlistGarbageCollector();
	
	if (this.dead_sockets!=dead_sockets || this.alive_sockets != alive_sockets)
	{
	    this.dead_sockets = dead_sockets;
	    this.alive_sockets = alive_sockets;
	    
	    static if (irpc_socket_debug) printf("\tTotal connections: %d (and %d dead waiting gc)\n", alive_sockets, dead_sockets);
	
	}
	
    }
    
    void socketlistGarbageCollector()
    {
	if (dead_sockets <= 0) return; 
        // garbage collector
	irpcClientSocket[] aux_icscks = icscks[];
	icscks.length = 0;
	foreach(irpcClientSocket ics; aux_icscks) 
	{
	    if (ics.cSocket.isAlive() || ics.recvQueue.getReadSz()>0) 
	    {
		icscks ~= ics;
	    }
	}
    }
    
    /*
	-1 : significa bloquear, timeout infinito.
	0 : significa no bloquear, timeout 0.
	> 0 : especifica el timeout exacto en milisegundos. (BUG: en gdc esto actúa como -1.)
    */
    
    int process_read_events(int timeout_msec = -1)
    {
	update_socketstats();
	sset.reset();
	sset.add(listener);
	foreach(irpcClientSocket ics; alive_socket_list) 
	{
	    sset.add(ics.cSocket);
	}
	int nEvents = 0;
	// writefln("%d sockets alive",  alive_sockets);
	if (timeout_msec<0) timeout_msec = 300 * 1000; // 5 min
	nEvents = Socket.select(sset, null, null, 1000*timeout_msec); 

	// Esto espera prácticamente hasta el infinito, aunque tenga timeout. :-(
	// cabe esperar que a los 10 minutos se produzca un timeout.
	// ** BUG ** con dmd el timeout se produce, con gdc no.
	// sset se ve modificado para contener solo los sockets con nuevos eventos.
	if (nEvents < 1) return nEvents;
	
	if(sset.isSet(listener)) //connection request
	{
	    accept_connection();
	    if (nEvents < 2) return nEvents;
	}
        
	foreach(irpcClientSocket ics; alive_socket_list) 
	{
            // if (!ics.cSocket.isAlive()) continue;
	    if (!sset.isSet(ics.cSocket)) continue;
            
	    ics.recv();
	}
	return nEvents;
    }
    
}
