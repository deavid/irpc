module irpcchatter;

import std.stdio;
import irpcsocket;

class BaseChatter
{
    irpcClientSocket ics; // Parent al que está asociado.
    
    void process_incoming_message(string msg)   { }
}