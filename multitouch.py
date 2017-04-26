"""
source: http://blog.sendapatch.se/2009/november/macbook-multitouch-in-python.html
"""
import ctypes
from ctypes.util import find_library

CFArrayRef = ctypes.c_void_p
CFMutableArrayRef = ctypes.c_void_p
CFIndex = ctypes.c_long

MultitouchSupport = ctypes.CDLL("/System/Library/PrivateFrameworks/MultitouchSupport.framework/MultitouchSupport")

CFArrayGetCount = MultitouchSupport.CFArrayGetCount
CFArrayGetCount.argtypes = [CFArrayRef]
CFArrayGetCount.restype = CFIndex

CFArrayGetValueAtIndex = MultitouchSupport.CFArrayGetValueAtIndex
CFArrayGetValueAtIndex.argtypes = [CFArrayRef, CFIndex]
CFArrayGetValueAtIndex.restype = ctypes.c_void_p

MTDeviceCreateList = MultitouchSupport.MTDeviceCreateList
MTDeviceCreateList.argtypes = []
MTDeviceCreateList.restype = CFMutableArrayRef

class MTPoint(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float),
                ("y", ctypes.c_float)]

class MTVector(ctypes.Structure):
    _fields_ = [("position", MTPoint),
                ("velocity", MTPoint)]

class MTData(ctypes.Structure):
    _fields_ = [
      ("frame", ctypes.c_int),
      ("timestamp", ctypes.c_double),
      ("identifier", ctypes.c_int),
      ("state", ctypes.c_int),  # Current state (of unknown meaning).
      ("unknown1", ctypes.c_int),
      ("unknown2", ctypes.c_int),
      ("normalized", MTVector),  # Normalized position and vector of
                                 # the touch (0 to 1).
      ("size", ctypes.c_float),  # The area of the touch.
      ("unknown3", ctypes.c_int),
      # The following three define the ellipsoid of a finger.
      ("angle", ctypes.c_float),
      ("major_axis", ctypes.c_float),
      ("minor_axis", ctypes.c_float),
      ("unknown4", MTVector),
      ("unknown5_1", ctypes.c_int),
      ("unknown5_2", ctypes.c_int),
      ("unknown6", ctypes.c_float),
    ]

MTDataRef = ctypes.POINTER(MTData)

MTContactCallbackFunction = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, MTDataRef,
    ctypes.c_int, ctypes.c_double, ctypes.c_int)

MTDeviceRef = ctypes.c_void_p

MTRegisterContactFrameCallback = MultitouchSupport.MTRegisterContactFrameCallback
MTRegisterContactFrameCallback.argtypes = [MTDeviceRef, MTContactCallbackFunction]
MTRegisterContactFrameCallback.restype = None

MTDeviceStart = MultitouchSupport.MTDeviceStart
MTDeviceStart.argtypes = [MTDeviceRef, ctypes.c_int]
MTDeviceStart.restype = None

###

def get_position(data):
    return (data.normalized.position.x, data.normalized.position.y)

def get_positions(data_ptr, n_fingers):
    return [get_position(data_ptr[i]) for i in xrange(n_fingers)]

def get_ellipse(data):
    return (data.angle, data.major_axis, data.minor_axis)

def get_ellipses(data_ptr, n_fingers):
    return [get_ellipse(data_ptr[i]) for i in xrange(n_fingers)]

class TouchPad:
    def __init__(self, data, n_fingers, timestamp):
        self.n_fingers = n_fingers
        self.positions = get_positions(data, n_fingers)
        self.ellipses = get_ellipses(data, n_fingers)
        self.timestamp = timestamp

def inner_callback(device, data_ptr, n_fingers, timestamp, frame, callback):
    touch = TouchPad(data_ptr, n_fingers, timestamp)
    callback(touch)
    return 0

def bind_callback(callback):
    fcn = lambda a,b,c,d,e: inner_callback(a,b,c,d,e,callback=callback)
    return MTContactCallbackFunction(fcn)

def start_devices_with_callback(callback):
    devices = MultitouchSupport.MTDeviceCreateList()
    num_devices = CFArrayGetCount(devices)
    print devices
    print "num_devices =", num_devices
    for i in xrange(num_devices):
        device = CFArrayGetValueAtIndex(devices, i)
        print "device #%d: %016x" % (i, device)
        MTRegisterContactFrameCallback(device, callback)
        MTDeviceStart(device, 0)
