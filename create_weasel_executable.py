import os
from sys import platform
import venv

print("Creating Python Virtual Environment...")
venv_dir = os.path.join(os.getcwd(), "venv")
icon_file = os.path.join(os.getcwd(), "Documents" , "images" , "favicon.ico")
icon_png = os.path.join(os.getcwd(), "Documents" , "images" , "uni-sheffield-logo.png")
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

print("Cleaning up installation files...")
os.system(activation_command + ' && python setup.py clean')

print("Creating list of hidden-imports and data to collect and add...")
hidden_modules = ['xnat', 'requests', 'dipy', 'dipy.data', 'matplotlib', 'lmfit', 'fpdf', 'reportlab', 'reportlab.platypus', 'joblib', 'cv2', 'ukat']
string_hidden_imports = ' '.join(['--hidden-import '+ mod for mod in hidden_modules])
collect_data_folders = ['External', 'dipy']
string_collect_data = ' '.join(['--collect-datas '+ mod for mod in collect_data_folders])
if platform == "win32" or platform == "win64" or os.name == 'nt':
	data_folders = ['API;.', 'Menus;.', 'Pipelines;.']
else:
	data_folders = ['API:.', 'Menus:.', 'Pipelines:.']
string_data = ' '.join(['--add-data '+ mod for mod in data_folders])

print("Starting compilation...")
os.system(activation_command + ' && pyinstaller ' + string_hidden_imports + ' ' + string_collect_data + ' ' + string_data + ' --clean --onefile -i ' + str(icon_file) + ' Weasel.py')
# Add the "Scripting"/"Pipelines" folder when we make official release
# Add the --windowed flag when we have full confidence of running without errors and all logged in the Activity Log.


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


# If compiled in MacOS, we need to create the App Bundle manually.
if platform == "darwin" or os.name == 'posix':
	os.system('sudo chmod 775 Weasel')
	os.system('sips -i ' + str(icon_png))
	os.system('DeRez -only icns ' +  str(icon_png) + ' > icon.rsrc')
	os.system('Rez -append icon.rsrc -o Weasel')
	os.system('SetFile -a C Weasel')
	os.system('rm -f icon.rsrc')

print("Binary file successfully created and saved in the Weasel repository!")
