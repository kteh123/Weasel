import os, shutil
from sys import platform
import venv

def CopyTree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            CopyTree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                shutil.copy2(s, d)

print("Preparing the Folder Structure...")
docs_folder = os.path.join(os.getcwd(), "Documents")
manual_folder = os.path.join(docs_folder, "Manual")
temporary_folder = os.path.join(docs_folder, "temp") 
weasel_copy_folder = os.path.join(temporary_folder, "WEASEL")
#############################################################
api_folder = os.path.join(os.getcwd(), "API")
coremodules_folder = os.path.join(os.getcwd(), "CoreModules")
dicom_folder = os.path.join(os.getcwd(), "DICOM")
displays_folder = os.path.join(os.getcwd(), "Displays")
menus_folder = os.path.join(os.getcwd(), "Menus")
pipelines_folder = os.path.join(os.getcwd(), "Pipelines")
weasel_file = os.path.join(os.getcwd(), "Weasel.py")

print("Deleting contents inside the 'Manual' folder")
if os.path.exists(manual_folder):
    shutil.rmtree(manual_folder)

print("Creating temporary Python files and modules to generate the documentation...")
os.makedirs(weasel_copy_folder, exist_ok=True)
CopyTree(api_folder, os.path.join(weasel_copy_folder, "API"))
CopyTree(coremodules_folder, os.path.join(weasel_copy_folder, "CoreModules"))
CopyTree(dicom_folder, os.path.join(weasel_copy_folder, "DICOM"))
CopyTree(displays_folder, os.path.join(weasel_copy_folder, "Displays"))
CopyTree(menus_folder, os.path.join(weasel_copy_folder, "Menus"))
CopyTree(pipelines_folder, os.path.join(weasel_copy_folder, "Pipelines"))
shutil.copyfile(weasel_file, os.path.join(weasel_copy_folder, "Weasel.py"))

print("Creating Python Virtual Environment for the occasion...")
venv_dir = os.path.join(os.getcwd(), "venv")
os.makedirs(venv_dir, exist_ok=True)
venv.create(venv_dir, with_pip=True)

print("Activating the Python Virtual Environment created...")
# Windows
if platform == "win32" or platform == "win64" or os.name == 'nt':
	activation_command = str(venv_dir) + "\\Scripts\\activate"
# MacOS and Linux
else:
	activation_command = ". " + venv_dir + "/bin/activate"

print("Installing Python packages in the Virtual Environment...")
os.system(activation_command + ' && pip install -e .')

print("Creating WEASEL manual using pdoc3...")
doc_command = "pdoc --html --force --output-dir " + str(docs_folder) + " " + str(weasel_copy_folder)
os.system(activation_command + ' && ' + doc_command)

print("Moving documentation files to the 'Manual' folder and deleting temporary files...")
shutil.rmtree(temporary_folder)
shutil.rmtree(venv_dir)
shutil.rmtree("Weasel.egg-info")
shutil.move(os.path.join(docs_folder, "WEASEL"), manual_folder)

print("HTML documentation files successfully created and saved in the 'Manual' folder!")