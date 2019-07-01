#!/usr/bin/env python3
# coding: utf-8

import statistics

class getData:

  # ペイロード取得
  def getPayload(devAddr,addr,dataList):

      #初期値
      payload = ""
      pulseMin = ""
      pulseMax = ""
      pulseMid = ""
      pulseMidList = []

      if addr in dataList :
          for advertiseData in dataList[addr]:

              # 脈拍:最小値
              pulseMin = getData.getPulseMin(advertiseData,pulseMin)
              # 脈拍:最大値
              pulseMax = getData.getPulseMax(advertiseData,pulseMax)
              # 脈拍:中央値(リスト)
              pulseMidList = getData.getPulseMid(advertiseData,pulseMidList)
              # 歩数
              stepCount = getData.getStepCount(advertiseData)
              # ストレス 
              stress = getData.getStress(advertiseData)
              # 状態表示
              status = getData.getStatus(advertiseData)
 
          # 脈拍:中央値算出
          print(pulseMidList)
          defPulseMid = statistics.median(pulseMidList)
          # 脈拍:中央値
          pulseMidStr = str(format(round(defPulseMid),'x'))
          if len(pulseMidStr) == 1:
              pulseMid = "0"+pulseMidStr
          else:
              pulseMid = pulseMidStr
          
          # 送信用Payload 
          payload=devAddr+pulseMid+pulseMax+pulseMin+stepCount+stress+status
      else :
          payload = ""

      return payload
 
  # 脈拍:最小値取得
  def getPulseMin(advertiseData,pulseMin):

      if pulseMin == "":
          pulseMin = advertiseData[4:6]
      else:
          newPulse = advertiseData[4:6]
          
          # 10進数で比較
          minPulse = int(pulseMin,16)
          pulse = int(newPulse,16)

          if minPulse > pulse:
             pulseMin = newPulse

      return pulseMin
  
  # 脈拍:最大値取得
  def getPulseMax(advertiseData,pulseMax):

      if pulseMax == "":
          pulseMax = advertiseData[4:6]
      else:
          newPulse = advertiseData[4:6]
          # 10進数で比較
          maxPulse = int(pulseMax,16)
          pulse = int(newPulse,16)

          if maxPulse < pulse:
             pulseMax = newPulse

      return pulseMax

  # 脈拍:中央値をリストに詰め込む
  def getPulseMid(advertiseData,pulseMid):

      newPulse = advertiseData[4:6]
      # 10進数を詰め込む
      pulse = int(newPulse,16)
      pulseMid.append(pulse)
      return pulseMid

  # 歩数取得
  def getStepCount(advertiseData):

      stepCount = advertiseData[6:10]
      return stepCount

  # ストレス取得
  def getStress(advertiseData):

      stress = advertiseData[18:20]
      return stress

  # 状態表示取得
  def getStatus (advertiseData):

      status = advertiseData[20:22]
      return status

  # デバイスリストのソート(RSSI強度順)
  def sortDevice(deviceList):

      targetDeviceList = []
      
      # ソート
      for k, v in sorted(deviceList.items(), key=lambda x: x[1]):
          targetDeviceList.append(k)

      return targetDeviceList
  
  # 送信用Payload作成
  def makePayload(sortDeviceList,payloadList,index):
      payload = ""

      # 1-4ユーザー分
      if index == 1:
          if len(sortDeviceList) > 0 and sortDeviceList[0] in payloadList:
              payload = payload + payloadList[sortDeviceList[0]]
          if len(sortDeviceList) > 1 and sortDeviceList[1] in payloadList: 
              payload = payload + payloadList[sortDeviceList[1]]
          if len(sortDeviceList) > 2 and sortDeviceList[2] in payloadList:
              payload = payload + payloadList[sortDeviceList[2]]
          if len(sortDeviceList) > 3 and sortDeviceList[3] in payloadList:
              payload = payload + payloadList[sortDeviceList[3]]

      # 5-8ユーザー分
      if index == 2:
          if len(sortDeviceList) > 4 and sortDeviceList[4] in payloadList:
              payload = payload + payloadList[sortDeviceList[4]]
          if len(sortDeviceList) > 5 and sortDeviceList[5] in payloadList:
              payload = payload + payloadList[sortDeviceList[5]]
          if len(sortDeviceList) > 6 and sortDeviceList[6] in payloadList:
              payload = payload + payloadList[sortDeviceList[6]]
          if len(sortDeviceList) > 7 and sortDeviceList[7] in payloadList:
              payload = payload + payloadList[sortDeviceList[7]]

      return payload
