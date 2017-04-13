.. _build_instructions:

Building from source
====================

This section outlines the procedure to follow if you need to build a bundle of
amtt (which can be useful if you want to distribute the application without
having to build it in every machine).

Python version
--------------

amtt is written in Python and was developed with **Python 3.5**.
It has been tested to work with Python 3.6 as well, although as of the time of
writing this text, creating a bundle with Python 3.6+ is not supported. The
reason is explained in the following note.


**Note:** amtt uses PyInstaller in order to build standalone archives. While
amtt should work with any Python 3.5+ version, PyInstaller does not usually
support the latest Python version right away. Before proceeding, please check
with the |PyInstaller| home page for the maximum supported Python version.
If in doubt, it is recommended that you use Python 3.5 (either 32 or 64 bit).

Requirements
------------

Download and install Python
"""""""""""""""""""""""""""

* For **Windows**, download the |PythonInstallerWin| (either 32 or 64 bit will work). Upon installing, make sure to check the "Add Python to PATH" option.
* For **Linux**, Python should be available via your package manager. You can also refer to the |PyEnv| project, which allows you to install any Python version to any distribution locally (as well as the system meets the pyenv dependencies).
* For **MacOS**, you can install Python via the |PythonInstallerMac|, via |Homebrew| or via the |PyEnv| project.

Clone or download the amtt repository
"""""""""""""""""""""""""""""""""""""

The ammt repository is located in GitHub: https://github.com/errikos/amtt .

* You can clone the repository by using git::

    git clone https://github.com/errikos/amtt.git

* Or, if you do not want to clone, you can download the master snapshot: https://github.com/errikos/amtt/archive/master.zip

Installing the application
--------------------------

After you have downloaded the source, you can start the installation process.

Change directory, or ``cd``, to the directory containing the source code (you will first need to extract archive if you downloaded the master snapshot). Then, you have two options:

* via ``pip`` (**recommended**):

  ``pip`` is a package manager for Python packages and is automatically installed if you install Python via the Windows/MacOS installers and the Homebrew/pyenv projects. For package manager based installations in Linux, you may need to install it manually.

  Once inside the source directory, execute::

      pip install .


* without ``pip``, via ``distutils``:

  ``distutils`` are bundled in the standard Python distribution.

  1. To fetch the dependencies and build the application::

      python setup.py build

  2. To install the application, after building::

      python setup.py install

  3. In you encounter an error like the following::

      error: The 'pyexcel' distribution was not found and is required by amtt

   then execute the install command again::

      python setup.py install

  The above two commands will install the application in your local python distribution (the one that resembles to the executed ``python`` command) along with all the required dependencies. They will also install the application executables, which can then be called from the command line (see `Running the application`_ below for more details).


Running the application
-----------------------

There are two ways to run the application. The easier way is via the user interface. However, you can also run the application via the command line. The installation procedure described above installs both.

Open a command prompt (Windows) or a terminal (Linux/MacOS).

* To run the graphical user interface, execute ``amtt-gui``.
* To run the command line interface, execute ``amtt``.


Building an application bundle
------------------------------

If you want to distribute the application among many users, the easiest way is to create an application bundle, i.e. a standalone executable, that is ready-to-run on any machine.

This bundle will have to dependencies whatsoever and will run on a given machine, even if no Python version is installed on it.

To create an application bundle:

1. Make sure you have followed the installation procedure in `Installing the application`_.
2. Install ``PyInstaller``:

  * via ``pip`` (easiest, trouble-free method)::

      pip install PyInstaller

  * without ``pip``:

    1. Download the latest PyInstaller package from PyPi: https://pypi.python.org/pypi/PyInstaller/
    2. Extract it, ``cd`` to the extracted directory and execute::

        python setup.py install

3. While in the project root folder (where ``setup.py`` resides), execute::

    python setup.py build_standalone

After the process is complete, you will find the bundle in the ``dist`` directory.

Please note that the build process builds a bundle for the operating system you are currently using. It is not possible to cross-compile and create application bundles for other operating systems.

Therefore, you can only build for Linux from a Linux installation, for MacOS from a MacOS installation and for Windows from a Windows installation.

.. |PyInstaller| raw:: html

   <a href="https://pyinstaller.readthedocs.io/en/stable/" target="_blank">
     PyInstaller
   </a>

.. |PythonInstallerWin| raw:: html

   <a href="https://www.python.org/downloads/windows/" target="_blank">
     Python Windows Installer
   </a>

.. |PythonInstallerMac| raw:: html

   <a href="https://www.python.org/downloads/mac-osx/" target="_blank">
     Python MacOS Installer
   </a>

.. |PyEnv| raw:: html

   <a href="https://github.com/pyenv/pyenv" target="_blank">
     pyenv
   </a>

.. |Homebrew| raw:: html

   <a href="https://brew.sh/" target="_blank">
     Homebrew
   </a>