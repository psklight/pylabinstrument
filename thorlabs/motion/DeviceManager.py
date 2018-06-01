from ctypes import cdll
from .. .ctools.tools import bind, null_function
import xml.etree.ElementTree as ET

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

def getAvailableSettings(devicename):
    if devicename not in list(devicetype_to_id.keys()):
        raise ValueError('Invalid device types.')
    
    root = deviceslist_et.find("./DeviceType[@Name='{}']".format(devicename))
    root = root.getchildren()[0]

    settings = []
    for e in root.getchildren():
        name = e.attrib['Name']
        settings.append(name)
    
    return settings

def extractor(root):
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

def getDeviceSettings(stagename):
    assert stagename in devicesettingslist, "{} is not in the available device list of.".format(stagename)
    root = devicesettingslist_et.findall(".//DeviceSettingsDefinition[@Name='{}']".format(stagename))
    if len(root)>1:
        raise Exception("Found more than one matching of {}. There should be one. Contact the code author.".format(stagename))
    root = root[0]
            
    return extractor(root)

def getDCPIDParams(settings_dict):
    params = dict()
    params['proportionalGain']  = settings_dict['DCServo']['DCProp']
    params['integralGain']      = settings_dict['DCServo']['DCInt']
    params['differentialGain']  = settings_dict['DCServo']['DCDiff']
    params['integralLimit']     = settings_dict['DCServo']['DCIntLim']
    params['parameterFilter']   = 15
    return params

def getHomingParams(settings_dict):
    params = dict()
    params['direction'] = settings_dict['Home']['HomeDir']
    params['limitSwitch'] = settings_dict['Home']['HomeLimitSwitch']
    params['velocity'] = settings_dict['Home']['HomeVel']
    params['offsetDistance'] = settings_dict['Home']['HomeZeroOffset']
    return params

def getMotorParams(settings_dict):
    motorparams = dict()
    motorparams['stepPerRev'] = settings_dict['Physical']['StepsPerRev']
    motorparams['gearboxRatio'] = settings_dict['Physical']['GearboxRatio']
    motorparams['pitch'] = settings_dict['Physical']['Pitch']
    return motorparams

def getMotorTravelLimitsParams(settings_dict):
    limitparams = dict()
    limitparams['minPosition'] = settings_dict['Physical']['MinPos']
    limitparams['maxPosition'] = settings_dict['Physical']['MaxPos']
    return limitparams

def getMotorVelocityLimitsParams(settings_dict):
    speedparams = dict()
    speedparams['maxVelocity'] = settings['Physical']['MaxVel']
    speedparams['maxAcceleration'] = settings['Physical']['MaxAccn']
    return speedparams