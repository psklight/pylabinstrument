import pandas as pd
import re
import numpy as np
import time

import seabreeze.spectrometers as sb


def get_device_list():
    devices = sb.list_devices()


class Spectrometer(sb.Spectrometer):

    def __init__(self, device_name):
        super().__init__(self, device_name)

    def set_integration_time(self, time_ms):
        """
        Set integration time.
        :param time_ms: number of time in millisecond
        """
        self.integration_time_micros(time_ms*1000.0)

    def get_wavelength(self):
        return self.wavelengths()

    def measure(self):
        return self.intensities()

    def measure_average(self, n=1, wait=0.1):
        assert n>1, 'n must be more than 0.'
        assert wait>=0.0, 'wait must be equal to or more than 0.'
        wl = self.get_wavelength()
        spec_read = np.zeros(shape=wl.shape)
        for i in range(0, n):
            spec_read += self.measure()
            time.sleep(wait)
        spec_read = spec_read/n
        spec_bg_df = pd.DataFrame({'wavelength': wl, 'count': spec_bg})
        return spec_read


def load_spectrum_OceanView(filename, wlmin=None, wlmax=None, rename_column=True):
    """
    Load spectral data captured by Ophir's OceanView. The header lines are detected using a phrase "Begin Spectral Data". The first column of the data is assumed to be wavelength.
    :param filename: filepath to the file to be loaded
    :param wlmin: min value of wavelength to filter when loaded
    :param wlmax: max value of wavelength to filter when loaded
    :param rename_column: If True, rename columns to ['wavelength', 'spectral power density']. If a list, rename to that list.
    :return:
    """
    # eliminate metadata at the beginning
    with open(filename, 'r') as f:
        count = 0
        while re.search("Begin Spectral Data", f.readline()) is None:
            count += 1

    data = pd.read_csv(filename, sep="\t", skiprows=count, header=None)

    if wlmin is None:
        wlmin = data[0].min()

    if wlmax is None:
        wlmax = data[0].max()

    data = data.loc[data[0].between(wlmin, wlmax)]

    if rename_column is True:
        data.columns = ['wavelength', 'spectral power density']
    if isinstance(rename_column, list):
        data.columns = rename_column

    return data