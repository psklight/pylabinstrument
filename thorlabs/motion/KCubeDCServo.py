
import ctypes
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

c_word = c_ushort
c_dword = c_ulong

from .._tool import bind, null_function
from .. import _enumeration as enum
from time import sleep
from . import _KCubeDCServo as K


class Motor(object):

    def __init__(self, serial_no, channel=1):

        self._lockchange = False
        self._serial_no = serial_no
        self._channel = channel
        self._verbose = True

        self.serial_no_c = c_char_p(bytes(str(serial_no), "utf-8"))
        self.channel_c = c_short(channel)

    @property
    def serial_no(self):
        return self._serial_no

    @serial_no.setter
    def serial_no(self, value):
        assert self._lockchange is False, "The motor instance is open. Close the motor first befor changing serial number or channel."
        self._serial_no = value
        self.serial_no_c = c_char_p(bytes(str(serial_no), "utf-8"))

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        assert self._lockchange is False, "The motor instance is open. Close the motor first befor changing serial number or channel."
        self._channel = value
        self.channel_c = c_short(value)

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

    def get_channel_c(self):
        return self._channel_c

    def set_channel_c(self, value):
        self._channel_c = value

    channel_c = property(get_channel_c, set_channel_c)


    #################################################
    def open(self):
        if self._verbose:
            self.verboseMessage('Opening...')

        err_code = K.CC_Open(self.serial_no_c, self.channel_c)
        if err_code==0:
            self._lockchange = True
            K.CC_ClearMessageQueue(self.serial_no_c)
            self.loadSettings()  # for, for example, convert real and device unit
            if self._verbose:
                self.verboseMessage('Opening done.')
        else:
            raise Exception('Failed to open and establish connection with device. Error code {}.'.format(err_code))

    def close(self):
        if self._verbose:
            self.verboseMessage('Closing...')
        K.CC_Close(self.serial_no_c)
        self._lockchange = False
        if self._verbose:
            self.verboseMessage('Closing done.')

    def home(self):
        canhome = K.CC_CanHome(self.serial_no_c)
        if canhome:
            if self._verbose:
                self.verboseMessage('Homing')
            err_code = K.CC_Home(self._serial_no_c)
            if err_code==0:
                pass
            else:
                raise Exception('Error when homing. Error code {}.'.format(err_code))
        else:
            print('Device cannot perform home.')

    def moveToPosition(self, realpos):
        if self._verbose:
            self.verboseMessage('Moving to position')
        err_code = K.CC_MoveToPosition(self.serial_no_c, self.getDeviceUnitFromRealValue(realpos))
        if err_code==0:
            pass
        else:
            raise Exception('Error trying to move. Error code {}'.format(err_code))

    def getPosition(self):
        err_code = K.CC_RequestPosition(self.serial_no_c)
        if err_code is not 0:
            raise Exception('Error in requesting position. Error code {}'.format(err_code))
        sleep(0.1)
        devicepos = K.CC_GetPosition(self.serial_no_c)
        return self.getRealValueFromDeviceUnit(devicepos, unitType=0)

    def stop(self):
        err_code = K.CC_StopProfiled(self.serial_no_c)
        if err_code!=0:
            raise Exception('Failed to stop. Error code {}.'.format(err_code))

    def stopImmediate(self):
        err_code = K.CC_StopImmediate(self.serial_no_c)
        if err_code!=0:
            raise Exception('Failed to stop. Error code {}'.format(err_code))

    #####################################
    def identify(self):
        K.CC_Identify(self.serial_no_c)

    def blink(self):
        self.identify()

    def getDeviceInfo(self):
        K.TLI_BuildDeviceList()
        di = K.TLI_DeviceInfo()
        err_code = K.TLI_GetDeviceInfo(self.serial_no_c, byref(di))
        if err_code==0:
            raise Exception('Failed to get device info from K.TLI_GetDeviceInfo.')
        else:
            return di

    def getHardwareInfo(self):
        K.TLI_BuildDeviceList()
        hi = K.TLI_HardwareInformation()
        err_code = K.CC_GetHardwareInfoBlock(self.serial_no_c, byref(hi))
        if err_code==0:
            return hi
        else:
            raise Exception('Failed to get hardware info from K.CC_GetHardwareInfoBlock. Error code {}'.format(err_code))

    def getVelParams(self):
        acc = c_int(0)
        maxvel = c_int(0)
        err_code = K.CC_GetVelParams(self.serial_no_c, byref(acc), byref(maxvel))
        if err_code==0:
            return {'acceleration': acc.value, 'maxVelocity': maxvel.value}
        else:
            raise Exception('Error when getting velocity parameters. Error code {}'.format(err_code))

    def getMotorParams(self):
        params = dict()
        stepperrev = c_double(0.0)
        gearboxratio = c_double(0.0)
        pitch = c_double(0.0)
        err_code = K.CC_GetMotorParamsExt(self.serial_no_c, byref(stepperrev), byref(gearboxratio), byref(pitch))
        if err_code==0:
            params['stepPerRev'] = stepperrev.value
            params['gearboxRatio'] = gearboxratio.value
            params['pitch'] = pitch.value
            return params
        else:
            raise Exception('Failed to get motor parameter using K.CC_GetMotorParamsExt. Error code {}'.format(err_code))

    def setMotorParams(self, params):
        stepperrev = c_double(params['stepPerRev'])
        gearboxratio = c_double(params['gearboxRatio'])
        pitch = c_double(params['pitch'])
        err_code = K.CC_SetMotorParamsExt(self.serial_no_c, stepperrev, gearboxratio, pitch)
        if err_code!=0:
            raise Exception('Failed to set motor parameters. Error code {}'.format(err_code))

    def getMotorTravelMode(self):
        travelmode = K.CC_GetMotorTravelMode(self.serial_no_c)
        return travelmode

    def setMotorTravelMode(self, mode):
        assert mode in [0,1,2], "mode must be either 0 (undefined), 1 (linear), or 2 (rotational)"
        err_code = K.CC_SetMotorTravelMode(c_int(mode))

    def getMotorTravelLimits(self):
        minPosition = c_double(0.0)
        maxPosition = c_double(0.0)
        err_code = K.CC_GetMotorTravelLimits(self.serial_no_c, byref(minPosition), byref(maxPosition))
        if err_code==0:
            return {'minPosition': minPosition, 'maxPosition': maxPosition}
        else:
            raise Exception('Failed to get motor travel limits. Error code {}.'.format(err_code))

    def setMotorTravelLimits(self, params):
        minpos = c_double(float(params['minPosition']))
        maxpos = c_double(float(params['maxPosition']))
        err_code = K.CC_SetMotorTravelLimits(self.serial_no_c, minpos, maxpos)
        if err_code!=0:
            raise Exception('Failed to set motor travel limits. Error code {}'.format(err_code))

    def getMotorVelocityLimits(self):
        maxVelocity = c_double(0.0)
        maxAcceleration = c_double(0.0)
        err_code = K.CC_GetMotorVelocityLimits(self.serial_no_c, byref(maxVelocity), byref(maxAcceleration))
        if err_code==0:
            return {'maxVelocity': maxVelocity.value, 'maxAcceleration': maxAcceleration.value}
        else:
            raise Exception('Failed to get motor velocity limit. Error code {}.'.format(err_code))

    def setMotorVelocityLimits(self, params):
        maxvel = c_double(float(params['maxVelocity']))
        maxacc = c_double(float(params['maxAcceleration']))
        err_code = K.CC_SetMotorVelocityLimits(self.serial_no_c, maxvel, maxacc)
        if err_code!=0:
            raise Exception('Failed to set motor velocity limits. Error code {}'.format(err_code))

    def resetStageToDefaults(self):
        success = K.CC_ResetStageToDefaults(self.serial_no_c)
        if success is False:
            raise Exception('Failed to reset stage to defaults.')

    def loadSettings(self):
        success = K.CC_LoadSettings(self.serial_no_c)
        if success is False:
            raise Exception('Failed to load settings.')

    def persistSettings(self):
        success = K.CC_PersistSettings(self.serial_no_c)
        if success is False:
            raise Exception('Failed to persist settings.')

    def requestSettings(self):
        err_code = K.CC_RequestSettings(self.serial_no_c)
        if err_code!=0:
            raise Exception('Failed to request settings. Error code {}'.format(err_code))

    def getDCPIDParams(self):
        params_c = K.MOT_DC_PIDParameters()
        err_code = K.CC_GetDCPIDParams(self.serial_no_c, byref(params_c))
        if err_code==0:
            return params_c.getdict()
        else:
            raise Exception('Failed to get DC PID params. Error code {}.'.format(err_code))

    def setDCPIDParams(self, params):
        param_c = K.MOT_DC_PIDParameters()
        param_c.loaddict(params)
        if self._verbose:
            self.verboseMessage("Setting DC PID params...")
        err_code = K.CC_SetDCPIDParams(self.serial_no_c, byref(param_c))
        if err_code==0:
            if self._verbose:
                self.verboseMessage("Done setting DC PID params.")
        else:
            raise Exception('Failed to set DC PID params. Error code {}.'.format(err_code))

    def getHomingParams(self):
        param_c = K.MOT_HomingParameters()
        err_code = K.CC_GetHomingParamsBlock(self.serial_no_c, byref(param_c))
        if err_code==0:
            return param_c.getdict()
        else:
            raise Exception('Failed to get homing parameters. Error code {}.'.format(err_code))

    def setHomingParams(self, params):
        param_c = K.MOT_HomingParameters()
        param_c.loaddict(params)
        if self._verbose:
            self.verboseMessage("Setting homing params...")
        err_code = K.CC_SetHomingParamsBlock(self.serial_no_c, byref(param_c))
        if err_code==0:
            if self._verbose:
                self.verboseMessage("Done setting homing params.")
        else:
            raise Exception('Failed to set homing parameters. Error code {}.'.format(err_code))

    #####################################
    # UTILITY FUNCTIONS
    def verboseMessage(self, message):
        print('Device {}, Ch. {} -- {}...'.format(self.serial_no, self.channel, message))

    def getRealValueFromDeviceUnit(self, deviceunit, unitType=0):
        realval = c_double(0.0)
        err_code = K.CC_GetRealValueFromDeviceUnit(self.serial_no_c, deviceunit, byref(realval), c_int(unitType))
        if err_code==0:
            return realval.value
        else:
            raise Exception('Failed to get real value from device unit.')

    def getDeviceUnitFromRealValue(self, realval, unitType=0):
        deviceunit = c_int(0)
        err_code = K.CC_GetDeviceUnitFromRealValue(self.serial_no_c, c_double(realval), byref(deviceunit), c_int(unitType))
        return deviceunit.value