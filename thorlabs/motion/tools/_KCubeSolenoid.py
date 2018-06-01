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

from .. ..ctools.tools import bind, null_function
from ._enumeration import *
from .. import DeviceManager as dm

from comtypes import _safearray
import ctypes
from ctypes import byref, pointer
from time import sleep

lib = cdll.LoadLibrary(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.KCube.Solenoid.dll")

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


class SC_CycleParameters(StructureEx):
    _fields_ = [('openTime', c_uint),
                ('closedTime', c_uint),
                ('numCycles', c_uint)]

class KSC_MMIParams(StructureEx):
    _fields_ = [('unused', 10*c_int16),
                ('DisplayIntensity', c_int16),
                ('reserved', 6*c_int16)]


class KSC_TriggerConfig(StructureEx):
    _fields_ = [('Trigger1Mode', KSC_TriggerPortMode),
                ('Trigger1Polarity', KSC_TriggerPortPolarity),
                ('Trigger2Mode', KSC_TriggerPortMode),
                ('Trigger2Polarity', KSC_TriggerPortPolarity),
                ('reserved', 6*c_int16)]

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

Open = bind(lib, "SC_Open", [POINTER(c_char)], c_short)
Close = bind(lib, "SC_Close", [POINTER(c_char)], None)

Identify = bind(lib, "SC_Identify", [POINTER(c_char)], None)

GetOperatingMode = bind(lib, "SC_GetOperatingMode", [POINTER(c_char)], SC_OperatingModes)
SetOperatingMode = bind(lib, "SC_SetOperatingMode", [POINTER(c_char), SC_OperatingModes], c_short)

GetOperatingState = bind(lib, "SC_GetOperatingState", [POINTER(c_char)], SC_OperatingStates)
SetOperatingState = bind(lib, "SC_SetOperatingState", [POINTER(c_char), SC_OperatingStates], c_short)

GetSolenoidState = bind(lib, "SC_GetSolenoidState", [POINTER(c_char)], SC_SolenoidStates)

ClearMessageQueue = bind(lib, "SC_ClearMessageQueue", [POINTER(c_char)], None)

LoadSettings = bind(lib, "SC_LoadSettings", [POINTER(c_char)], c_bool)
RequestSettings = bind(lib, "SC_RequestSettings", [POINTER(c_char)], c_short)