from ctypes import create_string_buffer


class VisaObject(object):

    def __init__(self, resourceName, modelName = '', name=''):
        """
        INPUTS:
        resourceName -- a (python) string of the device to be connected. It has a specific format. Use Device Manager object to obtaing the resource name for the targeted device.
        modelName -- a b-string for model name, such as b'PM100'. This would be used to check whether functions can be run on the model or not.
        """
        self._lockchange = False
        self._verbose = True
        self._resourceName = resourceName
        self._resourceName_c = create_string_buffer(resourceName.encode(),256)
        self._modelName = modelName
        self._name = name
        self._library = None

        # for after establishing session
        self._idQuery = None
        self._resetDevice = None
        self._instrumentHandle = None

    @property
    def verbose(self):
        return self._verbose
    
    @verbose.setter
    def verbose(self, value):
        self._verbose = value

    @property
    def modelName(self):
        return self._modelName

    @modelName.setter
    def modelName(self, name):
        self._modelName = name
    

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

    ################################################################################

    def verboseMessage(self, message):
        if self.verbose:
            print('Device {} -- {}'.format(self.name, message))

    def isInSession(self):
        if self.instrumentHandle is None:
            return False
        else:
            return True

    def notInSessionMsg(self):
        return Exception('The power meter is not in session. Run .open() first.')