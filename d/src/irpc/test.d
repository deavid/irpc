import std.stdio;
import std.c.stdio;
import std.thread;
import std.c.time;
import std.string;
import std.regexp;
 
import irpcsocket;


bool terminate_asap = false;

version (linux) 
{
    import std.c.linux.linux;
    extern (C) typedef void (*sighandler_t)(int);
    extern (C) sighandler_t signal(int signal, sighandler_t handler);    
    
    extern (C) void sighandler(int sig) {
	    printf("signal %d caught...\n", sig);
	    terminate_asap = true;
    }    
}


/*int thread_readloop(void *sck)
{
    irpcSocket sckServer = cast(irpcSocket) sck;
    return sckServer.readloop();
}*/

int main(char[][]args)
{
    writefln("Hello from D!");
    version (linux) {
//	signal(SIGABRT, &sighandler);
//	signal(SIGTERM, &sighandler);
//	signal(SIGQUIT, &sighandler);
	signal(SIGINT, &sighandler);
    }    
    //writefln("size of string: %d", string.sizeof);
    /*
    messageQueue mQR = new messageQueue();
    int i;
    for (i=0;i<1000000;i++)
    {
	if (i % 23 == 0 )
	    mQR.write("\n");
	
	if (i < 100 || i % 13 > 0 )
	    mQR.write("test1");
	else
	{
	    string newitem;
	    if (mQR.getItem(newitem))
	    {
		if (i<200) writefln("> '%s'", newitem );
	    }
	}
	
	
    }
    mQR.printStatus();
    */
    
    // RET: >xD             true
    //      >ID   TAB  TAB  VALUE
    
    irpcSocket sckServer = new irpcSocket(10123);
    
    /*Thread reader = new Thread( &thread_readloop,cast(void *)sckServer);
    reader.start();*/
    while (sckServer.alive_sockets > 0 || !terminate_asap)
    {
	//sleep(1);
	usleep(1000);
	//usleep(100);
        foreach(irpcClientSocket ics; sckServer.icscks) 
        {
            while (ics.recvQueue.getReadSz())
            {
                string msg;
                ics.recvQueue.getItem(msg);
                /*writef("%s>", ics.remoteAddress);
                fwrite(cast(void*)msg,msg.length,1,stdout);
                writefln(">");*/
                auto m = std.regexp.search(msg, "^!call@([^\t]+)\t");
                if (m)
                {
		    string ID = m.match(1);
		    string ret = ">" ~ ID ~ "\t\ttrue";
		    // writefln("!>%s %s", m.match(0), m.match(1));
		    ics.sendMessage(ret);
                }
                
                
	    
            }
            if (terminate_asap)
            {
		ics.close();
            }
        }
    }
    sckServer.closeAll();
    delete sckServer;
    
    // sckServer.readloop();
    writefln("Program end.");
    //socket_listener2(10124);
    return 0; // 0 - means ok  .. -1 , 1 ... - means error.
}