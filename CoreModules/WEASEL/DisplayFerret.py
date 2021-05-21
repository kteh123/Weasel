from PyQt5.QtCore import  Qt
from PyQt5.QtWidgets import QMdiSubWindow, QLabel
from PyQt5.QtGui import  QIcon
#This import statement causes problems
#import weasel_apps.TRISTAN.Ferret.Ferret as ferret
import CoreModules.WEASEL.CloseAllSubWindows as closeAllSubWindows
import logging
logger = logging.getLogger(__name__)

#FERRET_LOGO = 'images\\FERRET_LOGO.png'

def displayFerret(self):
        """
        Displays Ferret in a sub window 
        """
        try:
            logger.info("Display.displayFerret called")
            #closeAllSubWindows.main(self)
            self.subWindow = QMdiSubWindow(self)
            self.subWindow.setAttribute(Qt.WA_DeleteOnClose)
            self.subWindow.setWindowFlags(Qt.CustomizeWindowHint | 
                                      Qt.WindowCloseButtonHint | 
                                      Qt.WindowMinimizeButtonHint |
                                      Qt.WindowMaximizeButtonHint)
            
            #ferretWidget = ferret(self.subWindow, self.statusBar)
            #self.subWindow.setWidget(ferretWidget.returnFerretWidget())
            self.subWindow.setWidget(QLabel("Ferret")) #Test string
            
            self.subWindow.setWindowTitle('Ferret')
            #self.subWindow.setWindowIcon(QIcon(FERRET_LOGO))
            self.mdiArea.addSubWindow(self.subWindow)
            self.subWindow.showMaximized()
        except Exception as e:
            print('Error in displayFerret: ' + str(e))
            logger.error('Error in displayFerret: ' + str(e)) 
