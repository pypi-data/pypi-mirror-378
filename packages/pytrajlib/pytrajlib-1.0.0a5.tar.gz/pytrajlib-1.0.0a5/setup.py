from setuptools import setup
setup(
    name="pytrajlib",
    version="1.0.0-alpha.5",
    cffi_modules=["src/pytrajlib/build.py:ffibuilder"],
)