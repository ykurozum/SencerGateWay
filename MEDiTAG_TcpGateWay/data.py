'''
Created on 2019/11/01

@author: myagi
'''
from base import Base

class air(Base):

    def __init__(self):
        '''
        Constructor
        '''
        self.pro = ""
        self.ver = ""

class Lrr(Base):

    def __init__(self):
        '''
        Constructor
        '''
        self.Lrrid = ""
        self.Chain = ""
        self.LrrRSSI = ""
        self.LrrSNR = ""
        self.LrrESP = ""

class DevEUI_uplink(Base):

    def __init__(self):
        '''
        Constructor
        '''
        self.Time = ""
        self.DevEUI = ""
        self.FPort = ""
        self.FCntUp = ""
        self.ADRbit = ""
        self.MType = ""
        self.FCntDn = ""
        self.payload_hex = ""
        self.mic_hex = ""
        self.Lrcid = ""
        self.LrrRSSI = ""
        self.LrrSNR = ""
        self.SpFact = ""
        self.SubBand = ""
        self.Channel = ""
        self.DevLrrCnt = ""
        self.Lrrid = ""
        self.Late = ""
        self.LrrLAT = ""
        self.LrrLON = ""
        self.Lrrs = {}
        self.CustomerID = ""
        self.CustomerData = {}
        self.ModelCfg = ""
        self.DevAddr = ""
        self.TxPower = 0
        self.NbTrans = 0


class Data(Base):
    '''
    送信データ
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.DevEUI_uplink = DevEUI_uplink()
