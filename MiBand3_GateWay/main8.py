import sys
from auth2 import MiBand3
from cursesmenu import *
from cursesmenu.items import *
from constants import ALERT_TYPES
from bluepy.btle import Peripheral
import time
import os
import binascii
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
MAC_ADDR = sys.argv[1]
print 'Attempting to connect to ', MAC_ADDR

def updateFirmware():
    fileName = raw_input('Enter the file Name with Extension\n')
    band.dfuUpdate(fileName)

#def handleNotification(self, cHandle, data):
 #if cHandle == 0x0041: 
  #c_data = binascii.b2a_hex(data)
 #print c_data

band = MiBand3(MAC_ADDR, debug=True)
band.setSecurityLevel(level = "high")

# Authenticate the MiBand
if len(sys.argv) > 2:
    if band.initialize():
        print("Initialized...")
    band.disconnect()
    sys.exit(0)
else:
    band.authenticate()

    #band.getServices()
    #band.getCharacteristics()
    #band.getDescriptors()
    #while True:
    #    if band.waitForNotifications(5.0):
    #        continue

    #Mi Band 3の時刻の取得
    dateandtime = band.readCharacteristic(0x002f)
    cdateandtime = binascii.b2a_hex(dateandtime)
    print( "Date and Time: %s" % cdateandtime )    
    band.writeCharacteristic(0x0051, "\x01\x00", False)
    #sleepを入れると100204の確率が下がる
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
    #前回取得したデータの前回取得したデータの最後のデータの時刻の次の分からのデータを取得する
    band.writeCharacteristic(0x003e, "\x01\x01\xe3\x07\x07\x1e\x12\x00\x00\x24", False)
    band.writeCharacteristic(0x003e, "\x02", False)

    while True:
        if band.waitForNotifications(0.5):
            continue
            #band.disconnect()
            sys.exit(0)
