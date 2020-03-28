from distutils.core import setup, Extension
import numpy
import os

os.environ["CC"] = "g++"

# define the extension module
cos_module_np = Extension('parse_pileup', sources=['parse_pileup.cpp'],
                          include_dirs=[numpy.get_include()],
                          extra_compile_args = ["-std=c++0x"],)


# run the setup
setup(ext_modules=[cos_module_np])
