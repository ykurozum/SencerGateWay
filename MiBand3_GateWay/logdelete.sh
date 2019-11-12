#!/bin/bash
DAYS=14

find $LOGDIR -mtime +$DAYS -a -type f -exec rm -f {} \;
exit 0
