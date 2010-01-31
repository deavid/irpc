/* Sieve of Eratosthenes prime numbers */

import std.stdio;

bool[] flags;
 
int main()
{   
    int i, count, prime, k, iter;
    int total_iter = 1;
    int ini_length, prev_length;
    count = 0;
    flags.length=2*3*5*7;
    writefln("%d iterations", total_iter);
    
    for (iter = 1; iter <= total_iter; iter++)
    {	
	flags[prev_length .. flags.length - 1] = 1;
	for (i = prev_length; i < flags.length; i++)
	{   
	    if (flags[i])
	    {	
		prime = i + i + 3;
		k = i + prime;
		while (k < flags.length)
		{
		    flags[k] = 0;
		    k += prime;
		}
		writef("%d ", prime);

		count += 1;
	    }
	}
	
	writefln("\n%d primes", count);
	writefln("memory used %.2f kb", flags.length/1024.0);
	prev_length = flags.length;
	flags.length = prev_length * 2;
    }
    return 0;
}