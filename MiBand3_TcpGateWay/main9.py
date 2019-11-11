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
import urllib.request

LOOP_INTERVAL = 10

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
 #print(c_data

def startGetData( MAC_ADDR, datapool, getStartBin):
    band = MiBand3(MAC_ADDR, debug=True, datapool=datapool)
    band.setSecurityLevel(level = "high")

    # Authenticate the MiBand
    band.authenticate()

    # get Mi Band3 time
    dateandtime = band.readCharacteristic(0x002f)
    # utils.hexbin2dttm( dateandtime, 0)

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

def sleepLoop():
    for i in range( LOOP_INTERVAL ):
        time.sleep( 1 )
        print( "loop "+str(i))

'''
データ送信
'''
def sendData(url, addr, body):

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

#--------------------------------------------
if len(sys.argv) > 2:
    if band.initialize():
        print("Initialized...")
        band.disconnect()
else:
    MAC_ADDR = sys.argv[1]
    print('Attempting to connect to ', MAC_ADDR)

    # 転送URL
    HOST = "http://192.168.10.199:1880/test"

    lastDttm = datetime.datetime(2019, 8, 12, 0, 0, 0 )
    while True:
        status = 0
        try:
            print("getStartDttm:"+ str( lastDttm ) )
            lastDttmHexStr = utils.dttm2hexEndianStr0x( lastDttm )
            getStartDttmStr = ""
            datapool = {"status":"" ,  "StartDttm":"", "LastDttm":"", "payload":[], "DeviceAddress":"" }
            startGetData( MAC_ADDR, datapool, lastDttmHexStr)
            status = datapool["status"]
            print( "ResultStatus:"+status )
            if( status == "100201" ):
                bodies = utils.splitDataPool( datapool )
                 for body in bodies
                     sendData(HOST, body)
                print("step1)")
                print("LastDttm in data pool:"+ str( lastDttm ) )
                lastDttm = lastDttm + timedelta(minutes=1)
                print("step2)")
        except KeyboardInterrupt:
            print ( "Interrupt catch!!" )
            break
        except :
            print ( sys.exc_info() )
        if( status != "100204" ):
            sleepLoop()
    sys.exit(0)

