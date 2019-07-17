#!/bin/bash
DIR=/home/pi/py/modem/log
DAYS=14

find $DIR -mtime +$DAYS -a -type f -exec rm -f {} \;
exit 0
