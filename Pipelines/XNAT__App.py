"""
Prompts an Input Window where the user can insert their XNAT portal credentials and download or upload the selected DICOM images.
"""

import os
import datetime
import zipfile
import warnings
import requests
import xnat

def isEnabled(self):
    return True

def download(weasel):
    try:
        url_input = {"type":"string", "label":"URL", "value":"https://test-ukrin.dpuk.org"}
        username_input = {"type":"string", "label":"Username", "value":"your.xnat.username"}
        password_input = {"type":"string", "label":"Password"}
        cancel, loginDetails = weasel.user_input(url_input, username_input, password_input, title="XNAT Login")
        if cancel: return
        url = loginDetails[0]['value'] # https://test-ukrin.dpuk.org
        username = loginDetails[1]['value']
        password = loginDetails[2]['value']
        with xnat.connect(url, user=username, password=password) as session:
            xnatProjects = [project.secondary_id for project in session.projects.values()]
            projectWindow = {"type":"dropdownlist", "label":"Project", "list":xnatProjects}
            cancel, project = weasel.user_input(projectWindow, title="XNAT Download")
            if cancel: return
            projectID = project[0]['list'][project[0]['value']]
            projectName = [project.name for project in session.projects.values() if project.secondary_id == projectID][0]
            if projectName:
                xnatSubjects = [subject.label for subject in session.projects[projectName].subjects.values()]
                xnatSubjects.insert(0, "All")
                subjectWindow = {"type":"dropdownlist", "label":"Subject", "list":xnatSubjects}
                cancel, subject = weasel.user_input(subjectWindow, title="XNAT Download")
                if cancel: return
                subjectName = subject[0]['list'][subject[0]['value']]
                if subjectName:
                    if subjectName == "All":
                        dataset = session.projects[projectName]
                        downloadFolder = selectXNATPathDownload(weasel)
                        weasel.information("The selected images will be downloaded to the root folder of the TreeView. The download progress can be checked in the terminal and you may continue using Weasel.", "XNAT Download")
                        dataset.download_dir(downloadFolder)
                        weasel.information("Download completed!", "XNAT Download")
                    else:
                        xnatExperiments = [experiment.label for experiment in session.projects[projectName].subjects[subjectName].experiments.values()]
                        xnatExperiments.insert(0, "All")
                        experimentWindow = {"type":"dropdownlist", "label":"Experiment", "list":xnatExperiments}
                        cancel, experiment = weasel.user_input(experimentWindow, title="XNAT Download")
                        if cancel: return
                        experimentName = experiment[0]['list'][experiment[0]['value']]
                        if experimentName:
                            if experimentName == "All":
                                dataset = session.projects[projectName].subjects[subjectName]
                                downloadFolder = selectXNATPathDownload(weasel)
                                weasel.information("The selected images will be downloaded to the root folder of the TreeView. The download progress can be checked in the terminal and you may continue using Weasel.", "XNAT Download")
                                dataset.download_dir(downloadFolder)
                                weasel.information("Download completed!", "XNAT Download")
                            else:
                                xnatScans = [scan.series_description for scan in session.projects[projectName].subjects[subjectName].experiments[experimentName].scans.values()]
                                xnatScans.insert(0, "All")
                                scanWindow = {"type":"dropdownlist", "label":"Scan", "list":xnatScans}
                                cancel, scan = weasel.user_input(scanWindow, title="XNAT Download")
                                if cancel: return
                                scanName = scan[0]['list'][scan[0]['value']]
                                if scanName:
                                    if scanName == "All":
                                        dataset = session.projects[projectName].subjects[subjectName].experiments[experimentName]
                                        downloadFolder = selectXNATPathDownload(weasel)
                                        weasel.information("The selected images will be downloaded to the root folder of the TreeView. The download progress can be checked in the terminal and you may continue using Weasel.", "XNAT Download")
                                        dataset.download_dir(downloadFolder)
                                        weasel.information("Download completed!", "XNAT Download")
                                    else:
                                        dataset = session.projects[projectName].subjects[subjectName].experiments[experimentName].scans[scanName]
                                        downloadFolder = selectXNATPathDownload(weasel)
                                        weasel.information("The selected images will be downloaded to the root folder of the TreeView. The download progress can be checked in the terminal and you may continue using Weasel.", "XNAT Download") 
                                        dataset.download_dir(downloadFolder)
                                        weasel.information("Download completed!", "XNAT Download")
            # Load the directory again
            # This loads the whole directory again, so it might take some time. It would be quicker if there was an incremental approach to the TreeView (.xml or .csv).
            weasel.read_dicom_folder()
        # Delete Login Details
        del loginDetails, url, username, password
        session.disconnect()
        return

    except Exception as e:
        weasel.log_error('Error in function XNATapp.download: ' + str(e))
        if "Could not determine if login was successful!" in str(e):
            weasel.information("The login details inserted are incorrect!", "XNAT Download") 


def upload(weasel):
    try:
        url_input = {"type":"string", "label":"URL", "value":"https://test-ukrin.dpuk.org"}
        username_input = {"type":"string", "label":"Username", "value":"your.xnat.username"}
        password_input = {"type":"string", "label":"Password"}
        cancel, loginDetails = weasel.user_input(url_input, username_input, password_input, title="XNAT Login")
        if cancel: return
        url = loginDetails[0]['value'] # https://test-ukrin.dpuk.org
        username = loginDetails[1]['value']
        password = loginDetails[2]['value']
        with xnat.connect(url, user=username, password=password) as session:
            xnatProjects = [project.secondary_id for project in session.projects.values()]
            projectWindow = {"type":"dropdownlist", "label":"Project", "list":xnatProjects}
            cancel, project = weasel.user_input(projectWindow, title="XNAT Upload")
            if cancel: return
            projectID = project[0]['list'][project[0]['value']]
            projectName = [project.name for project in session.projects.values() if project.secondary_id == projectID][0]
            if projectName:
                xnatSubjects = [subject.label for subject in session.projects[projectName].subjects.values()]
                xnatSubjects.insert(0, "Upload at Project Level")
                subjectWindow = {"type":"dropdownlist", "label":"Subject", "list":xnatSubjects}
                cancel, subject = weasel.user_input(subjectWindow, title="XNAT Upload")
                if cancel: return
                subjectName = subject[0]['list'][subject[0]['value']]
                if subjectName:
                    if subjectName == "Upload at Project Level":
                        uploadPaths = selectXNATPathUpload(weasel)
                        uploadZipFile = zipFiles(uploadPaths)
                        weasel.information("The selected images will be uploaded to the selected project. The upload progress can be checked in the terminal and you may continue using Weasel.", "XNAT Upload")
                        try:
                            weasel.message("Uploading files to XNAT...", "XNAT Upload")
                            session.services.import_(uploadZipFile, overwrite='none', project=session.projects[projectName].id, content_type='application/zip')
                            weasel.close_message()
                        except:
                            warnings.warn('The zip file being uploaded contains files already present in the selected image session and the upload assistant cannot overwrite or give the option to not overwrite. \n The selected file or folder was pre-archived in the selected XNAT project. \n Please login to the portal and review and/or archive the images.')
                        weasel.information("Upload completed!", "XNAT Upload")
                    else:
                        xnatExperiments = [experiment.label for experiment in session.projects[projectName].subjects[subjectName].experiments.values()]
                        xnatExperiments.insert(0, "Upload at Subject Level")
                        experimentWindow = {"type":"dropdownlist", "label":"Experiment", "list":xnatExperiments}
                        cancel, experiment = weasel.user_input(experimentWindow, title="XNAT Upload")
                        if cancel: return
                        experimentName = experiment[0]['list'][experiment[0]['value']]
                        if experimentName:
                            if experimentName == "Upload at Subject Level":
                                uploadPaths = selectXNATPathUpload(weasel)
                                uploadZipFile = zipFiles(uploadPaths)
                                weasel.information("The selected images will be uploaded to the selected subject. The upload progress can be checked in the terminal and you may continue using Weasel.", "XNAT Upload")
                                try:
                                    weasel.message("Uploading files to XNAT...", "XNAT Upload")
                                    session.services.import_(uploadZipFile, overwrite='none', project=session.projects[projectName].id, subject=session.projects[projectName].subjects[subjectName].id, content_type='application/zip')
                                    weasel.close_message()
                                except:
                                    warnings.warn('The zip file being uploaded contains files already present in the selected image session and the upload assistant cannot overwrite or give the option to not overwrite. \n The selected file or folder was pre-archived in the selected XNAT project. \n Please login to the portal and review and/or archive the images.')
                                weasel.information("Upload completed!", "XNAT Upload")
                            else:
                                uploadPaths = selectXNATPathUpload(weasel)
                                uploadZipFile = zipFiles(uploadPaths)
                                weasel.information("The selected images will be uploaded to the selected experiment. The upload progress can be checked in the terminal and you may continue using Weasel.", "XNAT Upload")
                                try:
                                    weasel.message("Uploading files to XNAT...", "XNAT Upload")
                                    session.services.import_(uploadZipFile, overwrite='none', project=session.projects[projectName].id, subject=session.projects[projectName].subjects[subjectName].id, experiment=session.projects[projectName].subjects[subjectName].experiments[experimentName].id, content_type='application/zip')
                                    weasel.close_message()
                                except:
                                    warnings.warn('The zip file being uploaded contains files already present in the selected image session and the upload assistant cannot overwrite or give the option to not overwrite. \n The selected file or folder was pre-archived in the selected XNAT project. \n Please login to the portal and review and/or archive the images.')
                                weasel.information("Upload completed!", "XNAT Upload")
        # Curl Command
        headers = {"Content-Type": "application/json", "Accept": "*/*"}
        # Update the project's indices
        for individual_experiment in session.projects[projectName].experiments:
            curl_url = url + "/xapi/viewer/projects/" + session.projects[projectName].id + "/experiments/" + individual_experiment
            response = requests.post(curl_url, headers=headers, auth=(username, password))
        # Delete Login Details
        del loginDetails, url, username, password
        # Delete ZIP File
        os.remove(uploadZipFile)
        session.disconnect()
    except Exception as e:
        weasel.log_error('Error in function XNATapp.upload: ' + str(e))
        if "Could not determine if login was successful!" in str(e):
            weasel.information("The login details inserted are incorrect!", "XNAT Download") 

    
def selectXNATPathDownload(weasel, tree_view_dir=True):
    if tree_view_dir == False:
        directory = weasel.selectFolder(title="Select the directory where you wish to download")
    else:
        directory = os.path.dirname(weasel.objXMLReader.file)
    return directory


def selectXNATPathUpload(weasel, tree_view=True):
    listPaths = []
    if tree_view == True:
        images = weasel.images()
        for image in images:
            listPaths.append(image.path)
    else:
        directory = weasel.selectFolder(title="Select the directory with the files you wish to upload")
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