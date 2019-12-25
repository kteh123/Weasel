
TRISTAN_GREY = """
                /* warm grey QWidget{background-color: rgb(215, 210, 203);} */
                QPushButton {
                             background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #CCCCBB, stop: 1 #FFFFFF);
                             border-width: 3px;
                             border-style: solid;
                             border-color: rgb(10, 10, 10);
                             border-radius: 5px;
                             text-align: centre;
                             font-weight: bold;
                             font-size: 9pt;
                             padding: 6px;} 

                QPushButton:hover {
                                   background-color: rgb(175, 175, 175);
                                   border-color: rgb(200, 51, 255);}

                QPushButton:pressed {background-color: rgb(112, 112, 112);}

                QComboBox {
                    border: 1px solid gray;
                    border-radius: 3px;
                    padding: 1px 18px 1px 3px;
                    min-width: 6em;
                    font-size: 9pt;
                    font-weight: bold;}
                
                QComboBox:hover {
                    background-color: rgb(175, 175, 175);
                    border-color: rgb(200, 51, 255);}

                QGroupBox{
                        background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #D9D9D9, stop: 1 #FFFFFF);
                        border: 2px solid gray;
                        border-radius: 5px;
                        padding: 1em;
                        margin-top: 1em; 
                        font-weight: bold;
                        font-size: 9pt;
                          }

                QLabel{ padding: 4px;
                        min-height: 1em;
                        text-align: centre;
                        font-weight: bold;
                        font-size: 9pt;
                        background: transparent;
                        }

                QDoubleSpinBox{
                    min-width: 4.5em;
                    padding: 4px;
                    font-size: 8pt;
                    font-weight: bold;}

                QDoubleSpinBox:hover{
                                     background-color: rgb(230, 230, 230);
                                     border-color: rgb(200, 51, 200);}

                QCheckBox{
                    width: 5px;
                    margin: 5px;
                    border-width: 5px;
                    padding: 5px;
                    spacing: 5px;
                    font-weight: bold;
                    font-size: 9pt;
                    background: transparent;}

                QCheckBox:hover{
                        background-color: rgb(175, 175, 175);
                        border-color: rgb(200, 51, 255);}

                """
