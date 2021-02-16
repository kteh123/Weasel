import os
import datetime
import zipfile
import warnings
import requests
from CoreModules.DeveloperTools import UserInterfaceTools
import xnat

def isEnabled(self):
    return True

def download(objWeasel):
    # Insert Try/Except
    ui = UserInterfaceTools(objWeasel)
    credentialsWindow = {"URL":"string,https://xnat.vital-it.ch", "Username":"string", "Password":"string"}
    info = "Please insert the XNAT URL and your XNAT credentials"
    loginDetails = ui.inputWindow(credentialsWindow, title="XNAT Login", helpText=info)
    if loginDetails is None: return
    url = loginDetails[0] # 
    username = loginDetails[1]
    password = loginDetails[2]
    with xnat.connect(url, user=username, password=password) as session:
        xnatProjects = [project.secondary_id for project in session.projects.values()]
        projectWindow = {"Project":"dropdownlist"}
        projectInfo = "URL: " + url + "<p>Select the Project to download the images from</p>"
        projectName = ui.inputWindow(projectWindow, title="XNAT Download", helpText=projectInfo, lists=[xnatProjects])
        if projectName is None: return
        if projectName:
            xnatSubjects = [subject.label for subject in session.projects[projectName[0]].subjects.values()]
            xnatSubjects.insert(0, "All")
            subjectWindow = {"Subject":"dropdownlist"}
            subjectInfo = "URL: " + url + "<p>Project: " + projectName[0] + "</p><p>Select the Subject to download the images from</p>"
            subjectName = ui.inputWindow(subjectWindow, title="XNAT Download", helpText=subjectInfo, lists=[xnatSubjects])
            if subjectName is None: return
            if subjectName:
                if subjectName[0] == "All":
                    dataset = session.projects[projectName[0]]
                    downloadFolder = selectXNATPathDownload(objWeasel)
                    ui.showInformationWindow("XNAT Download", "The selected images will be downloaded to the root folder of the TreeView. The download progress can be checked in the terminal and you may continue using Weasel.")
                    dataset.download_dir(downloadFolder)
                    ui.showInformationWindow("XNAT Download", "Download completed!")
                else:
                    xnatExperiments = [experiment.label for experiment in session.projects[projectName[0]].subjects[subjectName[0]].experiments.values()]
                    xnatExperiments.insert(0, "All")
                    experimentWindow = {"Experiment":"dropdownlist"}
                    experimentInfo = "URL: " + url + "<p>Project: " + projectName[0] + "</p><p>Subject: " + subjectName[0] + "</p><p>Select the Experiment to download the images from</p>"
                    experimentName = ui.inputWindow(experimentWindow, title="XNAT Download", helpText=experimentInfo, lists=[xnatExperiments])
                    if experimentName is None: return
                    if experimentName:
                        if experimentName[0] == "All":
                            dataset = session.projects[projectName[0]].subjects[subjectName[0]]
                            downloadFolder = selectXNATPathDownload(objWeasel)
                            ui.showInformationWindow("XNAT Download", "The selected images will be downloaded to the root folder of the TreeView. The download progress can be checked in the terminal and you may continue using Weasel.")
                            dataset.download_dir(downloadFolder)
                            ui.showInformationWindow("XNAT Download", "Download completed!")
                        else:
                            xnatScans = [scan.series_description for scan in session.projects[projectName[0]].subjects[subjectName[0]].experiments[experimentName[0]].scans.values()]
                            xnatScans.insert(0, "All")
                            scanWindow = {"Scan":"dropdownlist"}
                            scanInfo = "URL: " + url + "<p>Project: " + projectName[0] + "</p><p>Subject: " + subjectName[0] + "</p><p>Experiment: " + experimentName[0] + "</p><p>Select the Scan to download the images from</p>"
                            scanName = ui.inputWindow(scanWindow, title="XNAT Download", helpText=scanInfo, lists=[xnatScans])
                            if scanName:
                                if scanName[0] == "All":
                                    dataset = session.projects[projectName[0]].subjects[subjectName[0]].experiments[experimentName[0]]
                                    downloadFolder = selectXNATPathDownload(objWeasel)
                                    ui.showInformationWindow("XNAT Download", "The selected images will be downloaded to the root folder of the TreeView. The download progress can be checked in the terminal and you may continue using Weasel.")
                                    dataset.download_dir(downloadFolder)
                                    ui.showInformationWindow("XNAT Download", "Download completed!")
                                else:
                                    dataset = session.projects[projectName[0]].subjects[subjectName[0]].experiments[experimentName[0]].scans[scanName[0]]
                                    downloadFolder = selectXNATPathDownload(objWeasel)
                                    ui.showInformationWindow("XNAT Download", "The selected images will be downloaded to the root folder of the TreeView. The download progress can be checked in the terminal and you may continue using Weasel.") 
                                    dataset.download_dir(downloadFolder)
                                    ui.showInformationWindow("XNAT Download", "Download completed!")
    # Delete Login Details
    del loginDetails, url, username, password
    session.disconnect()
    return


def upload(objWeasel):
    # Insert Try/Except
    ui = UserInterfaceTools(objWeasel)
    credentialsWindow = {"URL":"string,https://xnat.vital-it.ch", "Username":"string", "Password":"string"}
    info = "Please insert the XNAT URL and your XNAT credentials"
    loginDetails = ui.inputWindow(credentialsWindow, title="XNAT Login", helpText=info)
    if loginDetails is None: return
    url = loginDetails[0] #
    username = loginDetails[1]
    password = loginDetails[2]
    with xnat.connect(url, user=username, password=password) as session:
        xnatProjects = [project.secondary_id for project in session.projects.values()]
        projectWindow = {"Project":"dropdownlist"}
        projectInfo = "URL: " + url + "<p>Select the Project to upload the images from</p>"
        projectName = ui.inputWindow(projectWindow, title="XNAT Upload", helpText=projectInfo, lists=[xnatProjects])
        if projectName is None: return
        if projectName:
            xnatSubjects = [subject.label for subject in session.projects[projectName[0]].subjects.values()]
            xnatSubjects.insert(0, "Upload at Project Level")
            subjectWindow = {"Subject":"dropdownlist"}
            subjectInfo = "URL: " + url + "<p>Project: " + projectName[0] + "</p><p>Select the Subject to upload the images from</p>"
            subjectName = ui.inputWindow(subjectWindow, title="XNAT Upload", helpText=subjectInfo, lists=[xnatSubjects])
            if subjectName is None: return
            if subjectName:
                if subjectName[0] == "Upload at Project Level":
                    uploadPaths = selectXNATPathUpload(objWeasel)
                    uploadZipFile = zipFiles(uploadPaths)
                    ui.showInformationWindow("XNAT Upload", "The selected images will be uploaded to the selected project. The upload progress can be checked in the terminal and you may continue using Weasel.")
                    try:
                        session.services.import_(uploadZipFile, overwrite='none', project=session.projects[projectName[0]].id, content_type='application/zip')
                    except:
                        warnings.warn('The zip file being uploaded contains files already present in the selected image session and the upload assistant cannot overwrite or give the option to not overwrite. \n The selected file or folder was pre-archived in the selected XNAT project. \n Please login to the portal and review and/or archive the images.')
                    ui.showInformationWindow("XNAT Upload", "Upload completed!")
                else:
                    xnatExperiments = [experiment.label for experiment in session.projects[projectName[0]].subjects[subjectName[0]].experiments.values()]
                    xnatExperiments.insert(0, "Upload at Subject Level")
                    experimentWindow = {"Experiment":"dropdownlist"}
                    experimentInfo = "URL: " + url + "<p>Project: " + projectName[0] + "</p><p>Subject: " + subjectName[0] + "</p><p>Select the Experiment to upload the images from</p>"
                    experimentName = ui.inputWindow(experimentWindow, title="XNAT Upload", helpText=experimentInfo, lists=[xnatExperiments])
                    if experimentName is None: return
                    if experimentName:
                        if experimentName[0] == "Upload at Subject Level":
                            uploadPaths = selectXNATPathUpload(objWeasel)
                            uploadZipFile = zipFiles(uploadPaths)
                            ui.showInformationWindow("XNAT Upload", "The selected images will be uploaded to the selected subject. The upload progress can be checked in the terminal and you may continue using Weasel.")
                            try:
                                session.services.import_(uploadZipFile, overwrite='none', project=session.projects[projectName[0]].id, subject=session.projects[projectName[0]].subjects[subjectName[0]].id, content_type='application/zip')
                            except:
                                warnings.warn('The zip file being uploaded contains files already present in the selected image session and the upload assistant cannot overwrite or give the option to not overwrite. \n The selected file or folder was pre-archived in the selected XNAT project. \n Please login to the portal and review and/or archive the images.')
                            ui.showInformationWindow("XNAT Upload", "Upload completed!")
                        else:
                            uploadPaths = selectXNATPathUpload(objWeasel)
                            uploadZipFile = zipFiles(uploadPaths)
                            ui.showInformationWindow("XNAT Upload", "The selected images will be uploaded to the selected experiment. The upload progress can be checked in the terminal and you may continue using Weasel.")
                            try:
                                session.services.import_(uploadZipFile, overwrite='none', project=session.projects[projectName[0]].id, subject=session.projects[projectName[0]].subjects[subjectName[0]].id, experiment=session.projects[projectName[0]].subjects[subjectName[0]].experiments[experimentName[0]].id, content_type='application/zip')
                            except:
                                warnings.warn('The zip file being uploaded contains files already present in the selected image session and the upload assistant cannot overwrite or give the option to not overwrite. \n The selected file or folder was pre-archived in the selected XNAT project. \n Please login to the portal and review and/or archive the images.')
                            ui.showInformationWindow("XNAT Upload", "Upload completed!")
    # Curl Command
    headers = {"Content-Type": "application/json", "Accept": "*/*"}
    # Update the project's indices
    for individual_experiment in session.projects[projectName[0]].experiments:
        curl_url = url + "/xapi/viewer/projects/" + session.projects[projectName[0]].id + "/experiments/" + individual_experiment
        response = requests.post(curl_url, headers=headers, auth=(username, password))
    # Delete Login Details
    del loginDetails, url, username, password
    # Delete ZIP File
    os.remove(uploadZipFile)
    session.disconnect()

    
def selectXNATPathDownload(self, tree_view_dir=False):
    if tree_view_dir == False:
        ui = UserInterfaceTools(self)
        directory = ui.selectFolder(title="Select the directory where you wish to download")
    else:
        directory = self.DICOMfolderPath
    return directory


def selectXNATPathUpload(self, tree_view=False):
    listPaths = []
    ui = UserInterfaceTools(self)
    if tree_view == True:
        images = ui.getCheckedImages()
        for image in images:
            listPaths.append(image.path)
    else:
        directory = ui.selectFolder(title="Select the directory with the files you wish to upload")
        for root, _, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                listPaths.append(filepath)
    return listPaths


def zipFiles(listPaths):
    dt = datetime.datetime.now()
    zip_file = zipfile.ZipFile(dt.strftime('%Y%m%d') + '_xnat_upload.zip', 'w')
    for file in listPaths:
        zip_file.write(file, compress_type=zipfile.ZIP_DEFLATED)
    zip_file.close()
    zip_path = os.path.realpath(zip_file.filename)
    return zip_path
