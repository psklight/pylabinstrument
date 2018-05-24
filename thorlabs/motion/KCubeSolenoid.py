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

operatingMode_dict = {'Manual': enum.SC_Manual, 'Single': enum.SC_Single, 'Auto': enum.SC_Auto, 'Triggered': enum.Triggered}
operatingMode_dict_reverse = {(val, key) for key, val in operatingMode_dict.items()}

operatingStates_dict = {'Active': enum.SC_Active, 'Inactive': enum.SC_Inactive}
operatingStates_dict_reverse = {(val, key) for key, val in operatingStates_dict.items()}

solenoidStates_dict = {'Open': enum.SC_SolenoidOpen, 'Closed': enum.SC_SelenoidClosed}
solenoidStates_dict_reverse = {(val, key) for key, val in solenoidStates_dict.items()}

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
    def getOperatingMode(self):
        mode = self.lib.GetOperatingMode(self.serial_no_c)
        return operatingMode_dict_reverse[mode]

    def setOperatingMode(self, mode):

        if self._verbose:
            self.verboseMessage('Setting operating mode...')

        if type(mode)==type(' '):
            if mode.lower().capitalize() not in list(operatingMode_dict.keys()):
                raise ValueError('Invalid mode. Mode must be in {}.'.format(operatingMode_dict.keys()))
            mode = operatingMode_dict[mode.lower().capitalize()]

        if mode not in list(operatingMode_dict_reverse.keys()):
            raise ValueError('Invalid mode. Mode must be in {}.'.format(operatingMode_dict.keys()))

        err_code = self.lib.SetOperatingMode(self.serial_no_c, mode)

        if err_code==0:
            if self._verbose:
                self.verboseMessage('Done setting operating mode.')
        else:
            raise Exception('Failed to set operating mode. Error code {}.'.format(err_code))

    def getOperatingState(self):
        state = self.lib.GetOperatingState(self.serial_no_c)
        return operatingStates_dict_reverse[state]

    def setOperatingState(self, state):

        if self._verbose:
            self.verboseMessage('Setting operating state...')

        if type(state) == type(' '):
            if state.lower().capitalize() not in list(operatingStates_dict.keys()):
                raise ValueError('Invalid operating state. Must be in {}.'.format(operatingStates_dict.keys()))
            state = operatingStates_dict[state.lower().capitalize()]

        if state not in list(operatingStates_dict_reverse.keys()):
            raise ValueError('Invalid operating state. Must be in {}.'.format(operatingStates_dict.keys()))

        err_code = self.lib.SetOperatingState(self.serial_no_c, state)

        if err_code==0:
            if self._verbose:
                self.verboseMessage('Done setting operating state.')
        else:
            raise Exception('Failed to set operating state. Error code {}.'.format(err_code))

    def getSolenoidState(self):
        state = self.lib.GetSolenoidState(self.serial_no_c)
        return solenoidStates_dict_reverse[state]