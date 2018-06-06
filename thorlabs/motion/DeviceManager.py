from ctypes import cdll
from .. .ctools.tools import bind, null_function
import xml.etree.ElementTree as ET
from . import KCubeDCServo as kdc
from .tools import _supported_devices as supDv

lib = cdll.LoadLibrary(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.DeviceManager.dll")
_filepath = r'C:\Program Files\Thorlabs\Kinesis\ThorlabsDefaultSettings.xml'  # might need to upgrade how I do this


tree = ET.parse(_filepath)
root = tree.getroot()
root.getchildren()
deviceslist_et = root.getchildren()[1]
devicesettingslist_et = root.getchildren()[2]

# list device types by name
devicetype_to_id = dict()
for e in deviceslist_et.getchildren():
    name = e.attrib['Name']
    devicetype_to_id[name] = e.attrib['ID']

deviceslist = list(devicetype_to_id.keys())
    
devicesettingslist = []
for e in devicesettingslist_et.getchildren():
    name = e.attrib['Name']
    devicesettingslist.append(name)



class DeviceManager(object):

    def getDevicesList(self):
        return deviceslist

    def getDeviceSettingsList(self):
        return devicesettingslist

    def getAvailableSettings(self, devicename):
        """
        Return settings that are available for a given device name, such as KDC101.
        Inputs:
        devicename -- a string of name of the controller, such as KDC101, KSC101
        """
        if devicename not in list(devicetype_to_id.keys()):
            raise ValueError('Invalid device types. Get device types by .getDevicesList().')
        
        root = deviceslist_et.find("./DeviceType[@Name='{}']".format(devicename))
        root = root.getchildren()[0]

        settings = []
        for e in root.getchildren():
            name = e.attrib['Name']
            settings.append(name)
        
        return settings

    def getDeviceSettings(self, stagename):
        """
        Return all settings for a specify stage name.
        Inputs:
        stagename -- a string of a stage name. A list of stage name can be obtained from .getDeviceSettingsList() or .getAvailableSettings(devicename)
        Outputs:
        setting_dict -- a dictionary of settings for the stage name
        """
        assert stagename in devicesettingslist, "{} is not in the available device list of.".format(stagename)
        root = devicesettingslist_et.findall(".//DeviceSettingsDefinition[@Name='{}']".format(stagename))
        if len(root)>1:
            raise Exception("Found more than one matching of {}. There should be one. Contact the code author.".format(stagename))
        root = root[0]
                
        return extractor(root)


    def getDCPIDParams(self, settings_dict):
        """
        Inputs:
        settings_dict -- a dict of settings of a particular stage. settings_dict can be obtained from .getDeviceSettings(stagename)
        """
        params = dict()
        params['proportionalGain']  = settings_dict['DCServo']['DCProp']
        params['integralGain']      = settings_dict['DCServo']['DCInt']
        params['differentialGain']  = settings_dict['DCServo']['DCDiff']
        params['integralLimit']     = settings_dict['DCServo']['DCIntLim']
        params['parameterFilter']   = 15
        return params

    def getHomingParams(self, settings_dict):
        """
        Inputs:
        settings_dict -- a dict of settings of a particular stage. settings_dict can be obtained from .getDeviceSettings(stagename)
        """
        params = dict()
        params['direction'] = settings_dict['Home']['HomeDir']
        params['limitSwitch'] = settings_dict['Home']['HomeLimitSwitch']
        params['velocity'] = settings_dict['Home']['HomeVel']
        params['offsetDistance'] = settings_dict['Home']['HomeZeroOffset']
        return params

    def getMotorParams(self, settings_dict):
        """
        Inputs:
        settings_dict -- a dict of settings of a particular stage. settings_dict can be obtained from .getDeviceSettings(stagename)
        """
        motorparams = dict()
        motorparams['stepPerRev'] = settings_dict['Physical']['StepsPerRev']
        motorparams['gearboxRatio'] = settings_dict['Physical']['GearboxRatio']
        motorparams['pitch'] = settings_dict['Physical']['Pitch']
        return motorparams

    def getMotorTravelLimitsParams(self, settings_dict):
        """
        Inputs:
        settings_dict -- a dict of settings of a particular stage. settings_dict can be obtained from .getDeviceSettings(stagename)
        """
        limitparams = dict()
        limitparams['minPosition'] = settings_dict['Physical']['MinPos']
        limitparams['maxPosition'] = settings_dict['Physical']['MaxPos']
        return limitparams

    def getMotorVelocityLimitsParams(self, settings_dict):
        """
        Inputs:
        settings_dict -- a dict of settings of a particular stage. settings_dict can be obtained from .getDeviceSettings(stagename)
        """
        speedparams = dict()
        speedparams['maxVelocity'] = settings['Physical']['MaxVel']
        speedparams['maxAcceleration'] = settings['Physical']['MaxAccn']
        return speedparams

    def discoverByType(self, typename):
        '''
        Return a list of serial number of KDC101 devices connected to the computer.
        typename -- a name of the device type to discover. For supported device, call .supportedDevices().
        '''
        assert typename.lower() in self.supportedDevices(), 'typename must be a member of {}'.format(self.supportedDevices())
        result = kdc.discover(supDv.name_to_num[typename.lower()])
        return result

    def supportedDevices(self):
        return list(supDv.name_to_num.keys())

#############################################################
### Module's utilities functions

def extractor(root):
    """
    A recursive function to generate a deep dict from a XML tree.
    Inputs:
    root -- a starting XML element whose children will be converted into a dict.
    """
    result = dict()
    for child in root.getchildren():
        if len(child.getchildren())==0:
            try:
                result[child.tag] = float(child.text)
            except:
                result[child.tag] = child.text
        else:
            result[child.tag] = extractor(child)
    return result