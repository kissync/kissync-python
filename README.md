SmartFile Desktop Sync
==========================
[![Build Status](https://travis-ci.org/travcunn/kissync-python.png?branch=master)](https://travis-ci.org/travcunn/kissync-python) [![Coverage Status](https://coveralls.io/repos/kissync/kissync-python/badge.png?branch=master)](https://coveralls.io/r/kissync/kissync-python?branch=master)

A cross platfom desktop file synchronization application for SmartFile


Running SmartFile Sync
===============

__Prerequisites:__

SmartFile Sync requires PySide (cross-platform) for the GUI. On Debian based systems, this can be installed using the following command:

    $ sudo apt-get install python-pyside
    
Other Python dependencies can be installed with the following commands:

    $ pip install --timeout=30 -r requirements.txt --use-mirrors
    $ pip install --timeout=30 -q -e . --use-mirrors


__Build and run:__

    $ git clone https://github.com/travcunn/kissync-python.git kissync
    $ cd kissync
    $ python main.py


Building a Windows installer
=====================
__Prerequisites:__

1. [Python 2.7](http://www.python.org/ftp/python/2.7.5/python-2.7.5.msi)
2. [py2exe](http://sourceforge.net/projects/py2exe/files/py2exe/0.6.9/py2exe-0.6.9.win32-py2.7.exe/download)
3. [NSIS 2.46](http://prdownloads.sourceforge.net/nsis/nsis-2.46-setup.exe?download)
4. [Win32 OpenSSL](http://www.slproweb.com/products/Win32OpenSSL.html)

Nsis requires the following plugins:

1. NsProcess (http://nsis.sourceforge.net/NsProcess_plugin)
2. AccessControl (http://nsis.sourceforge.net/AccessControl_plug-in)

__Build:__

In the console, run:

    $ installer_windows.cmd

Alternatively, you can open *installer_windows.cmd* from the Windows file explorer.

The installer will named "smartfile-installer.exe" in the directory "installer_windows"


Resource Packaging
===============
PySide has a simple packing system that allows for embedding of all the program resources (such as images) into one file. Using a program by Shuge Lee, these resources are collected automatically. This process has been simplified and automated in the make file. For images to be collected, they should be placed in "ui/images".

__Prerequisites:__ 

* pyside-rcc (included in pyside-tools)

On Ubuntu/Debian, this can be installed using the following command:

    $ sudo apt-get install pyside-tools

__Build:__

To build the resources automatically, run the following command in the console:

    $ make resources

__Using resources__:

Since building the resources with the make file puts a "resources.py" into the UI folder, any UI component that references external images will automatically discover the resources file, assuming it is in the same folder. 

To use any packaged resource in the UI, refer to the following example:
 
    QtGui.QIcon(":/menuicon.png")

This allows us to reference a resource with the file name ":/menuicon.png"

Links
====
[Official Kissync Website](http://www.kissync.com)

[MIT License](https://github.com/kissync/kissync-python/blob/master/LICENSE.MIT)
