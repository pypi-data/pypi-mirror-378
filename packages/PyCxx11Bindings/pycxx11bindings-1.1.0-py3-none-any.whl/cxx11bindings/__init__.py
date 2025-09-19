""".. include:: ../../README.md"""

import ctypes


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


class PyC11Stream:
    def __init__(self, stream):
        """context manager to create a C11Stream from a python stream"""
        self._inner_stream = stream
        self._c11_stream = C11Stream()

        def __py_read(_, out_buffer, count):
            try:
                data = self._inner_stream.read(count)
                ctypes.memmove(out_buffer, data, len(data))
                # short-read ok
                return len(data)
            except Exception as e:
                print("Read error occurred: ", e)
                return -1

        def __py_write(_, in_buffer, count):
            try:
                data = ctypes.string_at(in_buffer, count)
                self._inner_stream.write(data)
                return count
            except Exception as e:
                print("Write error occurred: ", e)
                return -1

        def __py_seek(_, offset, seek_dir):
            try:
                return self._inner_stream.seek(offset, seek_dir)
            except Exception as e:
                print("Seek error occurred: ", e)
                return -1

        def __py_flush(_):
            try:
                self._inner_stream.flush()
                return 0
            except Exception as e:
                print("Flush error occurred: ", e)
                return -1

        def __py_trunc(_, new_size):
            try:
                self._inner_stream.truncate(new_size)
                return new_size
            except Exception as e:
                print("Trunc error occurred: ", e)
                return -1

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
