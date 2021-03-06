import sys
from auth3 import MiBand3
from cursesmenu import *
from cursesmenu.items import *
from constants import ALERT_TYPES
from bluepy.btle import Peripheral
import datetime
from datetime import timedelta
import time
import os
import binascii
import utils
import struct
import logging

READ_INTERVAL_SEC = 10
LOOP_INTERVAL = 5
RETRY_COUNT = 3
LOG_FORMAT = '%(asctime)-15s %(name)s (%(levelname)s) > %(message)s'
logging.basicConfig(format=LOG_FORMAT)
log = logging.getLogger("MiBand3")
log = logging.getLogger("Receiver")
log_level = logging.INFO
#log_level = logging.WARNING 
#log_level = logging.DEBUG
log.setLevel(log_level)


def call_immediate():
    print 'Sending Call Alert'
    time.sleep(1)
    band.send_alert(ALERT_TYPES.PHONE)

def msg_immediate():
    print 'Sending Message Alert'
    time.sleep(1)
    band.send_alert(ALERT_TYPES.MESSAGE)

def detail_info():
    print 'MiBand'
    print 'Soft revision:',band.get_revision()
    print 'Hardware revision:',band.get_hrdw_revision()
    print 'Serial:',band.get_serial()
    print 'Battery:', band.get_battery_info()
    print 'Time:', band.get_current_time()
    print 'Steps:', band.get_steps()
    raw_input('Press Enter to continue')

def custom_message():
    band.send_custom_alert(5)

def custom_call():
    # custom_call
    band.send_custom_alert(3)

def custom_missed_call():
    band.send_custom_alert(4)

def l(x):
    print 'Realtime heart BPM:', x

def heart_beat():
    band.start_raw_data_realtime(heart_measure_callback=l)
    raw_input('Press Enter to continue')

def change_date():
    band.change_date()

def updateFirmware():
    fileName = raw_input('Enter the file Name with Extension\n')
    band.dfuUpdate(fileName)

#def handleNotification(self, cHandle, data):
 #if cHandle == 0x0041: 
  #c_data = binascii.b2a_hex(data)
 #print c_data

def startGetData( MAC_ADDR, datapool, getStartBin):
    #band = MiBand3(MAC_ADDR, debug=True, datapool=datapool)
    #band.setSecurityLevel(level = "high")
    #if band.initialize():
    #    print("Initialized...")
    #    band.disconnect()

    band = None

    band = MiBand3(MAC_ADDR, debug=True, datapool=datapool)
    band.setSecurityLevel(level = "high")

    # Authenticate the MiBand
    band.authenticate()
    
    # get Mi Band3 time
    mibandtime = band.readCharacteristic(0x002f)
    midttm = utils.hexbin2dttm( mibandtime, 0)

    band.writeCharacteristic(0x0051, "\x01\x00", False)
    # insert sleep when low down 100204
    time.sleep(0.24) 
    band.writeCharacteristic(0x005b, "\x01\x00", False)
    band.writeCharacteristic(0x005a, "\x01\x00", False)
    band.writeCharacteristic(0x005b, "\x00\x00", False)
    band.writeCharacteristic(0x0039, "\x01\x00", False)
    band.writeCharacteristic(0x0038, "\x0c", False)
    band.writeCharacteristic(0x0039, "\x00\x00", False)
    band.writeCharacteristic(0x0039, "\x01\x00", False)
    band.writeCharacteristic(0x0038, "\x06\x17\x00\x65\x6e\x5f\x55\x53", False)
    band.writeCharacteristic(0x0039, "\x00\x00", False)
    band.writeCharacteristic(0x0039, "\x01\x00", False)
    band.writeCharacteristic(0x0038, "\x11", False)
    band.writeCharacteristic(0x0039, "\x00\x00", False)
    band.writeCharacteristic(0x0045, "\x01\x00", True)
    band.writeCharacteristic(0x004e, "\x01\x00", True)
    band.writeCharacteristic(0x0042, "\x01\x00", True)
    band.writeCharacteristic(0x0048, "\x01\x00", True)
    band.writeCharacteristic(0x003f, "\x01\x00", False)
    band.writeCharacteristic(0x0039, "\x01\x00", False)
    band.writeCharacteristic(0x0038, "\x06\x19\x00\x00", False)
    band.writeCharacteristic(0x0039, "\x00\x00", False)
    # 
    # getStr = "\x01\x01\xe3\x07\x07\x1e\x12\x00\x00\x24"
    # getStartBin = b'\x01\x01\xe3\x07\x07\x1e\x12\x00\x00\x24'
    band.writeCharacteristic(0x003e, getStartBin, False)
    band.writeCharacteristic(0x003e, "\x02", False)

    while True:
        if band.waitForNotifications(0.5) == False:
            break
    band.disconnect()
    log.info('connection disconnected(nomal process)')

def sleepLoop():
    # print( "wait for "+str(LOOP_INTERVAL) + "sec" ),
    sys.stdout.flush()
    for i in range( LOOP_INTERVAL ):
        time.sleep( 1 )
        # print( "."),
        sys.stdout.flush()
    # print( "")

#--------------------------------------------
def startRead( MAC_ADDR, lastDttm ):

    for retry in xrange( RETRY_COUNT ):
        # print 'Attempting to connect to ', MAC_ADDR
        log.info('===================================================================' )
        log.info('Attempting to connect to ' + MAC_ADDR + '. Read dttm from ' + str( lastDttm) )
        status = "-1"
        # print("getStartDttm:"+ str( lastDttm ) )
        lastDttmHexBin = utils.dttm2hexEndianBin( lastDttm )
        datapool = {"status":"" ,  "StartDttm":"", "LastDttm":"", "payload":[], "DeviceAddress":"" }
        try:
            startGetData( MAC_ADDR, datapool, lastDttmHexBin)
            status = datapool["status"]
        except  Exception as e :
            # print ("X>except:------"  )
            # print ( e  )
            # print ("---------------"  )
            log.info('ExceptionCatch------------------')
            log.info( e )
            log.info('--------------------------------')
        finally:
            pass

        log.info('Result status:'+ status )
        if( status == "100201" ):
            ( lastDttm, result ) = utils.splitDataPool( datapool )
            utils.insertDb( result )
            # print("LastDttm in data pool:"+ str( lastDttm ) )
            lastDttm = lastDttm + timedelta(minutes=1)
            log.info( str(len(result)) + " data readed" )
            return lastDttm
        elif( status == "100204" ):
            if( retry < (RETRY_COUNT-1) ):
                # Retry
                log.info('Going to retry('+str(retry)+')' )
                sleepLoop()
        else:
            break

#-------------------------
while True:
    try:
        # Read Device List
        devices = utils.getDeviceList()
        # Loop of Device List
        for deviceInfo in devices:
            MAC_ADDR = deviceInfo[0]
            lastReadDttm = utils.getLastReadDttmByMACADDR( MAC_ADDR )
            lastDttm = startRead( MAC_ADDR, lastReadDttm )
            if ( lastDttm != None ):
                utils.saveLastReadDttmByMACADDR( MAC_ADDR, lastDttm )
            sleepLoop()

        # Read Interval
        time.sleep( READ_INTERVAL_SEC )
    except KeyboardInterrupt:
        log.info( "KeyboardInterrupt catch!!" )
        break
    except Exception as e:
        log.info( "Exception catch" )
        log.info( e )
        # print( e )
sys.exit(0)
