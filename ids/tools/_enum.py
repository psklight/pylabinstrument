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
    ARRAY
)

c_word = c_ushort
c_dword = c_ulong

############################################################
### TYPES
HIDS = c_dword
HWND = c_long

#############################################################
###  ERROR CODES

NO_SUCCESS  = -1
SUCCESS = 0
IO_REQUEST_FAILED = 2
CANT_OPEN_DEVICE = 3
INVALID_PARAMETER = 125
ACCESS_VIOLATION = 129
