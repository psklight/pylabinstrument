import win32com.client
import time

print("Performaing client dispatch to OphirLMMeasurement.CoLMMeasurement")
try:
    OphirCOM = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
except:
    raise Exception("Failed to perform client dispatch. Make sure ophir devices and drivers are properly installed and connected.")

def getDeviceList():
    OphirCOM.StopAllStreams()
    OphirCOM.CloseAll()
    # Scan for connected Devices
    device_list = OphirCOM.ScanUSB()
    return device_list

class OphirPM():

    def __init__(self, serial_no, channel=0, data_delay_time=0.2):
        self.serial_no = serial_no
        self.channel = channel
        self.device_handle = OphirCOM.OpenUSBDevice(serial_no)
        self.data_delay_time = data_delay_time

    def get_data(self, channel=None):
        if channel is None:
            channel = self.channel
        OphirCOM.StartStream(self.device_handle, channel)
        time.sleep(self.data_delay_time)
        data = OphirCOM.GetData(self.device_handle, channel)
        OphirCOM.StopStream(self.device_handle, channel)
        return data