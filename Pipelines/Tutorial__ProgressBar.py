"""
Tutorial showing the use of the Progress Bar in the Weasel GUI.
"""


from Displays.Messaging import ProgressBar

def main(weasel):

    maximum = 50000
    progress = ProgressBar(
        parent = weasel, 
        message = 'Look at my progress!',
        maximum = maximum)
    for i in range(maximum):
        progress.set_value(i)

    maximum = 100000
    progress.set_maximum(maximum)
    progress.set_message('And even more progress!!!!!!!!!!!!!')
    for i in range(maximum):
        progress.set_value(i)

    progress.close()


    outside = 100
    inside = 50
    progress_inside = ProgressBar(
        parent = weasel, 
        message = 'I can even make progress..',
        maximum = inside)
    progress_outside = ProgressBar(
        parent = weasel, 
        message = 'WHILE I am making progress!!',
        maximum = outside)
    for i in range(outside):
        progress_outside.set_value(i)
        for j in range(inside):
            progress_inside.set_value(j)

    progress_inside.close()
    progress_outside.close()