/* /usr/local/python/sicl/src/pysicl.c 

   1996 Nov 12	kuiper	instr_ioTK revised
   1999 Dec  7	skjerve	added gpib_open_net sub-routine
   2000 Jul   	kuiper	revised gpib_open to handle strings
   2002 Feb 27	kuiper	revised gpib_open to handle other (remote) buses
   2003	Nov 24	kuiper	added gpib_rcv_bin to handle output from "SER?"
			and other possible binary data
   2008 Oct 10	kuiper	converting to Python extension
*/

#include <Python.h>
#include <sicl.h>
#include <string.h>
#include <stdio.h>
#include <signal.h>
#ifndef PyDoc_STR
#define PyDoc_VAR(name)         static char name[]
#define PyDoc_STR(str)          (str)
#define PyDoc_STRVAR(name, str) PyDoc_VAR(name) = PyDoc_STR(str)
#endif

#define MSG_LEN 32768
char message[MSG_LEN];
char err_msg[256];
int  timeout = 10000; /* default is 10 seconds */
int  gpib_diags = 0; /* default is no diagnostic messages */

PyDoc_STRVAR(pysicl__doc__,
"GPIB (IEEE-488) functions based on SICL (Standard Instrument Control\n\
Library). Depends on libsicl.so. and libpython2.4.so.");

PyDoc_STRVAR(OpenCommand__doc__,
"gpib_open(address_string) -> int\n\n\
Returns a unique integer for the instrument at the specified\n\
GPIB address. For example,\n\
>>> gpib_open(lan[158.154.1.110]:19)\n\
4");

PyDoc_STRVAR(CloseCommand__doc__,
"gpib_close(intrument) -> response string\n\n\
Close the instrument\n\
where instrument is the integer returned by gpib_open.");

PyDoc_STRVAR(TimeoutCommand__doc__,
"gpib_timeout(int milliseconds) -> response string\n\n\
Set instrument timeout for subsequent gpib commands.");

PyDoc_STRVAR(DiagCommand__doc__,
"gpib_diags(1|0) -> response string\n\n\
Turn diagnostic printout for gpib module on or off.");

PyDoc_STRVAR(SendCommand__doc__,
"gpib_send(instrument, command) -> response string\n\n\
Send the command string to the designated instrument.");

PyDoc_STRVAR(RcvCommand__doc__,
"gpib_rcv(instrument, termination character) -> response string\n\n\
Receive from the designated instrument a response string up to the\n\
designation termination character (an integer, e.g. 10 for LF).");

PyDoc_STRVAR(PromptCommand__doc__,
"gpib_prompt(instrument, prompt string) -> response string\n\n\
Send the prompt string to the designated instrument and receive an\n\
appropriate response string.");

PyDoc_STRVAR(LockCommand__doc__,
"gpib_lock(instrument) -> response string\n\n\
Lock the instrument to this session.");

PyDoc_STRVAR(UnlockCommand__doc__,
"gpib_unlock(instrument) -> response string\n\n\
Unlock the instrument from this session.");

PyDoc_STRVAR(DevStsCommand__doc__,
"gpib_dev_status(instrument) -> response string\n\n\
Returns status byte for the instrument.");

static PyObject *
OpenCommand(PyObject *self,
		PyObject *args) {
   int	address;
   char *err_str;
   char *instr;
   int	error;
   char *result;
   int	instrument;  /* NOTE: in sicl, the instrument identifier is supposed
			to be of type INST. At present, INST is defined as
			int in sicl.h. If this ever changes, compilation
			should generate a warning, and another scheme will
			have to be found to associate an instrument with
			an integer code. */
   if (! PyArg_Parse(args, "(s)", &instr)) {
      return NULL;
   }
   instrument=iopen (instr);

   if ( instrument == 0 ) {
      error = igeterrno();
      err_str = igeterrstr (error);
      sprintf(err_msg,
	 "open of HPIB address %s failed: %s", instr ,err_str);
      PyErr_SetString(PyExc_Exception,err_msg);
      if (gpib_diags) {
        printf("open of HPIB address %s failed: %s\n", instr ,err_str);
      }
      PyErr_SetString(PyExc_Exception,err_msg);
      return NULL;
   } else {
      itimeout (instrument, timeout);
      return Py_BuildValue("i", instrument);
   }
}

static PyObject * TimeoutCommand(PyObject *self,
                PyObject *args) {
   if (! PyArg_Parse(args, "(i)", &timeout) ) {
      return NULL;
   } else {
      return Py_BuildValue("i", timeout);
   }
}

int gpib_dev_status(int id, int request, int *result) {
   /* repeat until not interrupt error */
   while ( igpibbusstatus(id, request, result) == I_ERR_INTERRUPT );
}


static PyObject * DiagCommand(PyObject *self,
		PyObject *args) {
   if (! PyArg_Parse(args, "(i)", &gpib_diags) ) {
      return NULL;
   }
   return Py_BuildValue("i", gpib_diags);
}

static PyObject * SendCommand(PyObject *self,
                PyObject *args) {
   char                 *err_str;
   int                  error;
   int                  instrument;
   long                 old_mask;
   int                  repeat;
   unsigned long        sent;
   int                  status;
   char			*command;

   if (! PyArg_Parse(args, "(is#)", &instrument, &command) ) {
      return NULL;
   }
   strcat(command,"\r\n"); /* HPIB messages need an EOL */
   if ( gpib_diags ) {
      printf ("Sending %s to instrument %d\n", command, instrument);
   }
   old_mask = sigblock( sigmask (SIGALRM) );
   while ( (status = ifwrite (instrument, command, strlen(command), 1, &sent))
        == I_ERR_INTERRUPT );
   /* The line above pre-dates signal blocking. TBHK 97/02/20 */
   sigsetmask (old_mask);
   if ( status ) {
      err_str = igeterrstr (status);
      sprintf(err_msg,
         "%s ifwrite to instrument %d failed: %s",
         command, instrument, err_str);
      PyErr_SetString(PyExc_Exception, err_msg);
      if (gpib_diags) {
        printf("%s ifwrite to instrument %d failed: %s",
               command, instrument, err_str);
      }
      return NULL;
   } else {
      if (gpib_diags) printf("flushing write buffer for instrument %d\n",
                              instrument);
      if ( status = iflush(instrument, I_BUF_WRITE) ) {
         err_str = igeterrstr (error);
         sprintf(err_msg,
            "%s iflush to instrument %d failed: %s",
            command, instrument, err_str);
         PyErr_SetString(PyExc_Exception, err_msg);
         if (gpib_diags) {
            printf("%s iflush to instrument %d failed: %s\n",
               command, instrument, err_str);
         }
         return NULL;
      } else {
         sprintf(message, "%s", command);
         return Py_BuildValue("s", message);
      }
   }
}

static PyObject * RcvCommand(PyObject *self,
                PyObject *args) {
   char *err_str;
   int  status;
   int instrument;
   long old_mask;
   char *p;
   int tchar;
   unsigned long cnt;

   if (! PyArg_Parse(args, "(ii)", &instrument, &tchar) ) {
      PyErr_SetString(PyExc_Exception, \
          "usage: gpib_rcv(instr_id,termination_char)");
      return NULL;
   }
   if ( gpib_diags ) {
      printf ("Setting timeout and termchar for instrument %d\n", instrument);
      fflush(stdout);
   }
   itimeout (instrument, timeout);
   itermchr (instrument, tchar);
   if ( gpib_diags ) {
      printf ("Saving current SIGALARM mask\n");
      fflush(stdout);
   }
   old_mask = sigblock( sigmask(SIGALRM) );
   if ( gpib_diags ) {
      printf ("Requesting input from instrument %d\n", instrument);
      fflush(stdout);
   }
   while ( ( status = ifread (instrument, message, MSG_LEN, 0, &cnt) )
              == I_ERR_INTERRUPT ); /* repeat until not interrupt error */
   if ( gpib_diags ) {
      printf ("Restoring SIGALARM mask\n");
      fflush(stdout);
   }
   sigsetmask (old_mask);
   if ( status ) {
      if ( gpib_diags ) {
         printf ("ifread returned status = %d\n",status);
         fflush(stdout);
      }
      err_str = igeterrstr (status);
      if (gpib_diags) {
        printf("input from instrument %d failed: %s\n", instrument, err_str);
        fflush(stdout);
      }
      sprintf(err_msg,
         "input from instrument %d failed: %s",
         instrument, err_str);
      PyErr_SetString(PyExc_Exception,err_msg);
      return NULL;
   } else {
      message[cnt] = '\0'; /* make sure it looks like a proper string */
      while (   message[strlen(message)-1] == '\n'
             || message[strlen(message)-1] == '\r'
             || message[strlen(message)-1] == ' ' ) {
         message[strlen(message) -1] = '\0';
         cnt--;
      }
      if ( gpib_diags ) {
         printf ("Received %d bytes:>%s<\n", cnt, message);
         fflush(stdout);
      }
      return Py_BuildValue("s", message);
   }
}


static PyObject * PromptCommand(PyObject *self, PyObject *args) {
   char 		*err_str;
   int			error;
   int			instrument;
   long			old_mask;
   int			repeat;
   unsigned long	sent;
   int  		status;
   char			*command;
   int			com_len;

   /* There is a bug in the library.  This should work with simply the
    * 's' format code but after the first call, that fails and using
    * 's#' provides a work-around. */
   if (! PyArg_Parse(args, "(is#)", &instrument, &command, &com_len) ) {
      return NULL;
   }
   if ( gpib_diags ) {
      printf ("gpib_prompt: length of received string is %d\n", 
	      com_len);
   }
   strcat(command,"\r\n"); /* HPIB messages need an EOL */
   if ( gpib_diags ) {
      printf ("gpib_prompt: sending %s to instrument %d\n", 
	      command, instrument);
   }
   itimeout (instrument, timeout);
   repeat = 1;
   while ( repeat ) {
     old_mask = sigblock( sigmask(SIGALRM) );
     status = ipromptf (instrument, "%s", "%8191t", command, message);
     sigsetmask (old_mask);
     if ( status != 2 ) {
       error = igeterrno ();
       if ( error != I_ERR_INTERRUPT ) repeat = 0;
     } else {
       repeat = 0;
     }
   }
   if ( status != 2 ) {
      err_str = igeterrstr ( error );
      sprintf(err_msg,
	 "ipromtf of '%s' to instrument %d failed: %s",
	 command, instrument, err_str);
      PyErr_SetString(PyExc_Exception, err_msg);
      if (gpib_diags) {
        printf("%s output to instrument %d failed: %s\n",
	       command, instrument, err_str);
      }
      return NULL;
   } else {
      if ( gpib_diags ) {
         printf ("gpib_prompt: received %d bytes: >%s<\n",
	         strlen(message),message);
      }
      while (   message[strlen(message)-1] == '\n'
             || message[strlen(message)-1] == '\r'
             || message[strlen(message)-1] == ' ' ) {
         message[strlen(message) -1] = '\0';
      }
      if ( gpib_diags ) {
         printf ("gpib_prompt: returns:>%s<\n", message);
      }
      return Py_BuildValue("s",message);
   }
}

static PyObject * LockCommand(PyObject *self,
                PyObject *args) {
   char *err_str;
   int  status;
   int instrument;
   int error;

   if (! PyArg_Parse(args, "(i)", &instrument) ) {
      return NULL;
   }
   while ( ( error = ilock (instrument) )
              == I_ERR_INTERRUPT ); /* repeat until not interrupt error */
   if ( error ) {
      err_str = igeterrstr(error);
      sprintf (err_msg,
         "locking instrument %s failed: %d",
         instrument, err_str);
      PyErr_SetString(PyExc_Exception, err_msg);
      if (gpib_diags) {
        printf ( "locking instrument %d failed: %s\n", instrument, err_str);
      }
      return NULL;
   } else {
      sprintf(message, "%d locked", instrument);
      return Py_BuildValue("s",message);
   }
}

static PyObject * UnlockCommand(PyObject *self,
                PyObject *args) {
   int instrument;
   int error;
   char *err_str;

   if (! PyArg_Parse(args, "(i)", &instrument) ) {
      return NULL;
   }
   if ( error = iunlock (instrument) ) {
      err_str = igeterrstr(error);
      sprintf (err_msg,
         "locking instrument %d failed: %s",
         instrument, err_str);
      PyErr_SetString(PyExc_Exception, err_msg);
      if (gpib_diags) {
        printf ( "locking instrument %d failed: %s\n", instrument, err_str);
      }
      return NULL;
   } else {
      sprintf(message, "%d unlocked", instrument);
      return Py_BuildValue("s",message);
   }
}

static PyObject * DevStsCommand(PyObject *self,
                PyObject *args) {
   int instrument;              /* instrument id        */
   unsigned char stb;           /* status byte          */
   char *err_str;
   int  status;

   if (! PyArg_Parse(args, "(i)", &instrument) ) {
      return NULL;
   }
   if ( gpib_diags ) {
      printf ("Requesting status of device %d\n", instrument);
   }
   while ( ( status = ireadstb (instrument, &stb) )
              == I_ERR_INTERRUPT ); /* repeat until not interrupt error */
   if ( status ) {
      err_str = igeterrstr (status);
      if ( gpib_diags ) {
         printf( "gpib_dev_status: status request of %d failed: %s\n",
                 instrument, err_str);
      }
      sprintf(err_msg,
         "status request of %d failed: %s", instrument, err_str);
      PyErr_SetString(PyExc_Exception, err_msg);
      return NULL;
   } else {
      sprintf(message,"%d", stb);
      return Py_BuildValue("s",message);
   }
}

static PyObject * CloseCommand(PyObject *self,
                PyObject *args) {
   int instrument;
   int error;
   char *err_str;

   if (! PyArg_Parse(args, "(i)", &instrument) ) {
      return NULL;
   }
   if ( error=iclose (instrument)) {
      err_str = igeterrstr(error);
      sprintf (err_msg,
         "closing instrument failed: %s", err_str);
      PyErr_SetString(PyExc_Exception, err_str);
      if (gpib_diags) {
        printf ( "closing instrument failed: %s\n", err_str);
      }
      return NULL;
   } else {
     sprintf(message, "%d closed", instrument);
     return Py_BuildValue("s",message);
   }
}

/* Registration table */

static struct PyMethodDef sicl_methods[] = {
  {"gpib_open",       OpenCommand,  METH_VARARGS, OpenCommand__doc__},
  {"gpib_close",      CloseCommand,     METH_VARARGS, CloseCommand__doc__},
  {"gpib_timeout",    TimeoutCommand,   METH_VARARGS, TimeoutCommand__doc__},
  {"gpib_diags",      DiagCommand,      METH_VARARGS, DiagCommand__doc__},
  {"gpib_send",       SendCommand,      METH_VARARGS, SendCommand__doc__},
  {"gpib_rcv",        RcvCommand,       METH_VARARGS, RcvCommand__doc__},
  {"gpib_prompt",     PromptCommand,    METH_VARARGS, PromptCommand__doc__},
  {"gpib_lock",       LockCommand,      METH_VARARGS, LockCommand__doc__},
  {"gpib_unlock",     UnlockCommand,    METH_VARARGS, UnlockCommand__doc__},
  {"gpib_dev_status", DevStsCommand,    METH_VARARGS, DevStsCommand__doc__},
  {NULL,          NULL}
};

/* module initializer */

void initpysicl() {
  (void) Py_InitModule3("pysicl", sicl_methods, pysicl__doc__);
}
