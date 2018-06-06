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

from .tools import _enumeration as enum
from time import sleep
from .tools import _KCubeSolenoid as K
from .tools import _motor

operatingMode_dict = {'Manual': enum.SC_Manual, 'Single': enum.SC_Single, 'Auto': enum.SC_Auto, 'Triggered': enum.SC_Triggered}
#operatingMode_dict_reverse = {val: key for key, val in operatingMode_dict.items()}
operatingMode_dict_reverse = dict([ [val_c.value, key] for key, val_c in operatingMode_dict.items()])

operatingStates_dict = {'Active': enum.SC_Active, 'Inactive': enum.SC_Inactive}
operatingStates_dict_reverse = {val_c.value: key for key, val_c in operatingStates_dict.items()}

solenoidStates_dict = {'Open': enum.SC_SolenoidOpen, 'Closed': enum.SC_SolenoidClosed}
solenoidStates_dict_reverse = {val_c.value: key for key, val_c in solenoidStates_dict.items()}

class Motor(_motor.Motor):

    def __init__(self, serial_no):

        self._lockchange = False
        self._serial_no = serial_no
        self._verbose = True

        self.serial_no_c = c_char_p(bytes(str(serial_no), "utf-8"))

        self._library = K

    @property
    def library(self):
        return self._library
    
    @library.setter
    def library(self, lib):
        self._library = lib

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
        mode = self.library.GetOperatingMode(self.serial_no_c)
        return operatingMode_dict_reverse[mode]

    def setOperatingMode(self, mode):

        if self._verbose:
            self.verboseMessage('Setting operating mode...')

        if type(mode)==type(' '):
            if mode.lower().capitalize() not in list(operatingMode_dict.keys()):
                raise ValueError('Invalid mode. Mode must be in {}.'.format(operatingMode_dict.keys()))
            mode = operatingMode_dict[mode.lower().capitalize()]

        if mode.value not in list(operatingMode_dict_reverse.keys()):
            raise ValueError('Invalid mode. Mode must be in {}.'.format(operatingMode_dict.keys()))

        err_code = self.library.SetOperatingMode(self.serial_no_c, mode)

        if err_code==0:
            if self._verbose:
                self.verboseMessage('Done setting operating mode.')
        else:
            raise Exception('Failed to set operating mode. Error code {}.'.format(err_code))

    def getOperatingState(self):
        state = self.library.GetOperatingState(self.serial_no_c)
        return operatingStates_dict_reverse[state]

    def setOperatingState(self, state):

        if self._verbose:
            self.verboseMessage('Setting operating state...')

        if type(state) == type(' '):
            if state.lower().capitalize() not in list(operatingStates_dict.keys()):
                raise ValueError('Invalid operating state. Must be in {}.'.format(operatingStates_dict.keys()))
            state = operatingStates_dict[state.lower().capitalize()]

        if state.value not in list(operatingStates_dict_reverse.keys()):
            raise ValueError('Invalid operating state. Must be in {}.'.format(operatingStates_dict.keys()))

        err_code = self.library.SetOperatingState(self.serial_no_c, state)

        if err_code==0:
            if self._verbose:
                self.verboseMessage('Done setting operating state.')
        else:
            raise Exception('Failed to set operating state. Error code {}.'.format(err_code))

    # def getSolenoidState(self):
    #     self.library.RequestSettings(self.serial_no_c)
    #     sleep(0.1)
    #     self.library.LoadSettings(self.serial_no_c)
    #     state = self.library.GetSolenoidState(self.serial_no_c)
    #     return state