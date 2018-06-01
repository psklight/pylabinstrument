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

from .tools import _visa_enum as enum
from .tools import _TLPM_wrapper as K
from visa import constants as vicons
from time import sleep



class PowerMeter(object):

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
        self._library = K

        # for after establishing session
        self._idQuery = None
        self._resetDevice = None
        self._instrumentHandle = None


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
    

    #########################################

    def open(self):
        """
        This function initializes the instrucment driver and perform initialization actions (according to Thorlabs TLPM library).
        """
        self.verboseMessage('Establishing session...')

        idquery = enum.ViBoolean()
        resetDevice = enum.ViBoolean()
        instrumentHandle = enum.ViSession()
        status = self.library.Open(self.resourceName_c, idquery, resetDevice, byref(instrumentHandle))

        if status==vicons.VI_SUCCESS:
            self.verboseMessage('Done establishing session.')
            self.instrumentHandle = instrumentHandle
            self.idQuery = idquery
            self.resetDevice = resetDevice

            # initialization procedure
            self.setTimeout(1000)
        else:
            raise Exception('Failed to establish session with device. Error code: {} : {}.'.format(status, ViErrors(status).getMessage()))

        return status


    def close(self):
        """
        This function closes the instrument driver session.
        """
        if self.instrumentHandle is not None:
            self.verboseMessage('Closing session...')
            status = self.library.Close(self.instrumentHandle)
            if status==vicons.VI_SUCCESS:
                self.verboseMessage('Done closing session.')
                self._idQuery = None
                self._resetDevice = None
                self._instrumentHandle = None


    ######################################
    # Measure --> Read
    def measure(self):
        """
        This function starts a new measurement cycle and after finishing measurement the result is received. Subject to the actual Average Count this may take up to seconds.
        OUTPUT:
        It returns a floating-point value.
        """
        if self.isInSession():
            power = c_double(0.0)
            status = self.library.MeasurePower(self.instrumentHandle, power)
            return power.value
        else:
            raise self.notInSessionMsg()



    ######################################
    # Measure --> Configure --> Average

    def setAvgTime(self, sec):
        """
        sec -- averaget time in seconds
        """
        if self.isInSession():

            # check against limits
            avgtimes = self.getAvgTimes()
            minval = avgtimes['minValue']
            maxval = avgtimes['maxValue']

            if not minval<=sec<=maxval:
                raise ValueError('Average time must be between {} sec and {} sec.'.format(minval, maxval))

            self.verboseMessage('Setting average time to {} seconds ...'.format(sec))
            status = self.library.SetAvgTime(self.instrumentHandle, enum.ViReal64(sec))
            if status==vicons.VI_SUCCESS:
                self.verboseMessage('Done setting average time.')
            else:
                raise Exception('Failed to set average time. Error  code: {} : {}.'.format(status, ViErrors(status).getMessage()))
        else:
            raise self.notInSessionMsg()


    def getAvgTime(self, attr=0):
        """
        INPUT:
        attr -- 0 for setvalue, 1 for minvalue, 2 for maxValue, 3 for default value.
        """
        if self.isInSession():
            if 0<=attr<=3:
                avgtime = enum.ViReal64()
                self.library.GetAvgTime(self.instrumentHandle, c_int16(attr), byref(avgtime))
                return avgtime.value
            else:
                raise ValueError('attr argument must be 0 (set value), 1 (min value), 2 (max value), or 3 (default value).')
        else:
            raise self.notInSessionMsg()


    def getAvgTimes(self):
        if self.isInSession():
            times = dict()

            avgtime = enum.ViReal64()
            self.library.GetAvgTime(self.instrumentHandle, c_int16(0), byref(avgtime))
            times['setValue'] = avgtime.value

            avgtime = enum.ViReal64()
            self.library.GetAvgTime(self.instrumentHandle, c_int16(1), byref(avgtime))
            times['minValue'] = avgtime.value

            avgtime = enum.ViReal64()
            self.library.GetAvgTime(self.instrumentHandle, c_int16(2), byref(avgtime))
            times['maxValue'] = avgtime.value

            avgtime = enum.ViReal64()
            self.library.GetAvgTime(self.instrumentHandle, c_int16(3), byref(avgtime))
            times['defaultValut'] = avgtime.value

            return times
        else:
            raise self.notInSessionMsg()


    def getAvgCount(self):
        if self.isInSession():
            count = enum.ViInt16()
            self.library.GetAvgCount(self.instrumentHandle, byref(count))
            return count.value
        else:
            raise self.notInSessionMsg()


    def setAvgCount(self, count=1):
        if self.isInSession():
            count = int(count)
            if count>=1:
                self.verboseMessage('Setting average count to {}...'.format(count))
                status = self.library.SetAvgCount(self.instrumentHandle, count)
                if status==vicons.VI_SUCCESS:
                    self.verboseMessage('Done setting average count.')
                else:
                    raise Exception('Failed to set average count. Error  code: {} : {}.'.format(status, ViErrors(status).getMessage()))
            else:
                raise ValueError('count must be integer >=1.')
        else:
            raise self.notInSessionMsg()


    ##############################################
    # Measure --> Configure --> Correction

    def getWavelength(self, attr=0):
        """
        INPUT:
        attr -- 0 for setvalue, 1 for minvalue, 2 for maxValue
        """
        if self.isInSession():
            if 0<=attr<=2:
                value = enum.ViReal64()
                self.library.GetWavelength(self.instrumentHandle, c_int16(attr), byref(value))
                return value.value
            else:
                raise ValueError('attr argument must be 0 (set value), 1 (min value), or 2 (max value)')
        else:
            raise self.notInSessionMsg()


    def getWavelengths(self):
        if self.isInSession():
            wls = dict()

            value = enum.ViReal64()
            self.library.GetWavelength(self.instrumentHandle, c_int16(0), byref(value))
            wls['setValue'] = value.value

            value = enum.ViReal64()
            self.library.GetWavelength(self.instrumentHandle, c_int16(1), byref(value))
            wls['minValue'] = value.value

            value = enum.ViReal64()
            self.library.GetWavelength(self.instrumentHandle, c_int16(2), byref(value))
            wls['maxValue'] = value.value

            return wls
        else:
            raise self.notInSessionMsg()


    def setWavelength(self, wl):
        """
        wl -- attenuation value in nanometer
        """
        if self.isInSession():

            # check against limits
            wls = self.getWavelengths()
            minval = wls['minValue']
            maxval = wls['maxValue']

            if not minval<=wl<=maxval:
                raise ValueError('wavelength must be between {} to {} nm.'.format(minval, maxval))

            self.verboseMessage('Setting wavelength to {} nm...'.format(wl))

            # When testing, success wavelength set returns None. Hence, need to change how error is handled.
            self.library.SetWavelength(self.instrumentHandle, enum.ViReal64(wl))

            # if status==vicons.VI_SUCCESS:
            #     self.verboseMessage('Done setting wavelength.')
            # else:
            #     raise Exception('Failed to set wavelength. Error  code: {} : {}.'.format(status, ViErrors(status).getMessage()))
            sleep(0.1)
            wl_now = self.getWavelength(0)
            if abs(wl_now-wl)<1e-5:
                self.verboseMessage('Done setting wavelength.')
            else:
                raise Exception('Failed to set wavelength.')

        else:
            raise self.notInSessionMsg()


    def getAttn(self, attr=0):
        """
        INPUT:
        attr -- 0 for setvalue, 1 for minvalue, 2 for maxValue, 3 for default value.
        """
        if self.isInSession():
            if 0<=attr<=3:
                value = enum.ViReal64()
                self.library.GetAvgCount(self.instrumentHandle, c_int16(attr), byref(value))
                return value.value
            else:
                raise ValueError('attr argument must be 0 (set value), 1 (min value), 2 (max value), or 3 (default value).')
        else:
            raise self.notInSessionMsg()


    def getAttns(self):
        if self.isInSession():
            attns = dict()

            value = enum.ViReal64()
            self.library.GetAttn(self.instrumentHandle, c_int16(0), byref(value))
            attns['setValue'] = value.value

            value = enum.ViReal64()
            self.library.GetAttn(self.instrumentHandle, c_int16(1), byref(value))
            attns['minValue'] = value.value

            value = enum.ViReal64()
            self.library.GetAttn(self.instrumentHandle, c_int16(2), byref(value))
            attns['maxValue'] = value.value

            value = enum.ViReal64()
            self.library.GetAttn(self.instrumentHandle, c_int16(3), byref(value))
            attns['defaultValut'] = value.value

            return attns
        else:
            raise self.notInSessionMsg()


    def setAttn(self, db=0):
        """
        db -- attenuation value in dB
        """
        if self.isInSession():

            # check against limits
            attns = self.getAttns()
            minval = attns['minValue']
            maxval = attns['maxValue']

            if not minval<=db<=maxval:
                raise ValueError('Attenuation must be between {} to {} dB.'.format(minval, maxval))

            self.verboseMessage('Setting attenuation to {} db...'.format(db))

            status = self.library.SetAttn(self.instrumentHandle, enum.ViReal64(db))
            if status==vicons.VI_SUCCESS:
                self.verboseMessage('Done setting attenuation.')
            else:
                raise Exception('Failed to set attenuation. Error  code: {} : {}.'.format(status, ViErrors(status).getMessage()))
        else:
            raise self.notInSessionMsg()

    def performDark(self):
        if self.isInSession():
            self.startDarkAdjust()
            while self.isDarkAdjustRunning():
                sleep(0.5)
            self.verboseMessage('Done performing dark current adjust.')
        else:
            raise self.notInSessionMsg()


    def getDarkOffset(self):
        if self.isInSession():
            darkOffset = enum.ViReal64()
            status = self.library.GetDarkOffset(self.instrumentHandle, byref(darkOffset))
            return darkOffset.value
        else:
            raise self.notInSessionMsg()

    def startDarkAdjust(self):
        if self.isInSession():
            self.verboseMessage('Starting dark current adjusting...')
            self.library.StartDarkAdjust(self.instrumentHandle)
            self.verboseMessage('Done starting dark current adjust. Use isDarkAdjustRunning() to check for status.')
        else:
            raise self.notInSessionMsg()

    def isDarkAdjustRunning(self):
        if self.isInSession():
            state = enum.ViInt16()
            self.library.GetDarkAdjustState(self.instrumentHandle, byref(state))
            state = True if state.value==1 else False
            return state
        else:
            raise self.notInSessionMsg()

    def cancelDarkAdjust(self):
        if self.isInSession():
            self.verboseMessage('Canceling dark current adjust...')
            self.library.CancelDarkAdjust(self.instrumentHandle)
            self.verboseMessage('Done canceling dark current adjust.')
        else:
            raise self.notInSessionMsg()


    #######################################
    # Measure --> Configure --> Power Measurement
    def isAutoRange(self):
        if self.isInSession():
            mode = enum.ViBoolean()
            self.library.GetPowerAutoRange(self.instrumentHandle, byref(mode))
            mode = True if mode.value == 1 else False
            return mode
        else:
            raise self.notInSessionMsg()


    def setAutoRange(self, tf):
        """
        tf -- True for on, False for off
        """
        if self.isInSession():
            self.verboseMessage('Setting auto range to {}.'.format(tf))
            status = self.library.SetPowerAutoRange(self.instrumentHandle, enum.ViBoolean(tf))
            print(status)
        else:
            raise self.notInSessionMsg()

    def getPowerRange(self):
        if self.isInSession():
            values = dict()

            value = enum.ViReal64()
            self.library.GetPowerRange(self.instrumentHandle, c_int16(0), byref(value))
            values['setValue'] = value.value

            value = enum.ViReal64()
            self.library.GetPowerRange(self.instrumentHandle, c_int16(1), byref(value))
            values['minValue'] = value.value

            value = enum.ViReal64()
            self.library.GetPowerRange(self.instrumentHandle, c_int16(2), byref(value))
            values['maxValue'] = value.value

            return values
        else:
            raise self.notInSessionMsg()

    def setPowerRange(self, power):
        """
        power -- the most positive signal level expected for the sensor input in watts.

        The power meter will automatically set to its (discrete) power range mode.
        """
        if self.isInSession():
            # check against limits
            powers = self.getPowerRange()
            minval = powers['minValue']
            maxval = powers['maxValue']

            if not minval<=power<=maxval:
                raise ValueError('Power range (max) must be between {} to {} watts.'.format(minval, maxval))

            self.verboseMessage('Setting power range to {} watts...'.format(power))

            status = self.library.SetPowerRange(self.instrumentHandle, enum.ViReal64(power))
            if status==vicons.VI_SUCCESS:
                self.verboseMessage('Done setting power range.')
            else:
                raise Exception('Failed to set power range. Error  code: {} : {}.'.format(status, ViErrors(status).getMessage()))
        else:
            raise self.notInSessionMsg()


    def getPowerUnit(self):
        if self.isInSession():
            unit = enum.ViInt16()
            self.library.GetPowerUnit(self.instrumentHandle, byref(unit))
            unit = 'W' if unit.value==0 else 'dBm'
            return unit
        else:
            raise self.notInSessionMsg()

    def setPowerUnit(self, unit):
        """
        unit -- 'W' for watts, 'dBm' for dBm
        """
        if self.isInSession():
            unit = unit.lower()
            if unit not in set(['w','dbm']):
                raise ValueError('Unit must be W or dBm.')
            else:
                unit = 0 if unit=='w' else 1
            self.library.SetPowerUnit(self.instrumentHandle, enum.ViInt16(unit))

        else:
            raise self.notInSessionMsg()


    #######################################
    ## UTILITIES FUNCTION
    def verboseMessage(self, message):
        if self._verbose:
            print('Device {} -- {}'.format(self._name, message))


    def setTimeout(self, ms):
        """
        ms -- a timeout value in millisecond
        """
        if self.isInSession():
            ms_c = c_uint32(ms)
            self.verboseMessage('Setting timeout to {} ...'.format(ms))
            status = self.library.SetTimeout(self.instrumentHandle, ms_c)
            self.verboseMessage('Done setting timeout.')
        else:
            raise self.notInSessionMsg()

    def getTimeout(self):
        """
        OUTPUT:
        ms -- a timeout value in millisecond (python)
        """
        if self.isInSession():
            ms_c = c_uint32(0)
            status = self.library.GetTimeout(self.instrumentHandle, byref(ms_c))
            return ms_c.value
        else:
            raise self.notInSessionMsg()


    def isInSession(self):
        if self.instrumentHandle is None:
            return False
        else:
            return True

    def notInSessionMsg(self):
        return Exception('The power meter is not in session. Run .open() first.')




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

