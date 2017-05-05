"""
Availability Model Translation Toolkit (amtt)

setuptools based packaging and installation module
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

import sys
import distutils
import subprocess

from amtt.version import __version__ as amtt_version


here = path.abspath(path.dirname(__file__))


class BuildStandaloneExeCommand(distutils.cmd.Command):
    """
    Custom command to build standalone executable using PyInstaller.

    Invoke by executing:
        python setup.py build_standalone
    """

    description = 'build standalone executable with PyInstaller'
    user_options = []

    def initialize_options(self):
        """Set default values for user options."""

    def finalize_options(self):
        """Post-process user options."""

    def run(self):
        """Run command."""
        sep = ';' if sys.platform == 'win32' else ':'
        path_base = path.dirname(sys.executable)
        command = ' '.join([
            '"' + path.join(path_base, 'pyinstaller') + '"',
            '  --onefile',
            '  --add-data amtt/ui/icon64x64.png{sep}amtt/ui'.format(sep=sep),
            '  --add-data amtt/ui/icon64x64.gif{sep}amtt/ui'.format(sep=sep),
            '  --add-data amtt/exporter/isograph/emitter/xml/template-2.1.xml'
            '{sep}amtt/exporter/isograph/emitter/xml'.format(sep=sep),
            '  amtt/main.py',
            '  -i resources/icon.ico',
            '  -n amtt_{plat}-{ver}'.format(plat=sys.platform,
                                            ver=amtt_version),
        ])
        self.announce('Building standalone executable with PyInstaller',
                      level=distutils.log.INFO)
        subprocess.check_call(command, shell=True)


# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='amtt',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=amtt_version,
    description='Availability Modelling Translation Toolkit',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/errikos/amtt',

    # Author details
    author='Ergys Dona',
    author_email='ergys.dona@cern.ch',

    # Choose your license
    license='GPL-3.0',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Manufacturing',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Physics',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords='availability engineering model translation toolkit',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['docs']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'networkx',
        'pydotplus',
        'pyexcel',
        'pyexcel-xls',
        'sliding-window',
        'lxml',
    ],

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        'amtt.ui': ['icon64x64.png', 'icon64x64.gif'],
        'amtt.exporter.isograph.emitter.xml': ['template-2.1.xml'],
    },

    # List additional groups of dependencies here (e.g. documentation
    # dependencies). You can install these using the following syntax:
    # $ pip install -e .[docs]
    extras_require={
        'docs': ['Sphinx', 'sphinx-rtd-theme'],
        'build': ['PyInstaller'],
    },

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'amtt=amtt.main:main',
            'amtt-gui=amtt.main:ui_main',
        ],
    },

    # Provide custom command for building standalone executable
    cmdclass={
        'build_standalone': BuildStandaloneExeCommand,
    },
)
