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

from . import _visa_enum as enum
from . import _TLPM_wrapper as K
from visa import constants as vicons

class DeviceManager(object):

    def __init__(self):
        # lib = cdll.LoadLibrary(r"C:\Program Files\IVI Foundation\VISA\Win64\Bin\TLPM_64.dll")
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


class PowerMeter(object):

    def __init__(self, resourceName, name=''):
        """
        resourceName -- a (python) string of the device to be connected. It has a specific format. Use Device Manager object to obtaing the resource name for the targeted device.
        """
        self._lockchange = False
        self._verbose = True
        self._resourceName = resourceName
        self._resourceName_c = create_string_buffer(resourceName.encode(),256)
        self._name = name
        self._library = K

        # for after establishing session
        self._idQuery = None
        self._resetDevice = None
        self._instrumentHandle = None


    @property
    def idQuery(self):
        return self._idQuery
    
    @idQuery.setter
    def idQuery(self,value):
        self._idQuery = value

    @property
    def resetDevice(self):
        return self._resetDevice

    @resetDevice.setter
    def resetDevice(self, value):
        self._resetDevice = value

    @property
    def instrumentHandle(self):
        return self._instrumentHandle
    
    @instrumentHandle.setter
    def instrumentHandle(self, value):
        self._instrumentHandle = value

    @property
    def resourceName(self):
        return self._resourceName
    
    @resourceName.setter
    def resourceName(self, name):
        self._resourceName = name

    @property
    def resourceName_c(self):
        return self._resourceName_c
    
    @resourceName_c.setter
    def resourceName_c(self, name):
        self.resourceName_c = name

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, newname):
        self._name = newname

    @property
    def library(self):
        return self._library

    @library.setter
    def library(self, lib):
        self._library = lib
    

    #########################################

    def open(self):
        """
        This function initializes the instrucment driver and perform initialization actions (according to Thorlabs TLPM library).
        """
        if self._verbose:
            self.verboseMessage('Establishing session...')

        idquery = enum.ViBoolean()
        resetDevice = enum.ViBoolean()
        instrumentHandle = enum.ViSession()
        status = self.library.Open(self.resourceName_c, idquery, resetDevice, byref(instrumentHandle))

        if status==vicons.VI_SUCCESS:
            if self._verbose:
                self.verboseMessage('Done establishing session.')
        else:
            raise Exception('Failed to establish session with device. Error code: {} : {}.'.format(status, ViErrors(status).getMessage()))

        return status


    def close(self):
        """
        This function closes the instrument driver session.
        """
        if self.instrumentHandle is not None:
            if self._verbose:
                self.verboseMessage('Closing session...')
            status = self.library.Close(self.instrumentHandle)
            if status==vicons.VI_SUCCESS:
                if self._verbose:
                    self.verboseMessage('Done closing session.')


    #######################################
    ## UTILITIES FUNCTION
    def verboseMessage(self, message):
        print('Device {} -- {}'.format(self._name, message))




class ViErrors(object):

    def __init__(self, err_code, instrumentHandle=0):
        self._err_code = err_code
        self._library = K
        self._instrumentHandle = instrumentHandle

    @property
    def err_code(self):
        return self._err_code

    @err_code.setter
    def err_code(self, value):
        self._err_code = value


    @property
    def library(self):
        return self._library
    

    @library.setter
    def library(self, lib):
        self._library = lib

    @property
    def instrumentHandle(self):
        return self._instrumentHandle
    
    @instrumentHandle.setter
    def instrumentHandle(self, value):
        self._instrumentHandle = value

    def getMessage(self):
        des = (enum.ViChar*512)()
        status = self.library.ErrorMessage(self.instrumentHandle, self.err_code, des)
        return des.value

    def __str__(self):
        return self.getMessage()