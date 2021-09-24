from PyQt5.QtCore import  Qt
from PyQt5.QtWidgets import (QApplication,                         
        QMdiArea, QWidget, QVBoxLayout, 
        QMdiSubWindow, QMainWindow,  
        QStatusBar, QLabel, 
        QTreeWidgetItem,
        QProgressBar)



class Message():

    def __init__(self,
            parent = None,
            message = "Your message here"):

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
            self.msgSubWindow.setWindowTitle("Message..")
            self.msgSubWindow.setWidget(self.widget)
             
        self.widget.show()
        if parent is None:
            self.app.exec()

    def set_message(self, message):
        self.label.setText('<H4>' + message + '</H4>')
        self.widget.adjustSize()
        
    def close(self):
        if self.parent is not None:
            self.msgSubWindow.close()



class ProgressBar():

    def __init__(self,
            parent = None,
            value = 0,
            maximum = 100,
            message = "Your message here"):

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
            self.msgSubWindow.setWindowTitle("Progress bar")
            self.msgSubWindow.setWidget(self.widget)
             
        self.widget.show()
        QApplication.processEvents()

    def set_value(self, value):
        self.progress_bar.setValue(value) 

    def set_maximum(self, maximum):
        self.progress_bar.setMaximum(maximum)

    def set_message(self, message):
        self.label.setText('<H4>' + message + '</H4>')
        self.widget.adjustSize()
        
    def close(self):
        if self.parent is not None:
            self.msgSubWindow.close()



