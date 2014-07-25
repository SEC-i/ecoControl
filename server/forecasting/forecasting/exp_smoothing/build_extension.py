from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import os
import sys
import subprocess
import numpy
import shlex
import logging
#from server.settings import BASE_DIR


logger = logging.getLogger('extensions')

def build_holtwinters_extension():
    # vsstudio is default compiler for python extensions and should definitely be used on windows. 
    # Newer versions of msvc are sometimes not compatible, although I didnt experience any incompabilities
    # anyway: if vsstudio 2008 not installed,try to use other vs studio version
    optional_command = []
    if os.name == "nt" and "VS90COMNTOOLS" not in os.environ.keys():

        vstools = [vs for vs in os.environ.keys() if vs.startswith("VS") and vs.endswith("COMNTOOLS")]
        #use another vs compiler, should work in most cases
        #optional_command = "SET VS90COMNTOOLS="+"%%VS120COMNTOOLS%%"+";"
        os.environ["VS90COMNTOOLS"] =os.environ[vstools[-1]]#set to path of other vs tools

    starting_directory = os.getcwd()
    #change working directory
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    #build extension and pass in modified envionment variables
    #filepath = os.path.realpath(os.path.join(BASE_DIR, "server/forecasting/forecasting/exp_smoothing/build_extension.py"))
    commandline_args = shlex.split(u"python " + "build_extension.py" + " build_ext --inplace",posix=(os.name == "posix"))
    proc = subprocess.Popen(commandline_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=dict(os.environ))
    out, err = proc.communicate()
    logger.debug(out)
    if len(err) > 0:
        logger.error(err)
  
    os.chdir(starting_directory)



if __name__ == "__main__":

	ext = Extension("holtwinters_fast", ["Choltwinters.pyx"],
	    include_dirs = [numpy.get_include()],
	    extra_link_args = [ '/MANIFEST']  if os.name == "nt" else [] )

	setup(ext_modules=[ext],
	      cmdclass = {'build_ext': build_ext})

