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
from .tools import _KCubeDCServo as K
from .tools import _motor


class Motor(_motor.Motor):

    def __init__(self, serial_no, channel=1):

        self._lockchange = False
        self._serial_no = serial_no
        self._channel = channel
        self._verbose = True

        self.serial_no_c = c_char_p(bytes(str(serial_no), "utf-8"))
        self.channel_c = c_short(channel)

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
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        assert self._lockchange is False, "The motor instance is open. Close the motor first befor changing serial number or channel."
        self._channel = value
        self.channel_c = c_short(value)

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

    def get_channel_c(self):
        return self._channel_c

    def set_channel_c(self, value):
        self._channel_c = value

    channel_c = property(get_channel_c, set_channel_c)


    #################################################
    def open(self):
        self.verboseMessage('Opening...')

        err_code = self.library.Open(self.serial_no_c, self.channel_c)
        if err_code==0:
            self._lockchange = True
            self.isInSession = True
            self.library.ClearMessageQueue(self.serial_no_c)
            self.loadSettings()  # for, for example, convert real and device unit
            self.verboseMessage('Opening done.')
        else:
            raise Exception('Failed to open and establish connection with device. Error code {}.'.format(err_code))

    def close(self):
        self.verboseMessage('Closing...')
        self.library.Close(self.serial_no_c)
        self._lockchange = False
        self.isInSession = False
        self.verboseMessage('Closing done.')


    def home(self):
        if self.isInSession:
            canhome = self.library.CanHome(self.serial_no_c)
            if canhome:
                self.verboseMessage('Homing')
                err_code = self.library.Home(self._serial_no_c)
                if err_code==0:
                    pass
                else:
                    raise Exception('Error when homing. Error code {}.'.format(err_code))
            else:
                print('Device cannot perform home.')
        else:
            raise self.notInSessionMsg()

    def moveToPosition(self, realpos):
        if self.isInSession:
            self.verboseMessage('Moving to position')
            err_code = self.library.MoveToPosition(self.serial_no_c, self.getDeviceUnitFromRealValue(realpos))
            if err_code==0:
                pass
            else:
                raise Exception('Error trying to move. Error code {}'.format(err_code))
        else:
            raise self.notInSessionMsg()


    def getPosition(self):
        if self.isInSession:
            err_code = self.library.RequestPosition(self.serial_no_c)
            if err_code is not 0:
                raise Exception('Error in requesting position. Error code {}'.format(err_code))
            sleep(0.1)
            devicepos = self.library.GetPosition(self.serial_no_c)
            return self.getRealValueFromDeviceUnit(devicepos, unitType=0)
        else:
            raise self.notInSessionMsg()
            

    def stop(self):
        if self.isInSession:
            err_code = self.library.StopProfiled(self.serial_no_c)
            if err_code!=0:
                raise Exception('Failed to stop. Error code {}.'.format(err_code))
        else:
            raise self.notInSessionMsg()
            

    def stopImmediate(self):
        if self.isInSession:
            err_code = self.library.StopImmediate(self.serial_no_c)
            if err_code!=0:
                raise Exception('Failed to stop. Error code {}'.format(err_code))
        else:
            raise self.notInSessionMsg()
            

    #####################################

    def getVelParams(self):
        if self.isInSession:
            acc = c_int(0)
            maxvel = c_int(0)
            err_code = self.library.GetVelParams(self.serial_no_c, byref(acc), byref(maxvel))
            if err_code==0:
                return {'acceleration': acc.value, 'maxVelocity': maxvel.value}
            else:
                raise Exception('Error when getting velocity parameters. Error code {}'.format(err_code))
        else:
            raise self.notInSessionMsg()
            

    def getMotorParams(self):
        if self.isInSession:
            params = dict()
            stepperrev = c_double(0.0)
            gearboxratio = c_double(0.0)
            pitch = c_double(0.0)
            err_code = self.library.GetMotorParamsExt(self.serial_no_c, byref(stepperrev), byref(gearboxratio), byref(pitch))
            if err_code==0:
                params['stepPerRev'] = stepperrev.value
                params['gearboxRatio'] = gearboxratio.value
                params['pitch'] = pitch.value
                return params
            else:
                raise Exception('Failed to get motor parameter using self.library.GetMotorParamsExt. Error code {}'.format(err_code))
        else:
            raise self.notInSessionMsg()
        

    def setMotorParams(self, params):
        if self.isInSession:
            stepperrev = c_double(params['stepPerRev'])
            gearboxratio = c_double(params['gearboxRatio'])
            pitch = c_double(params['pitch'])
            err_code = self.library.SetMotorParamsExt(self.serial_no_c, stepperrev, gearboxratio, pitch)
            if err_code!=0:
                raise Exception('Failed to set motor parameters. Error code {}'.format(err_code))
        else:
            raise self.notInSessionMsg()
            

    def getMotorTravelMode(self):
        if self.isInSession:
            travelmode = self.library.GetMotorTravelMode(self.serial_no_c)
            return travelmode
        else:
            raise self.notInSessionMsg()
            

    def setMotorTravelMode(self, mode):
        assert mode in [0,1,2], "mode must be either 0 (undefined), 1 (linear), or 2 (rotational)"
        if self.isInSession:
            err_code = self.library.SetMotorTravelMode(c_int(mode))
        else:
            raise self.notInSessionMsg()
        

    def getMotorTravelLimits(self):
        if self.isInSession:
            minPosition = c_double(0.0)
            maxPosition = c_double(0.0)
            err_code = self.library.GetMotorTravelLimits(self.serial_no_c, byref(minPosition), byref(maxPosition))
            if err_code==0:
                return {'minPosition': minPosition, 'maxPosition': maxPosition}
            else:
                raise Exception('Failed to get motor travel limits. Error code {}.'.format(err_code))
        else:
            raise self.notInSessionMsg()
            

    def setMotorTravelLimits(self, params):
        if self.isInSession:
            minpos = c_double(float(params['minPosition']))
            maxpos = c_double(float(params['maxPosition']))
            err_code = self.library.SetMotorTravelLimits(self.serial_no_c, minpos, maxpos)
            if err_code!=0:
                raise Exception('Failed to set motor travel limits. Error code {}'.format(err_code))
        else:
            raise self.notInSessionMsg()
        

    def getMotorVelocityLimits(self):
        if self.isInSession:
            maxVelocity = c_double(0.0)
            maxAcceleration = c_double(0.0)
            err_code = self.library.GetMotorVelocityLimits(self.serial_no_c, byref(maxVelocity), byref(maxAcceleration))
            if err_code==0:
                return {'maxVelocity': maxVelocity.value, 'maxAcceleration': maxAcceleration.value}
            else:
                raise Exception('Failed to get motor velocity limit. Error code {}.'.format(err_code))
        else:
            raise self.notInSessionMsg()
            

    def setMotorVelocityLimits(self, params):
        if self.isInSession:
            maxvel = c_double(float(params['maxVelocity']))
            maxacc = c_double(float(params['maxAcceleration']))
            err_code = self.library.SetMotorVelocityLimits(self.serial_no_c, maxvel, maxacc)
            if err_code!=0:
                raise Exception('Failed to set motor velocity limits. Error code {}'.format(err_code))
        else:
            raise self.notInSessionMsg()


    def getDCPIDParams(self):
        if self.isInSession:
            params_c = self.library.MOT_DC_PIDParameters()
            err_code = self.library.GetDCPIDParams(self.serial_no_c, byref(params_c))
            if err_code==0:
                return params_c.getdict()
            else:
                raise Exception('Failed to get DC PID params. Error code {}.'.format(err_code))
        else:
            raise self.notInSessionMsg()
        

    def setDCPIDParams(self, params):
        if self.isInSession:
            param_c = self.library.MOT_DC_PIDParameters()
            param_c.loaddict(params)
            self.verboseMessage("Setting DC PID params...")
            err_code = self.library.SetDCPIDParams(self.serial_no_c, byref(param_c))
            if err_code==0:
                self.verboseMessage("Done setting DC PID params.")
            else:
                raise Exception('Failed to set DC PID params. Error code {}.'.format(err_code))
        else:
            raise self.notInSessionMsg()
        

    def getHomingParams(self):
        if self.isInSession:
            param_c = self.library.MOT_HomingParameters()
            err_code = self.library.GetHomingParamsBlock(self.serial_no_c, byref(param_c))
            if err_code==0:
                return param_c.getdict()
            else:
                raise Exception('Failed to get homing parameters. Error code {}.'.format(err_code))
        else:
            raise self.notInSessionMsg()
        

    def setHomingParams(self, params):
        if self.isInSession:
            param_c = self.library.MOT_HomingParameters()
            param_c.loaddict(params)
            self.verboseMessage("Setting homing params...")
            err_code = self.library.SetHomingParamsBlock(self.serial_no_c, byref(param_c))
            if err_code==0:
                self.verboseMessage("Done setting homing params.")
            else:
                raise Exception('Failed to set homing parameters. Error code {}.'.format(err_code))
        else:
            raise self.notInSessionMsg()
            

    #####################################
    # UTILITY FUNCTIONS


def discover():
    '''
    Return a list of serial number of KDC101 devices connected to the computer.
    '''
    err_code = K.BuildDeviceList()
    if err_code==0:
        n = K.GetDeviceListSize()
        size = 512
        sbuffer = ctypes.create_string_buffer(b"",size)
        err_code = K.GetDeviceListByTypeExt(sbuffer, c_dword(size), c_int(27))
        if err_code==0:
            pbuffer = sbuffer.value
            serialList = pbuffer.decode('UTF-8').strip(',').split(',')
            return serialList
        else:
            raise Exception('Failed to get device list by type. Error code: {}.'.format(err_code))
    else:
        raise Exception('Failed to build device list. Error code: {}.'.format(err_code))

def identify(serial_no):
    motor = Motor(serial_no)
    motor.verbose = False
    motor.open()
    # K.Identify(c_char_p(bytes(str(serialNo), "utf-8")))
    motor.identify()
    motor.close()
