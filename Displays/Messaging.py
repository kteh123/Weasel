"""
Classes that provide pop-up windows that display messages 
and progress bars to the user.
"""

from PyQt5.QtCore import  Qt
from PyQt5.QtWidgets import (QApplication,                         
        QMdiArea, QWidget, QVBoxLayout, 
        QMdiSubWindow, QMainWindow,  
        QStatusBar, QLabel, 
        QTreeWidgetItem,
        QProgressBar)



class Message():
    """
    Class that provides a pop-up window that displays a message 
    to the user.
    """
    def __init__(self,
            parent = None,
            message = "Your message here",
            title = "Message ..."):
        """
        If parent is not None, creates the MDI subwindow 
        that will act as a pop-up window. Otherwise a QWidget object is 
        displayed as a subwindow.

        A label to display the message is created.
        A QWidget widget is also created and vertical layout is added to it.
        The message label is added to the vertical layout.

        If parent is not None, then an MDI subwindow is created and 
        the above widget set as its widget.  Othewise, the above widget
        is displayed as a window.
        """
        self.parent = parent

        if parent is None:
            self.app = QApplication([])
            
        self.label = QLabel('<H4>' + message + '</H4>')
        self.widget = QWidget()
        self.widget.setLayout(QVBoxLayout())
        self.widget.layout().addWidget(self.label)
        self.widget.layout().setAlignment(Qt.AlignTop)
        self.widget.adjustSize()  
        
        if parent is not None:
            self.msgSubWindow = QMdiSubWindow(parent.mdiArea)
            self.msgSubWindow.setAttribute(Qt.WA_DeleteOnClose)
            self.msgSubWindow.setObjectName("Message")
            self.msgSubWindow.setWindowTitle(title)
            self.msgSubWindow.setWidget(self.widget)
            self.parent.mdiArea.addSubWindow(self.msgSubWindow)
             
        self.widget.show()
        if parent is None:
            self.app.exec()


    def set_message(self, message):
        """
        Sets the message text. 

        Input argument
        **************
        message - message string. 
        """
        self.label.setText('<H4>' + message + '</H4>')
        self.widget.adjustSize()
        
    def close(self):
        """
        Closes the subwindow displaying the message
        """
        if self.parent is not None:
            self.msgSubWindow.close()



class ProgressBar():
    """
    Class that provides a pop-up window with a message
    and progress bar to the user.
    """
    def __init__(self,
            parent = None,
            value = 0,
            maximum = 100,
            message = "Your message here",
            title = "Progress bar"):
        """
        A QWidget widget is created and a vertical layout added to it.
        A progress bar and label to display a message are added to the
        vertical layout. 

        If parent is not None, then an MDI subwindow is created and 
        the above widget set as its widget.
        """
        self.parent = parent

        if parent is None:
            self.app = QApplication([])
 
        self.label = QLabel('<H4>' + message + '</H4>')
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)
        self.widget = QWidget()
        self.widget.setLayout(QVBoxLayout())
        self.widget.layout().addWidget(self.label)
        self.widget.layout().addWidget(self.progress_bar)
        self.widget.layout().setAlignment(Qt.AlignTop)
        self.widget.adjustSize()  
        
        if parent is not None:
            self.msgSubWindow = QMdiSubWindow(parent.mdiArea)
            self.msgSubWindow.setAttribute(Qt.WA_DeleteOnClose)
            self.msgSubWindow.setObjectName("Progress bar")
            self.msgSubWindow.setWindowTitle(title)
            self.msgSubWindow.setWidget(self.widget)
            self.parent.mdiArea.addSubWindow(self.msgSubWindow)
             
        self.widget.show()
        QApplication.processEvents()

    def set_value(self, value):
        """
        Sets the value property (amount of progress) of the progress bar
        """
        self.progress_bar.setValue(value) 

    def set_maximum(self, maximum):
        """
        Sets the maximum value (value when progress is complete)
        of the progress bar.
        """
        self.progress_bar.setMaximum(maximum)

    def set_message(self, message):
        """
        Sets the message text. 

        Input argument
        **************
        message - message string. 
        """
        self.label.setText('<H4>' + message + '</H4>')
        self.widget.adjustSize()
        
    def close(self):
        """
        Closes the subwindow displaying the progress bar & message
        """
        if self.parent is not None:
            self.msgSubWindow.close()

