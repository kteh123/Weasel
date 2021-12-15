
WEASEL_GREY = """
                QPushButton {
                             background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #CCCCBB, stop: 1 #FFFFFF);
                             border-width: 3px;
                             margin: 1px;
                             border-style: solid;
                             border-color: rgb(10, 10, 10);
                             border-radius: 5px;
                             text-align: centre;
                             color: black;
                             font-weight: bold;
                             font-size: 9pt;
                             padding: 3px;} 

                QPushButton:hover {
                                   background-color: rgb(175, 175, 175);
                                   border: 1px solid red;
                                   }
                                   
                QPushButton:pressed {background-color: rgb(112, 112, 112);}


                QComboBox {
                    margin: 0.25em;
                    border: 1px solid gray;
                    border-radius: 3px;
                    padding: 0px 0px 0px 0px;
                    min-width: 4em;
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
                        padding: 0;
                        margin-top: 0.3em; 
                        margin-left: 0; 
                        margin-right: 0;
                        margin-bottom: 0em;
                        font-weight: bold;
                        font-size: 8pt;
                          }

                QGroupBox:title {subcontrol-position: top middle; 
                    padding: -7px 0px 0px 3px; 
                    color:black;}

                QLabel{ padding: 1px;
                        min-height: 1em;
                        text-align: centre;
                        font-weight: bold;
                        font-size: 9pt;
                        background: transparent;
                        margin: 0em;
                        }

                QTableWidget{color: black;}

                QSpinBox{
                    font-size: 9pt;
                    font-weight: bold;}

                QSpinBox::up-arrow{max-height: 16px;}

                QSpinBox::down-arrow{max-height: 16px;}

                QDoubleSpinBox{
                    font-size: 9pt;
                    font-weight: bold;}

                QDoubleSpinBox::up-arrow{max-height: 16px;}

                QDoubleSpinBox::down-arrow{max-height: 16px;}

                QCheckBox{
                    width: 5px;
                    margin: 0.5em;
                    min-height: 1em;
                    border-width: 5px;
                    padding: 4px;
                    spacing: 5px;
                    font-weight: bold;
                    font-size: 9pt;
                    background: transparent;}

                QCheckBox:hover{
                        background-color: rgb(175, 175, 175);
                        border-color: rgb(200, 51, 255);}
                
                QTreeView {
                    background-color:  qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,  stop: 0 #CCCCBB, stop: 1 #FFFFFF);
                    show-decoration-selected: 1;
                    color: black;
                    }

                QTreeView::branch:hover {
                    background: #cce5ff;
                    }

               QTreeView::branch:selected {
                    background: #4da3ff;
                    color: white;
                    }

                QTreeView::branch:selected:hover {
                    background: #CCCCBB;
                    color: white;
                    }

                QTreeView::item{
                    margin-right:0;}

                QTreeView::item:selected {
                    background: #4da3ff;
                    color:white;
                    }

                QTreeView::item:hover {
                    background: #cce5ff;
                    color: white;
                    }

                QTreeView::item:selected:hover {
                    background: #CCCCBB;
                    color: black;
                    }

QListWidget {
    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                                            stop: 0 #CCCCBB, stop: 1 #FFFFFF);
    }

QListWidget {
alternate-background-color: yellow;
}

QListWidget {
    show-decoration-selected: 1; /* make the selection span the entire width of the view */
}

QListWidget::item:alternate {
    background: #EEEEEE;
}


QListWidget::item:selected:hover {
                    background: darkblue;
                    color: white;
                    }

QListWidget::item:hover {
                    background: #cce5ff;
}


QTableWidget {
    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                                            stop: 0 #CCCCBB, stop: 1 #FFFFFF);
    }
                

                QTableWidget::item {
                    border: 5px solid rgba(68, 119, 170, 150);
                    background-color:rgba(68, 119, 170, 125);
                    }

            QHeaderView, QHeaderView::section {
                background-color: rgba(125, 125, 125, 125);
                font-weight: bold;
                font-size: x-large;
                }

                """
