"""
wrapper for SICL library

GPIB (IEEE-488) functions based on SICL (Standard Instrument Control Library).
Depends on libsicl.so. and libpython2.4.so."

Full documentation for the library can be found at
http://dsnra.jpl.nasa.gov/dss/manuals/StandardInstrumentControlLibrary%20-%20UsersGuide.pdf

Formatted I/O
=============
The formatted I/O functions iprintf, ipromptf and iscanf are buffered.
Formatted I/O Conversion Formatted I/O functions convert data under the control
of the format string. The format string specifies how the argument is converted
before it is input or output. A typical format string syntax is::
  %[format flags][field width][. precision][, array size][argument modifier]format code

The iprintf function formats the arguments according to the format string and
sends data to a device:
iprintf(id, format [,arg1][,arg2][,...]);

The iscanf function receives and converts data according to the
format string:
iscanf(id, format [,arg1][,arg2][,...]);

The ipromptf function formats and sends data to a device, and then
immediately receives and converts the response data:
ipromptf(id, writefmt, readfmt[,arg1] [,arg2][,...]);

Formatted I/O Buffers
---------------------

The SICL software maintains both a read and a write buffer for formatted I/O
operations. Occasionally, you may want to control the actions of these buffers.
See the isetbuf function for other options for buffering data.

The write buffer is maintained by the iprintf and the write portion of the
ipromptf functions. It queues characters to send to the device so that
they are sent in large blocks, thus increasing performance. The write
buffer automatically flushes when it sends a newline character from the
format string (see the %t format code to change this feature).
The write buffer also flushes immediately after the write portion of the
ipromptf function. It may occasionally be flushed at other
non-deterministic times, such as when the buffer fills. When the write
buffer flushes, it sends its contents to the device.

The read buffer is maintained by the iscanf and the read portion of the
ipromptf functions. The read buffer queues the data received from a
device until it is needed by the format string. The read buffer is
automatically flushed before the write portion of an ipromptf. Flushing
the read buffer destroys the data in the buffer and guarantees that the
next call to iscanf or ipromptf reads data directly from the device rather
than from data that was previously queued.

Non-Formatted I/O
-----------------

There are two non-buffered and non-formatted I/O functions called iread and
iwrite. These are raw I/O functions and should not be intermixed with
formatted I/O functions.

If raw I/O must be mixed, use the ifread/ifwrite functions. These
functions have the same parameters as iread and iwrite, but read or
write raw output data to the formatted I/O buffers. 
"""

import ctypes as ct
from Electronics.Interfaces.GPIB.devices import *

import logging
module_logger = logging.getLogger(__name__)

sicllib = ct.CDLL("/usr/lib/libsicl.so")

_open = sicllib.iopen
_open.argtypes = [ct.c_char_p]
_open.restype = ct.c_int

_timeout = sicllib.itimeout
_timeout.argtypes = [ct.c_int, ct.c_int]
_timeout.restype = ct.c_void_p

_print = sicllib.iprintf
_print.argtypes = [ct.c_int, ct.c_char_p]
_print.restype = ct.c_void_p

_scan = sicllib.iscanf
_scan.argtypes = [ct.c_int, ct.c_char_p, ct.c_char_p]
_scan.restype = ct.c_int

_prompt = sicllib.ipromptf
_prompt.argtypes = [ct.c_int, ct.c_char_p, ct.c_char_p, ct.c_char_p]
_prompt.restype = ct.c_void_p

_close = sicllib.iclose
_close.argtypes = [ct.c_int]
_close.restype = ct.c_void_p

_lock = sicllib.ilock
_lock.argtypes = [ct.c_int]
_lock.restype = ct.c_void_p

_unlock = sicllib.iunlock
_unlock.argtypes = [ct.c_int]
_unlock.restype = ct.c_void_p

_get_dev_status = sicllib.ireadstb
_get_dev_status.argtypes = [ct.c_int, ct.c_char_p]
_get_dev_status.restype = ct.c_int

_clear = sicllib.iclear
_clear.argtypes = [ct.c_int]
_clear.restype = ct.c_int

"""
_get_errstr gets the textual explanation of an error code. Pass this function
the error code you want and this function will return a human-readable string.
"""
_get_errstr = sicllib.igeterrstr
_get_errstr.argtypes =[ct.c_int]
_get_errstr.restype = ct.c_char_p

_read = sicllib.iread
_read.argtypes = [ct.c_int, ct.c_char_p, ct.c_ulong,
                  ct.POINTER(ct.c_int), ct.POINTER(ct.c_ulong)]
_read.restype = ct.c_int

def gpib_open(name):
  """
  Start a device session.
  
  Returns a unique integer for the instrument at the specified GPIB address.
  For example::
  >>> gpib_open(lan[158.154.1.110]:19)
  4

  @param name : LAN/GPIB address of the device
  @type  name : str

  @return: int
  """
  (devtype,devID) = name.split()
  address = eval(devtype)[devID]['addr']
  return _open(address)

def gpib_close(instrument_ID):
  """
  Close a device session
  
  @param instrument_ID : returned by gpib_open
  @type  instrument_ID : int

  @return: response str
  """
  return _close(instrument_ID)

def gpib_timeout(instrument, milliseconds):
  """
  Set instrument timeout for subsequent gpib commands.

  Set the maximum time in milliseconds to wait for an I/O operation to
  complete. A value of zero (0) disables timeouts.

  _timeout returns 0 if successful or a non-zero error number if an error
  occurs.
  
  @param milliseconds : timeout duration
  @type  milliseconds : int
  
  @return: response str
  """
  try:
    status = _timeout(instrument, milliseconds)
    return True
  except Exception, details:
    if status:
      module_logger.error(_get_errstr(status))
    raise RuntimeException, details
  return status
  
def gpib_diags(state):
  """
  Turn diagnostic printout for gpib module on or off.
  
  @param state : True for debug, False for original state
  @type  state : bool

  @return: response str
  """
  if state:
    self.loglevel = module_logger.getLoglevel()
    module_logger.setLoglevel(logging.DEBUG)
  else:
    module_logger.setLoglevel(self.loglevel)
  return True

def gpib_send(instrument_ID, command):
  """
  Send the command string to the designated instrument.

  iprintf converts data under the control of the format string. The format
  string specifies how the argument is converted before it is output. It
  contains regular characters and special conversion sequences. The iprintf
  function sends the regular characters (not a %character) in the format
  string directly to the device. Conversion specifications are introduced by
  the % character. Conversion specifications control the type, the conversion,
  and the formatting of the arg parameters.

  @param instrument_ID : GPIB identifier
  @type  instrument_ID : int
  
  @return: response str
  """
  return _print(instrument_ID, command)

def gpib_rcv(instrument_ID, term_char=10, format="%t"):
  """
  Receive from the designated instrument

  Read response buffer up to the designated termination character (an integer,
  e.g. 10 for LF). This is actually not used by iscanf.

  iscanf reads formatted data, converts the data, and stores the results into
  args.   It read bytes from the specified device and converts them using
  conversion rules contained in the format string. The number of args converted
  is returned.

  @param instrument_ID : GPIB identifier
  @type  instrument_ID : int

  @param term_char : termination character
  @type  term_char : int
  
  @return: response str
  """
  response = ct.create_string_buffer('\000'*2048)
  status = _scan(instrument_ID, format, response)
  module_logger.debug("gpib_rcv: %d values converted",status)
  return response.value.strip()

def gpib_read(instrument_ID, lendata):
  """
  Read raw data from the device or interface

  Implements iread(id, buf, bufsize, reason, actualcnt)::
   * buf is a pointer to the location where the block of data can
     be stored.
   * bufsize is an unsigned long integer containing the size, in bytes, of the
     buffer specified in buf.
   * reason is a pointer to an integer that contains the reason why the read
     terminated. If the reason parameter contains a zero (0), no termination
     reason is returned. Reasons include::
     ** I_TERM_MAXCNT - bufsize characters read.
     ** I_TERM_END END - indicator received on last character.
     ** I_TERM_CHR - Termination character enabled and received.
   * actualcnt is a pointer to an unsigned long integer. Upon exit, this
     contains the actual number of bytes read from the device or interface.
     If actualcnt parameter is NULL, the number of bytes read will not be
     returned.
  """
  data = ct.create_string_buffer('\000*16384')
  reason_p = ct.pointer(ct.c_int())
  num_recvd_p = ct.pointer(ct.c_ulong())
  status = _read(instrument_ID, data, lendata, reason_p, num_recvd_p)
  result = (data.value, reason_p.contents.value, num_recvd_p.contents.value)
  return result

def gpib_prompt(ID, text):
  """
  Format and send data to a device, and then receive and convert the response::
      ipromptf(id, writefmt, readfmt[,arg1] [,arg2][,...]);

  @param ID : instrument identifier
  @type  ID : int

  @param text : message to device
  @type  text : str

  @return: str
  """
  response = ct.create_string_buffer('\000'*2048)
  status = _prompt(ID, text, "%t", response)
  return response.value

def gpib_lock(instrument):
  """
  Lock the instrument to this session.

  Locks a session ensuring exclusive use of a resource.  Only that device is
  locked and only that session may access that device.

  Locks are implemented on a per-session basis. If a session within a given
  process locks a device, that device is only accessible from that session. It
  is also not accessible from any other process.  Attempting to call a SICL
  function that obeys locks on a device that is locked will cause the call
  either to hang until the device is unlocked, to timeout or to return with
  the error I_ERR_LOCKED (see isetlockwait).

  @param instrument : device ID
  @type  instrument : int

  @return: returns 0 if successful or non-zero error number if an error occurs.
  """
  return _lock(instrument)

def gpib_unlock(instrument):
  """
  Unlock the instrument from this session.

  @return: response str
  """
  return _unlock(instrument)
  
def gpib_dev_status(instrument):
  """
  Get status byte for the instrument.
  
  @return: str
  """
  response = ct.create_string_buffer('\000'*2048)
  status = _get_dev_status(instrument, response)
  return response.value

def clear(instrument):
  """
  Clear a device

  The iclear function also discards the data in both the read and the write
  formatted I/O buffers. This discard is equivalent to performing the following
  iflush call (in addition to the device clear function)::
    iflush (id, I_BUF_DISCARD_READ | I_BUF_DISCARD_WRITE);
  
  @param instrument : a device session

  @return: 0 if successful or a non-zero error number if an error occurs.
  """
  try:
    status = _clear(instrument)
    return True
  except Exception, details:
    raise RuntimeError, details
    if status:
      module_logger(_get_errstr(status))
    return False
  

if __name__ == "__main__":
  from Electronics.Interfaces.GPIB.devices import mms

  gpib_open(mms['14-1']['addr'])
  r = gpib_prompt(1,"CF?")
  print r