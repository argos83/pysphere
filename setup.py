#! /usr/bin/env python

import sys
from distutils.core import setup


VERSION = (0, 1, 0)


if __name__ == "__main__":

    try:
        if sys.argv[1] != "install":
            fd = open("pysphere/version.py", "w")
            # Do not edit. Auto generated
            fd.write("# Do not edit. Auto generated")
            fd.write("version = (%d, %d, %d)" % VERSION)
            fd.close()
    except:
        pass

    fd = open("README", "r")
    long_desc = fd.read()
    fd.close()

    setup(
        name="pysphere",
        version=".".join(["%d" % v for v in VERSION]),
        license="New BSD License",
        packages=["pysphere", "pysphere.resources", "pysphere.ZSI",
                  "pysphere.ZSI.wstools", "pysphere.ZSI.twisted",
                  "pysphere.ZSI.generate"],
        package_data={'pysphere.ZSI': ['LBNLCopyright']},
        description="Python API for interacting with the vSphere Web Services SDK",
        author="Sebastian Tello",
        author_email="argos83@gmail.com",
        url="http://pysphere.googlecode.com",
        long_description=long_desc
    )