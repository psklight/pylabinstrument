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
            OphirCOM.StartStream(self.device_handle, self.channel)
        else:
            raise Exception("Communication is already open.")

    def close(self):
        if self.device_handle is not None:
            OphirCOM.StopStream(self.device_handle, self.channel)
            OphirCOM.Close(self.device_handle)
            self.device_handle = None

    def measure(self, treat_data=True, max_attempt=1000):
        # if channel is None:
        #     channel = self.channel
        # OphirCOM.StartStream(self.device_handle, channel)
        # time.sleep(self.data_delay_time)
        count = 0
        while True:
            data = OphirCOM.GetData(self.device_handle, self.channel)
            # OphirCOM.StopStream(self.device_handle, channel)
            if treat_data:
                result = treat_data_func(data)
                if result.size!=0:
                    return result
                else:
                    count += 1
            else:
                return data
        return data


def treat_data_func(data):
    values = np.array(data[0])
    status = np.array(data[-1])
    where = np.argwhere(status==0)
    return np.squeeze(np.take(values, where))