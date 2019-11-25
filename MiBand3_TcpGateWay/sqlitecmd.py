#!/bin/python

import utils
import sys

while( True ):
    line = raw_input("sqlite>>")
    if ( line == 'quit' or line == 'exit' ):
        break
    print( "EXEC:"+line )
    result = utils.cmdDb( line )
    print( result )
    for row in result :
        print( row )
