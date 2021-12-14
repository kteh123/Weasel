"""
Programming interfaces for the Weasel menus. 
"""

from Menus.File import main as menuFile
from Menus.View import main as menuView
from Menus.Edit import main as menuEdit
from Menus.Help import main as menuHelp
from Menus.XNAT import main as menuXnat

class EditMenus():

    def menu(self, label = "Menu"):
        """
        Interface for Python menu builder
        """
        return self.menuBuilder.newSubMenu(label)

    def menu_file(self):
        """
        Returns the default file menu
        """    
        return menuFile(self)  

    def menu_view(self):
        """
        Returns the default view menu
        """    
        return menuView(self) 

    def menu_edit(self):
        """
        Returns the default edit menu
        """    
        return menuEdit(self) 

    def menu_help(self):
        """
        Returns the default help menu
        """    
        return menuHelp(self)
    
    def menu_xnat(self):
        """
        Returns the default XNAT menu
        """    
        return menuXnat(self) 

    def refresh_menus(self):
        """
        Refreshes the enabled status of each menu item
        """  
        for menu in self.menuBuilder.listMenus:
            for menuItem in menu.actions():
                if not menuItem.isSeparator():
                    module = menuItem.data()
                    if hasattr(module, "enable"):
                        enable = getattr(module, "enable")(self)
                        menuItem.setEnabled(enable)                