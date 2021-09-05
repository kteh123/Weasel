# from tqdm import trange, tqdm

from PyQt5.QtGui import (QCursor)
from PyQt5.QtWidgets import (QApplication, QMessageBox)
from PyQt5.QtCore import  Qt

import CoreModules.WEASEL.MessageWindow as messageWindow


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

    def question(self, question="You wish to proceed (OK) or not (Cancel)?", title="Message Window Title"):
        """
        Displays a question window in the User Interface with the title in "title" and
        with the question in "question". The 2 strings in the arguments are the input by default.
        The user has to click either "OK" or "Cancel" in order to continue using the interface.
        It returns 0 if reply is "Cancel" and 1 if reply is "OK".
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

    def message(self, msg="Message in the box", title="Window Title"):
        """
        Displays a Message window with the text in "msg" and the title "title".
        """
        if self.cmd == True:
            print("=====================================")
            print(title + ": " + msg)
            print("=====================================")
        else:
            messageWindow.displayMessageSubWindow(self, "<H4>" + msg + "</H4>", title)

    def close_message(self):
        """
        Closes the message window 
        """
        if self.cmd == False:
            self.msgSubWindow.close()

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
            messageWindow.displayMessageSubWindow(self, ("<H4>" + msg + "</H4>").format(index), title)
            messageWindow.setMsgWindowProgBarMaxValue(self, max)
            messageWindow.setMsgWindowProgBarValue(self, index)

    def update_progress_bar(self, index=0, msg=None):
        """
        Updates the progress bar with a new index.
        """
        if self.cmd == True:
            if msg is not None: print(msg)
            self.tqdm_prog.update(index)
        else:
            messageWindow.setMsgWindowProgBarValue(self, index, msg)

    def close_progress_bar(self):
        """
        Closes the Progress Bar.
        """
        if self.cmd == True and self.tqdm_prog:
            self.tqdm_prog.close()
        else:
            messageWindow.hideProgressBar(self)
            messageWindow.closeMessageSubWindow(self)

    def set_status(self, msg="I'm done with this!"):
        """
        Displays a message in the status bar.
        """
        self.statusBar.showMessage(msg)
