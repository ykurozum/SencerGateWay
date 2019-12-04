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

def sendPayload( target, getStart , host, sendInterval):
    # global COM_PORT_NO
    try:
        #portttyStr = PORT_ADDR + str(COM_PORT_NO)
        #print( "Try open port is:"+portttyStr )

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

            sendData(host, one[0], one[1], pkt)
            cur = cur + 1
            lastDttmStr = one[1]
            print ( "send done:")
            pkt = ''
            getStart = datetime.datetime.strptime(lastDttmStr, '%Y-%m-%d %H:%M:%S')
            utils.saveLastSendDttmByMACADDR( target, getStart)
            print ( "Going to sleep...Zzzzzz ("+ str(sendInterval) +")sec" )
            time.sleep( sendInterval )

    except Exception as e:
        print( e )
        #if ( COM_PORT_NO < PORTMAX ):
        #  COM_PORT_NO = COM_PORT_NO + 1
        #else:
        #  COM_PORT_NO = 0
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

            SEND_INERVAL = int(config["sendInterval"])
            print("SEND_INERVAL = %d" % SEND_INERVAL)

            PAR_DEVICE_INTERVAL = int(config["deviceInterval"])
            print("PAR_DEVICE_INTERVAL = %d" % PAR_DEVICE_INTERVAL)

            # Read Device List
            devices = utils.getDeviceList()
            # Loop of Device List
            for deviceInfo in devices:
                MAC_ADDR = deviceInfo[0]
                lastSendDttm = utils.getLastSendDttmByMACADDR( MAC_ADDR )
                print ("MAC_ADDR:"+ MAC_ADDR + " lastSend:"+str(lastSendDttm) )
                lastDttm = sendPayload( MAC_ADDR, lastSendDttm, HOST, SEND_INERVAL )
                print (" lastEndRead:"+str(lastDttm) )
                print ( "Going to next device. just sleep...Zzzzzz ("+ str( PAR_DEVICE_INTERVAL ) +")sec" )
                time.sleep( PAR_DEVICE_INTERVAL )

        except KeyboardInterrupt:
            print ( "Interrupt catch!!" )
            break
        except:
            print ( sys.exc_info() )
    sys.exit(0)

main()
