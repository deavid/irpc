module messagequeue;

import std.stdio;
import std.c.time;
import std.gc;


class circularBuffer(TItem)
{
    
    const int MIN_SIZE = 1; // evitaría algún overlap ocasional?
    // private:
    TItem[] queue; // Cada una ocupa 16bytes. 128 son 2kb.
    int readcursor = 0;
    int writecursor = 0;
    int size = 0;
    int readsz = 0;
    int writesz = 0;
    int acc_read = 0;
    int acc_write = 0;
    
    public:
    this(int queueSize = 64) 
    {
	queue.length = queueSize;
	size = queueSize;
	writesz = size;
    }
    ~this() 
    {
	printStatus();
    }
    
    int getReadSz()
    {
	return readsz;
    }
    
    void waitForWriteSpace()
    {
	while (writesz<=MIN_SIZE*2) {
	    usleep(1000);
	}
    }
    
    bool putItem(in TItem item) // approx. 0.3us
    {
	if (writesz<=MIN_SIZE) 
	    return false;
	assert(writesz>MIN_SIZE);
	if (writecursor==size) writecursor-=size;
	assert(writecursor<size);
	addRoot(cast(void*)item);
	queue[writecursor]=item;
	writesz--;
	writecursor++;
	readsz++;
	acc_write++;
	return true;
    }
    
    bool getItem(out TItem item)
    {
	if (readsz<=0) return false; 
	if (readcursor==size) readcursor-=size;
	assert(readcursor<size);
	item = queue[readcursor];
	removeRoot(cast(void*)item);
	readcursor++;
	readsz--;
	writesz++;
	acc_read ++;
	return true;
    }
    void printStatus()
    {
	writefln("status for queue:");
	writefln(" - size: %d items. ", size);
	writefln(" - items waiting read: %d items. ", readsz);
	writefln(" - items available for write: %d items. ", writesz);
	writefln(" - write cursor at %d (%d,%d)", writecursor, acc_write % size,acc_write / size);
	writefln(" - read cursor at %d (%d,%d)", readcursor, acc_read % size,acc_read / size);
	writefln(" - queue length: %d ", queue.length);
	
    }
}

alias circularBuffer!(string) circularStringBuffer;

class messageQueue : circularStringBuffer 
{
    string partialWriteBuffer;
    string partialReadBuffer;

    /**
    * read es una función diseñada para la lectura parcial de datos.
    * todos los datos que se "leen" pasan a el partialReadBuffer, hasta 
    * que se confirme que han sido leidos. Posteriores llamadas a read
    * leerán siempre el mismo segmento de datos hasta que éste quede 
    * confirmado.
    * el valor del argumento maxsize indica la cantidad de bytes que
    * puede entregar la función como máximo absoluto.
    */
    
    char[] read(in int maxsize=1024)
    {
	char[] buf;
	while (partialReadBuffer.length < maxsize && readsz>0)
	{
	    string item;
	    if (!getItem(item)) break;
	    item~="\n";
	    partialReadBuffer~=item;
	}
	if (partialReadBuffer.length < maxsize )
	    buf = partialReadBuffer[]; // Es todo lo que había.
	else
	    buf = partialReadBuffer[0 .. maxsize]; // solo el paquete pedido.
	return buf;
    }
    
    void readACK(in int readed)
    {
	assert(partialReadBuffer.length >= readed);
	if (readed < partialReadBuffer.length)
	    partialReadBuffer = partialReadBuffer[readed .. partialReadBuffer.length];
	else
	    partialReadBuffer.length=0; // Si la lectura era completa;
	
    }
    
    bool write(in string buf)
    {
	int i;
	int lastSlice;
	
	for( i = 0; i<buf.length; i++ )
	{
	    if (buf[i] == 10) // Bajada de linea
	    {
		string toAppend;
		if (lastSlice==0)
		{
		    toAppend = partialWriteBuffer ~ buf[lastSlice .. i];
		    partialWriteBuffer="";
		} 
		else
		{
		    toAppend = buf[lastSlice .. i];
		}
		
		if (toAppend.length)
		{
		    waitForWriteSpace();
		    // Debe copiarse SIEMPRE el objeto, porque de lo contrario
		    // .. el original puede quedar reescrito.
		    putItem(toAppend.dup); 
		}
		
		lastSlice = i+1;
	    }
	}
	if (lastSlice < buf.length)
	{
	    partialWriteBuffer~=buf[lastSlice .. buf.length];
	}
	
	return true;
    }
    
    void printStatus()
    {
	super.printStatus();
 	writefln(" - partialWriteBuffer: %s ", partialWriteBuffer);
    }
}