'''
Created on 2019/11/01

@author: myagi
'''
import sys
import json

class Base(object):

    '''
    Constructor
    '''
    def __init__(self):
        pass

    def toDictionary(self):
        jsonDict = {}
        for key in self.__dict__.keys():
            attr = getattr(self,key)
            if isinstance(attr, Base ) :
                jsonDict.update({key : attr.toDictionary()})
            else :
                jsonDict.update({key : attr})
        return jsonDict

class BaseJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Base):
            return obj.toDictionary()
        return json.JSONEncoder.default(self, obj)

