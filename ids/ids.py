from ctypes import c_int, c_ulong, ARRAY, pointer, POINTER
from ctypes import byref
import ctypes
import pandas as pd
import warnings
import typing
import numpy as np
from pyueye import ueye
from time import sleep

from .tools import _ids_wrapper as K
from .tools import _enum as enum

# _lib_api_path = r"C:\Windows\System32\uEye_api_64.dll"
# _lib = cdll.LoadLibrary(lib_api_path)

class DeviceManager(object):

	def __init__(self):
		self._library = K
		self._camerasList = None

	@property
	def library(self):
		return self._library

	@library.setter
	def library(self, lib):
		self._library = lib

	@property
	def camerasList(self):
		return self._camerasList
	
	@camerasList.setter
	def camerasList(self):
		data = self.getCameraList()
		self._camerasList = data
	

	################################################
	def getNumberOfCameras(self):
		num = c_int(0)
		err_code = self.library.GetNumberOfCameras(byref(num))
		if err_code==125:
			raise Exception('Failed to get number of camera. Error code {}'.format(err_code))
		else:
			return num.value

	def getCameraList(self):
		n_cam = self.getNumberOfCameras()

		plist = pd.DataFrame()
		plist = pd.DataFrame(columns=['CameraID', 'DeviceID', 'SensorID','InUse','SerNo','Model','Status'])
		if n_cam<1:
			warnings.warn('Found no camera.')

		if 1<=n_cam<=10:

			# Using 'incomplete' structure, not good. See _ids_wrapper for more detail.
			# CAMERA_LIST = self.library.UEYE_CAMERA_LIST
			# class UEYE_CAMERA_LIST(self.library.StructureEx):
				# pass
			# UEYE_CAMERA_LIST._fields_ = [("count", c_ulong),
            #    ("cameras", ARRAY(self.library.UEYE_CAMERA_INFO, n_cam)) ]

			clist = self.library.UEYE_CAMERA_LIST()

			# use a fixed number of maximum camera the module can be detected.
			clist.count = ctypes.c_ulong(n_cam)
			clist.cameras = ctypes.cast( (ctypes.c_ubyte*ctypes.sizeof(self.library.UEYE_CAMERA_INFO)*n_cam)(), ctypes.POINTER(self.library.UEYE_CAMERA_INFO*10) ).contents

			err_code = self.library.GetCameraList(byref(clist))
		else:
			warnings.warn('Found {} cameras. Only 10 will be listed.'.format(n_cam))

		if err_code==enum.ACCESS_VIOLATION:
			raise Exception('Error code {}: ACCESS_VILOATION.'.format(err_code))
		if err_code==enum.CANT_OPEN_DEVICE:
			raise Exception('Error code {}: Cannot open device.'.format(err_code))
		if err_code==enum.INVALID_PARAMETER:
			raise Exception('Error code {}: Invalid parameter.'.format(err_code))
		if err_code==enum.IO_REQUEST_FAILED:
			raise Exception('Error code {}: IO request failed.'.format(err_code))
		if err_code==enum.NO_SUCCESS:
			raise Exception('Error code {}: No success.'.format(err_code))
		else:
			cdict = clist.getdict()
			cameras = cdict['cameras']

			for i in range(0,min([n_cam,10])):
			    camera = cameras[i]
			    data = [camera.CameraID, camera.DeviceID, camera.SensorID, camera.InUse, camera.SerNo, camera.Model, camera.Status]
			    plist.loc[i] = data
			
		return plist
			

class Camera(object):

	def __init__(self, cameraId):
		self._cameraId = cameraId
		self._cameraId_c = enum.HIDS(cameraId)
		self._library = K
		self._isInSession = False
		self._verbose = True
		self._imgMem = None
		self._width = 1600
		self._height = 1200
		self._bitpixel = 8

	@property
	def width(self):
		return self._width

	@width.setter
	def width(self, value):
		self._width = value

	@property
	def height(self):
		return self._height
	
	@height.setter
	def height(self, value):
		self._height = value

	@property
	def bitpixel(self):
		return self._bitpixel
	
	@bitpixel.setter
	def bitpixel(self, value):
		self._bitpixel = value

	@property
	def imgMem(self):
		return self._imgMem

	@imgMem.setter
	def imgMem(self, value: dict):
		self._imgMem = value

	@property
	def verbose(self):
		return self._verbose
	
	@verbose.setter
	def verbose(self, value):
		assert type(value) is bool, 'Only accept boolean value. Non-boolean value given.'
		self._verbose = value

	@property
	def isInSession(self):
		return self._isInSession
	
	@isInSession.setter
	def isInSession(self, value):
		assert type(value) is bool, 'Only accept boolean value. Non-boolean value given.'
		self._isInSession = value

	@property
	def cameraId(self):
		return self._cameraId

	@cameraId.setter
	def cameraId(self, id):
		self._cameraId = id

	@property
	def cameraId_c(self):
		return self._cameraId_c
	
	@cameraId_c.setter
	def cameraId(self, value):
		self._cameraId_c = value

	@property
	def library(self):
		return self._library

	@library.setter
	def library(self, value):
		self._library = value
	
	
	##############################################################
	def open(self):
		self.verboseMessage('Opening camera session...')
		err_code = self.library.InitCamera(pointer(self.cameraId_c), enum.HWND())
		if err_code == enum.SUCCESS:
			self.isInSession = True
			self.setDisplayMode()
			self.setColorMode()
			self.allocImgMem()
			self.setImgMem()
			self.setExternalTrigger()
			self.verboseMessage('Done opening camera session. Success.')
		else:
			raise Exception('Failed to open camera session. Error code: {}.'.format(err_code))

	def close(self):
		self.verboseMessage('Closing camera session...')
		self.freeImgMem()
		err_code = self.library.ExitCamera(self.cameraId_c)
		if err_code==enum.SUCCESS:
			self.verboseMessage('Done closing camera session.')
			self.isInSession = False
		else:
			raise Exception('Failed to close camera session. Error code: {}.'.format(err_code))


	def captureSingle(self):
		if self.isInSession:

			#self.setImgMem()

			self.verboseMessage('Capturing a single frame...')
			err_code = self.library.CaptureSingle(self.cameraId_c, ctypes.c_int(0x0000))  # #IS_DONT_WAIT  = 0x0000, or IS_GET_LIVE = 0x8000
			sleep(0.5)
			if err_code==enum.SUCCESS:
				ImageData = np.ones((self.height,self.width), dtype=np.uint8)
				err_code = self.library.CopyImageMem(self.cameraId_c, self.imgMem['pcImgMem'], self.imgMem['pid'], ImageData.ctypes.data_as(ctypes.c_char_p))
				if err_code!=enum.SUCCESS:
					raise Exception('Failed to copy image from memory. Error code: {}.'.format(err_code))
				else:
					return ImageData
				self.verboseMessage('Done capturing a single frame.')
			else:
				raise Exception('Failed to capture a single frame. Error code: {}.'.format(err_code))
		else:
			raise self.notInSessionMsg()


	################################################################

	def setDisplayMode(self, mode=enum.SET_DM_DIB):
		if self.isInSession:
			err_code = self.library.SetDisplayMode(self.cameraId_c, mode)
			if err_code!=enum.SUCCESS:
				raise Exception('Failed to set display mode. Error code: {}.'.format(err_code))
		else:
			raise self.notInSessionMsg()

	def setColorMode(self, mode = ueye.IS_CM_SENSOR_RAW8):
		if self.isInSession:
			self.verboseMessage('Setting color mode...')
			err_code = self.library.SetColorMode(self.cameraId_c, mode)
			if err_code==enum.SUCCESS:
				self.verboseMessage('Done setting color mode.')
			else:
				raise Exception('Fail to set color mode. Error code: {}.'.format(err_code))
		else:
			raise self.notInSessionMsg()

	def setExternalTrigger(self, mode = ueye.IS_SET_TRIGGER_SOFTWARE):
		if self.isInSession:
			self.verboseMessage('Setting external trigger mode...')
			err_code = self.library.SetExternalTrigger(self.cameraId_c, mode)
			if err_code==enum.SUCCESS:
				self.verboseMessage('Done setting external trigger mode.')
			else:
				raise Exception('Fail to set external trigger mode. Error code: {}.'.format(err_code))
		else:
			raise self.notInSessionMsg()

	def getErrorMsg(self, err_code):
		if self.isInSession:
			err_code_c = c_int(err_code)
			msg = ctypes.create_string_buffer("",size=512)
			self.library.GetError()
		else:
			raise self.notInSessionMsg()

	def allocImgMem(self):
		if self.isInSession:
			w = c_int(self.width)
			h = c_int(self.height)
			px = c_int(self.bitpixel)
			pcImgMem = ctypes.c_char_p()  # placeholder for image memory
			pid = c_int()  # ID for the allocated memory

			self.verboseMessage('Allocating image memory...')

			err_code = self.library.AllocImageMem(self.cameraId_c, w, h, px, byref(pcImgMem), byref(pid))
			if err_code==enum.SUCCESS:
				self.verboseMessage('Done allocating image memory.')
			else:
				raise Exception('Failed to allocate image memory. Error code: {}.'.format(err_code))
		else:
			raise self.notInSessionMsg()

		self.imgMem = {'pcImgMem': pcImgMem, 'pid': pid}

		return self.imgMem

	def setImgMem(self):
		if self.isInSession:
			self.verboseMessage('Setting image memory...')
			err_code = self.library.SetImageMem(self.cameraId_c, self.imgMem['pcImgMem'], self.imgMem['pid'])
			if err_code==enum.SUCCESS:
				self.verboseMessage('Done setting image memory. pid: {}'.format(self.imgMem['pid']))
			else:
				return Exception('Failed to set image memory. Error code: {}'.format(err_code))
		else:
			raise self.notInSessionMsg()

	def freeImgMem(self):
		if self.isInSession:
			self.verboseMessage('Freeing image memory...')
			err_code = self.library.FreeImageMem(self.cameraId_c, self.imgMem['pcImgMem'], self.imgMem['pid'])
			if err_code==enum.SUCCESS:
				self.verboseMessage('Done freeing image memory.')
			else:
				raise Exception('Failed to free image memory. Error code: {}.'.format(err_code))
		else:
			raise self.notInSessionMsg()

	##############################################################
	# UTILITIES
	def verboseMessage(self, message):
		if self._verbose:
			print('Camera ID {} -- {}'.format(self._cameraId, message))

	def notInSessionMsg(self):
		return Exception('The power meter is not in session. Run .open() first.')

