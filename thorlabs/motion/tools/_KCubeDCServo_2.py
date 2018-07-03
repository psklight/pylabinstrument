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
# from .. import DeviceManager as dm

from comtypes import _safearray
import ctypes
from ctypes import byref, pointer
from time import sleep

libname0 = "Thorlabs.MotionControl.DeviceManager.dll"
libname = "Thorlabs.MotionControl.KCube.DCServo.dll"
foldername = "Thorlabs"

from .... import locateDlls
dllpath0 = locateDlls.locateDll(libname0, foldername)
dllpath  = locateDlls.locateDll(libname,  foldername)
print(dllpath0.replace("\\","\\\\"))
lib0 = cdll.LoadLibrary(dllpath0.replace("\\","\\\\"))
lib = cdll.LoadLibrary(dllpath.replace("\\","\\\\"))