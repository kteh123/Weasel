def main(weasel):

    menu = weasel.menu("Help")  
        
    menu.item(
        label = 'Help', 
        icon = 'Documents/images/question-mark.png', 
        pipeline = 'Help__WeaselWeb')