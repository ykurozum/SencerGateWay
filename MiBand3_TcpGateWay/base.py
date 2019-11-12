'''
Created on 2019/11/01

@author: myagi
'''
import sys
import json

'''
JSONシリアライズ対応の基本クラス
'''
class Base(object):

    '''
    Constructor
    '''
    def __init__(self):
        pass

    # jsonからシリアライズ
    def Serialize(self, argJsonData) :

        jsonData = argJsonData
        if isinstance(argJsonData, basestring ) :
            jsonData = json.loads(argJsonData)

        for key in self.__dict__.keys():
            if isinstance(getattr(self,key), Base ) or getattr(self,key) == None :
                valclass = getattr(self,key)
                if valclass == None :
                    valclass = getattr(sys.modules["Classes.DataPDO"],key)()

                valclass.Serialize(jsonData[key])
                setattr(self,key, valclass)

            elif isinstance(getattr(self,key), int ) :
                setattr(self,key, int(jsonData[key]))
            else :
                setattr(self,key, jsonData[key])

    # Mapを作成
    def toDictionary(self):
        jsonDict = {}
        for key in self.__dict__.keys():
            attr = getattr(self,key)
            if isinstance(attr, Base ) :
                jsonDict.update({key : attr.toDictionary()})
            else :
                jsonDict.update({key : attr})
        return jsonDict

'''
Baseを継承したクラスのオブジェクトをJSONにする
'''
class BaseJSONEncoder(json.JSONEncoder):

    # オーバーライド
    def default(self, obj):
        if isinstance(obj, Base):
            return obj.toDictionary()
        return json.JSONEncoder.default(self, obj)

