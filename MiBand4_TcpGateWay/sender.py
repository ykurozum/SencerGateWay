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
import logging

IDX_ADDRESS = 0
IDX_COMMENT = 3

# for logging
LOG_FORMAT = '%(asctime)-15s %(name)s (%(levelname)s) > %(message)s'
logging.basicConfig(format=LOG_FORMAT)
log = logging.getLogger("Sender")
log_level = logging.INFO
#log_level = logging.WARNING
#log_level = logging.DEBUG
log.setLevel(log_level)

configParser = configparser.ConfigParser()
configParser.read("config.ini")
config = configParser["config"]

HOST = config["host"]
# print("HOST = {}".format(HOST))
log.info("HOST = {}".format(HOST))

SEND_TIMEOUT = config["sendTimeout"]
log.info("SEND_TIMEOUT = {}".format(SEND_TIMEOUT))


SEND_INERVAL = float(config["sendInterval"])
# print("SEND_INERVAL = {}".format(SEND_INERVAL))
log.info("SEND_INERVAL = {}".format(SEND_INERVAL))

PAR_DEVICE_INTERVAL = float(config["deviceInterval"])
# print("PAR_DEVICE_INTERVAL = {}".format(PAR_DEVICE_INTERVAL))
log.info("PAR_DEVICE_INTERVAL = {}".format(PAR_DEVICE_INTERVAL))

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
    # print("send:\n" + body)
    req = urllib2.Request(url, body, headers )
    # for debug
    startTime = time.time()
    log.debug('url open start: data time:' + d.DevEUI_uplink.Time)
    res = urllib2.urlopen(req, timeout= float(SEND_TIMEOUT) )

    # for debug
    elapsed_time = time.time() - startTime
    log.debug('url open done: Elapsed time:%s(sec)', elapsed_time)

    # print("status: " + str(res.getcode()))

def sendPayload( target, devname, getStart , host):
    # global COM_PORT_NO
    result = []
    # log output
    if not devname:
        devname = "<Undefined>"

    try:
        #portttyStr = PORT_ADDR + str(COM_PORT_NO)
        #print( "Try open port is:"+portttyStr )

        # for debug
        log.debug( "Start selecting target device(%s) data to send from DB. from dttm:%s", devname, getStart)

        result = utils.selectDb( target.replace(":","") , getStart)
        # print( " DEV:"+ target + "  count:"+ str( len( result ) ) )
        cur = 0

        # for debug
        log.debug( "End select. result count is %s", len(result) )

        if( len( result ) > 0 ):
            log.info( "Start sending.... DevName:"+devname+" DevAddr:"+ target + " StartDttm:" + str( getStart ) + " DataCount:" + str( len( result)) )

        # loop for result of select data
        while ( cur < len( result ) ):
            lastDttmStr = ''
            one = result[cur]
            # dttmobj = datetime.datetime.strptime(one[1], '%Y-%m-%d %H:%M:%S')
            # hexdttm = utils.dttm2hexStr( dttmobj )
            pkt = one[2]
            # print ( "send PKT:DevAddr:"+one[0] + " Dttm:" + one[1] + " Payload:" + one[2] )

            sendData(host, one[0], one[1], pkt)
            cur = cur + 1
            lastDttmStr = one[1]
            # print ( "send done:")
            pkt = ''
            getStart = datetime.datetime.strptime(lastDttmStr, '%Y-%m-%d %H:%M:%S')
            # print ( "Going to sleep...Zzzzzz ("+ str(SEND_INERVAL) +")sec" )
            time.sleep( SEND_INERVAL )

    except Exception as e:
        # print( e )
        log.error('ExceptionCatch(5):%s', e)

    finally:
        # log output
        if( len( result ) > 0 ):
            log.info( "Send completely.  DevAddr:"+ target + " EndDttm  :" + str( getStart ) + " SentDataCount:" + str( cur ) )
            # for debug
            log.debug('start result save to device.csv')
            # result save
            utils.saveLastSendDttmByMACADDR( target, getStart)
            # for debug
            log.debug('save done')
        else:
            log.debug( "No data Send. There is no transmission target.")

    return getStart


#-------------------------
def main():
    while True:
        try:
            # Read Device List
            devices = utils.getDeviceList()
            # Loop of Device List
            for deviceInfo in devices:
                MAC_ADDR = deviceInfo[IDX_ADDRESS]
                DEV_NAME = deviceInfo[IDX_COMMENT]

                try:
                    lastSendDttm = utils.getLastSendDttmByMACADDR( MAC_ADDR )
                    # print ("MAC_ADDR:"+ MAC_ADDR + " lastSend:"+str(lastSendDttm) )
                    lastDttm = sendPayload( MAC_ADDR, DEV_NAME, lastSendDttm, HOST )
                    # print (" lastEndRead:"+str(lastDttm) )
                    # print ( "Going to next device. just sleep...Zzzzzz ("+ str( PAR_DEVICE_INTERVAL ) +")sec" )
                    time.sleep( PAR_DEVICE_INTERVAL )
                except Exception as e:
                    # print ( sys.exc_info() )
                    log.info('ExceptionCatch(2): '+ MAC_ADDR)
                    log.info(e)

        except KeyboardInterrupt:
            # print ( "Interrupt catch!!" )
            log.error("KeybordInterrupt(1) catch!!")
            break
        except:
            # print ( sys.exc_info() )
            log.exception('ExceptionCatch(2):')

    sys.exit(0)

main()
