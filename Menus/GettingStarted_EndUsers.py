
from Menus.Tutorial import main as menu_tutorial

def main(weasel):
   
    weasel.menu_file()
    weasel.menu_view()
    weasel.menu_edit()

    menu_tutorial(weasel)
    
    weasel.menu_xnat()
    
    weasel.menu_help()
  