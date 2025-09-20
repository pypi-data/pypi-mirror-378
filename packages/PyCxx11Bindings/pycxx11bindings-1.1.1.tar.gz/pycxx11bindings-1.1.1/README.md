[![img](https://img.shields.io/github/contributors/dicomstudio/PyCxx11Bindings.svg?style=flat-square)](https://github.com/dicomstudio/PyCxx11Bindings/graphs/contributors)
[![img](https://img.shields.io/github/forks/dicomstudio/PyCxx11Bindings.svg?style=flat-square)](https://github.com/dicomstudio/PyCxx11Bindings/network/members)
[![img](https://img.shields.io/github/stars/dicomstudio/PyCxx11Bindings.svg?style=flat-square)](https://github.com/dicomstudio/PyCxx11Bindings/stargazers)
[![img](https://img.shields.io/github/issues/dicomstudio/PyCxx11Bindings.svg?style=flat-square)](https://github.com/dicomstudio/PyCxx11Bindings/issues)
[![img](https://img.shields.io/github/license/dicomstudio/PyCxx11Bindings.svg?style=flat-square)](https://github.com/dicomstudio/PyCxx11Bindings/blob/main/LICENSE)
[![img](https://img.shields.io/github/actions/workflow/status/dicomstudio/PyCxx11Bindings/test.yaml.svg?label=test&style=flat-square)](https://github.com/dicomstudio/PyCxx11Bindings/actions/workflows/test.yaml)
[![img](https://img.shields.io/github/actions/workflow/status/dicomstudio/PyCxx11Bindings/release.yaml.svg?label=release&style=flat-square)](https://github.com/dicomstudio/PyCxx11Bindings/actions/workflows/release.yaml)
[![img](https://img.shields.io/badge/pre--commit-enabled-brightgreen.svg?logo=pre-commit&style=flat-square)](https://github.com/dicomstudio/PyCxx11Bindings/blob/main/.pre-commit-config.yaml)

[![img](https://img.shields.io/pypi/v/PyCxx11Bindings.svg?style=flat-square)](https://pypi.org/project/PyCxx11Bindings)
[![img](https://img.shields.io/pypi/pyversions/PyCxx11Bindings.svg?style=flat-square)](https://pypi.org/project/PyCxx11Bindings)


# PyCxx11Bindings

## About The Project

ctypes provides a set of marshaling capabilities for C-style APIs, but it does not support C++ Stream/APIs directly.

### Installation

This package is available on [PyPI](https://pypi.org/project/PyCxx11Bindings/). You install it using pip:

    pip install PyCxx11Bindings

## Usage

In your Python code, you can now write something like:

```python
from ctypes import *
from cxx11bindings import *
_acme_convert = _func(
    "acme_convert", c_bool, [POINTER(C11Stream), POINTER(C11Stream)]
)

def acme_convert(instream, outstream):
  with PyC11Stream(instream) as srcWrap:
    with PyC11Stream(outstream) as dstWrap:
      ret = _acme_convert(srcWrap, dstWrap)
      if not ret:
        raise ValueError(f"Fail to convert to ACME")

if __name__ == "__main__":
  in_file = open(sys.argv[1], "rb")
  out_file = open(sys.argv[2], "wb")
  acme_convert(in_file, out_file)
```

## Contributing

Any Contributions are greatly appreciated! If you have a question, an issue or would like to contribute, please read our [contributing guidelines](CONTRIBUTING.md).

## License

Distributed under the [MIT License](LICENSE)

## References

* https://github.com/dicomstudio/Cxx11Bindings
* https://github.com/dicomstudio/Cxx11BindingsSharp
