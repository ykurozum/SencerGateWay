import re
import binascii
import datetime
import sqlite3
import time
import struct
from data import Data
from base import BaseJSONEncoder
import json

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

def dttm2hexEndianStr0x( dttm ):
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
アドレス取得
'''
def getAddr(addr):
    # 結合文字削除
    temp = addr.replace(":","")
    # 下位6文字
    return temp[len(temp)-6:]

def splitDataPool( datapool ):
    resultDataPool = []
    dataDttm = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%dT%H:%M:%S%z")
    print( "Split in startDttm:"+ dataDttm)
    num = 0
    for payloadHex in datapool["payload"]:
        payload = payloadHex[2:]
        splitedList = [payload[i: i+8] for i in range(0, len(payload), 8)]
        for onePayload in splitedList:
            devAddr = datapool["DeviceAddress"]
            print ( ">>>" + devAddr + ":" + dataDttm + ":" + onePayload + "<<<")
            # 送信データ作成
            d = Data()
            d.DevEUI_uplink.DevAddr = getAddr(devAddr)
            d.DevEUI_uplink.Time = dataDttm
            d.DevEUI_uplink.payload_hex = onePayload
            body = json.dumps(d, cls = BaseJSONEncoder, sort_keys = True)
            resultDataPool.append(body);
            num = num + 1
    print( "Split count:"+ str( num ))
    print( "Split out lastDttm:"+ str( dataDttm ))
    return resultDataPool

def create_table( conn, cur):
    cur.execute("CREATE TABLE IF NOT EXISTS mi_payload(devaddr text, dttm datetime, payload text) ")
    cur.execute("CREATE TABLE IF NOT EXISTS mi_data( devaddr text, loadedDttm datetime, sentDttm datetime) ")

def initDb():
    dbname = "midata.db"
    conn = sqlite3.connect( dbname, isolation_level='EXCLUSIVE' )
    cursor = conn.cursor()
    create_table(conn, cursor)
    return ( conn, cursor)

#----
def insertDb( insertData ):
    print( "InsertData in ")
    try:
        ( conn, cur) = initDb()
        #ret = cur.executemany("INSERT INTO mi_payload(devaddr, dttm, payload) values (?,?,?)" ,
        #       [("e0f694b52142", datetime.datetime(2019,8,15,20,19,18), "e0f694b5214207e3080b1122501b0053" ),
        #        ("e0f694b52142", datetime.datetime.now(), "e0f694b5214207e3080b1122501b0054" )] )
        ret = cur.executemany("INSERT INTO mi_payload(devaddr, dttm, payload) values (?,?,?)" , insertData )
        conn.commit()
        #--
        #ret = cur.execute("SELECT * FROM mi_payload;")
        #for row in ret.fetchall():
        #    print "'%s'" % row[0], row[1], type(row[1])
        #--
    except Exception, e:
        print e
        conn.rollback()
    finally:
        conn.close()
    print( "InsertData out")

def selectDb( DevAddr ):
    result = []
    try:
        ( conn, cur) = initDb()
        ret = cur.execute("SELECT * FROM mi_payload where devaddr = '"+ DevAddr + "' order by dttm;")
        for row in ret.fetchall():
            result.append( (row[0], row[1], row[2] ) )
        #--
    except Exception, e:
        print e
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
        print e
        if conn: conn.rollback()
    finally:
        if conn: conn.close()
    return result

#while True:
#    result = selectDb()
#    #for one in result:
#    #    print ( one )
#    print ( "---DataSize is:"+str( len( result ) ) )
#    time.sleep(5)

