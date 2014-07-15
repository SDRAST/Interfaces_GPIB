import ctypes as ct

import logging
module_logger = logging.getLogger(__name__)

sicllib = ct.CDLL("/usr/lib/libsicl.so")

gpib_open = sicllib.iopen
gpib_open.argtypes = [ct.c_char_p]
gpib_open.restype = ct.c_int

gpib_timeout = sicllib.timeout
gpib_timeout.argtypes = [ct.c_int, ct.c_int]
gpib_timeout.restype = c_void_p

gpib_print = sicllib.iprintf
gpib_print.argtypes = [c_int, c_char_p]
gpib_print.restype = c_void_p

gpib_prompt = sicllib.ipromptf
gpib_prompt.argtypes = [c_int, c_char_p, c_char_p, ct.c_void_p]
gpib_prompt.restype = c_void_p

gpib_close = sicllib.iclose
gpib_close.argtypes = [c_int]
gpib_close.restype = c_void_p