#!/usr/bin/env python3
# coding: utf-8

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
import json
import configparser
from data import Data
from base import BaseJSONEncoder

READ_INTERVAL_SEC = 10
LOOP_INTERVAL = 5

def call_immediate():
    print('Sending Call Alert')
    time.sleep(1)
    band.send_alert(ALERT_TYPES.PHONE)

def msg_immediate():
    print('Sending Message Alert')
    time.sleep(1)
    band.send_alert(ALERT_TYPES.MESSAGE)

def detail_info():
    print('MiBand')
    print('Soft revision:',band.get_revision())
    print('Hardware revision:',band.get_hrdw_revision())
    print('Serial:',band.get_serial())
    print('Battery:', band.get_battery_info())
    print('Time:', band.get_current_time())
    print('Steps:', band.get_steps())
    raw_input('Press Enter to continue')

def custom_message():
    band.send_custom_alert(5)

def custom_call():
    # custom_call
    band.send_custom_alert(3)

def custom_missed_call():
    band.send_custom_alert(4)

def l(x):
    print('Realtime heart BPM:', x)

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
 #print(c_data)

'''
受信
'''
def startGetData( MAC_ADDR, datapool, getStartBin):
    #band = MiBand3(MAC_ADDR, debug=True, datapool=datapool)
    #band.setSecurityLevel(level = "high")
    #if band.initialize():
    #    print("Initialized...")
    #    band.disconnect()

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

    try:
        while True:
            if band.waitForNotifications(0.5) == False:
                break
    except KeyboardInterrupt:
        print("Catch Interrupt: disconnect")
    finally:
        # utils.dumpDataPool( band.datapool )
        band.disconnect()

'''
スリープ
'''
def sleepLoop():
    print("waiting...")
    time.sleep(LOOP_INTERVAL)
#     for i in range( LOOP_INTERVAL ):
#         time.sleep( 1 )
#         print( "wait "+str(i))

'''
データ受信
'''
def startRead( MAC_ADDR, lastDttm ):

    print('Attempting to connect to ', MAC_ADDR)

    for retry in range(5):
        status = 0
        print("getStartDttm:"+ str( lastDttm ) )
        lastDttmHexBin = utils.dttm2hexEndianBin( lastDttm )
        datapool = {"status":"" ,  "StartDttm":"", "LastDttm":"", "payload":[], "DeviceAddress":"" }
        try:
            # 受信
            startGetData( MAC_ADDR, datapool, lastDttmHexBin)
            status = datapool["status"]
            print( "ResultStatus:"+str( status ) )
        except:
            status = -1
            print( "ResultStatus:"+str( status ) )

        if( status == "100201" ):
            # ペイロード分割
            result = utils.splitDataPool( datapool )
            print("LastDttm in data pool:"+ str( lastDttm ) )
            return (lastDttm, result)
        else:
            # Retry
            sleepLoop()

'''
データ送信
'''
def sendData(url, addr, data):

    d = Data()
    d.DevEUI_uplink.DevAddr = getAddr(addr)
    d.DevEUI_uplink.Time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%dT%H:%M:%S%z")
    d.DevEUI_uplink.payload_hex = data
    body = json.dumps(d, cls = BaseJSONEncoder, sort_keys = True)

    try:
        headers = {
            'Content-Type': 'application/json',
        }
        print("send:\n" + body)

        req = urllib.request.Request(url, body.encode(), headers)
        with urllib.request.urlopen(req) as res:
            content = res.read()

        print("receive:\n" + content.decode('sjis'))

    except urllib.error.HTTPError as err:
        print("error: " + str(err.code) + " " + err.reason)
    except urllib.error.URLError as err:
        print("error: " +  err.reason)
    except (Error, Exception) as err:
        print("error: " + err)

'''
メイン処理
'''
if __name__ == '__main__':

    # 設定読み込み
    configParser = configparser.ConfigParser()
    configParser.read("config.ini")
    config = configParser["config"]

    # 転送URL
    HOST = config["host"]
    print("HOST = " + HOST)

    while True:
        try:

            # Read Device List
            devices = utils.getDeviceList()

            # Loop of Device List
            for deviceInfo in devices:
                # アドレス
                MAC_ADDR = deviceInfo[0]
    #             lastReadDttm = utils.getLastReadDttmByMACADDR( MAC_ADDR )
                dttm = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S")
                lastReadDttm = datetime.datetime.strptime( dttm, '%Y-%m-%d %H:%M:%S')
                print ("MAC_ADDR:"+ MAC_ADDR + " lastStartRead:"+str(lastReadDttm) )

                # 受信
                result = startRead( MAC_ADDR, lastReadDttm )
                lastDttm = result[0]
                print (" lastEndRead:"+str(lastDttm) )

                # 送信
                for data in result[1]:
                    sendData(HOST, MAC_ADDR, data)

                # 待ち
#                 sleepLoop()

            # Read Interval
#             time.sleep( READ_INTERVAL_SEC )
        except KeyboardInterrupt:
            print ( "Interrupt catch!!" )
            break
        except:
            print ( sys.exc_info() )
    sys.exit(0)