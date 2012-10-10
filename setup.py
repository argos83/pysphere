#! /usr/bin/env python

import sys
try:
    from setuptools import setup
except:
    from distutils.core import setup


VERSION = (0, 1, 7)


if __name__ == "__main__":

    try:
        if sys.argv[1] != "install":
            fd = open("pysphere/version.py", "w")
            # Do not edit. Auto generated
            fd.write("# Do not edit. Auto generated\n")
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
                  "pysphere.ZSI.wstools", "pysphere.ZSI.generate"],
        package_data={'pysphere.ZSI': ['LBNLCopyright']},
        description="Python API for interacting with the vSphere Web Services SDK",
        author="Sebastian Tello",
        author_email="argos83@gmail.com",
        url="http://pysphere.googlecode.com",
        download_url="http://pysphere.googlecode.com/files/pysphere-0.1.7.zip",
        keywords = ["vSphere", "Virtual", "vmware", "ESX", "ESXi",
                    "VirtualCenter", "SDK", "API"],
        classifiers = [
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.5",
            "Programming Language :: Python :: 2.6",
            "Programming Language :: Python :: 2.7",
            "Operating System :: OS Independent",
            "Development Status :: 5 - Production/Stable",
            "Environment :: Other Environment",
            "Intended Audience :: Developers",
            "Intended Audience :: System Administrators",
            "Intended Audience :: Science/Research",
            "Intended Audience :: Information Technology",
            "License :: OSI Approved :: BSD License",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Software Development :: Quality Assurance",
            "Topic :: Software Development :: Testing",
            "Topic :: System :: Distributed Computing",
            "Topic :: System :: Emulators",
            "Topic :: System :: Operating System",
            "Topic :: System :: Systems Administration",
            "Topic :: Utilities"
        ],
        long_description=long_desc
    )