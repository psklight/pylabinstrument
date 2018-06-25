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
    ARRAY
)

c_word = c_ushort
c_dword = c_ulong


lib = cdll.LoadLibrary(r"C:\Program Files\IVI Foundation\VISA\Win64\Bin\TLCCS_64.dll")

from ....ctools.tools import bind, null_function
from ....ctools._visa_enum import *

Init = bind(lib, "tlccs_init", [ViRsrc, ViBoolean, ViBoolean, ViPSession], ViStatus)
Open = bind(lib, "tlccs_init", [ViRsrc, ViBoolean, ViBoolean, ViPSession], ViStatus)
Close = bind(lib, "tlccs_close", [ViSession], ViSession)

GetDeviceStatus = bind(lib, "tlccs_getDeviceStatus", [ViSession, POINTER(c_int32)], ViStatus)

StartScan = bind(lib, "tlccs_startScan", [ViSession], ViStatus)

GetScanData = bind(lib, "tlccs_getScanData", [ViSession, POINTER(c_double)], ViStatus)
GetWavelengthData = bind(lib, "tlccs_getWavelengthData", [ViSession, c_int16, POINTER(c_double), POINTER(c_double), POINTER(c_double)], ViStatus)

GetIntegrationTime = bind(lib, "tlccs_getIntegrationTime", [ViSession, POINTER(c_double)], ViStatus)
SetIntegrationTime = bind(lib, "tlccs_setIntegrationTime", [ViSession, c_double], ViStatus)