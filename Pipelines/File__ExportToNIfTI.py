def isEnabled(weasel):
    return True

def main(weasel):
    try:
        seriesList = weasel.series()
        local_path = weasel.select_folder()
        if local_path is None: return
        for i, series in enumerate(seriesList):
            weasel.progress_bar(max=len(seriesList), index=i+1, msg="Saving series " + series.label + " to NIfTI")
            series.export_as_nifti(directory=local_path)
        weasel.close_progress_bar()
        weasel.information(msg="Selected series successfully saved as NIfTI", title="Export to NIfTI")
    except Exception as e:
        # Record error message in the log and prints in the terminal
        weasel.log_error('Error in function ExportNIfTI.main: ' + str(e))
        # If we want to show the message in the GUI
        weasel.error(msg=str(e), title="Error Exporting to NIfTI")