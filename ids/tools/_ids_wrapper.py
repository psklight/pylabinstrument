from ctypes import (
    Structure,
    cdll,
    c_bool,
    c_short,
    c_int,
    c_uint,
    c_int16,
    c_int32,
    c_char,
    c_byte,
    c_long,
    c_float,
    c_double,
    POINTER,
    CFUNCTYPE,
    c_ushort,
    c_ulong,
    c_char_p,
    ARRAY
)

c_word = c_ushort
c_dword = c_ulong

from ...ctools.tools import bind, null_function
from . import _enum as enum


class StructureEx(Structure):

    def getdict(self):
        return dict((f, getattr(self, f)) for f, _ in self._fields_)

    def loaddict(self, d):
        """
        d -- a dictionary of parameters. The keys of the dictionary much match the attributes of the class.
        """
        for f in d.keys():
            if not hasattr(self, f):
                raise AttributeError('Given dictionary has unmatched attributes.')
            for field, ctype in self._fields_:
                if field == f:
                    break
            if ctype in [c_short, c_long, c_int, c_int16, c_int32, c_uint, c_ushort, c_ulong]:
                setattr(self, f, ctype(int(d[f])))
            if ctype in [c_float, c_double]:
                setattr(self, f, ctype(float(d[f])))

    def __str__(self):
        return print(self.getdict())


class UEYE_CAMERA_INFO(StructureEx):
	_fields_ = [("CameraID", c_dword),
				("DeviceID", c_dword),
				("SensorID", c_dword),
				("InUse", c_dword),
				("SerNo", 16*c_char),
				("Model", 16*c_char),
				("Status", c_dword),
				("Reserved", 2*c_dword),
				("FullModelName", 32*c_char),
				("Reserved2", 5*c_dword)]

class UEYE_CAMERA_LIST(StructureEx):
    # making it 'incomplete' ctypes type
    pass
	# _fields_ = [("count", c_ulong),
	# 			("cameras", ARRAY(UEYE_CAMERA_INFO,1)) ]


lib_api_path = r"C:\Windows\System32\uEye_api_64.dll"
lib_api = cdll.LoadLibrary(lib_api_path)

GetNumberOfCameras = bind(lib_api, "is_GetNumberOfCameras", [POINTER(c_int)], c_int)
GetCameraList = bind(lib_api, "is_GetCameraList", [POINTER(UEYE_CAMERA_LIST)], c_int)

InitCamera = bind(lib_api, "is_InitCamera", [POINTER(enum.HIDS), POINTER(enum.HWND)], c_int)
ExitCamera = bind(lib_api, "is_ExitCamera", [enum.HIDS], c_int)