""".. include:: ../../README.md"""

import ctypes
import io
from enum import Enum, auto


class C11Stream(ctypes.Structure):  # forward declaration
    pass


# Define the function pointer type
READ_CB = ctypes.CFUNCTYPE(
    ctypes.c_int32,
    ctypes.POINTER(C11Stream),
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_int32,
)
WRITE_CB = ctypes.CFUNCTYPE(
    ctypes.c_int32,
    ctypes.POINTER(C11Stream),
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_int32,
)
SEEK_CB = ctypes.CFUNCTYPE(
    ctypes.c_int64, ctypes.POINTER(C11Stream), ctypes.c_int64, ctypes.c_int
)
FLUSH_CB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(C11Stream))
TRUNC_CB = ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.POINTER(C11Stream), ctypes.c_int64)


# now that callbacks are defined, we can define the structure:
class C11Stream(ctypes.Structure):
    _fields_ = [
        ("read", READ_CB),  #
        ("write", WRITE_CB),  #
        ("seek", SEEK_CB),  #
        ("flush", FLUSH_CB),  #
        ("trunc", TRUNC_CB),
    ]


class ErrorCodes(Enum):
    C11_E_POINTER = -2147483648  # int32 negative value for 0x80000000
    C11_E_NOTSUPPORTED = (auto(),)
    C11_E_INVALIDARG = (auto(),)
    C11_E_ARGUMENTOUTOFRANGE = (auto(),)
    C11_E_OBJECTDISPOSED = (auto(),)
    C11_E_IO = (auto(),)


EXCEPTION_CODE_MAP = {
    AttributeError: ErrorCodes.C11_E_POINTER,
    NotImplementedError: ErrorCodes.C11_E_NOTSUPPORTED,
    ValueError: ErrorCodes.C11_E_INVALIDARG,
    IndexError: ErrorCodes.C11_E_ARGUMENTOUTOFRANGE,
    RuntimeError: ErrorCodes.C11_E_OBJECTDISPOSED,
    IOError: ErrorCodes.C11_E_IO,
}
# Reverse mapping: ErrorCodes to Python exception types
CODE_EXCEPTION_MAP = {v: k for k, v in EXCEPTION_CODE_MAP.items()}


def exception_to_code(exc):
    """Map Python exception types to integer codes using a dictionary."""
    for exc_type, code in EXCEPTION_CODE_MAP.items():
        if isinstance(exc, exc_type):
            return code
    assert False
    return -1  # Unknown exception


class PyC11Stream(io.IOBase):
    def __init__(self, stream):
        """dual personality stream.
        context manager to create a C11Stream from a python streami
        """
        self._inner_stream = stream
        self._c11_stream = C11Stream()

        def __py_read(_, out_buffer, count):
            try:
                data = self._inner_stream.read(count)
                ctypes.memmove(out_buffer, data, len(data))
                # short-read ok
                return len(data)
            except Exception as e:
                return exception_to_code(e)

        def __py_write(_, in_buffer, count):
            try:
                data = ctypes.string_at(in_buffer, count)
                self._inner_stream.write(data)
                return count
            except Exception as e:
                return exception_to_code(e)

        def __py_seek(_, offset, seek_dir):
            try:
                return self._inner_stream.seek(offset, seek_dir)
            except Exception as e:
                return exception_to_code(e)

        def __py_flush(_):
            try:
                self._inner_stream.flush()
                return 0
            except Exception as e:
                return exception_to_code(e)

        def __py_trunc(_, new_size):
            try:
                self._inner_stream.truncate(new_size)
                return new_size
            except Exception as e:
                return exception_to_code(e)

        self._c11_stream.read = READ_CB(__py_read)
        self._c11_stream.write = WRITE_CB(__py_write)
        self._c11_stream.seek = SEEK_CB(__py_seek)
        self._c11_stream.flush = FLUSH_CB(__py_flush)
        self._c11_stream.trunc = TRUNC_CB(__py_trunc)

    def __enter__(self):
        """return the internal stream pointer"""
        return ctypes.byref(self._c11_stream)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """flush is done directly by the inner stream"""
        pass

    # Implementing IOBase methods to make PyC11Stream behave like a stream

    def read(self, size=-1):
        return self._inner_stream.read(size)

    def write(self, b):
        return self._inner_stream.write(b)

    def seek(self, offset, whence=io.SEEK_SET):
        return self._inner_stream.seek(offset, whence)

    def flush(self):
        return self._inner_stream.flush()

    def close(self):
        return self._inner_stream.close()

    def readable(self):
        return self._inner_stream.readable()

    def writable(self):
        return self._inner_stream.writable()

    def seekable(self):
        return self._inner_stream.seekable()
