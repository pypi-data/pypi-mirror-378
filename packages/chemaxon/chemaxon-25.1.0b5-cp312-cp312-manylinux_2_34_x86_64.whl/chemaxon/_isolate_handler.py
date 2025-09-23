import ctypes
import os
import re
import threading


class _Opaque(ctypes.Structure):
    """:meta private:"""
    pass

LIBRARY_NAME_PATTERN = re.compile("chemaxon-lib\\.(so|dylib|dll)")
""":meta private:"""

# Idea: use one thread for MainThread and create and tear down IsolateThreads for each other threads.
# Isolate threads enable separate memory space for each thread. So static fields on the java side will become separate
# memory space for the different threads in the generated native code.
class _IsolateHandler:
    """:meta private:"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            library_path = os.path.join(os.path.dirname(__file__), "libs")

            # This is needed because the native shared library extension is differ based on the operation system
            files = os.listdir(library_path)
            cls._instance.cxn = None
            for f in files:
                if LIBRARY_NAME_PATTERN.fullmatch(f):
                    cls._instance.cxn = ctypes.cdll.LoadLibrary(os.path.join(str(library_path), f))
                    break

            if 'awt.dll' in files:
                ctypes.cdll.LoadLibrary(os.path.join(str(library_path), 'awt.dll'))
            if 'libawt_xawt.so' in files:
                ctypes.cdll.LoadLibrary(os.path.join(str(library_path), 'libawt_xawt.so'))

            if cls._instance.cxn is None:
                raise Exception("Could not find chemaxon-lib!")

            cls._instance.main_isolate, cls._instance.main_isolate_thread = _create_new_thread(cls._instance.cxn)
            cls._instance.isolate_torn_down = False
        return cls._instance

    def __del__(self):
        if self._instance.main_isolate_thread is not None:
            self.cxn.graal_tear_down_isolate(self.main_isolate_thread)
            self.isolate_torn_down = True


    def get_isolate_thread(self):
        if threading.current_thread() is threading.main_thread():
            return self._instance.main_isolate_thread

        return _attach_new_thread(self._instance.main_isolate)

    def cleanup_isolate_thread(self, thread):
        if threading.current_thread() is not threading.main_thread():
            _detach_thread(thread)

    def get_lib(self):
        return self.cxn

def _create_new_thread(cxnLib):
    """:meta private:"""
    isolate = ctypes.pointer(_Opaque())
    thread = ctypes.pointer(_Opaque())
    # start native environment
    cxnLib.graal_create_isolate(None, ctypes.pointer(isolate), ctypes.pointer(thread))
    return isolate, thread


def _attach_new_thread(isolate):
    thread = ctypes.pointer(_Opaque())
    rc = _cxn.graal_attach_thread(isolate, ctypes.byref(thread))
    if rc != 0:
        raise RuntimeError(f"graal_attach_thread failed: {rc}")
    return thread


def _detach_thread(thread):
    if thread is not None:
        _cxn.graal_detach_thread(thread)

_isolate_handler = _IsolateHandler()
""":meta private:"""
_cxn = _isolate_handler.get_lib()
""":meta private:"""
