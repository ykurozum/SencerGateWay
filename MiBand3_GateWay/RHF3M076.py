#!/usr/bin/env python3
# coding: utf-8

import serial
import re
import time
from logging import getLogger

# Class for RHF3M076
class RHF3M076:

    # Constructor
    def __init__(self, port='/dev/ttyACM0', baud=9600, timeout=0.1):
    # def __init__(self, port='/dev/ttyACM1', baud=9600, timeout=0.1):
    # def __init__(self, port='/dev/ttyACM2', baud=9600, timeout=0.1):
        print("!!!! Modem Initailzer IN")
        self._port = port
        self._baud = baud
        self._timeout = timeout
        self._crlf = '\r\n'
        self._logger = getLogger(type(self).__name__)
        self._open()

    # シリアルポートのOpen
    def _open(self):
        self._modem = serial.Serial()
        self._modem.port = self._port
        self._modem.baudrate = self._baud
        self._modem.timeout = self._timeout

        try:
            self._modem.open()
            self._modem.reset_input_buffer()
            return()
        except Exception as e:
            self._logger.error('Serial port open failed.')
            raise(e)

    # シリアルポートに送信
    def _write(self, cmd):
        try:
            cmd = cmd + self._crlf
            ret = self._modem.write(cmd.encode())
            return(ret)
        except Exception as e:
            print('ERROR: Send to serial port failed.')
            raise(e)

    # シリアルポートから受信(送信結果)
    def _read(self):
        len = self._waitResponse()
        ret = self._modem.readline().decode().replace(self._crlf, '')
        return(ret)

    def _waitResponse(self):
        while self._modem.inWaiting() == 0:
            time.sleep(0.1)
        return(self._modem.inWaiting())

    # Payload送信処理
    def sendPayload(self, Payload):
        # コマンド設定
        cmd = 'AT+CMSGHEX="' + Payload + '"'
        print( "SEND COMMAND:"+ cmd )
        self._write(cmd)
        len = self._waitResponse()
        ack = True
        # 応答結果判定
        #while True:
        #    line = self._read()
        #    if line == '+CMSGHEX: Done': break
        #    if line == '+CMSGHEX: ACK Received':
        #        ack = True
        return(ack)

    # Destructor
    # シリアルポートのclose
    def __del__(self):
        print("!!!!   Modem Destractor IN")
        self._modem.close()
