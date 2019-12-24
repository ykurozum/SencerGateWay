#!/usr/bin/env python3
# coding: utf-8

import datetime
import time
import json
import urllib.request
from bluepy import btle
from beacontools import BeaconScanner,IBeaconFilter
from data import Data
from base import BaseJSONEncoder
import configparser
import traceback
import logging
import logging.config
from urllib.error import URLError

# for logging
logging.config.fileConfig("logging.conf")
log = logging.getLogger("TagGateWay")

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
    return temp

'''
データ送信
'''
def sendData(url, addr, data):

    d = Data()
    d.DevEUI_uplink.DevAddr = addr
    d.DevEUI_uplink.DevEUI = getAddr(addr)
    d.DevEUI_uplink.Time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%dT%H:%M:%S%z")
    d.DevEUI_uplink.payload_hex = data
    body = json.dumps(d, cls = BaseJSONEncoder, sort_keys = True)

    # POST
    headers = {
        'Content-Type': 'application/json',
    }
    # print("send:\n" + body)

    req = urllib.request.Request(url, body.encode(), headers)
    res = urllib.request.urlopen(req)
    # print("status: " + str(res.getcode()))

'''
メイン
'''
if __name__ == '__main__':
    # 初期設定
    log.debug("!!!Tag GateWay START!!!")

    # 設定読み込み
    configParser = configparser.ConfigParser()
    configParser.read("config.ini")
    config = configParser["config"]

    # 対象UUID
    UUID = config["uuid"]
    log.debug("UUID = " + UUID)

    # スキャン時間[秒]
    SCAN_TIME = config.getint("scan_time")
    log.info( "SCAN_TIME = " + str(SCAN_TIME))

    # スキャンInterval時間[秒]
    SCAN_INTERVAL_TIME = config.getint("scan_interval_time")
    log.info( "SCAN_INTERVAL_TIME = " + str(SCAN_INTERVAL_TIME))

    # 転送URL
    HOST = config["host"]
    log.info( "HOST = " + HOST)

    # 受信ペイロード長
    PAYLOAD_LEN = 58

    # デバイススキャンクラスを初期化
    # index=0 が /dev/hci0 に対応
    scanner = btle.Scanner(0)

    while True:

        try:
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
               log.debug("Device not found")
               continue

            # データ取得用スキャン
            devices = scanner.scan(SCAN_TIME)


            for addr in deviceList.keys():
                log.debug("Device:"+ addr )

                for device in devices:

                    if device.addr == addr:

                        # データ取得
                        data = getData(device)
                        if (len(data) == PAYLOAD_LEN):
                            # データ送信
                            sendData(HOST, device.addr, data)
                            log.debug( "Sent ADDR:" + device.addr + " DATA:" + data)

            time.sleep(SCAN_INTERVAL_TIME)
        except KeyboardInterrupt:
            log.info("Keybord Interrupt catch!")
            break
        except Exception as e:
            # print(traceback.format_exc())
            log.error("ExceptionCatch(1):"+str(e) + " URL:"+HOST)
        except URLError as e:
            log.error("ExceptionCatch(2):"+str(e))
        except e:
            log.error("ExceptionCatch(3):"+str(e))
