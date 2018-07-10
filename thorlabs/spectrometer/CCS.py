from ctypes import (
	byref
	)
import ctypes

from ...ctools import _visa_enum as enum
from .tools import _TLCCS_wrapper as K
from ..templates.VisaObject import VisaObject
from visa import constants as vicons
from time import sleep
import numpy as np

SCANNING = 1
PIX_NUM = 3648

class CCS(VisaObject):

	def __init__(self, resourceName, modelName = '', name=''):
		super().__init__(resourceName, modelName, name)
		self.library = K
		self.integrationTime = 0.01
		self.averageNumber = 5
		self.pixel_num = PIX_NUM
	

	@property
	def averageNumber(self):
		return self._averageNumber

	@averageNumber.setter
	def averageNumber(self, value):
		self._averageNumber = value
	

	@property
	def integrationTime(self):
		return self._integrationTime
	
	@integrationTime.setter
	def integrationTime(self, value):
		self._integrationTime = value

	@property
	def library(self):
		return self._library

	@library.setter
	def library(self, value):
		self._library = value

	#############################################################
	def open(self):
		"""
		This function initializes the instrucment driver and perform initialization actions (according to Thorlabs TLPM library).
		"""
		self.verboseMessage('Establishing session...')

		idquery = enum.ViBoolean()
		resetDevice = enum.ViBoolean()
		instrumentHandle = enum.ViSession()
		status = self.library.Open(self.resourceName_c, idquery, resetDevice, byref(instrumentHandle))

		if status==vicons.VI_SUCCESS:
			self.verboseMessage('Done establishing session.')
			self.instrumentHandle = instrumentHandle
			self.idQuery = idquery
			self.resetDevice = resetDevice
			self.setIntegrationTime(self.integrationTime)
		else:
			raise Exception('Failed to establish session with device. Error code: {} : {}.'.format(status))

		return status

	def close(self):
		if self.isInSession:
			self.verboseMessage('Closing session...')
			status = self.library.Close(self.instrumentHandle)
			if status==vicons.VI_SUCCESS:
				self.verboseMessage('Done closing session.')
				self.idQuery = None
				self.resetDevice = None
				self.instrumentHandle = None

	def getStatus(self):
		if self.isInSession:
			dstatus = ctypes.c_int32()
			status = self.library.GetDeviceStatus(self.instrumentHandle, byref(dstatus))
			if status == vicons.VI_SUCCESS:
				return dstatus
		else:
			raise self.notInSessionMsg()

	def sweep(self, avgN=1, waitTime=0):
		"""
		avgN -- a number of averaging
		waitTime -- time in second to wait before the next sweep
		"""
		if self.isInSession:
			self.verboseMessage('Sweeping {} time(s)...'.format(avgN))
			datas = np.zeros((avgN, 3648), dtype=np.float)
			for i in range(avgN):
				status = self.library.StartScan(self.instrumentHandle)
				sleep(0.1)

				while self.getStatus==1: #still scanning
					sleep(0.1)

				data = (ctypes.c_double*3648)()
				status = self.library.GetScanData(self.instrumentHandle, data)
				datas[i] = np.ctypeslib.as_array(data)

				if waitTime>0:
					sleep(waitTime)

			wl = self.getWavelength()

			self.verboseMessage('Done sweeping {} time(s).'.format(avgN))
			return (datas, wl)
		else:
			raise self.notInSessionMsg()

	def sweepAvg(self):
		if self.isInSession:
			(datas, wl) = self.sweep(self.averageNumber, waitTime=0)
			return (np.mean(datas, axis=0), wl)
		else:
			raise self.notInSessionMsg()

	def getWavelength(self, dataset=0):
		assert dataset == 0 or data==1, 'Accept only 0 (factory setting) or 1 (user defined).'
		if self.isInSession:
			data = (ctypes.c_double*3648)()
			minWL = ctypes.c_double()
			maxWL = ctypes.c_double()
			status = self.library.GetWavelengthData(self.instrumentHandle, ctypes.c_int16(dataset), data, byref(minWL), byref(maxWL))
			if status == vicons.VI_SUCCESS:
				return np.ctypeslib.as_array(data)
		else:
			raise self.notInSessionMsg()

	def getIntegrationTime(self):
		"""
		Return integration time in seconds.
		"""
		if self.isInSession:
			time = ctypes.c_double()
			status = self.library.GetIntegrationTime(self.instrumentHandle, byref(time))
			if status==vicons.VI_SUCCESS:
				self.integrationTime = time.value
				return time.value
			else:
				raise Exception('Failed to get integration time')
		else:
			raise self.notInSessionMsg()

	def setIntegrationTime(self, sec):
		"""
		sec -- integration time in second
		"""
		assert 1e-5<=sec<=6, 'Integration time must be between 1e-5 to 6 seconds.'
		if self.isInSession:
			self.verboseMessage('Setting integration time...')
			status = self.library.SetIntegrationTime(self.instrumentHandle, ctypes.c_double(sec))
			if status==vicons.VI_SUCCESS:
				self.verboseMessage('Done setting integration time.')
				self.integrationTime = sec
			else:
				raise Exception('Failed to set integration time.')
		else:
			raise self.notInSessionMsg()
