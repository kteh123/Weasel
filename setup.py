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

# Write the name of the extra Python Packages for development here
extra_requirements = ['xnat==0.3.25', 'dipy==1.3.0', 'fslpy==3.0.0', 'itk-elastix==0.8.0', 'pandas==0.25.1', 'scikit-image==0.16.2', 'scikit-learn==0.21.3', 'tqdm']

class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        if platform == "win32" or "win64":
            os.system('rmdir /s Weasel.egg-info')
        else:
            os.system('rm -vrf Weasel.egg-info')

setup(
    # Software Info
    name="Weasel",
    author='Steven Shillitoe & Joao Sousa',
    author_email='s.shillitoe@sheffield.ac.uk & j.g.sousa@sheffield.ac.uk',
    version="1.0",
    description="Prototyping Medical Imaging Applications.",
    long_description = long_description,
    long_description_content_type='text/markdown',
    url="https://weasel.pro",
    license="Apache-2.0",

    # Python Packages and Installation
    python_requires='>=3.5, <4',
    packages=find_packages(),
    install_requires= [requirements, extra_requirements],

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
