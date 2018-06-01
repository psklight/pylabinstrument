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

# lib = cdll.LoadLibrary(r"C:\Program Files (x86)\IVI Foundation\VISA\WinNT\Bin\TLPM_32.dll")
lib = cdll.LoadLibrary(r"C:\Program Files\IVI Foundation\VISA\Win64\Bin\TLPM_64.dll")

from .._tool import bind, null_function
from ._visa_enum import *

Init = bind(lib, "TLPM_init", [ViRsrc, ViBoolean, ViBoolean, ViPSession], ViStatus)
Open = bind(lib, "TLPM_init", [ViRsrc, ViBoolean, ViBoolean, ViPSession], ViStatus)
Close = bind(lib , "TLPM_close", [ViSession], ViStatus)

FindResources = bind(lib, "TLPM_findRsrc", [ViSession, ViPUInt32], ViStatus)
GetResourceInfo = bind(lib, "TLPM_getRsrcInfo", [ViSession, ViUInt32, 256*ViChar, 256*ViChar, 256*ViChar, POINTER(ViBoolean)], ViStatus)
GetResourceName = bind(lib, "TLPM_getRsrcName", [ViSession, ViUInt32, 256*ViChar], ViStatus)

ErrorMessage = bind(lib, "TLPM_errorMessage", [ViSession, ViStatus, c_char_p], ViStatus)