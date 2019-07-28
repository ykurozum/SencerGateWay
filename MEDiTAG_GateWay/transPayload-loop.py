#!/usr/bin/env python3
# coding: utf-8

import datetime
import time
import os
from collections import defaultdict
from getData import getData
from bluepy import btle
from RHF3M076 import RHF3M076
from beacontools import BeaconScanner,IBeaconFilter
from logging import basicConfig, getLogger, DEBUG

# デバイスリスト
deviceList = {}

# 受信データリスト
dataList = defaultdict(list)

# payloadリスト
payloadList ={}

# データ取得回数
getDataCount = 20
#getDataCount = 10

# スキャン時間
scantime = 1.0

# スキャン回数初期値
initCount = 1

# 対象UUID
targetUuid = "deac3f40-8290-11e5-b15c-0002a5d5c51b"

# logディレクトリパス
logDirPath = "/home/pi/py/modem/log/" 

# メイン処理
def main(count):
    # 初期設定
    #basicConfig(level=DEBUG)
    #logger = getLogger(__name__)

    # デバイスのスキャン:引数はスキャンする秒数
    devices = scanner.scan(scantime)

    # モデムの設定
    modem = RHF3M076()
    # 取得したデバイスに対して処理
    #for device in devices:
    # 対象UUIDのリスト分Loop
    for addr in deviceList.keys():
        # データ取得したデバイス分Loop
        for device in devices:
            if device.addr == addr:
                # valueText=デバイスから取得したデータの値
                for (valueText) in device.getScanData():
                    # Manufactureデータの取得
                    if valueText[1] == 'Manufacturer' and len(valueText[2]) == 58:
                        # アドバタイズデータ
                        advertiseData = valueText[2]
                        dataList[addr].append(advertiseData)
                    else:
                        continue
        # 上限到達
        if  count == getDataCount:
            devAddrRep = addr.replace(":","")
            devAddr = devAddrRep[6:12]
            payload = getData.getPayload(devAddr,addr,dataList)

            if len(payload) > 0:
                payloadList[addr] = payload
              
            else:
                continue
                #break

# 対象UUIDのデバイスアドレス取得用のcallback
def callback(bt_addr, rssi, packet, additional_info):
    # リスト内に同一keyが存在するか
    if bt_addr in deviceList :
        # RSSIの比較
        if deviceList[bt_addr] < rssi:
             # RSSI更新
             deviceList[bt_addr] = rssi
    else:
         deviceList[bt_addr] = rssi

if __name__ == '__main__':

    # 初期設定
    basicConfig(level=DEBUG)
    logger = getLogger(__name__)

    # 送信回数:初期値
    sendCount = 0

    # モデムの設定
    modem = RHF3M076()

    # デバイススキャンクラスを初期化
    # index=0 が /dev/hci0 に対応
    scanner = btle.Scanner(0)

    # スキャン回数：初期値
    count = initCount

    while True:

        logdate = datetime.datetime.today().strftime("%Y%m%d")
        f = open( logDirPath + logdate + '.log','a')
        f.write('ackError:' + test)
        f.close()

        # デバイススキャン
        if sendCount == 0 and count == initCount:
            # デバイススキャンクラスを初期化
            # index=0 が /dev/hci0 に対応
            scanner = btle.Scanner(0)

            # 対象UUIDのデバイスアドレス、RSSIを取得
            iBeaconScanner = BeaconScanner(callback,
            device_filter=IBeaconFilter(uuid=targetUuid))
            iBeaconScanner.start()
            time.sleep(scantime)
            iBeaconScanner.stop()

        # スキャン結果が取得できなかった
        if len(deviceList) == 0:
           sendCount = 0
           count = initCount
           continue 
        
        # メイン処理実行
        main(count)
 
        # スキャン回数上限チェック
        if count < getDataCount:
            count = count + 1
        # 上限到達
        else:

            if len(payloadList) > 0:
                # RSSI強度でソート
                sortDeviceList = getData.sortDevice(deviceList)

                # payload送信
                # 1-4ユーザー分Payload作成
                firstPayload = getData.makePayload(sortDeviceList,payloadList,1)
                # 5-8ユーザー分Payload作成
                secondPayload = getData.makePayload(sortDeviceList,payloadList,2)

                # Payload送信
                # 1-4ユーザー分
                if len(firstPayload) > 0:
                    if not modem.sendPayload(firstPayload):
                        f = open( logDirPath + logdate + '.log','a')
                        f.write('ackError:' + firstPayload + '\n')
                        f.close()
                        #logger.error('Payload 1-4user send failed:'+ firstPayload)

                # 10秒間隔を空ける
                time.sleep(10)

                # 5-8ユーザー分
                if len(secondPayload) > 0:
                    if not modem.sendPayload(secondPayload):
                        f = open( logDirPath + logdate + '.log','a')
                        f.write('ackError:' + secondPayload + '\n')
                        f.close()
                        #logger.error('Payload 5-8user send failed:'+ secondPayload)

            # 送信回数判定
            if sendCount < 1:
                sendCount = sendCount + 1
            # 上限到達
            else:
                # 送信回数初期化
                sendCount = 0 
                # デバイスリスト初期化
                deviceList={}

            # スキャン回数,受信データ初期化
            count = initCount
            dataList = defaultdict(list)
