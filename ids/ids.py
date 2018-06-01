from ctypes import c_int
from ctypes import byref

from . import _ids
from ._enumeration_error_code import *

# _lib_api_path = r"C:\Windows\System32\uEye_api_64.dll"
# _lib = cdll.LoadLibrary(lib_api_path)

def getNumberOfCameras():
	num = c_int(0)
	err_code = _ids.GetNumberOfCameras(byref(num))
	if err_code==125:
		raise Exception('Failed to get number of camera. Error code {}'.format(err_code))
	else:
		return num.value

def getCameraList():
	clist = _ids.UEYE_CAMERA_LIST()
	err_code = _ids.GetCameraList(byref(clist))
	if err_code==ACCESS_VIOLATION:
		raise Exception('Error code {}: ACCESS_VILOATION.'.format(err_code))
	if err_code==CANT_OPEN_DEVICE:
		raise Exception('Error code {}: Cannot open device.'.format(err_code))
	if err_code==INVALID_PARAMETER:
		raise Exception('Error code {}: Invalid parameter.'.format(err_code))
	if err_code==IO_REQUEST_FAILED:
		raise Exception('Error code {}: IO request failed.'.format(err_code))
	if err_code==NO_SUCCESS:
		raise Exception('Error code {}: No success.'.format(err_code))
	else:
		return clist

class Camera(object):

	def __init__(self, cameraId):
		self._cameraId = cameraId

	def open(self):
		

