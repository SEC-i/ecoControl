from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import numpy

ext = Extension("_Choltwinters", ["Choltwinters.pyx"],
    include_dirs = [numpy.get_include()],
    extra_link_args = [ '/MANIFEST'] )
                
                
setup(ext_modules=[ext],
      cmdclass = {'build_ext': build_ext})