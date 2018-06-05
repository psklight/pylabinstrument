from ctypes import c_int, c_ulong, ARRAY, pointer, POINTER
from ctypes import byref
import ctypes
import pandas as pd
import warnings

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
		if n_cam>=1:

			CAMERA_LIST = self.library.UEYE_CAMERA_LIST
			CAMERA_LIST._fields_ = [("count", c_ulong),
                ("cameras", ARRAY(self.library.UEYE_CAMERA_INFO, n_cam)) ]

			clist = CAMERA_LIST()

			clist.count = ctypes.c_ulong(n_cam)
			clist.uci = ctypes.cast( (ctypes.c_ubyte*ctypes.sizeof(self.library.UEYE_CAMERA_INFO)*n_cam)(), ctypes.POINTER(self.library.UEYE_CAMERA_INFO*n_cam) ).contents

			err_code = self.library.GetCameraList(byref(clist))
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

				for i in range(0,n_cam):
				    camera = cameras[i]
				    data = [camera.CameraID, camera.DeviceID, camera.SensorID, camera.InUse, camera.SerNo, camera.Model, camera.Status]
				    plist.loc[i] = data

				# plist.set_index('CameraID', inplace=True)
		else:
			warnings.warn('Found no camera.')
		return plist
			

class Camera(object):

	def __init__(self, cameraId):
		self._cameraId = cameraId
		self._cameraId_c = enum.HIDS(cameraId)
		self._library = K

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
		err_code = self.library.InitCamera(pointer(self.cameraId_c), POINTER(enum.HWND)())
		return err_code

	def close(self):
		pass