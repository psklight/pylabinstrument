import win32com.client
import time
import numpy as np

print("Performaing client dispatch to OphirLMMeasurement.CoLMMeasurement")
try:
    OphirCOM = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
except:
    raise Exception("Failed to perform client dispatch. Make sure ophir devices and drivers are properly installed and connected.")


def get_devicelist():
    OphirCOM.StopAllStreams()
    OphirCOM.CloseAll()
    # Scan for connected Devices
    device_list = OphirCOM.ScanUSB()
    return device_list


def close_all():
    OphirCOM.CloseAll()


def stop_all_streams():
    OphirCOM.StopAllStreams()


class OphirPM:

    def __init__(self, serial_no, channel=0, data_delay_time=0.2):
        self.serial_no = serial_no
        self.channel = channel
        self.device_handle = None
        self.data_delay_time = data_delay_time

    def open(self):
        if self.device_handle is None:
            self.device_handle = OphirCOM.OpenUSBDevice(self.serial_no)
        else:
            raise Exception("Communication is already open.")

    def close(self):
        if self.device_handle is not None:
            OphirCOM.Close(self.device_handle)
            self.device_handle = None

    def measure(self, channel=None, treat_data=True):
        if channel is None:
            channel = self.channel
        OphirCOM.StartStream(self.device_handle, channel)
        time.sleep(self.data_delay_time)
        data = OphirCOM.GetData(self.device_handle, channel)
        OphirCOM.StopStream(self.device_handle, channel)
        if treat_data:
            return treat_data_func(data)
        else:
            return data


def treat_data_func(data):
    values = np.array(data[0])
    status = np.array(data[-1])
    where = np.argwhere(status==0)
    return np.squeeze(np.take(values, where))