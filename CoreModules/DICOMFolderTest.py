from DICOMFolder import DICOMFolder

folder = DICOMFolder(path='C:\\Users\\steve\\Dropbox\\Data\\WeaselDevSmall')
# folder = DICOMFolder()

# for f in folder.files(): print(f)
folder.create_dataframe()
folder.write_csv()
folder.read_csv()
folder.create_element_tree()
folder.write_xml()
folder.read_xml()
folder.drop_multiframe()
# folder.convert_multiframe()
print('DONE')
