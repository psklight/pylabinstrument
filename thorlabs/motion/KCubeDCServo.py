
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
    c_char_p
)

c_word = c_ushort
c_dword = c_ulong

from .._tool import bind, null_function
from .._enumeration import MOT_MotorTypes, MOT_JogModes, MOT_StopModes, MOT_TravelDirection, MOT_HomeLimitSwitchDirection, MOT_LimitSwitchModes, MOT_LimitSwitchSWModes, MOT_DirectionSense, MOT_TravelModes
from .. import DeviceManager as dm

from comtypes import _safearray
import ctypes
from ctypes import byref, pointer
from time import sleep

lib = cdll.LoadLibrary("Thorlabs.MotionControl.KCube.DCServo.dll")

#encoder_counters = {
#    'MTS25-Z8':     34304,
#    'MTS50-Z8':     34304,
#    'Z8':           34304,
#    'Z6':           24600,
#    'PRM1-Z8':      1919.64,
#    'CR1-Z7':       12288}

# Define data structures
class TLI_DeviceInfo(Structure):
    _fields_ = [("typeID", c_dword),
                ("description", (65 * c_char)),
                ("serialNo", (9 * c_char)),
                ("PID", c_dword),
                ("isKnownType", c_bool),
                ("motorType", MOT_MotorTypes),
                ("isPiezoDevice", c_bool),
                ("isLaser", c_bool),
                ("isCustomType", c_bool),
                ("isRack", c_bool),
                ("maxChannels", c_short)]

    def __str__(self):
        d = dict()
        d['typeID'] = self.typeID
        d['description'] = self.description
        d['serialNo'] = self.serialNo
        d['PID'] = self.PID
        d['isKnownType'] = self.isKnownType
        d['motorType'] = self.motorType
        d['isPiezoDevice'] = self.isPiezoDevice
        d['isCustomType'] = self.isCustomType
        d['isRack'] = self.isRack
        d['maxChannels'] = self.maxChannels
        return str(d)


class TLI_HardwareInformation(Structure):
    _fields_ = [("serialNumber", c_dword),
                ("modelNumber", (8 * c_char)),
                ("type", c_word),
                ("firmwareVersion", c_dword),
                ("notes", (48 * c_char)),
                ("deviceDependantData", (12 * c_byte)),
                ("hardwareVersion", c_word),
                ("modificationState", c_word),
                ("numChannels", c_short)]


class MOT_VelocityParameters(Structure):
    _fields_ = [("minVelocity", c_int),
                ("acceleration", c_int),
                ("maxVelocity", c_int)]


class MOT_JogParameters(Structure):
    _fields_ = [("mode", MOT_JogModes),
                ("stepSize", c_uint),
                ("velParams", MOT_VelocityParameters),
                ("stopMode", MOT_StopModes)]


class MOT_HomingParameters(Structure):
    _fields_ = [("direction", MOT_TravelDirection),
                ("limitSwitch", MOT_HomeLimitSwitchDirection),
                ("velocity", c_uint),
                ("offsetDistance", c_uint)]


class MOT_LimitSwitchParameters(Structure):
    _fields_ = [("clockwiseHardwareLimit", MOT_LimitSwitchModes),
                ("anticlockwiseHardwareLimit", MOT_LimitSwitchModes),
                ("clockwisePosition", c_dword),
                ("anticlockwisePosition", c_dword),
                ("softLimitMode", MOT_LimitSwitchSWModes)]

class MOT_DC_PIDParameters(Structure):
    _fields_ = [("proportionalGain", c_int),
                ("integralGain", c_int),
                ("differentialGain", c_int),
                ("integralLimit", c_int),
                ("parameterFilter", c_word)]

class KMOT_MMIParams(Structure):
    _fields_ = [("JoystickMODE", c_int),
                ("JoystickMaxVelocity", c_int32),
                ("JoystickAcceleration", c_int32),
                ("JoystickDirectionSense", MOT_DirectionSense),
                ("PresetPos1", c_int32),
                ("PresetPos2", c_int32),
                ("DisplayIntensity", c_int16),
                ("reserved",6*c_int16)]

class KMOT_TriggerConfig(Structure):
    _fields_ = [("Trigger1Mode", c_int),
                ("Trigger1Polarity", c_int),
                ("Trigger2Mode", c_int),
                ("Trigger2Polarity", c_int)]

class KMOT_TriggerParams(Structure):
    _fields_ = [("TriggerStartPositionFwd", c_int32),
                ("TriggerIntervalFwd", c_int32),
                ("TriggerPulseCountFwd", c_int32),
                ("TriggerStartPositionRev", c_int32),
                ("TriggerIntervalRev", c_int32),
                ("TriggerPulseCountRev", c_int32),
                ("TriggerPulseWidth", c_int32),
                ("CycleCount", c_int32),
                ("reserved", 6*c_int32)]

TLI_BuildDeviceList = bind(lib, "TLI_BuildDeviceList", None, c_short)
TLI_GetDeviceListSize = bind(lib, "TLI_GetDeviceListSize", None, c_short)
# TLI_GetDeviceList = bind(lib, "TLI_GetDeviceList", [_safearray.tagSAFEARRAY], c_short)
# TLI_GetDeviceList  <- TODO: Implement SAFEARRAY first. BENCHTOPSTEPPERMOTOR_API short __cdecl TLI_GetDeviceList(SAFEARRAY** stringsReceiver);
# TLI_GetDeviceListByType  <- TODO: Implement SAFEARRAY first. BENCHTOPSTEPPERMOTOR_API short __cdecl TLI_GetDeviceListByType(SAFEARRAY** stringsReceiver, int typeID);
# TLI_GetDeviceListByTypes  <- TODO: Implement SAFEARRAY first. BENCHTOPSTEPPERMOTOR_API short __cdecl TLI_GetDeviceListByTypes(SAFEARRAY** stringsReceiver, int * typeIDs, int length);
TLI_GetDeviceListExt = bind(lib, "TLI_GetDeviceListExt", [POINTER(c_char), c_dword], c_short)
TLI_GetDeviceListByTypeExt = bind(lib, "TLI_GetDeviceListByTypeExt", [POINTER(c_char), c_dword, c_int], c_short)
TLI_GetDeviceListByTypesExt = bind(lib, "TLI_GetDeviceListByTypesExt", [POINTER(c_char), c_dword, POINTER(c_int), c_int], c_short)
TLI_GetDeviceInfo = bind(lib, "TLI_GetDeviceInfo", [POINTER(c_char), POINTER(TLI_DeviceInfo)], c_short)

# KDC specific functions
CC_Open = bind(lib, "CC_Open", [POINTER(c_char)], c_short)
CC_Close = bind(lib, "CC_Close", [POINTER(c_char)], c_short)
CC_Identify = bind(lib, "CC_Identify", [POINTER(c_char)], None)

CC_Home = bind(lib, "CC_Home", [POINTER(c_char)], c_short)
CC_MoveToPosition = bind(lib, "CC_MoveToPosition", [POINTER(c_char), c_int], c_short)
CC_StopProfiled = bind(lib, "CC_StopProfiled", [POINTER(c_char)], c_short)
CC_StopImmediate = bind(lib, "CC_StopImmediate", [POINTER(c_char)], c_short)

CC_RequestPosition = bind(lib, "CC_RequestPosition", [POINTER(c_char)], c_short)
CC_GetPosition = bind(lib, "CC_GetPosition", [POINTER(c_char)], c_int)

CC_GetVelParams = bind(lib, "CC_GetVelParams", [POINTER(c_char), POINTER(c_int), POINTER(c_int)], c_short)

CC_GetRealValueFromDeviceUnit = bind(lib, "CC_GetRealValueFromDeviceUnit", [POINTER(c_char), c_int, POINTER(c_double), c_int], c_short)
CC_GetDeviceUnitFromRealValue = bind(lib, "CC_GetDeviceUnitFromRealValue", [POINTER(c_char), c_double, POINTER(c_int), c_int], c_short)

CC_GetHardwareInfoBlock = bind(lib, "CC_GetHardwareInfoBlock", [POINTER(c_char), POINTER(TLI_HardwareInformation)], c_short)

CC_ClearMessageQueue = bind(lib, "CC_ClearMessageQueue", [POINTER(c_char)], None)

CC_GetMotorParamsExt = bind(lib, "CC_GetMotorParamsExt", [POINTER(c_char), POINTER(c_double), POINTER(c_double), POINTER(c_double)], c_short)
CC_SetMotorParamsExt = bind(lib, "CC_SetMotorParamsExt", [POINTER(c_char), c_double, c_double, c_double], c_short)
CC_SetMotorTravelLimits = bind(lib, "CC_SetMotorTravelLimits", [POINTER(c_char), c_double, c_double], c_short)
CC_SetMotorTravelMode = bind(lib, "CC_SetMotorTravelMode", [POINTER(c_char), MOT_TravelModes], c_short)
CC_SetMotorVelocityLimits = bind(lib, "CC_SetMotorVelocityLimits", [POINTER(c_char), c_double, c_double], c_short)

CC_RequestSettings = bind(lib, "CC_RequestSettings", [POINTER(c_char)], c_short)
CC_ResetStageToDefaults = bind(lib, "CC_ResetStageToDefaults", [POINTER(c_char)], c_short)
CC_LoadSettings = bind(lib, "CC_LoadSettings", [POINTER(c_char)], c_bool)
CC_PersistSettings = bind(lib, "CC_PersistSettings", [POINTER(c_char)], c_bool)

CC_CanHome = bind(lib, "CC_CanHome", [POINTER(c_char)], c_bool)

class Motor(object):

    def __init__(self, serial_no, channel=1):

        self._lockchange = False
        self._serial_no = serial_no
        self._channel = channel
        self._verbose = False

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

        err_code = CC_Open(self.serial_no_c, self.channel_c)
        if err_code==0:
            self._lockchange = True
            CC_ClearMessageQueue(self.serial_no_c)
            self.loadSettings()  # for, for example, convert real and device unit
            if self._verbose:
                self.verboseMessage('Opening done.')
        else:
            raise Exception('Failed to open and establish connection with device. Error code {}.'.format(err_code))

    def close(self):
        if self._verbose:
            self.verboseMessage('Closing...')
        CC_Close(self.serial_no_c)
        self._lockchange = False
        if self._verbose:
            self.verboseMessage('Closing done.')

    def home(self):
        canhome = CC_CanHome(self.serial_no_c)
        if canhome:
            if self._verbose:
                self.verboseMessage('Homing')
            err_code = CC_Home(self._serial_no_c)
            if err_code==0:
                pass
            else:
                raise Exception('Error when homing. Error code {}.'.format(err_code))
        else:
            print('Device cannot perform home.')

    def moveToPosition(self, realpos):
        if self._verbose:
            self.verboseMessage('Moving to position')
        err_code = CC_MoveToPosition(self.serial_no_c, self.getDeviceUnitFromRealValue(realpos))
        if err_code==0:
            pass
        else:
            raise Exception('Error trying to move. Error code {}'.format(err_code))

    def getPosition(self):
        err_code = CC_RequestPosition(self.serial_no_c)
        if err_code is not 0:
            raise Exception('Error in requesting position. Error code {}'.format(err_code))
        sleep(0.1)
        devicepos = CC_GetPosition(self.serial_no_c)
        return self.getRealValueFromDeviceUnit(devicepos, unitType=0)

    def getVelParams(self):
        acc = c_int(0)
        maxvel = c_int(0)
        err_code = CC_GetVelParams(self.serial_no_c, byref(acc), byref(maxvel))
        if err_code==0:
            return {'acceleration': acc.value, 'maxVelocity': maxvel.value}
        else:
            raise Exception('Error when getting velocity parameters. Error code {}'.format(err_code))

    def stop(self):
        err_code = CC_StopProfiled(self.serial_no_c)
        if err_code!=0:
            raise Exception('Failed to stop. Error code {}.'.format(err_code))

    def stopImmediate(self):
        err_code = CC_StopImmediate(self.serial_no_c)
        if err_code!=0:
            raise Exception('Failed to stop. Error code {}'.format(err_code))

    #####################################
    def identify(self):
        CC_Identify(self.serial_no_c)

    def blink(self):
        self.identify()

    def getDeviceInfo(self):
        TLI_BuildDeviceList()
        di = TLI_DeviceInfo()
        err_code = TLI_GetDeviceInfo(self.serial_no_c, byref(di))
        if err_code==0:
            raise Exception('Failed to get device info from TLI_GetDeviceInfo.')
        else:
            return di

    def getHardwareInfo(self):
        TLI_BuildDeviceList()
        hi = TLI_HardwareInformation()
        err_code = CC_GetHardwareInfoBlock(self.serial_no_c, byref(hi))
        if err_code==0:
            return hi
        else:
            raise Exception('Failed to get hardware info from CC_GetHardwareInfoBlock. Error code {}'.format(err_code))

    def getMotorParams(self):
        params = dict()
        stepperrev = c_double(0.0)
        gearboxratio = c_double(0.0)
        pitch = c_double(0.0)
        err_code = CC_GetMotorParamsExt(self.serial_no_c, byref(stepperrev), byref(gearboxratio), byref(pitch))
        if err_code==0:
            params['stepPerRev'] = stepperrev.value
            params['gearboxRatio'] = gearboxratio.value
            params['pitch'] = pitch.value
            return params
        else:
            raise Exception('Failed to get motor parameter using CC_GetMotorParamsExt. Error code {}'.format(err_code))

    def setMotorParams(self, params):
        stepperrev = c_double(params['stepPerRev'])
        gearboxratio = c_double(params['gearboxRatio'])
        pitch = c_double(params['pitch'])
        err_code = CC_SetMotorParamsExt(self.serial_no_c, stepperrev, gearboxratio, pitch)
        if err_code!=0:
            raise Exception('Failed to set motor parameters. Error code {}'.format(err_code))

    def setMotorTravelMode(self, mode):
        assert mode in [0,1,2], "mode must be either 0 (undefined), 1 (linear), or 2 (rotational)"
        err_code = CC_SetMotorTravelMode(c_int(mode))

    def setMotorTravelLimits(self, params):
        minpos = c_double(float(params['minPosition']))
        maxpos = c_double(float(params['maxPosition']))
        err_code = CC_SetMotorTravelLimits(self.serial_no_c, minpos, maxpos)
        if err_code!=0:
            raise Exception('Failed to set motor travel limits. Error code {}'.format(err_code))

    def setMotorVelocityLimits(self, params):
        maxvel = c_double(float(params['maxVelocity']))
        maxacc = c_double(float(params['maxAcceleration']))
        err_code = CC_SetMotorVelocityLimits(self.serial_no_c, maxvel, maxacc)
        if err_code!=0:
            raise Exception('Failed to set motor velocity limits. Error code {}'.format(err_code))

    def resetStageToDefaults(self):
        success = CC_ResetStageToDefaults(self.serial_no_c)
        if success is False:
            raise Exception('Failed to reset stage to defaults.')

    def loadSettings(self):
        success = CC_LoadSettings(self.serial_no_c)
        if success is False:
            raise Exception('Failed to load settings.')

    def persistSettings(self):
        success = CC_PersistSettings(self.serial_no_c)
        if success is False:
            raise Exception('Failed to persist settings.')

    def requestSettings(self):
        err_code = CC_RequestSettings(self.serial_no_c)
        if err_code!=0:
            raise Exception('Failed to request settings. Error code {}'.format(err_code))


    #####################################
    # UTILITY FUNCTIONS
    def verboseMessage(self, message):
        print('Device {}, Ch. {} -- {}...'.format(self.serial_no, self.channel, message))

    def getRealValueFromDeviceUnit(self, deviceunit, unitType=0):
        realval = c_double(0.0)
        err_code = CC_GetRealValueFromDeviceUnit(self.serial_no_c, deviceunit, byref(realval), c_int(unitType))
        if err_code==0:
            return realval.value
        else:
            raise Exception('Failed to get real value from device unit.')

    def getDeviceUnitFromRealValue(self, realval, unitType=0):
        deviceunit = c_int(0)
        err_code = CC_GetDeviceUnitFromRealValue(self.serial_no_c, c_double(realval), byref(deviceunit), c_int(unitType))
        return deviceunit.value