
def buildToolsMenu(self, toolsMenu):
        #result = getattr(obj, "method")(args)
        try:
            pathToolsMenuXML = 'Developer\\Tools\\toolsMenu.xml'
            toolsXMLtree = ET.parse(pathToolsMenuXML)
            tools = toolsXMLtree.getroot()
            for tool in tools:
                action = tool.find('./action').text
                shortcut = tool.find('./shortcut').text
                tooltip = tool.find('./tooltip').text
                print (tooltip)
                module = tool.find('./module').text
                print(module)
                function = tool.find('./function').text

                self.button = QAction(action, self)
                self.button.setShortcut(shortcut)
                self.button.setStatusTip(tooltip)
                if module == 'self':
                   method = getattr(self,function)
                   self.button.triggered.connect(method)
                else:
                   print(module, function)
                   method = getattr(copyDICOM_Image,function)(self)
                   self.button.triggered.connect(lambda:method)
                self.button.setEnabled(False)
                toolsMenu.addAction(self.button)

                #menu = QtWidgets.QMenu()
#items = {'item 1': lambda: self.printMe('item 1'), 
        # 'item 2': lambda: self.printMe('item 2'), 
        # 'item 3': lambda: self.printMe('item 3')}
#for key, value in items.items():
 #   menu.addAction(key, value)

        self.binaryOperationsButton = QAction('Binary Operation', self)
        self.binaryOperationsButton.setShortcut('Ctrl+B')
        self.binaryOperationsButton.setStatusTip('Performs binary operations on two images')
        self.binaryOperationsButton.triggered.connect(self.displayBinaryOperationsWindow)
        self.binaryOperationsButton.setEnabled(False)
        toolsMenu.addAction(self.binaryOperationsButton)

        self.copySeriesButton = QAction('Copy Series', self)
        self.copySeriesButton.setShortcut('Ctrl+C')
        self.copySeriesButton.setStatusTip('Copy a DICOM series')
        self.copySeriesButton.triggered.connect(
            lambda:copyDICOM_Image.copySeries(self))
        self.copySeriesButton.setEnabled(False)
        toolsMenu.addAction(self.copySeriesButton)

        self.invertImageButton = QAction('Invert Image', self)
        self.invertImageButton.setShortcut('Ctrl+I')
        self.invertImageButton.setStatusTip('Invert a DICOM Image or series')
        self.invertImageButton.triggered.connect(
            lambda: invertDICOM_Image.invertImage(self)
            )
        self.invertImageButton.setEnabled(False)
        toolsMenu.addAction(self.invertImageButton)
        except Exception as e:
            print('Error in function buildToolsMenu: ' + str(e))