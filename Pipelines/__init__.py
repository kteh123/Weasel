"""
A collection of Weasel buttons that contain processes and calculations that are performed in the GUI.

Some of the buttons (the ones where the filename starts with "Tutorial__") are good examples of how to develop new pipelines for Weasel and how to extend its usage.

The golden rule for every pipeline is that every file/button contains a main function with "weasel" as the only input argument: `def main(weasel): `. The developer can import and use any python packages that are necessary for processing within each pipeline.

For more information and details about the functions and classes belonging to the input argument "weasel", please consult the documentation of the `API` module. Examples such as `weasel.images()` and `weasel.progress_bar()` can be found in the `ReadWrite.py` and `Messaging.py` files respectively inside the `API` folder.
"""