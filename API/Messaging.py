# from tqdm import trange, tqdm

from PyQt5.QtGui import (QCursor)
from PyQt5.QtWidgets import (QApplication, QMessageBox)
from PyQt5.QtCore import  Qt

from Displays.ProgressBar import ProgressBar
from Displays.Message import Message


class Messaging():
    """
    An API with GUI elements for messaging to the user. 
    """

    def cursor_arrow_to_hourglass(self):
        """
        Turns the arrow shape for the cursor into an hourglass. 
        """   
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

    def cursor_hourglass_to_arrow(self):
        """
        Restores the cursor into an arrow after it was set to hourglass 
        """   
        QApplication.restoreOverrideCursor()     

    def information(self, msg="Message in the box", title="Window Title"):
        """
        Display a Window with information message and the user must press 'OK' to continue.
        """
        if self.cmd == True:
            print("=====================================")
            print("INFORMATION")
            print(title + ": " + msg)
            print("=====================================")
        else:
            QMessageBox.information(self, title, msg)

    def warning(self, msg="Message in the box", title="Window Title"):
        """
        Display a Window with warning message and the user must press 'OK' to continue.
        """
        if self.cmd == True:
            print("=====================================")
            print("WARNING")
            print(title + ": " + msg)
            print("=====================================")
        else:
            QMessageBox.warning(self, title, msg)

    def error(self, msg="Message in the box", title="Window Title"):
        """
        Display a Window with error message and the user must press 'OK' to continue.
        """
        if self.cmd == True:
            print("=====================================")
            print("ERROR")
            print(title + ": " + msg)
            print("=====================================")
        else:
            QMessageBox.critical(self, title, msg)

    def question(self, question="Do you wish to proceed?", title="Question for the user"):
        """Displays a question window in the User Interface
        
        The user has to click either "OK" or "Cancel" in order to continue using the interface.
        It returns False if reply is "Cancel" and True if reply is "OK".
        """
        if self.cmd == True:
            print("=====================================")
            print("QUESTION")
            reply = input(question)
            print("=====================================")
            if reply == "OK" or reply == "Ok" or reply == "ok" or reply == "Y" or reply == "y" or reply == "YES" \
                or reply == "yes" or reply == "Yes" or reply == "1" or reply == '':
                return True
            else:
                return False
        else:
            buttonReply = QMessageBox.question(self, title, question, 
                          QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
            if buttonReply == QMessageBox.Ok:
                return True
            else:
                return False

    def message(self, msg="Message in the box", title="Message.."):
        """
        Displays a Message window with the text in "msg" and the title "title".
        """
        if self.cmd == True:
            print("=====================================")
            print(title + ": " + msg)
            print("=====================================")
        else:
            self.msgWindow = Message(parent = self, message = "<H4>" + msg + "</H4>")

    def close_message(self):
        """
        Closes the message window 
        """
        if self.cmd == False:
            self.msgWindow.close()

    def progress_bar(self, max=1, index=0, msg="Progressing...", title="Progress Bar"):
        """
        Displays a progress bar with the unit set in "index".

        Note: launching a new progress bar at each iteration costs time, so this
        should only be used in iterations where the progress bar is updated infrequently
        For iterations with frequent updates, use progress_bar outside the iteration
        and then update_progress_bar inside the iteration
        """
        if self.cmd == True:
            print("=====================================")
            print(title + ": " + msg)
            print("=====================================")
            self.tqdm_prog = tqdm(total=max)
            self.tqdm_prog.update(index)
        else:
            for subWin in self.mdiArea.subWindowList():
                if subWin.objectName() == "Progress bar":
                    subWin.close()
            self.progressBar = ProgressBar(
                parent = self, 
                message = ("<H4>" + msg + "</H4>").format(index), 
                value = index, 
                maximum = max)

    def update_progress_bar(self, index=0, msg=None):
        """
        Updates the progress bar with a new index.
        """
        if self.cmd == True:
            if msg is not None: print(msg)
            self.tqdm_prog.update(index)
        else:
            self.progressBar.set_value(index)

    def close_progress_bar(self):
        """
        Closes the Progress Bar.
        """
        if self.cmd == True and self.tqdm_prog:
            self.tqdm_prog.close()
        else:
            self.progressBar.close()

    def set_status(self, msg="I'm done with this!"):
        """
        Displays a message in the status bar.
        """
        self.statusBar.showMessage(msg)
