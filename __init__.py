"""
GPIB - Module for controlling instruments with the IEEE-488 bus.

Based on the Agilent SICL library using module pysicl. This is an example
of a pysicl session::
>>> import pysicl
>>> pysicl.gpib_open("lan[128.149.22.44]:gpib0,19")
'1'
>>> pysicl.gpib_prompt(1,"*IDN?")
'Hewlett-Packard, ESG-1000B, US38080113, B.01.03'
>>> pysicl.gpib_dev_status(1)
'4'
>>> pysicl.gpib_close(1)
'1 closed'

The GPIB module provides a higher level interface.

This only works for 32-bit architecture and needs the following files installed
/etc/opt/sicl/hwconfig.cf
/usr/include/sicl.h
/usr/lib/libsicl.so
"""

import pysicl

def ask(device, request):
    """
    Send 'request' to 'device' and obtain 'response'.
    """
    try:
        instr = pysicl.gpib_open(device)
        resp = pysicl.gpib_prompt(instr, request)
        pysicl.gpib_close(instr)
    except:
        return "No response due to error"
    return resp

def dev_status(device):
    """
    Returns the status byte of the device.
    """
    try:
        instr = pysicl.gpib_open(device)
        status = pysicl.gpib_dev_status(instr)
        pysicl.gpib_close(instr)
    except:
        return -1
    return status

def find_devices(controller):
    """
    Find the GPIB addresses of devices attached to the controller
    """
    pysicl.gpib_timeout(500)
    for addr in range(1,31):
        print addr
        if addr != 21:
            status = dev_status(controller+str(addr))
            print addr,status
            if status > -1:
                print addr,":",status
    pysicl.gpib_timeout(10000)
    
#============================= Python Gpib Emulation ==========================

class Gpib:
  """
  Gleaned from various posts and online sources. There doesn't seem to be a
  reference for this API.
  
  The ibXXX commands are not traditional NI functions.
  
  The Linux Gpib package uses a file /etc/gpib.conf that has entries like::
    interface {
      minor = 0
      board_type = "ni_usb_b"
      name = "joe"
      pad = 0
      master = yes
  }
  """
  
  def __init__(self, name='gpib0'):
    pass

  def clear(self):
    """
    Clear device.
    """
    pass

  def ibcnt(self):
    """
    Get the actual length read.
    
    In traditional NI functions, this is global variable that stores the number
    of bytes read back or sent out by the most recent ibrd or ibwrt.
    """
    pass

  def ibsta(self):
    """
    Get status
    """
    pass

  def read(self, len=512):
    """
    read data bytes
    """
    pass

  def readbin(self, len=512):
    """
    readbin() automatically returns the proper length (equal to ibcnt).
    """
    pass

  def ren(self, val):
    """
    set remote enable
    """
    pass

  def rsp(self):
    """
    Returns the serial poll byte from the instrument trigger()
    """
    pass

  def tmo(self, value):
    """
    adjust I/O timeout
    """
    pass
  
  def trigger(self):
    """
    trigger device
    """
    pass
  
  def wait(self, mask):
    """
    wait for event
    """
    pass
  
  def write(self, str):
    """
    write data bytes
    """
    pass

  def writebin(self, str, len):
    pass
  
RQS = 2048
SRQ = 4096
TIMO = 16384
error = 'gpib.error'

