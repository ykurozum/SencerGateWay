import os
import re
import binascii
import datetime
from datetime import timedelta
import sqlite3
import time
import struct
import csv

DEVICE_FILE = 'devices.csv'
DB_FILE = 'midata.db'

# set environment depend path parameter
RUN_HOME = os.environ.get("MI_HOME")
if RUN_HOME != None :
    RUN_HOME = re.sub( "/$", "", RUN_HOME)
    DEVICE_FILE = RUN_HOME + "/"+ DEVICE_FILE 
    DB_FILE = RUN_HOME + "/"+ DB_FILE

print( "DeviceFile is :" +   DEVICE_FILE )
print( "sqlite DB file:" +   DB_FILE  )

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

def splitDataPool( datapool ):
    resultDataPool = []
    startDttm = datapool["StartDttm"]
    dataDttm = startDttm
    # print( "Split in startDttm:"+ str( dataDttm ))
    num = 0
    for payloadHex in datapool["payload"]:
        payload = payloadHex[2:]
        splitedList = [payload[i: i+8] for i in range(0, len(payload), 8)]
        for onePayload in splitedList:
            hexDttm = dttm2hexStr( dataDttm )[:-2]
            devAddr = datapool["DeviceAddress"]
            hexPayload = devAddr + hexDttm + onePayload
            # print ( ">>>" + devAddr + ":" + hexDttm + ":" + onePayload + "<<<")
            resultDataPool.append( (devAddr, dataDttm, hexPayload) );
            dataDttm = dataDttm + timedelta(minutes=1) 
            num = num + 1
    # print( "Split count:"+ str( num ))
    # print( "Split out lastDttm:"+ str( dataDttm ))
    return ( dataDttm , resultDataPool )

def create_table( conn, cur):
    cur.execute("CREATE TABLE IF NOT EXISTS mi_payload(devaddr text, dttm datetime, payload text) ")
    cur.execute("CREATE TABLE IF NOT EXISTS mi_data( devaddr text, loadedDttm datetime, sentDttm datetime) ")

def initDb():
    dbname = DB_FILE
    conn = sqlite3.connect( dbname, isolation_level='EXCLUSIVE' )
    cursor = conn.cursor()
    create_table(conn, cursor)
    return ( conn, cursor)

#----
def insertDb( insertData ):
    # print( "InsertData in ")
    try:
        ( conn, cur) = initDb()
        ret = cur.executemany("INSERT INTO mi_payload(devaddr, dttm, payload) values (?,?,?)" , insertData )
        conn.commit()
        #--
        #ret = cur.execute("SELECT * FROM mi_payload;")
        #for row in ret.fetchall():
        #    print "'%s'" % row[0], row[1], type(row[1])
        #--
    except Exception, e:
        # print e
        conn.rollback()
    finally:
        conn.close()
    # print( "InsertData out")
    
def selectDb( DevAddr, StartDttm ):
    result = []
    try:
        ( conn, cur) = initDb()
        query = "SELECT * FROM mi_payload where devaddr = '"+ DevAddr + "' AND dttm > '" +str(StartDttm)+ "' order by dttm;"
        # print ( query )
        ret = cur.execute( query )
        for row in ret.fetchall():
            result.append( (row[0], row[1], row[2] ) )
        #--
    except Exception, e:
        # print e
        if conn: conn.rollback()
    finally:
        if conn: conn.close()
    return result

def deleteDb( DevAddr, LastDttm ):
    result = []
    try:
        ( conn, cur) = initDb()
        ret = cur.execute("DELETE FROM mi_payload where devaddr = '"+ DevAddr + "' AND dttm <= '"+LastDttm+"';")
        conn.commit()
    except Exception, e:
        # print e
        if conn: conn.rollback()
    finally:
        if conn: conn.close()
    return result

def cmdDb( cmd ):
    result = []
    try:
        ( conn, cur) = initDb()
        ret = cur.execute( cmd )
        for row in ret.fetchall():
            # result.append( (row[0], row[1], row[2] ) )
            result.append( row )
        conn.commit()
    except Exception, e:
        # print e
        if conn: conn.rollback()
    finally:
        if conn: conn.close()
    return result

def infoDb():
    # print( "++++++++++++++++" )
    try:
        ( conn, cur) = initDb()
        query = "select name from sqlite_master where type='table';"
        ret = cur.execute( query )
        tbls = []
        for row in ret.fetchall():
            tbls.append( row[0] )
        # conn.commit()

        for tbl in tbls:
            print( "Table:" + tbl )
            query = "PRAGMA table_info('"+tbl+"');"
            ret = cur.execute( query )
            for row in ret.fetchall():
                print( "      :" + str(row[0]) + " " + row[1] +" "+ row[2])


    except Exception, e:
        print e
        # if conn: conn.rollback()
    finally:
        if conn: conn.close()
    return 

 
# getDeviceList
def getDeviceList():
    devFile = open( DEVICE_FILE )
    reader = csv.reader( devFile )
    devices = []
    for row in reader:
        # read device list
        if row[0].startswith( '#' ) == False:
            devices.append( row )
    devFile.close()
    return devices

# last read dttm from CSV
def getLastReadDttmByMACADDR( MAC_ADDR ):
    dttm = getLastDttmByMACADDR( MAC_ADDR, 1)
    return dttm

# last send dttm from CSV
def getLastSendDttmByMACADDR( MAC_ADDR ):
    dttm = getLastDttmByMACADDR( MAC_ADDR, 2)
    return dttm

# last dttm from CSV by colum
def getLastDttmByMACADDR( MAC_ADDR, idx ):
    devFile = open( DEVICE_FILE )
    devices = getDeviceList()
    lastDttm = None
    for deviceInfo in devices:
        if deviceInfo[0] == MAC_ADDR:
            lastStr = deviceInfo[idx]
            lastDttm = datetime.datetime.strptime( lastStr, '%Y-%m-%d %H:%M:%S')

    devFile.close( )
    return lastDttm

# update last read dttm to CSV
def saveLastReadDttmByMACADDR( MAC_ADDR, lastReadDttm ):
    # print( "---save---Dev:" + MAC_ADDR + " lastRead:" + str(lastReadDttm))
    saveLastDttmByMACADDR( MAC_ADDR, lastReadDttm, 1)

def saveLastSendDttmByMACADDR( MAC_ADDR, lastSendDttm ):
    # print( "===save===Dev:" + MAC_ADDR + " lastSend:" + str(lastSendDttm))
    saveLastDttmByMACADDR( MAC_ADDR, lastSendDttm, 2)

def saveLastDttmByMACADDR( MAC_ADDR, lastDttm, idx ):
    devices = getDeviceList()

    devFile = open( DEVICE_FILE, 'w' )
    writer = csv.writer( devFile )
    writer.writerow(['# DevAddr','LastRead','LastSend'])
    for row in devices:
        # read device list
        if row[0] == MAC_ADDR :
            row[idx] = str(lastDttm)
        writer.writerow( row )
    devFile.close()
    return devices

#while True:
#    result = selectDb()
#    #for one in result:
#    #    print ( one )
#    print ( "---DataSize is:"+str( len( result ) ) )
#    time.sleep(5)

