def main(weasel):

    menu = weasel.menu("XNAT")  
        
    menu.item(
        label = 'Download DICOM from XNAT', 
        tooltip = 'Prompts the user to choose the images to download from XNAT',
        icon = 'Documents/images/XNAT-LOGO.png',
        pipeline = 'XNAT__App',
        functionName = 'download'),

    menu.item(
        label = 'Upload DICOM to XNAT',
        tooltip = 'Prompts the user to upload the selected images to XNAT',
        icon = 'Documents/images/XNAT-LOGO.png',
        pipeline = 'XNAT__App',
        functionName = 'upload'),