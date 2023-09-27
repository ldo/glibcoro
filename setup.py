#+
# Setuptools script to install glibcoro. Make sure setuptools
# <https://setuptools.pypa.io/en/latest/index.html> is installed.
# Invoke from the command line in this directory as follows:
#
#     python3 setup.py build
#     sudo python3 setup.py install
#
# Written by Lawrence D'Oliveiro <ldo@geek-central.gen.nz>.
#-

import sys
import setuptools
from setuptools.command.build_py import \
    build_py as std_build_py

class my_build_py(std_build_py) :
    "customization of build to perform additional validation."

    def run(self) :
        try :
            exec \
              (
                "async def dummy() :\n"
                "    pass\n"
                "#end dummy\n"
              )
        except SyntaxError :
            sys.stderr.write("This module requires Python 3.5 or later.\n")
            sys.exit(-1)
        #end try
        super().run()
    #end run

#end my_build

setuptools.setup \
  (
    name = "glibcoro",
    version = "0.5",
    description = "asyncio-compatible wrapper for GLib event loop, for Python 3.5 or later",
    author = "Lawrence D'Oliveiro",
    author_email = "ldo@geek-central.gen.nz",
    url = "https://gitlab.com/ldo/glibcoro",
    py_modules = ["glibcoro"],
    cmdclass =
        {
            "build_py" : my_build_py,
        },
  )
