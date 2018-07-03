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
    c_uint32
)

c_word = c_ushort
c_dword = c_ulong


from ....locateDll import locateDll
libname = "TLPM_64.dll"
foldername = "IVI Foundation"
dllpath  = locateDll(libname,  foldername)
lib = cdll.LoadLibrary(dllpath.replace("\\","\\\\"))



from ....ctools.tools import bind, null_function
from ....ctools._visa_enum import *

Init = bind(lib, "TLPM_init", [ViRsrc, ViBoolean, ViBoolean, ViPSession], ViStatus)
Open = bind(lib, "TLPM_init", [ViRsrc, ViBoolean, ViBoolean, ViPSession], ViStatus)
Close = bind(lib , "TLPM_close", [ViSession], ViStatus)

FindResources = bind(lib, "TLPM_findRsrc", [ViSession, ViPUInt32], ViStatus)
GetResourceInfo = bind(lib, "TLPM_getRsrcInfo", [ViSession, ViUInt32, 256*ViChar, 256*ViChar, 256*ViChar, POINTER(ViBoolean)], ViStatus)
GetResourceName = bind(lib, "TLPM_getRsrcName", [ViSession, ViUInt32, 256*ViChar], ViStatus)

# Utility
ErrorMessage = bind(lib, "TLPM_errorMessage", [ViSession, ViStatus, c_char_p], ViStatus)
SetTimeout = bind(lib, "TLPM_setTimeoutValue", [ViSession, ViUInt32], ViStatus)
GetTimeout = bind(lib, "TLPM_getTimeoutValue", [ViSession, POINTER(ViUInt32)], ViStatus)

# Measure --> Configure --> Average
SetAvgTime = bind(lib, "TLPM_setAvgTime", [ViSession, ViReal64], ViStatus)
GetAvgTime = bind(lib, "TLPM_getAvgTime", [ViSession, ViInt16, POINTER(ViReal64)], ViStatus)
SetAvgCount = bind(lib, "TLPM_setAvgCnt", [ViSession, ViInt16], ViStatus)
GetAvgCount = bind(lib, "TLPM_getAvgCnt", [ViSession, POINTER(ViInt16)], ViStatus)

# Measure --> Configure --> Correction
SetAttn = bind(lib, "TLPM_setAttenuation", [ViSession, ViReal64], ViStatus)
GetAttn = bind(lib, "TLPM_getAttenuation", [ViSession, ViInt16, POINTER(ViReal64)], ViStatus)
SetWavelength = bind(lib, "TLPM_setWavelength", [ViSession, ViReal64])
GetWavelength = bind(lib, "TLPM_getWavelength", [ViSession, ViInt16, POINTER(ViReal64)], ViStatus)
StartDarkAdjust = bind(lib, "TLPM_startDarkAdjust", [ViSession], ViStatus)
CancelDarkAdjust = bind(lib, "TLPM_cancelDarkAdjust", [ViSession], ViStatus)
GetDarkAdjustState = bind(lib, "TLPM_getDarkAdjustState", [ViSession, POINTER(ViInt16)], ViStatus)
GetDarkOffset = bind(lib, "TLPM_getDarkOffset", [ViSession, POINTER(ViReal64)], ViStatus)

# Measure --> Configure --> Power Measurement
SetPowerAutoRange = bind(lib, "TLPM_setPowerAutoRange", [ViSession, ViBoolean], ViStatus)
GetPowerAutoRange = bind(lib, "TLPM_getPowerAutorange", [ViSession, POINTER(ViBoolean)], ViStatus)

SetPowerRange = bind(lib, "TLPM_setPowerRange", [ViSession, ViReal64], ViStatus)
GetPowerRange = bind(lib, "TLPM_getPowerRange", [ViSession, ViInt16, POINTER(ViReal64)], ViStatus)

SetPowerUnit = bind(lib, "TLPM_setPowerUnit", [ViSession, ViInt16], ViStatus)
GetPowerUnit = bind(lib, "TLPM_getPowerUnit", [ViSession, POINTER(ViInt16)], ViStatus)

# Measure --> Read
MeasurePower = bind(lib, "TLPM_measPower", [ViSession, POINTER(ViReal64)], ViStatus)
