import os
from sys import platform
import venv

print("Creating Python Virtual Environment...")
venv_dir = os.path.join(os.getcwd(), "venv")
os.makedirs(venv_dir, exist_ok=True)
venv.create(venv_dir, with_pip=True)

print("Activating the Python Virtual Environment created...")
# Windows
if platform == "win32" or platform == "win64" or os.name == 'nt':
	#activation_command = "venv\\Scripts\\activate.bat"
	activation_command = str(venv_dir) + "\\Scripts\\activate"
# MacOS and Linux
else:
	#activation_command = "venv/bin/activate"
	activation_command = ". " + venv_dir + "/bin/activate"

print("Installing Python packages in the Virtual Environment...")
os.system(activation_command + ' && pip install -e .')
print("Cleaning up installation files...")
os.system(activation_command + ' && python setup.py clean')

print("Starting compilation...")
os.system(activation_command + ' && pyinstaller --hidden-import requests --hidden-import xnat --add-data README.md --collect-datas External --onefile Weasel.py')

print("Cleaning up compilation files...")
# Windows
if platform == "win32" or platform == "win64" or os.name == 'nt':
	os.system('move dist\* .')
	os.system('rmdir build /S /Q')
	os.system('rmdir dist /S /Q')
	os.system('del Weasel.spec')
	print("Deleting the created Python Virtual Environment for the process...")
	os.system('rmdir venv /S /Q')
# MacOS and Linux
else:
	os.system('mv dist/* .')
	os.system('rm -rf build/ dist/')
	os.system('rm Weasel.spec')
	print("Deleting the created Python Virtual Environment for the process...")
	os.system('rm -r venv/')

print("Binary file successfully created and saved in the Weasel repository!")