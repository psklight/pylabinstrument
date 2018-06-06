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
from .tools import _supported_devices as supDv
from . import KCubeDCServo as kdc
import warnings

operatingMode_dict = {'Manual': enum.SC_Manual, 'Single': enum.SC_Single, 'Auto': enum.SC_Auto, 'Triggered': enum.SC_Triggered}
#operatingMode_dict_reverse = {val: key for key, val in operatingMode_dict.items()}
operatingMode_dict_reverse = dict([ [val_c.value, key] for key, val_c in operatingMode_dict.items()])

operatingStates_dict = {'Active': enum.SC_Active, 'Inactive': enum.SC_Inactive, 'Open': enum.SC_Active, 'Closed': enum.SC_Inactive, 'On': enum.SC_Active, 'Off': enum.SC_Inactive }
operatingStates_dict_reverse = {val_c.value: key for key, val_c in operatingStates_dict.items()}

solenoidStates_dict = {'Open': enum.SC_SolenoidOpen, 'Closed': enum.SC_SolenoidClosed}
solenoidStates_dict_reverse = {val_c.value: key for key, val_c in solenoidStates_dict.items()}

class Motor(_motor.Motor):

    def __init__(self, serial_no, name=""):

        self._lockchange = False
        self._serial_no = serial_no
        self._verbose = True
        self.serial_no_c = c_char_p(bytes(str(serial_no), "utf-8"))
        self._library = K
        self._name = name

    def open(self):
        super().open()
        self.setOperatingMode('Manual')

    def shutterTo(self, state):
        if self.isInSession:
            self.setOperatingState(state)
        else:
            raise self.notInSessionMsg()

    def shutterOn(self):
        self.shutterTo('on')

    def shutterOff(self):
        self.shutterTo('off')

    ####################################################
    def getOperatingMode(self):
        if self.isInSession:
            mode = self.library.GetOperatingMode(self.serial_no_c)
            return operatingMode_dict_reverse[mode]
        else:
            raise self.notInSessionMsg()
            

    def setOperatingMode(self, mode):
        if self.isInSession:

            if type(mode)==type(' '):
                if mode.lower().capitalize() not in list(operatingMode_dict.keys()):
                    raise ValueError('Invalid mode. Mode must be in {}.'.format(operatingMode_dict.keys()))
                mode_in = mode
                mode = operatingMode_dict[mode.lower().capitalize()]

            if mode.value not in list(operatingMode_dict_reverse.keys()):
                raise ValueError('Invalid mode. Mode must be in {}.'.format(operatingMode_dict.keys()))

            self.verboseMessage('Setting operating mode to {}...'.format(mode_in))

            err_code = self.library.SetOperatingMode(self.serial_no_c, mode)

            if mode_in.lower() != "manual":
                warnings.warn('Given mode is not manual. The module only supports manual for now. The motor might not work as intended.')

            if err_code==0:
                self.verboseMessage('Done setting operating mode.')
            else:
                raise Exception('Failed to set operating mode. Error code {}.'.format(err_code))
        else:
            raise self.notInSessionMsg()
            

    def getOperatingState(self):
        if self.isInSession:
            state = self.library.GetOperatingState(self.serial_no_c)
            return operatingStates_dict_reverse[state]
        else:
            raise self.notInSessionMsg()

    def setOperatingState(self, state):
        if self.isInSession:
            self.verboseMessage('Setting operating state...')

            if type(state) == type(' '):
                if state.lower().capitalize() not in list(operatingStates_dict.keys()):
                    raise ValueError('Invalid operating state. Must be in {}.'.format(operatingStates_dict.keys()))
                state = operatingStates_dict[state.lower().capitalize()]

            if state.value not in list(operatingStates_dict_reverse.keys()):
                raise ValueError('Invalid operating state. Must be in {}.'.format(operatingStates_dict.keys()))

            err_code = self.library.SetOperatingState(self.serial_no_c, state)

            if err_code==0:
                self.verboseMessage('Done setting operating state.')
            else:
                raise Exception('Failed to set operating state. Error code {}.'.format(err_code))
        else:
            raise self.notInSessionMsg()
            

def discover(typename='ksc'):
    '''
    Return a list of serial number of KDC101 devices connected to the computer.
    Inputs:
    typename -- a name of the device type to discover. For supported device, call .supportedDevices(). The default is 'kdc' because of this class is for.
    '''
    result = kdc.discover(typename)
    return result

def supportedDevices():
    return kdc.supportedDevices()