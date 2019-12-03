#!/bin/bash
DAYS=14
LOGDIR=/home/pi/py/miband_tcp/log

find $LOGDIR -mtime +$DAYS -a -type f -exec rm -f {} \;
exit 0
