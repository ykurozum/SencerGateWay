import sys
import utils
import time
import datetime
from datetime import timedelta
from RHF3M076 import RHF3M076


SEND_INTERVAL = 10
ONEPKT_SIZE = 3
COM_PORT_NO = 0
PORTMAX = 100
PORT_ADDR =  "/dev/ttyACM"

def sendPayload( target, getStart ):
    global COM_PORT_NO
    try:
        portttyStr = PORT_ADDR + str(COM_PORT_NO)
        print( "Try open port is:"+portttyStr )

        result = utils.selectDb( target.replace(":","") , getStart)
        print( " DEV:"+ target + "  count:"+ str( len( result ) ) )
        cur = 0
        # loop for result of select data
        while ( cur < len( result ) ):
            modem = RHF3M076(port=portttyStr )
            pkt = ''
            lastDttmStr = ''
            for idx in range( 0, ONEPKT_SIZE ):
                if( cur >= len( result ) ) :
                    break
                one = result[cur]
                pkt = pkt + one[2]
                cur = cur + 1
                print ( "DevAddr:"+one[0] + " Dttm:" + one[1] + " Payload:" + one[2] )
                lastDttmStr = one[1]
            modem.sendPayload( pkt )
            print ( "send done:"+ pkt )
            pkt = ''
            getStart = datetime.datetime.strptime(lastDttmStr, '%Y-%m-%d %H:%M:%S')
            utils.saveLastSendDttmByMACADDR( target, getStart)
            modem = None
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
            # Read Device List
            devices = utils.getDeviceList()
            # Loop of Device List
            for deviceInfo in devices:
                MAC_ADDR = deviceInfo[0]
                lastSendDttm = utils.getLastSendDttmByMACADDR( MAC_ADDR )
                print ("MAC_ADDR:"+ MAC_ADDR + " lastSend:"+str(lastSendDttm) )
                lastDttm = sendPayload( MAC_ADDR, lastSendDttm )
                print (" lastEndRead:"+str(lastDttm) )
    
        except KeyboardInterrupt:
            print ( "Interrupt catch!!" )
            break
        except:
            print ( sys.exc_info() )
    sys.exit(0)

main()
