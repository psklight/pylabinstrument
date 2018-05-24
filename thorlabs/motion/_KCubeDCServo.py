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
from .._enumeration import *
from .. import DeviceManager as dm

from comtypes import _safearray
import ctypes
from ctypes import byref, pointer
from time import sleep

lib = cdll.LoadLibrary(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.KCube.DCServo.dll")

class StructureEx(Structure):

    def getdict(self):
        return dict((f, getattr(self, f)) for f, _ in self._fields_)

    def loaddict(self, d):
        """
        d -- a dictionary of parameters. The keys of the dictionary much match the attributes of the class.
        """
        for f in d.keys():
            if not hasattr(self, f):
                raise AttributeError('Given dictionary has unmatched attributes.')
            for field, ctype in self._fields_:
                if field == f:
                    break
            if ctype in [c_short, c_long, c_int, c_int16, c_int32, c_uint, c_ushort, c_ulong]:
                setattr(self, f, ctype(int(d[f])))
            if ctype in [c_float, c_double]:
                setattr(self, f, ctype(float(d[f])))

# Define data structures
class TLI_DeviceInfo(StructureEx):
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


class TLI_HardwareInformation(StructureEx):
    _fields_ = [("serialNumber", c_dword),
                ("modelNumber", (8 * c_char)),
                ("type", c_word),
                ("firmwareVersion", c_dword),
                ("notes", (48 * c_char)),
                ("deviceDependantData", (12 * c_byte)),
                ("hardwareVersion", c_word),
                ("modificationState", c_word),
                ("numChannels", c_short)]


class MOT_VelocityParameters(StructureEx):
    _fields_ = [("minVelocity", c_int),
                ("acceleration", c_int),
                ("maxVelocity", c_int)]


class MOT_JogParameters(StructureEx):
    _fields_ = [("mode", MOT_JogModes),
                ("stepSize", c_uint),
                ("velParams", MOT_VelocityParameters),
                ("stopMode", MOT_StopModes)]


class MOT_HomingParameters(StructureEx):
    _fields_ = [("direction", MOT_TravelDirection),
                ("limitSwitch", MOT_HomeLimitSwitchDirection),
                ("velocity", c_uint),
                ("offsetDistance", c_uint)]


class MOT_LimitSwitchParameters(StructureEx):
    _fields_ = [("clockwiseHardwareLimit", MOT_LimitSwitchModes),
                ("anticlockwiseHardwareLimit", MOT_LimitSwitchModes),
                ("clockwisePosition", c_dword),
                ("anticlockwisePosition", c_dword),
                ("softLimitMode", MOT_LimitSwitchSWModes)]

class MOT_DC_PIDParameters(StructureEx):
    _fields_ = [("proportionalGain", c_int),
                ("integralGain", c_int),
                ("differentialGain", c_int),
                ("integralLimit", c_int),
                ("parameterFilter", c_word)]

class KMOT_MMIParams(StructureEx):
    _fields_ = [("JoystickMODE", c_int),
                ("JoystickMaxVelocity", c_int32),
                ("JoystickAcceleration", c_int32),
                ("JoystickDirectionSense", MOT_DirectionSense),
                ("PresetPos1", c_int32),
                ("PresetPos2", c_int32),
                ("DisplayIntensity", c_int16),
                ("reserved",6*c_int16)]

class KMOT_TriggerConfig(StructureEx):
    _fields_ = [("Trigger1Mode", c_int),
                ("Trigger1Polarity", c_int),
                ("Trigger2Mode", c_int),
                ("Trigger2Polarity", c_int)]

class KMOT_TriggerParams(StructureEx):
    _fields_ = [("TriggerStartPositionFwd", c_int32),
                ("TriggerIntervalFwd", c_int32),
                ("TriggerPulseCountFwd", c_int32),
                ("TriggerStartPositionRev", c_int32),
                ("TriggerIntervalRev", c_int32),
                ("TriggerPulseCountRev", c_int32),
                ("TriggerPulseWidth", c_int32),
                ("CycleCount", c_int32),
                ("reserved", 6*c_int32)]

BuildDeviceList = bind(lib, "TLI_BuildDeviceList", None, c_short)
GetDeviceListSize = bind(lib, "TLI_GetDeviceListSize", None, c_short)
# TLI_GetDeviceList = bind(lib, "TLI_GetDeviceList", [_safearray.tagSAFEARRAY], c_short)
# TLI_GetDeviceList  <- TODO: Implement SAFEARRAY first. BENCHTOPSTEPPERMOTOR_API short __cdecl TLI_GetDeviceList(SAFEARRAY** stringsReceiver);
# TLI_GetDeviceListByType  <- TODO: Implement SAFEARRAY first. BENCHTOPSTEPPERMOTOR_API short __cdecl TLI_GetDeviceListByType(SAFEARRAY** stringsReceiver, int typeID);
# TLI_GetDeviceListByTypes  <- TODO: Implement SAFEARRAY first. BENCHTOPSTEPPERMOTOR_API short __cdecl TLI_GetDeviceListByTypes(SAFEARRAY** stringsReceiver, int * typeIDs, int length);
GetDeviceListExt = bind(lib, "TLI_GetDeviceListExt", [POINTER(c_char), c_dword], c_short)
GetDeviceListByTypeExt = bind(lib, "TLI_GetDeviceListByTypeExt", [POINTER(c_char), c_dword, c_int], c_short)
GetDeviceListByTypesExt = bind(lib, "TLI_GetDeviceListByTypesExt", [POINTER(c_char), c_dword, POINTER(c_int), c_int], c_short)
GetDeviceInfo = bind(lib, "TLI_GetDeviceInfo", [POINTER(c_char), POINTER(TLI_DeviceInfo)], c_short)

# KDC specific functions
Open = bind(lib, "CC_Open", [POINTER(c_char)], c_short)
Close = bind(lib, "CC_Close", [POINTER(c_char)], c_short)
Identify = bind(lib, "CC_Identify", [POINTER(c_char)], None)

Home = bind(lib, "CC_Home", [POINTER(c_char)], c_short)
MoveToPosition = bind(lib, "CC_MoveToPosition", [POINTER(c_char), c_int], c_short)
StopProfiled = bind(lib, "CC_StopProfiled", [POINTER(c_char)], c_short)
StopImmediate = bind(lib, "CC_StopImmediate", [POINTER(c_char)], c_short)

RequestPosition = bind(lib, "CC_RequestPosition", [POINTER(c_char)], c_short)
GetPosition = bind(lib, "CC_GetPosition", [POINTER(c_char)], c_int)

GetVelParams = bind(lib, "CC_GetVelParams", [POINTER(c_char), POINTER(c_int), POINTER(c_int)], c_short)

GetRealValueFromDeviceUnit = bind(lib, "CC_GetRealValueFromDeviceUnit", [POINTER(c_char), c_int, POINTER(c_double), c_int], c_short)
GetDeviceUnitFromRealValue = bind(lib, "CC_GetDeviceUnitFromRealValue", [POINTER(c_char), c_double, POINTER(c_int), c_int], c_short)

GetHardwareInfoBlock = bind(lib, "CC_GetHardwareInfoBlock", [POINTER(c_char), POINTER(TLI_HardwareInformation)], c_short)

ClearMessageQueue = bind(lib, "CC_ClearMessageQueue", [POINTER(c_char)], None)

GetMotorParamsExt = bind(lib, "CC_GetMotorParamsExt", [POINTER(c_char), POINTER(c_double), POINTER(c_double), POINTER(c_double)], c_short)
GetMotorVelocityLimits = bind(lib, "CC_GetMotorVelocityLimits", [POINTER(c_char), POINTER(c_double), POINTER(c_double)], c_short)
GetMotorTravelMode = bind(lib, "CC_GetMotorTravelMode", [POINTER(c_char)], MOT_TravelModes)
GetMotorTravelLimits = bind(lib, "CC_GetMotorTravelLimits", [POINTER(c_char), POINTER(c_double), POINTER(c_double)], c_short)

SetMotorParamsExt = bind(lib, "CC_SetMotorParamsExt", [POINTER(c_char), c_double, c_double, c_double], c_short)
SetMotorTravelLimits = bind(lib, "CC_SetMotorTravelLimits", [POINTER(c_char), c_double, c_double], c_short)
SetMotorTravelMode = bind(lib, "CC_SetMotorTravelMode", [POINTER(c_char), MOT_TravelModes], c_short)
SetMotorVelocityLimits = bind(lib, "CC_SetMotorVelocityLimits", [POINTER(c_char), c_double, c_double], c_short)

RequestSettings = bind(lib, "CC_RequestSettings", [POINTER(c_char)], c_short)
ResetStageToDefaults = bind(lib, "CC_ResetStageToDefaults", [POINTER(c_char)], c_short)
LoadSettings = bind(lib, "CC_LoadSettings", [POINTER(c_char)], c_bool)
PersistSettings = bind(lib, "CC_PersistSettings", [POINTER(c_char)], c_bool)

CanHome = bind(lib, "CC_CanHome", [POINTER(c_char)], c_bool)

GetDCPIDParams = bind(lib, "CC_GetDCPIDParams", [POINTER(c_char), POINTER(MOT_DC_PIDParameters)], c_short)
SetDCPIDParams = bind(lib, "CC_SetDCPIDParams", [POINTER(c_char), POINTER(MOT_DC_PIDParameters)], c_short)

GetHomingParamsBlock = bind(lib, "CC_GetHomingParamsBlock", [POINTER(c_char), POINTER(MOT_HomingParameters)], c_short)
SetHomingParamsBlock = bind(lib, "CC_SetHomingParamsBlock", [POINTER(c_char), POINTER(MOT_HomingParameters)], c_short)