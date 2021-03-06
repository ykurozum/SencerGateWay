import sys
from auth3 import MiBand3
from auth4 import MiBand4
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
import configparser
import logging.config


APPVERSION = '1.1'

# logging configuration
logging.config.fileConfig("logging.conf")
log = logging.getLogger("Receiver")
log.debug("!!!Receiver START!!!")

# Configuration
configParser = configparser.ConfigParser()
configParser.read("config.ini")
config = configParser["config"]

# MiBand3 key
AUTH_KEY = binascii.a2b_hex(config["authKey"].strip())
log.info("AUTH_KEY = {}".format(binascii.b2a_hex(AUTH_KEY)))

# reception period
DATA_PERIOD = int(config["dataPeriod"])
log.info("DATA_PERIOD = {}".format(DATA_PERIOD))

READ_INTERVAL = int(config["readInterval"])
log.info("READ_INTERVAL = {}".format(READ_INTERVAL))

LOOP_INTERVAL = int(config["loopInterval"])
log.info("LOOP_INTERVAL = {}".format(LOOP_INTERVAL))

RETRY_COUNT = int(config["retryCount"])
log.info("RETRY_COUNT = {}".format(RETRY_COUNT))

BEFORE_24H_MODE = config["before24HMode"]
log.info("BEFORE_24H_MODE = {}".format(BEFORE_24H_MODE))

CONNECT_TIMEOUT = int(config["connectTimeout"])
log.info("CONNECT_TIMEOUT = {}".format(CONNECT_TIMEOUT))

# MiBand version
VERSION3 = '3'
VERSION4 = '4'

# index of device file
IDX_ADDRESS = 0
IDX_LASTREAD = 1
IDX_LASTSEND = 2
IDX_COMMENT = 3
IDX_KEY = 4


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

'''
MiBand3
'''
def startGetData3( MAC_ADDR, key, datapool, getStartBin):
    #band = MiBand3(MAC_ADDR, debug=True, datapool=datapool)
    #band.setSecurityLevel(level = "high")
    #if band.initialize():
    #    print("Initialized...")
    #    band.disconnect()

    band = None

    band = MiBand3(MAC_ADDR, key, debug=True, datapool=datapool)
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

'''
MiBand4
'''
def startGetData4( MAC_ADDR, key, datapool, getStartBin):
    band = MiBand4(MAC_ADDR, key, debug=True, datapool=datapool, connect_timeout=CONNECT_TIMEOUT )
    band.setSecurityLevel(level = "medium")

    band.authenticate()

    dateandtime = band.readCharacteristic(0x002c)
    #time.sleep(0.24)
    band.writeCharacteristic(0x004e, "\x01\x00", False)
    band.writeCharacteristic(0x0061, "\x01\x00", False)
    band.writeCharacteristic(0x0060, "\x01\x00", False)
    band.writeCharacteristic(0x0060, "\x82\x00\x02", False)
    band.writeCharacteristic(0x0060, "\x83\x00\xf9\x03\xd8\x41\x1a\x7f\x61\xb5\x0b\x11\xcb\x45\x82\x89\x11\x66", False)
    band.writeCharacteristic(0x0061, "\x00\x00", False)
    band.writeCharacteristic(0x0036, "\x01\x00", False)
    band.writeCharacteristic(0x0035, "\x0c", False)
    band.writeCharacteristic(0x0036, "\x00\x00", False)
    band.writeCharacteristic(0x0036, "\x01\x00", False)
    band.writeCharacteristic(0x0035, "\x06\x17\x00\x65\x6e\x5f\x55\x53", False)
    band.writeCharacteristic(0x0036, "\x00\x00", False)
    band.writeCharacteristic(0x0036, "\x01\x00", False)
    band.writeCharacteristic(0x0035, "\x11", False)
    band.writeCharacteristic(0x0036, "\x00\x00", False)
    band.writeCharacteristic(0x0042, "\x01\x00", True)
    band.writeCharacteristic(0x0036, "\x01\x00", False)
    band.writeCharacteristic(0x0035, "\x0d", False)
    band.writeCharacteristic(0x0036, "\x00\x00", False)
    band.writeCharacteristic(0x004b, "\x01\x00", True)
    band.writeCharacteristic(0x005a, "\x01\x00", False)
    band.writeCharacteristic(0x004d, "\x00\xc3\x00\x21\x00\x00\x00\x00\x01", False)
    band.writeCharacteristic(0x003f, "\x01\x00", True)
    band.writeCharacteristic(0x0045, "\x01\x00", True)
    band.writeCharacteristic(0x003c, "\x01\x00", False)
    band.writeCharacteristic(0x0036, "\x01\x00", False)
    band.writeCharacteristic(0x0035, "\x06\x19\x00\x00", False)
    band.writeCharacteristic(0x0036, "\x00\x00", False)
    band.writeCharacteristic(0x003b, getStartBin, False)
    band.writeCharacteristic(0x003b, "\x02", False)
    while True:
        if band.waitForNotifications(0.5) == False:
            break
    band.disconnect()

def sleepLoop():
    # print( "wait for "+str(LOOP_INTERVAL) + "sec" ),
    sys.stdout.flush()
    for i in range( LOOP_INTERVAL ):
        time.sleep( 1 )
        # print( "."),
        sys.stdout.flush()
    # print( "")

#--------------------------------------------
def startRead( MAC_ADDR, devname, key, type, lastDttm ):

    for retry in xrange( RETRY_COUNT ):
        # print 'Attempting to connect to ', MAC_ADDR
        # log output
        if not devname:
            devname = "<Undefined>"
        log.info('Attempting to connect to NAME:'+ devname +' ADDR:' + MAC_ADDR + '. Read dttm from ' + str( lastDttm) )
        status = "-1"
        # print("getStartDttm:"+ str( lastDttm ) )
        lastDttmHexBin = utils.dttm2hexEndianBin( lastDttm )
        datapool = {"status":"" ,  "StartDttm":"", "LastDttm":"", "payload":[], "DeviceAddress":"" }
        try:
            if (type == VERSION3):
                # MiBand3
                startGetData3( MAC_ADDR, key, datapool, lastDttmHexBin)
            elif (type == VERSION4):
                # MiBand4
                startGetData4( MAC_ADDR, key, datapool, lastDttmHexBin)
            status = datapool["status"]
        except  Exception as e :
            # print ("X>except:------"  )
            # print ( e  )
            # print ("---------------"  )
             log.info( e )
#            log.exception('ExceptionCatch: %s', e)
        finally:
            pass

        log.info('Result status:'+ status )
        if( status == "100201" ):
            ( lastDttm, result ) = utils.splitDataPool( datapool )
            utils.insertDb( result )
            # print("LastDttm in data pool:"+ str( lastDttm ) )
            log.info( "LastDttm in data pool:"+ str( lastDttm ) )
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

            log.info('===================================================================' )
            MAC_ADDR = deviceInfo[IDX_ADDRESS]
            DEV_NAME = deviceInfo[IDX_COMMENT]

            try:

                lastReadDttm = utils.getLastReadDttmByMACADDR( MAC_ADDR )
                if ( BEFORE_24H_MODE ):
                    before24HDttm = datetime.datetime.now() - timedelta(hours = DATA_PERIOD)
                    if ( lastReadDttm < before24HDttm ):
                        strDttm = before24HDttm.strftime('%Y-%m-%d %H:%M:%S')
                        before24HDttm = datetime.datetime.strptime( strDttm, '%Y-%m-%d %H:%M:%S')
                        log.info( "(24H mode ON)Overwrite to read start dttm:"+ str(lastReadDttm) +" to "+ str(before24HDttm ) )
                        lastReadDttm = before24HDttm

                val = deviceInfo[IDX_KEY].strip()
                if (val == ''):
                    # MiBand3
                    lastDttm = startRead( MAC_ADDR, DEV_NAME, AUTH_KEY, VERSION3, lastReadDttm )
                else:
                    # MiBand4
                    key = binascii.a2b_hex(val)
                    lastDttm = startRead( MAC_ADDR, DEV_NAME, key, VERSION4, lastReadDttm )

                if ( lastDttm != None ):
                    utils.saveLastReadDttmByMACADDR( MAC_ADDR, lastDttm )
                # sleepLoop()
            except Exception as e:
                log.info( "Exception catch " + MAC_ADDR )
                log.info( e )
                # print( e )

        # Read Interval
        time.sleep( READ_INTERVAL )
    except KeyboardInterrupt:
        log.info( "KeyboardInterrupt catch!!" )
        break
    except Exception as e:
        log.info( "Exception catch" )
        log.info( e )
        # print( e )
sys.exit(0)
