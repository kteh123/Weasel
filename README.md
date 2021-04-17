<h2 align="center"><img src="Docs/images/uni-sheffield-logo.png" height="128"></h2>

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![Software](https://img.shields.io/badge/Software-DICOM%20Viewer-green)
![Status](https://img.shields.io/badge/Status-Prototype-orange)

# Weasel

Prototype DICOM image viewer.  
To use, open the File Menu and select the 'View DICOM Studies' option. Browse to a folder containing DICOM image files and an XML file 
describing their study/series/image structure. Select this XML file to build a tree view visual representation of this structure. 
To view an image, either double click it or select it, open the Tools menu and select the 'View Image' menu item. 
To view an inverted image, select an image in the tree view, open the Tools menu and select the 'Invert Image' item.

The 'Sample Data' folder contains 24 DICOM images and an XML file describing thier structure. To use this prototype download the source code and this folder to your computer.  Run the source code and browse to the 'Sample Data' folder and select the DICOM.xml file using File\View DICOM Studies

# Installation

**Git** is required to download this repository, unless you choose to download the `.zip` file. In order for Weasel to run successfully, it is required to have **Python (>=3.7)** installed.

Download URLs:

[Git](https://git-scm.com/downloads)

[Python](https://www.python.org/downloads/)


There are 2 options downloading and installing Weasel requirements:

#### Option 1
Download and install everything in one go by opening a Terminal (MacOS and Linux) or a CMD (Windows) and type in the following command:

`pip install -e git+https://github.com/QIB-Sheffield/WEASEL#egg=WEASEL --src <download_path>`

After the installation is finished, it's recommended that you go to the directory where Weasel was installed

`cd <download_path>/weasel`

and run the command

`python setup.py clean` 

to clean the installation files that are not needed anymore.

#### Option 2
First, download the repository via `git clone` or by downloading the `.zip` file and extracting its contents.
Then open a Terminal (MacOS and Linux) or a CMD (Windows), navigate to the downloaded Weasel folder

`cd <Weasel_folder_path>`

and run the command 

`pip install -e .` 

to install all Weasel dependencies. Finally, run the command

`python setup.py clean` 

to clean the installation files that are not needed anymore.

#### For users that are more familiar with Python (Developers)
Running `pip install -e .` will read the `setup.py` file and install the required Python packages to run Weasel successfully. If there are any other Python packages you wish to be installed with Weasel, you can edit the `setup.py` file and add packages to the variable `extra_requirements`.

The core Python modules used in Weasel are in requirements.txt so alternatively you may choose to run `pip install -r requirements.txt` and then any other Python packages of your choice can be installed separately in your machine or in your virtual environment.

# Start the Graphical User Interface
Open a Terminal (MacOS and Linux) or a CMD (Windows), navigate to the downloaded Weasel folder

`cd <Weasel_folder_path>`

and start Weasel by running the command

`python Weasel.py`

If you're a developer, you may start Weasel by opening an IDE (Sublime Text, VS Code, Visual Studio, etc.) and run the Weasel.py script.

# Generate the Executable

If you wish to get one file that executes the whole software, you can compile the Python project into an executable of the operative system you're using by using `pyinstaller`.

First, you need to install it by running:

`pip install pyinstaller`

Then you have to navigate to your Weasel folder

`cd <Weasel_folder_path>`

and run the following command:

`pyinstaller --hidden-import requests --hidden-import xnat --exclude-module External --onefile Weasel.py`

If you wish to go forward with this procedure, it's highly recommended that you use a new and clean python virtual environment to install the relevant packages and make use of those only during compilation.

The generated executable can be found in the `dist` folder. You may delete the `build` folder and the `Weasel.spec` file which are created during this process.

## Multiframe Images

Weasel runs the command `emf2sf` of [dcm4che](https://www.dcm4che.org/) on Multiframe DICOM. The authors will describe more details about this on the [website](https://weasel.pro).
