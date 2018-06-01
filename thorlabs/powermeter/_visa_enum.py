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


ViStatus = c_long
ViRsrc = c_char_p
ViBoolean = c_int
ViSession = c_long
ViPSession = POINTER(c_long)
ViPUInt32 = POINTER(c_uint32)
ViUInt32 = c_uint32
ViChar = c_char
