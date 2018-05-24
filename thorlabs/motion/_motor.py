

class Motor(object):

    def __init__(self, serial_no):

        self._lockchange = False
        self._serial_no = serial_no
        self._verbose = True

        self.serial_no_c = c_char_p(bytes(str(serial_no), "utf-8"))

        self._lib = None

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
    def lib(self):
        return self._lib

    @lib.setter
    def lib(self, library):
        self._lib = library


    #################################################
    def open(self):
        if self._verbose:
            self.verboseMessage('Opening...')

        if hasattr(self,'channel'):
            err_code = self.lib.Open(self.serial_no_c, self.channel_c)
        else:
            err_code = self.lib.Open(self.serial_no_c)

        if err_code==0:
            self._lockchange = True
            self.lib.ClearMessageQueue(self.serial_no_c)
            self.loadSettings()  # for, for example, convert real and device unit
            if self._verbose:
                self.verboseMessage('Opening done.')
        else:
            raise Exception('Failed to open and establish connection with device. Error code {}.'.format(err_code))

    def close(self):
        if self._verbose:
            self.verboseMessage('Closing...')
        self.lib.Close(self.serial_no_c)
        self._lockchange = False
        if self._verbose:
            self.verboseMessage('Closing done.')

    #####################################
    def identify(self):
        self.lib.Identify(self.serial_no_c)

    def blink(self):
        self.identify()

    def getDeviceInfo(self):
        self.lib.BuildDeviceList()
        di = self.lib.DeviceInfo()
        err_code = self.lib.GetDeviceInfo(self.serial_no_c, byref(di))
        if err_code==0:
            raise Exception('Failed to get device info from self.lib.GetDeviceInfo.')
        else:
            return di

    def getHardwareInfo(self):
        self.lib.BuildDeviceList()
        hi = self.lib.HardwareInformation()
        err_code = self.lib.GetHardwareInfoBlock(self.serial_no_c, byref(hi))
        if err_code==0:
            return hi
        else:
            raise Exception('Failed to get hardware info from self.lib.GetHardwareInfoBlock. Error code {}'.format(err_code))

    def loadSettings(self):
        success = self.lib.LoadSettings(self.serial_no_c)
        if success is False:
            raise Exception('Failed to load settings.')

    def persistSettings(self):
        success = self.lib.PersistSettings(self.serial_no_c)
        if success is False:
            raise Exception('Failed to persist settings.')

    def requestSettings(self):
        err_code = self.lib.RequestSettings(self.serial_no_c)
        if err_code!=0:
            raise Exception('Failed to request settings. Error code {}'.format(err_code))

    #####################################
    # UTILITY FUNCTIONS
    def verboseMessage(self, message):
        if hasattr(self,'channel'):
            print('Device {}, Ch. {} -- {}...'.format(self.serial_no, self.channel, message))
        else:
            print('Device {} -- {}...'.format(self.serial_no, message))
