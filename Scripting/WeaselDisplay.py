from PyQt5.QtWidgets import (QApplication, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
import CoreModules.WEASEL.MessageWindow as messageWindow
import CoreModules.WEASEL.TreeView as treeView

class WeaselDisplay():
    """
    A class for accessing GUI elements from within a pipeline script. 
    """
 
    def cursor_arrow_to_hourglass(self):
        """
        Turns the arrow shape for the cursor into an hourglass (for length calculations). 
        """   
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

    def cursor_hourglass_to_arrow(self):
        """
        Restores the cursor into an arrow after it was set to hourglass 
        """   
        QApplication.restoreOverrideCursor()

    def progress_bar(self, max=1, index=0, msg="Iteration Number {}", title="Progress Bar"):
        """
        Displays a progress bar with the unit set in "index".
        Note: launching a new progress bar at each iteration costs time, so this
        should only be used in iterations where the progress bar is updated infrequently
        For iterations with frequent updates, use progress_bar outside the iteration
        and then update_progress_bar inside the iteration
        """
        messageWindow.displayMessageSubWindow(self, ("<H4>" + msg + "</H4>").format(index), title)
        messageWindow.setMsgWindowProgBarMaxValue(self, max)
        messageWindow.setMsgWindowProgBarValue(self, index)

    def update_progress_bar(self, index=0):
        """
        Updates the progress bar with a new index.
        """
        messageWindow.setMsgWindowProgBarValue(self, index)

    def close_progress_bar(self):
        """
        Closes the Progress Bar.
        """
        messageWindow.hideProgressBar(self)
        messageWindow.closeMessageSubWindow(self)

    def message(self, msg="Hello world!", title="Message window"):
        """
        Displays a window in the User Interface with the title in "title" and
        with the message in "msg". 
        """
        messageWindow.displayMessageSubWindow(self, "<H4>" + msg + "</H4>", title)

    def close_message(self):
        """
        Closes the message window 
        """
        self.msgSubWindow.close()

    def information(self, msg="Are you OK today?", title="Message window"):
        """
        Displays an information window in the User Interface with the title in "title" and
        with the message in "msg". The user has to click "OK" in order to continue using the interface.
        """
        QMessageBox.information(self, title, msg)

    def question(self, msg="Shall we carry on?", title="Message Window Title"):
        """
        Displays a question window in the User Interface with the title in "title" and
        with the question in "msg". 
        The user has to click either "OK" or "Cancel" in order to continue using the interface.
        It returns 0 if reply is "Cancel" and 1 if reply is "OK".
        """
        buttonReply = QMessageBox.question(self, title, msg, 
                      QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
        if buttonReply == QMessageBox.Ok:
            return 1
        else:
            return 0

    def close_all_windows(self):
        """
        Closes all open windows.
        """
        self.mdiArea.closeAllSubWindows()

    def folder(self, msg='Please select a folder'):
        """
        Ask the user to select a folder
        """
        return QFileDialog.getExistingDirectory(self,
            msg, 
            self.weaselDataFolder, 
            QFileDialog.ShowDirsOnly)

    def refresh(self):
        """
        Displays the XML tree saved on disk
        """  
        xml = self.xml()     
        treeView.makeDICOMStudiesTreeView(self, xml)

    def close_project(self):
        """
        Closes the DICOM folder
        """
        if self.project_open():
            treeView.closeTreeView(self)
            self.DICOMFolder = ''
