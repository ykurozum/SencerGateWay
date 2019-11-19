# coding: utf-8

import binascii
import datetime
from datetime import timedelta
import csv

def hexbin2dttm( hexbin, sidx ):
    hex = binascii.b2a_hex( hexbin )
    yyStr  = str(hex)[sidx+2:sidx+4] + str(hex)[sidx:sidx+2]
    yy  = int( str(hex)[sidx+2:sidx+4] + str(hex)[sidx:sidx+2], 16 )
    mm  = int( str(hex)[sidx+4:sidx+6], 16)
    dd  = int( str(hex)[sidx+6:sidx+8], 16)
    hh  = int( str(hex)[sidx+8:sidx+10], 16)
    MM  = int( str(hex)[sidx+10:sidx+12], 16)
    ss  = int( str(hex)[sidx+12:sidx+14], 16)
    dttm = datetime.datetime( yy, mm, dd, hh, MM, ss, 0)
    return dttm

def dttm2hexStr( dttm ):
    yyyy = ( str( hex( dttm.year)   )[2:].zfill(4) )
    mm   = ( str( hex( dttm.month)  )[2:].zfill(2) )
    dd   = ( str( hex( dttm.day)    )[2:].zfill(2) )
    hh   = ( str( hex( dttm.hour)   )[2:].zfill(2) )
    MM   = ( str( hex( dttm.minute) )[2:].zfill(2) )
    ss   = ( str( hex( dttm.second) )[2:].zfill(2) )
    hexDttm = yyyy+mm+dd+hh+MM+ss
    return hexDttm

def dttm2hexEndianStr( dttm ):
    yyyyStr = str( hex( dttm.year) )[2:].zfill(4)
    yyyyEndian = yyyyStr[2:] + yyyyStr[:2]
    yyyy = yyyyEndian
    mm   = ( str( hex( dttm.month) )[2:].zfill(2) )
    dd   = ( str( hex( dttm.day) )[2:].zfill(2) )
    hh   = ( str( hex(dttm.hour) )[2:].zfill(2) )
    MM   = ( str( hex(dttm.minute) )[2:].zfill(2) )
    ss   = ( str( hex(dttm.second) )[2:].zfill(2) )
    hexDttm = yyyy+mm+dd+hh+MM+ss
    return hexDttm

def dttm2hexEndianBin( dttm ):
    hexStr = dttm2hexEndianStr( dttm )
    splitedHex = [hexStr[i: i+2] for i in range(0, len(hexStr), 2)]
    str0x = "0101"
    for one in splitedHex:
        str0x = str0x + one
    str0x = str0x + "24"
    b = binascii.unhexlify( str0x )
    return b

def dumpDataPool( datapool ):
    print str( datapool["StartDttm"] )
    for payload in datapool["payload"]:
        print payload

'''
受信データ分割
'''
def splitDataPool( datapool ):
    resultDataPool = []
    startDttm = datapool["StartDttm"]
    dataDttm = startDttm
    print( "Split in startDttm:"+ str( dataDttm ))
    num = 0
    for payloadHex in datapool["payload"]:
        payload = payloadHex[2:]
        splitedList = [payload[i: i+8] for i in range(0, len(payload), 8)]
        for onePayload in splitedList:
            hexDttm = dttm2hexStr( dataDttm )[:-2]
            devAddr = datapool["DeviceAddress"]
            resultDataPool.append( onePayload );
            dataDttm = dataDttm + timedelta(minutes=1)
            num = num + 1
    print( "Split count:"+ str( num ))
    print( "Split out lastDttm:"+ str( dataDttm ))
    return resultDataPool


'''
デバイスリスト読み込み'
'''
def getDeviceList(deviceFile):
    devFile = open( deviceFile )
    reader = csv.reader( devFile )
    devices = []
    for row in reader:
        # read device list
        if row[0].startswith( '#' ) == False:
            devices.append( row )
    devFile.close()
    return devices

