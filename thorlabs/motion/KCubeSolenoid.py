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

from .. import _enumeration as enum
from time import sleep
from . import _KCubeSolenoid as K
from . import _motor

class Motor(_motor.Motor):

    def __init__(self, serial_no):

        self._lockchange = False
        self._serial_no = serial_no
        self._verbose = True

        self.serial_no_c = c_char_p(bytes(str(serial_no), "utf-8"))

        self.lib = K

    @property
    def serial_no(self):
        return self._serial_no

    @serial_no.setter
    def serial_no(self, value):
        assert self._lockchange is False, "The motor instance is open. Close the motor first befor changing serial number or channel."
        self._serial_no = value
        self.serial_no_c = c_char_p(bytes(str(serial_no), "utf-8"))

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

    ####################################################