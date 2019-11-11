#!/usr/bin/env python3
# coding: utf-8

import datetime
import time
import json
import urllib.request
from bluepy import btle
from beacontools import BeaconScanner,IBeaconFilter
from logging import basicConfig, getLogger, DEBUG
from data import Data
from base import BaseJSONEncoder

# デバイスリスト
deviceList = {}

'''
対象UUIDのデバイスアドレス取得用のcallback
    bt_addr: デバイスアドレス
    rssi: 電波強度
'''
def callback(bt_addr, rssi, packet, additional_info):
    # リスト内に同一keyが存在するか
    if bt_addr in deviceList :
        # RSSIの比較
        if deviceList[bt_addr] < rssi:
             # RSSI更新
             deviceList[bt_addr] = rssi
    else:
         deviceList[bt_addr] = rssi

'''
データ取得
'''
def getData(device):

    # AD Type: Manufacture Specific
    ADT_TYPE = 0xFF

    return device.getValueText(ADT_TYPE)

'''
アドレス取得
'''
def getAddr(addr):
    # 結合文字削除
    temp = addr.replace(":","")
    # 下位6文字
    return temp[len(temp)-6:]

'''
ログ出力
'''
def log(logDirPath, message):
    logdate = datetime.datetime.today().strftime("%Y%m%d")
    f = open( logDirPath + logdate + '.log','a')
    f.write(message + '\n')
    f.close()

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
        log(LOG_DIR_PATH, "error: " + body)
    except urllib.error.URLError as err:
        print("error: " +  err.reason)
        log(LOG_DIR_PATH, "error: " + body)
    except (Error, Exception) as err:
        print("error: " + err)
        log(LOG_DIR_PATH, "error: " + body)

'''
メイン
'''
if __name__ == '__main__':

    # logディレクトリパス
    LOG_DIR_PATH = "/home/pi/py/log/"

    # 対象UUID
    UUID = "deac3f40-8290-11e5-b15c-0002a5d5c51b"

    # スキャン時間[秒]
    SCAN_TIME = 1

    # 転送URL
    URL = "http://192.168.10.199:1880/test"

    # 初期設定
    basicConfig(level=DEBUG)
    logger = getLogger(__name__)

    # デバイススキャンクラスを初期化
    # index=0 が /dev/hci0 に対応
    scanner = btle.Scanner(0)

    while True:

        logdate = datetime.datetime.today().strftime("%Y%m%d")

        # アドレス取得用スキャン
        # 対象UUIDのデバイスアドレス、RSSIを取得
        iBeaconScanner = BeaconScanner(callback,
        device_filter=IBeaconFilter(uuid=UUID))
        iBeaconScanner.start()
        time.sleep(SCAN_TIME)
        iBeaconScanner.stop()

        # スキャン結果が取得できなかった
        if len(deviceList) == 0:
           continue

        # データ取得用スキャン
        devices = scanner.scan(SCAN_TIME)

        for addr in deviceList.keys():

            for device in devices:

                if device.addr == addr:

                    # データ取得
                    data = getData(device)

                    # データ送信
                    sendData(URL, device.addr, data)
