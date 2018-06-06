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
    byref,
    pointer
)

class Motor(object):

    def __init__(self, serial_no, name=""):

        self._lockchange = False
        self._serial_no = serial_no
        self._verbose = True
        self.serial_no_c = c_char_p(bytes(str(serial_no), "utf-8"))
        self._library = None
        self._isInSession = False
        self._name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        assert type(name) is str, 'Name must be a python string.'
        self._name = name
    
    @property
    def isInSession(self):
        return self._isInSession

    @isInSession.setter
    def isInSession(self, value):
        assert type(value) is bool, 'Only accept boolean. Non-boolean given.'
        self._isInSession = value

    @property
    def serial_no(self):
        return self._serial_no

    @serial_no.setter
    def serial_no(self, value):
        assert self._lockchange is False, "The motor instance is open. Close the motor first befor changing serial number or channel."
        self._serial_no = value
        self.serial_no_c = c_char_p(bytes(str(serial_no), "utf-8"))

    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, value):
        assert type(value) is type(True), "Verbose property can only be True of False."
        self._verbose = value
    
    def get_serial_no_c(self):
        return self._serial_no_c

    def set_serial_no_c(self, value):
        self._serial_no_c = value

    serial_no_c = property(get_serial_no_c, set_serial_no_c)

    @property
    def library(self):
        return self._library

    @library.setter
    def library(self, library):
        self._library = library


    #################################################
    def open(self):
        self.verboseMessage('Opening...')

        if hasattr(self,'channel'):
            err_code = self.library.Open(self.serial_no_c, self.channel_c)
        else:
            err_code = self.library.Open(self.serial_no_c)

        if err_code==0:
            self._lockchange = True
            self.isInSession = True
            self.library.ClearMessageQueue(self.serial_no_c)
            self.loadSettings()  # for, for example, convert real and device unit
            self.verboseMessage('Opening done.')
        else:
            raise Exception('Failed to open and establish connection with device. Error code {}.'.format(err_code))

    def close(self):
        self.verboseMessage('Closing...')
        self.library.Close(self.serial_no_c)
        self._lockchange = False
        self.isInSession = False
        self.verboseMessage('Closing done.')

    #####################################
    def identify(self):
        if self.isInSession:
            self.library.Identify(self.serial_no_c)
        else:
            raise self.notInSessionMsg()

    def blink(self):
        if self.isInSession:
            self.identify()
        else:
            raise self.notInSessionMsg()

    def canHome(self):
        if self.isInSession:
            result = self.library.CanHome(self.serial_no_c)
            return result
        else:
            raise self.notInSessionMsg()
            
        
    def getDeviceInfo(self):
        self.library.BuildDeviceList()
        di = self.library.DeviceInfo()
        err_code = self.library.GetDeviceInfo(self.serial_no_c, byref(di))
        if err_code==0:
            raise Exception('Failed to get device info from self.library.GetDeviceInfo.')
        else:
            return di
        
    def getHardwareInfo(self):
        self.library.BuildDeviceList()
        hi = self.library.HardwareInformation()
        err_code = self.library.GetHardwareInfoBlock(self.serial_no_c, byref(hi))
        if err_code==0:
            return hi
        else:
            raise Exception('Failed to get hardware info from self.library.GetHardwareInfoBlock. Error code {}'.format(err_code))

    def loadSettings(self):
        if self.isInSession:
            success = self.library.LoadSettings(self.serial_no_c)
            if success is False:
                raise Exception('Failed to load settings.')
        else:
            raise self.notInSessionMsg()
            
    def persistSettings(self):
        if self.isInSession:
            success = self.library.PersistSettings(self.serial_no_c)
            if success is False:
                raise Exception('Failed to persist settings.')
        else:
            raise self.notInSessionMsg()
            
    def requestSettings(self):
        if self.isInSession:
            err_code = self.library.RequestSettings(self.serial_no_c)
            if err_code!=0:
                raise Exception('Failed to request settings. Error code {}'.format(err_code))
        else:
            raise self.notInSessionMsg()

    def resetStageToDefaults(self):
        if self.isInSession:
            success = self.library.ResetStageToDefaults(self.serial_no_c)
            if success is False:
                raise Exception('Failed to reset stage to defaults.')
        else:
            raise self.notInSessionMsg()
            
            

    #####################################
    # UTILITY FUNCTIONS
    def verboseMessage(self, message):
        if self.verbose:
            if self.name=="":
                if hasattr(self,'channel'):
                    print('Device {}, Ch. {} -- {}...'.format(self.serial_no, self.channel, message))
                else:
                    print('Device {} -- {}...'.format(self.serial_no, message))
            else:
                print('Device {} -- {}...'.format(self.name, message))

    def notInSessionMsg(self):
        return Exception('The power meter is not in session. Run .open() first.')


    def getRealValueFromDeviceUnit(self, deviceunit, unitType=0):
        if self.isInSession:
            realval = c_double(0.0)
            err_code = self.library.GetRealValueFromDeviceUnit(self.serial_no_c, deviceunit, byref(realval), c_int(unitType))
            if err_code==0:
                return realval.value
            else:
                raise Exception('Failed to get real value from device unit.')
        else:
            raise self.notInSessionMsg()
        

    def getDeviceUnitFromRealValue(self, realval, unitType=0):
        if self.isInSession:
            deviceunit = c_int(0)
            err_code = self.library.GetDeviceUnitFromRealValue(self.serial_no_c, c_double(realval), byref(deviceunit), c_int(unitType))
            return deviceunit.value
        else:
            raise self.notInSessionMsg()
            