"""
This folder contains Python and XML files that define the menus in the
menu bar at the top of the Weasel GUI. 

The following files contain the definition of standard Weasel menus 
that allow the user to access key Weasel functionality
(see individual files for more details):

File.py - Definition of the File menu

Edit.py - Definition of the Edit menu

Help.py - Definition of the Help menu

View.py - Definition of the View menu

XNAT.py - Definition of the XNAT menu

Tutorial.py - Definition the Tutorial menu. 

The above files can be combined in an overarching menu file 
that defines all the menus in the menu bar. The following files
are examples of this:
 
GettingStarted_Developers.py

GettingStarted_EndUsers.py

A developer may create their own bespoke menu file similiar to these
2 files including their own menus as well as including any or all
of the above standard Weasel menus. To do this a developer may wish
to copy, rename and edit one of the above 2 files.

Every menu file must include a function called main 
with the argument weasel; thus,

def main(weasel):

within the main function, the following function calls will include 
the standard Weasel menus,

    weasel.menu_file()  file menu
    weasel.menu_view()  view menu
    weasel.menu_edit()  edit menu
    weasel.menu_xnat()  XNAT menu
    weasel.menu_help()  help menu

The following function call will create a new menu called "My Menu" 
in the menu bar,

myMenu = weasel.menu("My Menu")

Items in this menu are created with the following function call,

    myMenu.item(

        label = 'My Menu Item',

        tooltip = 'My menu item allows the user to .......',

        pipeline = 'My_Module_Name')

where 
      
      label = Menu item name in the drop down menu.

      tooltip = Menu item tooltip displayed when the mouse pointer 
                hovers over the menu item.

      pipeline = The name of the Python module without the .py extension
                that contains the functionality invoked by the this menu item.
                When this menu item is selected, it expects to call a function 
                called main in this module.  Therefore, this module must 
                contain a function with the definition 

                    def main(weasel):

                that contains the logic underpinning the functionality of this
                menu item.

The following function call will draw a horizontal line in the menu 
to separate different parts

    menu.separator()

The name of the new menu file must be included in the config.xml file, that is 
in the root of the Weasel source code, enclosed in <menu_config_file> tags thus

    <menu_config_file>GettingStarted_EndUsers.py</menu_config_file>

Menus.xml is an xml definition of several menus in the menu bar of Weasel
"""
