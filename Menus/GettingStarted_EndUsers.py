"""
This menu illustrates an approach to building menus through the Weasel Programming Interface.

It uses the Weasel default menus "File", View", "Edit", "Tutorial", "XNAT", and "Help".

This menu is best suited to demo Weasel and it's the default menu in `config.xml`.
"""
from Menus.Tutorial import main as menu_tutorial

def main(weasel):
   
    weasel.menu_file()
    weasel.menu_view()
    weasel.menu_edit()

    menu_tutorial(weasel)
    
    weasel.menu_xnat()
    
    weasel.menu_help()
  