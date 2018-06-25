from ctypes import (
    Structure,
    cdll,
    c_bool,
    c_short,
    c_int,
    c_uint,
    c_int16,
    c_int32,
    c_char,
    c_byte,
    c_long,
    c_float,
    c_double,
    POINTER,
    CFUNCTYPE,
    c_ushort,
    c_ulong,
    c_char_p,
    c_uint32,
    byref,
    create_string_buffer
)

from ...ctools import _visa_enum as enum
from .tools import _TLPM_wrapper as K
from visa import constants as vicons
from time import sleep

class DeviceManager(object):

    def __init__(self):
        self._library = K
        self._numOfResources = 0

    @property
    def library(self):
        return self._library

    @library.setter
    def library(self, lib):
        self._library = lib
    
    @property
    def numOfResources(self):
        return self._numOfResources

    @numOfResources.setter
    def numOfResources(self, num):
        assert type(num)==type(0) and  num>=0, "The number should be an integer."
        self._numOfResources = num
    

    ###############################################

    def discover(self):
        self.findResources()
        rlist = self.getResourceList()
        return rlist


    ###############################################

    def findResources(self):
        """
        Return the number of found resources
        """
        handles = enum.ViSession(0)
        resourceCount = c_uint32(0)
        status = self.library.FindResources(handles, byref(resourceCount))
        if status==vicons.VI_SUCCESS:
            self.numOfResources = resourceCount.value
        return resourceCount.value


    def getResourceList(self):
        rlist = []
        for r in range(0, self.numOfResources):
            info = self.getResourceInfo(r)
            name = self.getResourceName(r)
            info['resourceName'] = name
            rlist.append(info)
        return rlist


    def getResourceInfo(self, index):
        modelName = (enum.ViChar*256)()
        serialNo = (enum.ViChar*256)()
        manufacturer = (enum.ViChar*256)()
        deviceAvailable = enum.ViBoolean()
        status = self.library.GetResourceInfo(c_long(0), c_uint32(index), modelName, serialNo, manufacturer, byref(deviceAvailable))
        if status==vicons.VI_SUCCESS:
            return {'index': index, 'modelName': modelName.value, 'serialNo': serialNo.value, 'manufacturer': manufacturer.value, 'deviceAvailable': deviceAvailable.value}
        if status==vicons.VI_ERROR_INV_OBJECT:
            raise Exception('Index specifies an invalid object. Found {} resources.'.format(self.numOfResources))


    def getResourceName(self, index):
        name = (enum.ViChar*256)()
        status = self.library.GetResourceName(c_long(0), c_uint32(index), name)
        if status==vicons.VI_SUCCESS:
            return name.value
        if status==vicons.VI_ERROR_INV_OBJECT:
            raise Exception('Index specifies an invalid object. Found {} resources.'.format(self.numOfResources))
