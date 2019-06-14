#!/usr/bin/env python3
# coding: utf-8

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
getDataCount = 5

# 対象UUID
targetUuid = "deac3f40-8290-11e5-b15c-0002a5d5c51b"

# メイン処理
def main(count):
    # 初期設定
    #basicConfig(level=DEBUG)
    #logger = getLogger(__name__)

    # デバイスのスキャン:引数はスキャンする秒数
    devices = scanner.scan(1.0)

    # モデムの設定
    modem = RHF3M076()
    # 取得したデバイスに対して処理
    for device in devices:
        for addr in deviceList.keys():
            if device.addr == addr:
                # valueText=デバイスから取得したデータの値
                for (valueText) in device.getScanData():
                    # Manufactureデータの取得
                    if valueText[1] == 'Manufacturer' and len(valueText[2]) == 58:
                        # デバイスアドレス
                        devAddrRep = device.addr.replace(":","")
                        devAddr = devAddrRep[6:12]
                        # アドバタイズデータ
                        advertiseData = valueText[2]
                        dataList[addr].append(advertiseData)
                        
                        if count == getDataCount:
                            payloadList[addr] = getData.getPayload(devAddr,addr,dataList)
                            break
                    else:
                        continue
            else:
                continue
                #break

# 対象UUIDのデバイスアドレス取得用のcallback
def callback(bt_addr, rssi, packet, additional_info):
    # リスト内に同一keyが存在するか
    if bt_addr in deviceList :
        # RSSIの比較
        if deviceList[bt_addr] > rssi:
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

    # スキャン回数:初期値
    count = 0

    # モデムの設定
    modem = RHF3M076()

    # デバイススキャンクラスを初期化
    # index=0 が /dev/hci0 に対応
    scanner = btle.Scanner(0)

    # スキャン回数：初期値
    count = 0 

    while True:

        # デバイススキャン
        if sendCount == 0 and count == 0:
            print("list")
            # デバイススキャンクラスを初期化
            # index=0 が /dev/hci0 に対応
            scanner = btle.Scanner(0)

            # 対象UUIDのデバイスアドレス、RSSIを取得
            iBeaconScanner = BeaconScanner(callback,
            device_filter=IBeaconFilter(uuid=targetUuid))
            iBeaconScanner.start()
            time.sleep(1)
            iBeaconScanner.stop()

        # スキャン結果が取得できなかった
        if len(deviceList) == 0:
           sendCount = 0
           count = 0
           continue 
        
        # メイン処理実行
        main(count)
 
        # スキャン回数上限チェック
        if count < getDataCount:
            count = count + 1
        # 上限到達
        else:
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
                    logger.error('Payload 1-4user send failed:'+ firstPayload)
            # 5-8ユーザー分
            if len(secondPayload) > 0:
                if not modem.sendPayload(secondPayload):
                    logger.error('Payload 5-8user send failed:'+ secondPayload)

            # 送信回数判定
            if sendCount < 1:
                sendCount = sendCount + 1
            # 上限到達
            else:
                # 送信回数初期化
                sendCount = 0 
                # デバイスリスト初期化
                print("after:" + str(deviceList))
                deviceList={}

            # スキャン回数,受信データ初期化
            count = 0
            dataList = defaultdict(list)
