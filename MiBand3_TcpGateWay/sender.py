import sys
import utils
import time
import datetime
from datetime import timedelta
import json
import configparser
import urllib2
from data import Data
from base import BaseJSONEncoder
import traceback


SEND_INTERVAL = 2
ONEPKT_SIZE = 3
COM_PORT_NO = 0
PORTMAX = 100
PORT_ADDR =  "/dev/ttyACM"

def getAddr(addr):
    temp = addr.replace(":","")
    return temp

def sendData(url, addr, dttm, data):

    d = Data()
    d.DevEUI_uplink.DevAddr = addr
    d.DevEUI_uplink.DevEUI = getAddr(addr)
    tmpdt = datetime.datetime.strptime(dttm, '%Y-%m-%d %H:%M:%S')
    d.DevEUI_uplink.Time = tmpdt.strftime("%Y-%m-%dT%H:%M:%S+0900")
    d.DevEUI_uplink.payload_hex = data
    body = json.dumps(d, cls = BaseJSONEncoder, sort_keys = True)

    headers = {
        'Content-Type': 'application/json',
    }
    print("send:\n" + body)
    req = urllib2.Request(url, body, headers)
    res = urllib2.urlopen(req)

    print("status: " + str(res.getcode()))

def sendPayload( target, getStart , host):
    global COM_PORT_NO
    try:
        portttyStr = PORT_ADDR + str(COM_PORT_NO)
        print( "Try open port is:"+portttyStr )

        result = utils.selectDb( target.replace(":","") , getStart)
        print( " DEV:"+ target + "  count:"+ str( len( result ) ) )
        cur = 0
        # loop for result of select data
        while ( cur < len( result ) ):
            lastDttmStr = ''
            one = result[cur]
            # dttmobj = datetime.datetime.strptime(one[1], '%Y-%m-%d %H:%M:%S')
            # hexdttm = utils.dttm2hexStr( dttmobj )
            pkt = one[2]
            print ( "send PKT:DevAddr:"+one[0] + " Dttm:" + one[1] + " Payload:" + one[2] )

#            for idx in range( 0, ONEPKT_SIZE ):
#                if( cur >= len( result ) ) :
#                    break
#                one = result[cur]
#                pkt = pkt + one[2]
#                cur = cur + 1
#                print ( "DevAddr:"+one[0] + " Dttm:" + one[1] + " Payload:" + one[2] )
#                lastDttmStr = one[1]
            sendData(host, one[0], one[1], pkt)
            cur = cur + 1
            lastDttmStr = one[1]
            print ( "send done:")
            pkt = ''
            getStart = datetime.datetime.strptime(lastDttmStr, '%Y-%m-%d %H:%M:%S')
            utils.saveLastSendDttmByMACADDR( target, getStart)
            print ( "Going to sleep...Zzzzzz ("+ str(SEND_INTERVAL) +")sec" )
            time.sleep( SEND_INTERVAL )

    except Exception as e:
        print( e )
        if ( COM_PORT_NO < PORTMAX ):
          COM_PORT_NO = COM_PORT_NO + 1
        else:
          COM_PORT_NO = 0
        #getStart = getStart + timedelta(minutes=1)
    return getStart


#-------------------------
def main():
    while True:
        try:
            configParser = configparser.ConfigParser()
            configParser.read("config.ini")
            config = configParser["config"]

            HOST = config["host"]
            print("HOST = " + HOST)

            # Read Device List
            devices = utils.getDeviceList()
            # Loop of Device List
            for deviceInfo in devices:
                MAC_ADDR = deviceInfo[0]
                lastSendDttm = utils.getLastSendDttmByMACADDR( MAC_ADDR )
                print ("MAC_ADDR:"+ MAC_ADDR + " lastSend:"+str(lastSendDttm) )
                lastDttm = sendPayload( MAC_ADDR, lastSendDttm, HOST )
                print (" lastEndRead:"+str(lastDttm) )

        except KeyboardInterrupt:
            print ( "Interrupt catch!!" )
            break
        except:
            print ( sys.exc_info() )
    sys.exit(0)

main()
