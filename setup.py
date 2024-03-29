import os
from sys import platform
from setuptools import setup, find_packages, Command
#import logging
#logger = logging.getLogger(__name__)
#logger.info("setup.py called")

# Use README.md as the long description
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

# Get core requirements from text file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        if platform == "win32" or platform == "win64" or os.name == 'nt':
            os.system('rmdir /S /Q Weasel.egg-info')
        else:
            os.system('rm -vrf Weasel.egg-info')

setup(
    # Software Info
    name="Weasel",
    author='Steven Shillitoe, Joao Sousa & Steven Sourbron',
    author_email='s.shillitoe@sheffield.ac.uk, j.g.sousa@sheffield.ac.uk, s.sourbron@sheffield.ac.uk',
    version="0.2",
    description="Prototyping Medical Imaging Applications.",
    long_description = long_description,
    long_description_content_type='text/markdown',
    url="https://weasel.pro",
    license="Apache-2.0",

    # Python Packages and Installation
    python_requires='>=3.5, <4',
    packages=find_packages(),
    install_requires= [requirements],

    # Classifiers - the purpose in the future is to create a wheel (pip install wheel) and then upload to PYPI
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate you support Python 3. These classifiers are *not*
        # checked by 'pip install'. See instead 'python_requires' below.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
    ],

    cmdclass={'clean': CleanCommand}

)
