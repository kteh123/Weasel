import os
from sys import platform
import venv

print("Pull request commit")
# Write the name of the extra Python Packages for development here
extra_packages = ['dipy==1.3.0', 'fslpy==3.0.0', 'scikit-image', 'scikit-learn', 'SimpleITK', 'itk-elastix', 'ukat', 'mdr-library']

print("Creating Python Virtual Environment...")
venv_dir = os.path.join(os.getcwd(), "venv")
icon_file = os.path.join(os.getcwd(), "Documents" , "images" , "favicon.ico")
icon_png = os.path.join(os.getcwd(), "Documents" , "images" , "uni-sheffield-logo.png")
os.makedirs(venv_dir, exist_ok=True)
venv.create(venv_dir, with_pip=True)

print("Activating the Python Virtual Environment created...")
# Windows
if platform == "win32" or platform == "win64" or os.name == 'nt':
	activation_command = '"' + os.path.join(venv_dir, "Scripts", "activate") + '"'
# MacOS and Linux
else:
	activation_command = '. "' + os.path.join(venv_dir, "bin", "activate") + '"'

print("Installing Python packages in the Virtual Environment...")
os.system(activation_command + ' && pip install -e .')
for pypi in extra_packages:
	os.system(activation_command + ' && pip install ' + pypi)

print("Cleaning up installation files...")
os.system(activation_command + ' && python setup.py clean')

print("Creating list of hidden-imports and data to collect and add...")
hidden_modules = ['xnat', 'requests', 'dipy', 'dipy.data', 'matplotlib', 'lmfit', 'fpdf', 'reportlab', 'reportlab.platypus', 'joblib', 'cv2', 'SimpleITK ', 'itk', 'ukat', 'MDR', 'MDR.MDR', 'MDR.Tools', 'sklearn.utils._typedefs', 'sklearn.utils._cython_blas', 'sklearn.neighbors.typedefs', 'sklearn.neighbors.quad_tree', 'sklearn.tree._utils', 'sklearn.neighbors._partition_nodes']
string_hidden_imports = ' '.join(['--hidden-import '+ mod + ' ' for mod in hidden_modules])
collect_data_folders = ['External', 'dipy']
string_collect_data = ' '.join(['--collect-datas '+ mod + ' ' for mod in collect_data_folders])
# Pyinstaller doesn't have hooks for the itk package
itk_path_win = 'venv\\lib\\site-packages\\itk'
intermediate_python_folder = [fldr.name for fldr in os.scandir('venv/lib') if fldr.is_dir()][0] # It's known there's a Python subfolder between 'lib' and 'site-packages' for Unix systems
itk_path_unix = 'venv/lib/' + intermediate_python_folder + '/site-packages/itk'
if platform == "win32" or platform == "win64" or os.name == 'nt':
	data_folders = ['API;.\\API', 'CoreModules;.\\CoreModules', 'Displays;.\\Displays', 'Documents;.\\Documents', 'Menus;.\\Menus', 'Pipelines;.\\Pipelines', 'External;.\\External', itk_path_win+';.\\itk']
else:
	data_folders = ['API:./API', 'CoreModules:./CoreModules', 'Displays:./Displays', 'Documents:./Documents', 'Menus:./Menus', 'Pipelines:./Pipelines', 'External:./External', itk_path_unix+':./itk']
string_data = ' '.join(['--add-data='+ mod + ' ' for mod in data_folders])

print("Starting compilation...")
os.system(activation_command + ' && pyinstaller ' + string_hidden_imports + ' ' + string_collect_data + ' ' + string_data + ' --clean --onefile -i ' + str(icon_file) + ' Weasel.py')

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


# If compiled in MacOS, we need to change permissions and add the icon manually.
if platform == "darwin" or os.name == 'posix':
	os.system('sudo chmod 775 Weasel')
	os.system('sips -i ' + str(icon_png))
	os.system('DeRez -only icns ' +  str(icon_png) + ' > icon.rsrc')
	os.system('Rez -append icon.rsrc -o Weasel')
	os.system('SetFile -a C Weasel')
	os.system('rm -f icon.rsrc')

print("Binary file successfully created and saved in the Weasel repository!")
